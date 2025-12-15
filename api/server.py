import os
import uvicorn
from typing import Any, Dict
from fastapi import FastAPI, Response, Request,HTTPException
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

import jwt
import datetime

# --- CONFIGURATION ---
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@mantrawise.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "password")
JWT_SECRET = os.getenv("JWT_SECRET", "secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


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

# Helper for Basic Schema (Tables/Columns)
async def _fetch_tables_async(tool_instance, args):
    df = await tool_instance.sql_runner.run_sql(args, context=None)
    if df is None or df.empty:
        return {} # Return dict for easier merging
    
    tables_dict = {}
    for _, row in df.iterrows():
        schema = row.get('TABLE_SCHEMA') or row.get('table_schema')
        table = row.get('TABLE_NAME') or row.get('table_name')
        if not schema or not table: continue
        
        key = f"{schema}.{table}"
        if key not in tables_dict:
            tables_dict[key] = {
                "schema": schema, 
                "table": table, 
                "columns": [], 
                "relationships": [] # Initialize relationships list
            }
        
        col_name = row.get('COLUMN_NAME') or row.get('column_name')
        data_type = row.get('DATA_TYPE') or row.get('data_type')
        tables_dict[key]["columns"].append({"name": col_name, "type": data_type})
        
    return tables_dict

# Helper for Foreign Keys (Relationships)
async def _fetch_relationships_async(tool_instance, args, tables_dict):
    df = await tool_instance.sql_runner.run_sql(args, context=None)
    if df is None or df.empty:
        return tables_dict

    for _, row in df.iterrows():
        # Adjust casing based on DB driver return
        origin_schema = row.get('schema_name') or row.get('SCHEMA_NAME')
        origin_table = row.get('table_name') or row.get('TABLE_NAME')
        origin_col = row.get('column_name') or row.get('COLUMN_NAME')
        
        target_schema = row.get('foreign_schema') or row.get('FOREIGN_SCHEMA')
        target_table = row.get('foreign_table') or row.get('FOREIGN_TABLE')
        target_col = row.get('foreign_column') or row.get('FOREIGN_COLUMN')

        origin_key = f"{origin_schema}.{origin_table}"

        # Add relationship to the origin table
        if origin_key in tables_dict:
            tables_dict[origin_key]["relationships"].append({
                "column": origin_col,
                "target_schema": target_schema,
                "target_table": target_table,
                "target_column": target_col
            })
            
    return tables_dict

def create_server() -> CustomVannaServer:
    app = FastAPI(title="Mantra Wise Agent API", version="2.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"], 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    chat_handler = ChatHandler(vanna_agent)
    register_chat_routes(app, chat_handler)

    class LoginRequest(BaseModel):
        email: str
        password: str

    # --- 1. LOGIN ---
    @app.post("/api/login")
    def login(data: LoginRequest, response: Response):
        if data.email == ADMIN_EMAIL and data.password == ADMIN_PASSWORD:
            expiration = datetime.datetime.utcnow() + datetime.timedelta(days=7)
            payload = {
                "sub": data.email,
                "groups": ["admin"],
                "permissions": ["read", "write", "execute_sql"],
                "exp": expiration
            }
            token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            
            response.set_cookie(key="vanna_auth", value=token, httponly=False, max_age=604800, samesite="lax", secure=False)
            return {"status": "success", "user": {"email": data.email, "role": "admin"}}
        else:
            return Response(content='{"status": "error", "message": "Invalid credentials"}', status_code=401, media_type="application/json")

    # --- 2. SESSION CHECK (Helper to get User ID) ---
    def get_current_user(request: Request):
        token = request.cookies.get("vanna_auth")
        if not token:
             # Try header
             auth_header = request.headers.get('Authorization')
             if auth_header and auth_header.startswith('Bearer '):
                 token = auth_header.split(' ')[1]
        
        if not token: raise HTTPException(status_code=401, detail="Not authenticated")
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload.get("sub") # Returns email/id
        except:
            raise HTTPException(status_code=401, detail="Invalid token")

    @app.get("/api/me")
    def check_session(request: Request):
        user_id = get_current_user(request)
        return {"status": "authenticated", "user": {"email": user_id, "role": "admin"}}

    # --- 3. LOGOUT ---
    @app.post("/api/logout")
    def logout(response: Response):
        response.delete_cookie("vanna_auth")
        return {"status": "logged_out"}

    # --- 4. SCHEMA ENDPOINT (Now includes Relationships) ---
    @app.get("/api/schema")
    async def get_database_schema():
        class SimpleArgs:
            def __init__(self, s): self.sql = s

        # A. Fetch Tables & Columns
        sql_tables = ""
        if Config.DB_TYPE == "postgres":
             sql_tables = f"""
                SELECT table_schema, table_name, column_name, data_type
                FROM information_schema.columns 
                WHERE table_schema IN ('dbo', 'analytics_analytics')
                ORDER BY table_schema DESC, table_name, ordinal_position
            """
        # ... (MSSQL/MySQL logic omitted for brevity, assumes Postgres for now) ...
        
        try:
            tables_dict = await _fetch_tables_async(db_tool, SimpleArgs(sql_tables))
            
            # B. Fetch Relationships (Postgres Only implementation for now)
            if Config.DB_TYPE == "postgres":
                sql_rels = """
                    SELECT
                        tc.table_schema as "schema_name", 
                        tc.table_name as "table_name", 
                        kcu.column_name as "column_name",
                        ccu.table_schema AS "foreign_schema",
                        ccu.table_name AS "foreign_table",
                        ccu.column_name AS "foreign_column"
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                      AND tc.table_schema IN ('dbo', 'analytics_analytics');
                """
                tables_dict = await _fetch_relationships_async(db_tool, SimpleArgs(sql_rels), tables_dict)

            return {"tables": list(tables_dict.values())}

        except Exception as e:
            print(f"❌ Schema Fetch Error: {e}")
            return {"tables": [], "error": str(e)}

    # --- 5. PREFERENCES (User Scoped) ---
    class PrefRequest(BaseModel):
        key: str
        value: str

    @app.get("/api/preferences")
    def get_preferences(request: Request):
        user_id = get_current_user(request)
        return preference_store.get_prefs(user_id)

    @app.post("/api/preferences")
    def add_preference(pref: PrefRequest, request: Request):
        user_id = get_current_user(request)
        current = preference_store.get_prefs(user_id)
        current[pref.key] = pref.value
        preference_store.update_prefs(user_id, current)
        return {"status": "updated", "prefs": current}

    @app.delete("/api/preferences/{key}")
    def delete_preference(key: str, request: Request):
        user_id = get_current_user(request)
        current = preference_store.get_prefs(user_id)
        if key in current:
            del current[key]
            preference_store.update_prefs(user_id, current)
        return {"status": "deleted", "prefs": current}

    return CustomVannaServer(app)