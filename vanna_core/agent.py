from vanna import Agent
from vanna.core.registry import ToolRegistry
from vanna.tools import VisualizeDataTool
from vanna.tools.agent_memory import (
    SaveQuestionToolArgsTool, 
    SearchSavedCorrectToolUsesTool, 
    SaveTextMemoryTool
)

# Import our factories
from vanna_core.factories.llm_factory import LLMFactory
from vanna_core.factories.db_factory import DBFactory
from vanna_core.memory import get_agent_memory
from vanna_core.user import SimpleUserResolver

# --- GLOBAL INSTANCES ---
# We create these globally so 'train.py' can access them directly
llm_service = LLMFactory.get_llm_service()
db_tool = DBFactory.get_db_tool()
agent_memory = get_agent_memory()
user_resolver = SimpleUserResolver()

def create_vanna_agent():
    # Register Tools
    tools = ToolRegistry()
    
    # Register the DB connection
    tools.register_local_tool(db_tool, access_groups=['admin', 'viewer'])
    
    # Register Memory Tools
    tools.register_local_tool(SaveQuestionToolArgsTool(), access_groups=['admin']) 
    tools.register_local_tool(SearchSavedCorrectToolUsesTool(), access_groups=['admin', 'viewer'])
    tools.register_local_tool(SaveTextMemoryTool(), access_groups=['admin'])

    # Register Visualization
    tools.register_local_tool(VisualizeDataTool(), access_groups=['admin', 'viewer'])

    # Initialize Agent
    agent = Agent(
        llm_service=llm_service,
        tool_registry=tools,
        user_resolver=user_resolver,
        agent_memory=agent_memory
    )
    
    return agent

# Singleton instance
vanna_agent = create_vanna_agent()