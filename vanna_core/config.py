import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")
    
    # Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # DB
    DB_TYPE = os.getenv("DB_TYPE", "mysql")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_NAME = os.getenv("DB_NAME", "multitable_agent_db")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    # Memory
    CHROMA_PATH = os.getenv("CHROMA_PATH", "./vanna_storage")