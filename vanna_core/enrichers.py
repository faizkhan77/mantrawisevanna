import os
import pandas as pd
from typing import Dict, Any

from vanna.core.enricher import ToolContextEnricher
from vanna.core.tool import ToolContext
from vanna_core.config import Config
from vanna_core.store import preference_store

# Helper to satisfy Vanna's Runner interface which expects an object with .sql
class SimpleSqlArgs:
    def __init__(self, sql: str):
        self.sql = sql

class DatabaseSchemaEnricher(ToolContextEnricher):
    """
    Automatically fetches the database schema (Tables & Columns) 
    and adds it to the context metadata for every tool execution.
    """
    def __init__(self, db_tool):
        self.db_tool = db_tool
        self.schema_cache: Dict[str, Any] = {}
        self.is_loaded = False

    async def enrich_context(self, context: ToolContext) -> ToolContext:
        # If we haven't loaded schema yet, fetch it
        if not self.is_loaded:
            try:
                # 1. DYNAMIC QUERY GENERATION
                sql = ""
                if Config.DB_TYPE == "postgres":
                    sql = f"""
                        SELECT table_schema, table_name, column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_schema IN ('dbo', 'analytics_analytics')
                        ORDER BY table_schema, table_name, ordinal_position
                    """
                elif Config.DB_TYPE == "mysql":
                    sql = f"""
                        SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_SCHEMA = '{Config.DB_NAME}'
                        ORDER BY TABLE_NAME, ORDINAL_POSITION
                    """
                elif Config.DB_TYPE == "mssql":
                    sql = f"""
                        SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_CATALOG = '{Config.DB_NAME}' 
                          AND TABLE_SCHEMA IN ('dbo', 'analytics_analytics')
                        ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION
                    """
                
                # 2. Wrap SQL to satisfy native Runners (like PostgresRunner)
                args = SimpleSqlArgs(sql)

                # 3. Execute with context
                # We access the runner directly, so we pass the wrapped args
                df = await self.db_tool.sql_runner.run_sql(args, context=context)
                
                if df is not None and not df.empty:
                    # Convert DataFrame to a structured CSV string for the LLM
                    schema_text = df.to_csv(index=False)
                    self.schema_cache['schema_text'] = schema_text
                    self.is_loaded = True
            except Exception as e:
                print(f"⚠️ Failed to load schema context: {e}")
                self.schema_cache['schema_text'] = "Schema not available."

        # Add to context
        context.metadata['database_schema'] = self.schema_cache.get('schema_text', '')
        return context


class DocumentationEnricher(ToolContextEnricher):
    """
    Reads a markdown file (documentation.md) and adds it to context.
    """
    def __init__(self, file_path: str = "database/documentation.md"):
        self.file_path = file_path
        self.doc_content = ""
        self._load_file()

    def _load_file(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.doc_content = f.read()
        else:
            self.doc_content = "No additional documentation provided."

    async def enrich_context(self, context: ToolContext) -> ToolContext:
        # Add to context
        context.metadata['business_docs'] = self.doc_content
        return context


class UserPreferencesEnricher(ToolContextEnricher):
    """
    Injects user-defined key-value preferences into the context.
    """
    async def enrich_context(self, context: ToolContext) -> ToolContext:
        # Fetch from our memory store
        if context.user:
            user_id = context.user.id
            prefs = preference_store.get_prefs(user_id)
            # Add to metadata so tools can see it
            context.metadata['user_preferences'] = prefs
        return context