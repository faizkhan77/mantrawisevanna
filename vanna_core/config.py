import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Global configuration loaded from environment variables.
    Adapted for MS SQL Server.
    """

    # LLM
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini").lower()
    MODEL_NAME: str = os.getenv("MODEL_NAME", "models/gemini-1.5-pro")

    # Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")

    # DB - MS SQL CONFIG
    DB_TYPE: str = os.getenv("DB_TYPE", "mssql")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 1433))
    DB_NAME: str = os.getenv("DB_NAME", "MantraWise")
    DB_USER: str = os.getenv("DB_USER", "sa")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    # Critical for MS SQL
    DB_DRIVER: str = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

    # Memory
    CHROMA_PATH: str = os.getenv("CHROMA_PATH", "./vanna_storage")

    @classmethod
    def ensure_llm_key(cls) -> None:
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is required but not set")
        if cls.LLM_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is required but not set")
        if cls.LLM_PROVIDER == "groq" and not cls.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY is required but not set")