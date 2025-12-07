# config_vanna.py

from config import Config


def get_vanna_config() -> dict:
    """
    Build a config dict suitable for initializing Vanna integrations.

    This is an optional helper if you want a single object containing
    LLM + vector store + DB configuration.
    """
    # Resolve API key based on provider
    if Config.LLM_PROVIDER == "gemini":
        api_key = Config.GEMINI_API_KEY
    elif Config.LLM_PROVIDER == "openai":
        api_key = Config.OPENAI_API_KEY
    elif Config.LLM_PROVIDER == "groq":
        api_key = Config.GROQ_API_KEY
    else:
        raise ValueError("Invalid LLM_PROVIDER in environment")

    if not api_key:
        raise RuntimeError(
            f"API key for provider '{Config.LLM_PROVIDER}' is not set in environment"
        )

    return {
        "llm": {
            "provider": Config.LLM_PROVIDER,
            "api_key": api_key,
            "model": Config.MODEL_NAME,
        },
        "vector_store": {
            "persist_path": Config.CHROMA_PATH,
            "collection_name": "vanna_multitables",
        },
        "database": {
            "host": Config.DB_HOST,
            "port": Config.DB_PORT,
            "user": Config.DB_USER,
            "password": Config.DB_PASSWORD,
            "database": Config.DB_NAME,
        },
    }
