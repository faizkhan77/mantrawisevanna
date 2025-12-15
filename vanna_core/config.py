import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Global configuration capable of switching between MSSQL, PostgreSQL, and MySQL.
    """

    # LLM
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini").lower()
    MODEL_NAME: str = os.getenv("MODEL_NAME", "models/gemini-1.5-pro")

    # Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")

    # --- DATABASE SWITCHER ---
    # Options: "mssql", "postgres", "mysql"
    DB_TYPE: str = os.getenv("DB_TYPE", "postgres").lower()

    # Connection Details
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_NAME: str = os.getenv("DB_NAME", "mydatabase")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "root")
    
    # Auto-select port if not in env
    _default_ports = {"mssql": 1433, "postgres": 5432, "mysql": 3306}
    DB_PORT: int = int(os.getenv("DB_PORT", _default_ports.get(DB_TYPE, 5432)))

    # Driver (Only needed for MSSQL)
    DB_DRIVER: str = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

    # --- DYNAMIC FILE PATHS ---
    @classmethod
    def get_ddl_path(cls) -> str:
        if cls.DB_TYPE == "mssql":
            return "database/script.sql"
        elif cls.DB_TYPE == "postgres":
            return "database/full_schema.sql"
        elif cls.DB_TYPE == "mysql":
            return "database/tables.sql"
        return "database/full_schema.sql"

    # NEW: Selects the correct JSON examples file
    @classmethod
    def get_examples_path(cls) -> str:
        if cls.DB_TYPE == "postgres":
            return "database/examples_postgres.json"
        elif cls.DB_TYPE == "mysql":
            return "database/examples_mysql.json"
        # Default/MSSQL
        return "database/examples.json"

    # Memory
    CHROMA_PATH: str = os.getenv("CHROMA_PATH", "./vanna_storage")