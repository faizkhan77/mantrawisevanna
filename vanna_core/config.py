import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Global configuration loaded from environment variables.

    This is used primarily by the Vanna / DB integration code.
    """

    # LLM
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai").lower()
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4o")

    # Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")

    # DB
    DB_TYPE: str = os.getenv("DB_TYPE", "mysql")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    DB_NAME: str = os.getenv("DB_NAME", "multitable_agent_db")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    # Memory
    CHROMA_PATH: str = os.getenv("CHROMA_PATH", "./vanna_storage")

    @classmethod
    def ensure_llm_key(cls) -> None:
        """
        Optional helper to assert that the proper API key is set
        for the configured LLM provider. Call this early if you want
        hard failures instead of confusing runtime errors.
        """
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is required but not set")
        if cls.LLM_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is required but not set")
        if cls.LLM_PROVIDER == "groq" and not cls.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY is required but not set")
