from typing import List
from vanna import Agent
from vanna.core.registry import ToolRegistry
from vanna.tools import VisualizeDataTool
# FIX: Memory tools are in vanna.tools.agent_memory
from vanna.tools.agent_memory import (
    SaveQuestionToolArgsTool,
    SearchSavedCorrectToolUsesTool,
    SaveTextMemoryTool,
)
from vanna.core.system_prompt import DefaultSystemPromptBuilder
from vanna.core.tool import ToolSchema
from vanna.core.user import User
from vanna_core.user import CookieUserResolver
from vanna_core.factories.llm_factory import LLMFactory
from vanna_core.factories.db_factory import DBFactory
from vanna_core.memory import get_agent_memory
from vanna_core.enrichers import DatabaseSchemaEnricher, DocumentationEnricher
from vanna_core.config import Config
from vanna_core.store import preference_store

# --- GLOBAL SINGLETONS ---
llm_service = LLMFactory.get_llm_service()
db_tool = DBFactory.get_db_tool()
agent_memory = get_agent_memory()
user_resolver = CookieUserResolver()

# --- DYNAMIC PROMPT BUILDER ---
class DynamicSystemPromptBuilder(DefaultSystemPromptBuilder):
    async def build_system_prompt(self, user: User, tools: List[ToolSchema]) -> str:
        base_prompt = await super().build_system_prompt(user, tools)
        
        db_specific_instructions = ""
        
        if Config.DB_TYPE == "postgres":
            db_specific_instructions = """
            # 🔴 POSTGRESQL INSTRUCTIONS 🔴
            # 1. DIALECT: Use PostgreSQL syntax (PL/pgSQL).
            # 2. LIMITING: Use `LIMIT n` (NOT `TOP n`).
            # 3. QUOTING: Use double quotes for schema/tables if needed: "analytics_analytics"."dim_guests".
            # 4. BOOLEANS: Use `TRUE` and `FALSE`.
            # 5. DATES: Use `NOW()`.
            """
        elif Config.DB_TYPE == "mssql":
            db_specific_instructions = """
            # 🔴 MSSQL INSTRUCTIONS 🔴
            # 1. DIALECT: Use Transact-SQL (T-SQL).
            # 2. LIMITING: Use `SELECT TOP n`.
            # 3. QUOTING: Use brackets: [schema].[table].
            # 4. BOOLEANS: Use 1 and 0.
            # 5. DATES: Use `GETDATE()`.
            """
        elif Config.DB_TYPE == "mysql":
            db_specific_instructions = """
            # 🔴 MYSQL INSTRUCTIONS 🔴
            # 1. DIALECT: Use MySQL syntax.
            # 2. LIMITING: Use `LIMIT n`.
            # 3. QUOTING: Use backticks: `table`.
            """
        
        formatting_instructions = """
        
        # 🎨 FORMATTING RULES (IMPORTANT)
        # 1. You MUST use Markdown for all non-SQL responses.
        # 2. Use **Bold** for important entities (table names, metrics).
        # 3. Use Lists (- item) for steps or multiple points.
        # 4. If explaining a query, use `code blocks` for column names.
        # 5. Keep responses concise and professional.
        """

        # INJECT USER PREFERENCES (Language, Currency, etc)
        preference_instructions = ""
        
        print(f"\n🔍 [PROMPT BUILDER] Building prompt for user: {user.id}")
        
        if user:
            prefs = preference_store.get_prefs(user.id)
            print(f"🔍 [PROMPT BUILDER] Found Preferences: {prefs}")
            
            if prefs:
                preference_instructions = "\n# 👤 CRITICAL USER PREFERENCES\n"
                preference_instructions += "You MUST strictly adhere to the following constraints for the final response:\n"
                
                for key, value in prefs.items():
                    preference_instructions += f"- **{key.upper()}**: {value}\n"
                    # Add specific instructions for common keys to ensure LLM understands
                    if key.lower() == 'language':
                        preference_instructions += f"  (You MUST answer in {value}, translating any analysis or explanations. The SQL remains in English/Code.)\n"
                    if key.lower() == 'currency':
                        preference_instructions += f"  (All monetary values must be formatted in {value}.)\n"

        # Combine
        final_prompt = base_prompt + db_specific_instructions + formatting_instructions + preference_instructions

        return final_prompt

def create_vanna_agent() -> Agent:
    tools = ToolRegistry()
    tools.register_local_tool(db_tool, access_groups=["admin", "viewer"])
    tools.register_local_tool(SaveQuestionToolArgsTool(), access_groups=["admin"])
    tools.register_local_tool(SaveTextMemoryTool(), access_groups=["admin"])
    tools.register_local_tool(SearchSavedCorrectToolUsesTool(), access_groups=["admin", "viewer"])
    tools.register_local_tool(VisualizeDataTool(), access_groups=["admin", "viewer"])

    schema_enricher = DatabaseSchemaEnricher(db_tool=db_tool)
    doc_enricher = DocumentationEnricher("database/documentation.md")
    
    prompt_builder = DynamicSystemPromptBuilder()

    return Agent(
        llm_service=llm_service,
        tool_registry=tools,
        user_resolver=user_resolver,
        agent_memory=agent_memory,
        context_enrichers=[schema_enricher, doc_enricher],
        system_prompt_builder=prompt_builder
    )

vanna_agent: Agent = create_vanna_agent()