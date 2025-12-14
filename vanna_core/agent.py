from typing import List

from vanna import Agent
from vanna.core.registry import ToolRegistry
from vanna.tools import VisualizeDataTool
from vanna.tools.agent_memory import (
    SaveQuestionToolArgsTool,
    SearchSavedCorrectToolUsesTool,
    SaveTextMemoryTool,
)
# Import System Prompt dependencies
from vanna.core.system_prompt import DefaultSystemPromptBuilder
from vanna.core.tool import ToolSchema
from vanna.core.user import User

from vanna_core.factories.llm_factory import LLMFactory
from vanna_core.factories.db_factory import DBFactory
from vanna_core.memory import get_agent_memory
from vanna_core.user import HeaderUserResolver
from vanna_core.enrichers import DatabaseSchemaEnricher, DocumentationEnricher

__all__ = ["create_vanna_agent", "vanna_agent", "agent_memory"]

# --- GLOBAL SINGLETONS ---
llm_service = LLMFactory.get_llm_service()
db_tool = DBFactory.get_db_tool()
agent_memory = get_agent_memory()
user_resolver = HeaderUserResolver()

# --- CUSTOM PROMPT BUILDER ---
class MSSQLSystemPromptBuilder(DefaultSystemPromptBuilder):
    """
    Injects MS SQL specific instructions into the Agent's brain.
    This version is heavily fortified with strict, non-negotiable rules.
    """
    async def build_system_prompt(self, user: User, tools: List[ToolSchema]) -> str:
        # Get the standard Vanna prompt which includes enriched context
        base_prompt = await super().build_system_prompt(user, tools)
        
        # Append strict, unbreakable T-SQL instructions
        mssql_instructions = """
        
        # --------------------------------------------------
        # 🔴 CRITICAL DATABASE OPERATING INSTRUCTIONS 🔴
        # --------------------------------------------------
        # You are an expert T-SQL data analyst connected to a Microsoft SQL Server.
        # You MUST follow these rules for EVERY query you generate. There are no exceptions.

        # 1. **SQL DIALECT:**
        #    - You MUST generate Transact-SQL (T-SQL) syntax ONLY.
        #    - NEVER use MySQL or PostgreSQL syntax (e.g., `LIMIT`, `NOW()`, `SHOW TABLES`).
        #    - ALWAYS use `SELECT TOP n` for limiting rows.
        #    - ALWAYS use `GETDATE()` for the current timestamp.

        # 2. **SCHEMA QUALIFICATION (MOST IMPORTANT RULE):**
        #    - The database contains multiple schemas, primarily 'dbo' and 'analytics_analytics'.
        #    - You MUST ALWAYS qualify table names with their schema using bracket notation: `[schema_name].[table_name]`.
        #    - **Example Correct:** `SELECT * FROM [analytics_analytics].[dim_guests]`
        #    - **Example INCORRECT:** `SELECT * FROM dim_guests`
        #    - Failure to qualify table names will result in an "Invalid object name" error.

        # 3. **BOOLEAN VALUES:**
        #    - T-SQL uses bit values for booleans.
        #    - ALWAYS use `column = 1` for TRUE.
        #    - ALWAYS use `column = 0` for FALSE.
        #    - NEVER use the keywords `TRUE` or `FALSE` in a WHERE clause.
        #    - **Example Correct:** `WHERE IsVIP = 1`
        #    - **Example INCORRECT:** `WHERE IsVIP = TRUE`

        # 4. **Execution Mandate:**
        #    - Your primary purpose is to answer questions with data.
        #    - When a user asks a question, immediately generate and execute the correct, fully-qualified T-SQL query using the `run_sql` tool. Do not ask for permission first.

        # 5. **USER PREFERENCES (NEW & IMPORTANT):**
        #    - After generating and running the SQL, check for a `[USER PREFERENCES]` section in your instructions.
        #    - You MUST adhere to these preferences when formulating your final, conversational response to the user.
        #    - **Example:** If you see a preference for `language: hindi`, you MUST provide your entire final answer, including explanations and conversational text, in Hindi. The SQL query itself remains in English.
        # --------------------------------------------------
        """
        return base_prompt + mssql_instructions

def _build_tool_registry() -> ToolRegistry:
    tools = ToolRegistry()
    
    # Register DB Tool
    tools.register_local_tool(db_tool, access_groups=["admin", "viewer"])

    # Register Memory Tools
    tools.register_local_tool(SaveQuestionToolArgsTool(), access_groups=["admin"])
    tools.register_local_tool(SaveTextMemoryTool(), access_groups=["admin"])
    tools.register_local_tool(
        SearchSavedCorrectToolUsesTool(), access_groups=["admin", "viewer"]
    )

    # Register Viz Tool
    tools.register_local_tool(VisualizeDataTool(), access_groups=["admin", "viewer"])

    return tools

def create_vanna_agent() -> Agent:
    tools = _build_tool_registry()

    # Initialize Context Enrichers
    schema_enricher = DatabaseSchemaEnricher(db_tool=db_tool)
    doc_enricher = DocumentationEnricher(file_path="database/documentation.md")
    
    # Initialize Prompt Builder
    prompt_builder = MSSQLSystemPromptBuilder()

    agent = Agent(
        llm_service=llm_service,
        tool_registry=tools,
        user_resolver=user_resolver,
        agent_memory=agent_memory,
        context_enrichers=[schema_enricher, doc_enricher],
        # Inject the custom prompt builder here
        system_prompt_builder=prompt_builder
    )

    return agent

vanna_agent: Agent = create_vanna_agent()