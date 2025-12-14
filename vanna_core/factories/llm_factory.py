from vanna_core.config import Config
from vanna.integrations.openai import OpenAILlmService
from vanna.integrations.google import GeminiLlmService
from vanna_core.preference_llm import PreferenceAwareLlmService


class LLMFactory:
    @staticmethod
    def get_llm_service():
        provider = Config.LLM_PROVIDER

        if provider == "openai":
            base_llm = OpenAILlmService(
                model=Config.MODEL_NAME,
                api_key=Config.OPENAI_API_KEY
            )

        elif provider == "gemini":
            base_llm = GeminiLlmService(
                model=Config.MODEL_NAME,
                api_key=Config.GEMINI_API_KEY
            )

        elif provider == "groq":
            base_llm = OpenAILlmService(
                model=Config.MODEL_NAME,
                api_key=Config.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1"
            )

        else:
            raise ValueError(f"Unsupported LLM Provider: {provider}")

        # 🔑 THIS IS THE REGISTRATION
        return PreferenceAwareLlmService(base_llm)
