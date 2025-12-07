import pandas as pd
from vanna_core.config import Config
from vanna.tools import RunSqlTool
from vanna.integrations.mysql import MySQLRunner

# --- CUSTOM SAFE RUNNER ---
class SafeMySQLRunner(MySQLRunner):
    """
    A custom MySQL runner that cleans binary data (bytes) from the results
    to prevent Pydantic/JSON serialization errors.
    """
    # FIX: Defined as 'async def' because the parent class is async
    async def run_sql(self, sql: str, *args, **kwargs) -> pd.DataFrame:
        # FIX: We must 'await' the parent method to get the actual DataFrame
        df = await super().run_sql(sql, *args, **kwargs)
        
        # 2. Check and clean binary columns
        if df is not None and not df.empty:
            for col in df.columns:
                # Check if the column contains bytes/binary data
                if df[col].dtype == 'object':
                    # Get the first non-null value to check type
                    first_valid_index = df[col].first_valid_index()
                    if first_valid_index is not None:
                        first_valid = df[col].loc[first_valid_index]
                        if isinstance(first_valid, bytes):
                            # Convert bytes to Hex String (e.g., b'\x00' -> "00")
                            df[col] = df[col].apply(lambda x: x.hex() if isinstance(x, bytes) else x)
                        
        return df

# --- FACTORY ---
class DBFactory:
    @staticmethod
    def get_db_tool():
        if Config.DB_TYPE == "mysql":
            # Initialize our CUSTOM SafeRunner
            runner = SafeMySQLRunner(
                host=Config.DB_HOST,
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                port=Config.DB_PORT
            )
            # Wrap it in the Vanna Tool
            return RunSqlTool(sql_runner=runner)
        
        else:
            raise ValueError(f"Unsupported DB Type: {Config.DB_TYPE}")