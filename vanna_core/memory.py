from vanna.integrations.chromadb import ChromaAgentMemory
from vanna_core.config import Config

def get_agent_memory():
    return ChromaAgentMemory(
        collection_name="vanna_agent_memory",
        persist_directory=Config.CHROMA_PATH
    )