# config_vanna.py

from config import Config

def get_vanna_config():
    # Resolve API key based on provider
    if Config.LLM_PROVIDER == "gemini":
        api_key = Config.GEMINI_API_KEY
    elif Config.LLM_PROVIDER == "openai":
        api_key = Config.OPENAI_API_KEY
    elif Config.LLM_PROVIDER == "groq":
        api_key = Config.GROQ_API_KEY
    else:
        raise ValueError("Invalid LLM_PROVIDER in .env")

    return {
        "llm": {
            "provider": Config.LLM_PROVIDER,
            "api_key": api_key,
            "model": Config.MODEL_NAME
        },

        "vector_store": {
            "persist_path": Config.CHROMA_PATH,
            "collection_name": "vanna_multitables"
        },

        "database": {
            "host": Config.DB_HOST,
            "port": Config.DB_PORT,
            "user": Config.DB_USER,
            "password": Config.DB_PASSWORD,
            "database": Config.DB_NAME
        }
    }
