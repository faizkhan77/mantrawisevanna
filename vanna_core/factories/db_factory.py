import pandas as pd
import urllib.parse
from sqlalchemy import create_engine, text
from vanna_core.config import Config
from vanna.tools import RunSqlTool
from vanna.integrations.mssql import MSSQLRunner

class SafeMSSQLRunner(MSSQLRunner):
    def __init__(self, engine):
        self.engine = engine

    async def run_sql(self, sql, context=None, *args, **kwargs) -> pd.DataFrame:
        # FIX: Vanna 2.0 might pass the whole arguments object instead of just the string.
        # We check if 'sql' has a '.sql' attribute and extract it.
        if hasattr(sql, 'sql'):
            sql = sql.sql

        try:
            # Use SQLAlchemy engine to connect
            with self.engine.connect() as conn:
                # Use text() to safely handle the query string in SQLAlchemy
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
            print(f"❌ SQL Execution Error: {e}")
            # We return None or empty DF so Vanna handles the error gracefully
            raise e

class DBFactory:
    @staticmethod
    def get_db_tool():
        if Config.DB_TYPE == "mssql":
            driver = Config.DB_DRIVER.replace(' ', '+')
            
            # Connection String
            if not Config.DB_USER:
                url = (
                    f"mssql+pyodbc://@"
                    f"{Config.DB_HOST}/{Config.DB_NAME}"
                    f"?driver={driver}"
                    "&trusted_connection=yes"
                    "&TrustServerCertificate=yes"
                )
            else:
                encoded_pwd = urllib.parse.quote_plus(Config.DB_PASSWORD)
                url = (
                    f"mssql+pyodbc://{Config.DB_USER}:{encoded_pwd}"
                    f"@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
                    f"?driver={driver}"
                    "&TrustServerCertificate=yes"
                )

            engine = create_engine(url)
            runner = SafeMSSQLRunner(engine=engine)
            return RunSqlTool(sql_runner=runner)
        else:
            raise ValueError(f"Unsupported DB Type: {Config.DB_TYPE}")