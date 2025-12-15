import os
import uvicorn
from typing import Any, Dict
from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware

# Vanna Imports
from vanna.servers.fastapi.routes import register_chat_routes
from vanna.servers.base import ChatHandler
# FIX: Import 'db_tool' directly to bypass the registry wrapper
from vanna_core.agent import vanna_agent, db_tool 
from vanna_core.config import Config
from vanna.core.user import RequestContext
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
async def _fetch_schema_async(tool_instance, args):
    # Execute query using the raw tool's runner
    # Note: args is now an object with a .sql attribute
    df = await tool_instance.sql_runner.run_sql(args, context=None)
    
    if df is None or df.empty:
        print("⚠️ Schema Query returned NO results.")
        return {"tables": []}

    print(f"✅ Schema Query returned {len(df)} rows.")

    tables_dict = {}
    
    for _, row in df.iterrows():
        # Using .get() allows us to handle slight variations in driver casing if aliases fail
        schema = row.get('TABLE_SCHEMA') or row.get('table_schema')
        table = row.get('TABLE_NAME') or row.get('table_name')
        
        if not schema or not table:
            continue

        key = f"{schema}.{table}"
        
        if key not in tables_dict:
            tables_dict[key] = {
                "schema": schema,
                "table": table,
                "columns": []
            }
        
        col_name = row.get('COLUMN_NAME') or row.get('column_name')
        data_type = row.get('DATA_TYPE') or row.get('data_type')

        tables_dict[key]["columns"].append({
            "name": col_name,
            "type": data_type
        })
        
    return {"tables": list(tables_dict.values())}

def create_server() -> CustomVannaServer:
    app = FastAPI(title="Mantra Wise Agent API", version="1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"], # Add your frontend URL explicitly
        allow_credentials=True, # REQUIRED for Cookies
        allow_methods=["*"],
        allow_headers=["*"],
    )

    #  Register Vanna Chat Routes
    chat_handler = ChatHandler(vanna_agent)
    register_chat_routes(app, chat_handler)

    # --- AUTH ENDPOINT ---
    class LoginRequest(BaseModel):
        token: str

    @app.post("/api/login")
    def login(data: LoginRequest, response: Response):
        """
        Sets the httpOnly cookie so the Vanna Web Component works automatically.
        """
        # Validate against the same token used in user.py
        ADMIN_TOKEN = os.getenv("ADMIN_API_KEY", "secret-admin-key-123")
        
        if data.token == ADMIN_TOKEN:
            # Set Cookie
            response.set_cookie(
                key="vanna_auth",
                value=data.token,
                httponly=False, # Allow JS to see it if needed, or True for security
                max_age=86400,
                samesite="lax"
            )
            return {"status": "success", "role": "admin"}
        else:
            response.status_code = 401
            return {"status": "error", "message": "Invalid token"}

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
        # DYNAMIC SQL GENERATION BASED ON CONFIG.DB_TYPE
        sql = ""
        
        if Config.DB_TYPE == "postgres":
            # Postgres returns lowercase by default, so we alias to uppercase 
            # to match what the python code expects (though the python code is now robust)
            sql = f"""
                SELECT table_schema as "TABLE_SCHEMA", 
                       table_name as "TABLE_NAME", 
                       column_name as "COLUMN_NAME", 
                       data_type as "DATA_TYPE"
                FROM information_schema.columns 
                WHERE table_schema IN ('dbo', 'analytics_analytics')
                ORDER BY table_schema DESC, table_name, ordinal_position
            """
        elif Config.DB_TYPE == "mysql":
            sql = f"""
                SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = '{Config.DB_NAME}'
                ORDER BY TABLE_NAME, ORDINAL_POSITION
            """
        else: # MSSQL (Default)
            sql = f"""
                SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_CATALOG = '{Config.DB_NAME}' 
                  AND TABLE_SCHEMA IN ('dbo', 'analytics_analytics')
                ORDER BY TABLE_SCHEMA DESC, TABLE_NAME, ORDINAL_POSITION
            """
        
        try:
            # Helper class to wrap the string, satisfying native PostgresRunner
            class SimpleArgs:
                def __init__(self, s): self.sql = s
            
            args = SimpleArgs(sql)
            
            # Use the imported 'db_tool' global variable directly.
            return await _fetch_schema_async(db_tool, args)
            
        except Exception as e:
            print(f"❌ Schema Fetch Error: {e}")
            return {"tables": [], "error": str(e)}
        
    class QuestionRequest(BaseModel):
        question: str

    @app.post("/api/get-response")
    async def get_vanna_response(request: QuestionRequest):
        """
        This endpoint is for automation. It takes a question, gets the full
        conversational response from the Vanna agent, and returns the final text.
        """
        print(f"🤖 Received question for full response: '{request.question}'")
        final_response_text = "No text response was generated by the agent."
        
        try:
            # The agent's send_message function requires a RequestContext,
            # even if it's empty, since we removed authentication.
            context = RequestContext()

            # We loop through all the components the agent generates (like status
            # updates, charts, etc.) and save the last text part we see.
            async for component in vanna_agent.send_message(
                request_context=context,
                message=request.question
            ):
                # The 'simple_component' is the most reliable way to get the text
                # representation of any major UI component from Vanna.
                if hasattr(component, 'simple_component') and hasattr(component.simple_component, 'text'):
                    if component.simple_component.text:
                        final_response_text = component.simple_component.text

            print(f"✅ Final response captured: '{final_response_text}'")
            return {"response": final_response_text}

        except Exception as e:
            print(f"❌ Error during full response generation: {e}")
            return {"response": f"Error: {str(e)}"}
            
    return CustomVannaServer(app)