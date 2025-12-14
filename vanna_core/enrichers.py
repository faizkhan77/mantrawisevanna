import os
import pandas as pd
from typing import Dict, Any

from vanna.core.enricher import ToolContextEnricher
from vanna.core.tool import ToolContext
from vanna_core.config import Config
from vanna_core.store import preference_store

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
                # MS SQL Query to get schema info for BOTH raw and analytics schemas
                # We specifically look at 'dbo' (Raw) and 'analytics_analytics' (DBT Marts)
                sql = """
                    SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_CATALOG = '{}' 
                      AND TABLE_SCHEMA IN ('dbo', 'analytics_analytics')
                    ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION
                """.format(Config.DB_NAME)
                
                # Execute with context
                df = await self.db_tool.sql_runner.run_sql(sql, context=context)
                
                if df is not None and not df.empty:
                    # Convert DataFrame to a structured CSV string for the LLM
                    # Including TABLE_SCHEMA is crucial now so LLM knows which is which
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
        user_id = context.user.id
        prefs = preference_store.get_prefs(user_id)
        
        # Add to metadata so tools can see it
        context.metadata['user_preferences'] = prefs
        return context

