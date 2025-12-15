import pandas as pd
import urllib.parse
from sqlalchemy import create_engine, text

# Vanna Tools
from vanna.tools import RunSqlTool
from vanna.integrations.mssql import MSSQLRunner
from vanna.integrations.postgres import PostgresRunner
from vanna_core.config import Config

# --- 1. SAFE POSTGRES WRAPPER (Adds Logging) ---
class SafePostgresRunner(PostgresRunner):
    """
    Wraps the native PostgresRunner to add debug logging.
    """
    async def run_sql(self, args, context=None) -> pd.DataFrame:
        # Extract SQL string from the args object (Vanna 2.0 standard)
        sql = args.sql if hasattr(args, 'sql') else args
        
        print(f"\n🚀 [DEBUG] Executing SQL:\n{sql}\n")

        try:
            # Call the parent class's run_sql
            df = await super().run_sql(args, context)
            
            if df is not None:
                print(f"✅ [DEBUG] Query returned {len(df)} rows.")
            else:
                print("⚠️ [DEBUG] Query returned None.")
                
            return df
        except Exception as e:
            print(f"❌ [DEBUG] SQL Execution Error: {e}")
            # We re-raise so Vanna knows it failed
            raise e

# --- 2. SAFE MSSQL WRAPPER ---
class SafeMSSQLRunner(MSSQLRunner):
    def __init__(self, engine):
        self.engine = engine

    async def run_sql(self, sql, context=None, *args, **kwargs) -> pd.DataFrame:
        if hasattr(sql, 'sql'):
            sql = sql.sql

        print(f"\n🚀 [DEBUG] Executing MSSQL:\n{sql}\n")

        try:
            with self.engine.connect() as conn:
                df = pd.read_sql(text(sql), conn)
            
            # Clean binary columns
            if df is not None and not df.empty:
                for col in df.columns:
                    if df[col].dtype == 'object':
                        first_valid_index = df[col].first_valid_index()
                        if first_valid_index is not None:
                            first_valid = df[col].loc[first_valid_index]
                            if isinstance(first_valid, bytes):
                                df[col] = df[col].apply(lambda x: x.hex() if isinstance(x, bytes) else x)
            return df
        except Exception as e:
            print(f"❌ [DEBUG] MSSQL Error: {e}")
            raise e

# --- 3. GENERIC WRAPPER (MySQL) ---
class SafeGenericRunner:
    def __init__(self, engine):
        self.engine = engine

    async def run_sql(self, sql, context=None, *args, **kwargs) -> pd.DataFrame:
        if hasattr(sql, 'sql'):
            sql = sql.sql
        try:
            with self.engine.connect() as conn:
                return pd.read_sql(text(sql), conn)
        except Exception as e:
            print(f"❌ [DEBUG] Generic DB Error: {e}")
            raise e

# --- FACTORY ---
class DBFactory:
    @staticmethod
    def get_db_tool():
        db_type = Config.DB_TYPE
        
        # --- OPTION A: POSTGRESQL ---
        if db_type == "postgres":
            # Use our Safe wrapper instead of the raw runner
            runner = SafePostgresRunner(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD
            )
            return RunSqlTool(sql_runner=runner)

        # --- OPTION B: MSSQL ---
        elif db_type == "mssql":
            driver = Config.DB_DRIVER.replace(' ', '+')
            user = Config.DB_USER
            password = urllib.parse.quote_plus(Config.DB_PASSWORD) if Config.DB_PASSWORD else ""
            
            if not user:
                url = (f"mssql+pyodbc://@{Config.DB_HOST}/{Config.DB_NAME}"
                       f"?driver={driver}&trusted_connection=yes&TrustServerCertificate=yes")
            else:
                url = (f"mssql+pyodbc://{user}:{password}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
                       f"?driver={driver}&TrustServerCertificate=yes")

            engine = create_engine(url)
            runner = SafeMSSQLRunner(engine=engine)
            return RunSqlTool(sql_runner=runner)

        # --- OPTION C: MYSQL ---
        elif db_type == "mysql":
            password = urllib.parse.quote_plus(Config.DB_PASSWORD) if Config.DB_PASSWORD else ""
            url = f"mysql+pymysql://{Config.DB_USER}:{password}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
            
            engine = create_engine(url)
            runner = SafeGenericRunner(engine=engine)
            return RunSqlTool(sql_runner=runner)
        
        else:
            raise ValueError(f"Unsupported DB Type: {db_type}")