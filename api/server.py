import os
import uvicorn
from typing import Any, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Vanna Imports
from vanna.servers.fastapi.routes import register_chat_routes
from vanna.servers.base import ChatHandler
# FIX: Import 'db_tool' directly to bypass the registry wrapper
from vanna_core.agent import vanna_agent, db_tool 
from vanna_core.config import Config

from pydantic import BaseModel
from vanna_core.store import preference_store

# --- CONFIGURATION ---
def _get_cors_origins() -> list:
    allow_origins_env = os.getenv("CORS_ALLOW_ORIGINS", "*")
    return [o.strip() for o in allow_origins_env.split(",") if o.strip()]

class CustomVannaServer:
    def __init__(self, app: FastAPI):
        self.app = app

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        print(f"🚀 Custom Vanna Server running on http://{host}:{port}")
        uvicorn.run(self.app, host=host, port=port)

# Helper function to handle async DB call
async def _fetch_schema_async(tool_instance, sql):
    # Execute query using the raw tool's runner
    df = await tool_instance.sql_runner.run_sql(sql, context=None)
    
    if df is None or df.empty:
        print("⚠️ Schema Query returned NO results.")
        return {"tables": []}

    print(f"✅ Schema Query returned {len(df)} rows.")

    tables_dict = {}
    
    for _, row in df.iterrows():
        schema = row['TABLE_SCHEMA']
        table = row['TABLE_NAME']
        key = f"{schema}.{table}"
        
        if key not in tables_dict:
            tables_dict[key] = {
                "schema": schema,
                "table": table,
                "columns": []
            }
        
        tables_dict[key]["columns"].append({
            "name": row['COLUMN_NAME'],
            "type": row['DATA_TYPE']
        })
        
    return {"tables": list(tables_dict.values())}

def create_server() -> CustomVannaServer:
    app = FastAPI(title="Mantra Wise Agent API", version="1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Vanna Chat Routes
    chat_handler = ChatHandler(vanna_agent)
    register_chat_routes(app, chat_handler)

    # --- Pydantic Model for Request ---
    class PrefRequest(BaseModel):
        key: str
        value: str

    # --- PREFERENCE ENDPOINTS ---
    
    @app.get("/api/preferences")
    def get_preferences():
        # In a real app, get user_id from token. For now, use 'admin_user'
        return preference_store.get_prefs("admin_user")

    @app.post("/api/preferences")
    def add_preference(pref: PrefRequest):
        current = preference_store.get_prefs("admin_user")
        current[pref.key] = pref.value
        preference_store.update_prefs("admin_user", current)
        return {"status": "updated", "prefs": current}

    @app.delete("/api/preferences/{key}")
    def delete_preference(key: str):
        current = preference_store.get_prefs("admin_user")
        if key in current:
            del current[key]
            preference_store.update_prefs("admin_user", current)
        return {"status": "deleted", "prefs": current}

    # --- CUSTOM ENDPOINT ---
    @app.get("/api/schema")
    async def get_database_schema():
        sql = """
            SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA IN ('dbo', 'analytics_analytics')
            ORDER BY TABLE_SCHEMA DESC, TABLE_NAME, ORDINAL_POSITION
        """
        
        try:
            # FIX: Use the imported 'db_tool' global variable directly.
            # This is the raw RunSqlTool instance, not the wrapper.
            return await _fetch_schema_async(db_tool, sql)
            
        except Exception as e:
            print(f"❌ Schema Fetch Error: {e}")
            return {"tables": [], "error": str(e)}

    return CustomVannaServer(app)

