from vanna.integrations.chromadb import ChromaAgentMemory
from vanna_core.config import Config


def get_agent_memory() -> ChromaAgentMemory:
    """
    Return the shared Chroma-based agent memory.

    This is the memory instance used by vanna_core.agent, which is then shared
    with the FastAPI server and the training script.
    """
    return ChromaAgentMemory(
        collection_name="vanna_agent_memory",
        persist_directory=Config.CHROMA_PATH,
    )
