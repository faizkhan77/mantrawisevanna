from vanna_core.config import Config
from vanna.integrations.openai import OpenAILlmService
from vanna.integrations.google import GeminiLlmService

class LLMFactory:
    @staticmethod
    def get_llm_service():
        provider = Config.LLM_PROVIDER
        
        if provider == "openai":
            return OpenAILlmService(
                model=Config.MODEL_NAME,
                api_key=Config.OPENAI_API_KEY
            )
            
        elif provider == "gemini":
            return GeminiLlmService(
                model=Config.MODEL_NAME,
                api_key=Config.GEMINI_API_KEY
            )
            
        elif provider == "groq":
            # Groq is OpenAI compatible. We use the OpenAI service but point to Groq's URL.
            return OpenAILlmService(
                model=Config.MODEL_NAME,
                api_key=Config.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1" 
            )
            
        else:
            raise ValueError(f"Unsupported LLM Provider: {provider}")