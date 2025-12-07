from typing import List

from vanna import Agent
from vanna.core.registry import ToolRegistry
from vanna.tools import VisualizeDataTool
from vanna.tools.agent_memory import (
    SaveQuestionToolArgsTool,
    SearchSavedCorrectToolUsesTool,
    SaveTextMemoryTool,
)

from vanna_core.factories.llm_factory import LLMFactory
from vanna_core.factories.db_factory import DBFactory
from vanna_core.memory import get_agent_memory
from vanna_core.user import SimpleUserResolver

# Expose these for external use (train.py, server, etc.)
__all__ = ["create_vanna_agent", "vanna_agent", "agent_memory"]

# --- GLOBAL SINGLETONS (intentionally shared) ---

# LLM + DB + Memory are created once and reused everywhere
llm_service = LLMFactory.get_llm_service()
db_tool = DBFactory.get_db_tool()
agent_memory = get_agent_memory()
user_resolver = SimpleUserResolver()


def _build_tool_registry() -> ToolRegistry:
    """
    Internal helper to register all tools in a single place.
    """
    tools = ToolRegistry()

    # Database tool (SQL execution)
    tools.register_local_tool(db_tool, access_groups=["admin", "viewer"])

    # Memory tools: question logging, search, and raw text memory
    tools.register_local_tool(SaveQuestionToolArgsTool(), access_groups=["admin"])
    tools.register_local_tool(
        SearchSavedCorrectToolUsesTool(), access_groups=["admin", "viewer"]
    )
    tools.register_local_tool(SaveTextMemoryTool(), access_groups=["admin"])

    # Visualization
    tools.register_local_tool(VisualizeDataTool(), access_groups=["admin", "viewer"])

    return tools


def create_vanna_agent() -> Agent:
    """
    Factory for the primary Vanna Agent used by the API and trainer.
    """
    tools = _build_tool_registry()

    agent = Agent(
        llm_service=llm_service,
        tool_registry=tools,
        user_resolver=user_resolver,
        agent_memory=agent_memory,
    )

    return agent


# Singleton instance used by FastAPI server and training
vanna_agent: Agent = create_vanna_agent()
