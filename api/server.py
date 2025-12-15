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
    app = FastAPI(title="Mantra Wise Agent API", version="2.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"], 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Vanna Chat Routes
    chat_handler = ChatHandler(vanna_agent)
    register_chat_routes(app, chat_handler)

    # --- AUTH TYPES ---
    class LoginRequest(BaseModel):
        email: str
        password: str

    # --- 1. LOGIN ENDPOINT (Generates JWT) ---
    @app.post("/api/login")
    def login(data: LoginRequest, response: Response):
        if data.email == ADMIN_EMAIL and data.password == ADMIN_PASSWORD:
            
            # Create JWT Payload
            expiration = datetime.datetime.utcnow() + datetime.timedelta(days=7) # 7 Day Session
            payload = {
                "sub": data.email,
                "groups": ["admin", "viewer"],
                "permissions": ["read", "write", "execute_sql"],
                "exp": expiration
            }
            
            token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

            # Set HttpOnly Cookie
            response.set_cookie(
                key="vanna_auth",
                value=token,
                httponly=False, # Set to True in Prod, False allows JS debug
                max_age=604800, # 7 days
                samesite="lax",
                secure=False # Set to True if using HTTPS
            )
            return {"status": "success", "user": {"email": data.email, "role": "admin"}}
        else:
            return Response(content='{"status": "error", "message": "Invalid credentials"}', status_code=401, media_type="application/json")

    # --- 2. SESSION CHECK ENDPOINT (For Page Refresh) ---
    @app.get("/api/me")
    def check_session(request: Request):
        token = request.cookies.get("vanna_auth")
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return {"status": "authenticated", "user": {"email": payload.get("sub"), "role": "admin"}}
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    # --- 3. LOGOUT ENDPOINT ---
    @app.post("/api/logout")
    def logout(response: Response):
        response.delete_cookie("vanna_auth")
        return {"status": "logged_out"}

    # --- SCHEMA ENDPOINT ---
    @app.get("/api/schema")
    async def get_database_schema():
        # ... (Keep your existing dynamic schema logic exactly as before) ...
        sql = ""
        if Config.DB_TYPE == "postgres":
             sql = f"""
                SELECT table_schema as "TABLE_SCHEMA", 
                       table_name as "TABLE_NAME", 
                       column_name as "COLUMN_NAME", 
                       data_type as "DATA_TYPE"
                FROM information_schema.columns 
                WHERE table_schema IN ('dbo', 'analytics_analytics')
                ORDER BY table_schema DESC, table_name, ordinal_position
            """
        # ... (Include MySQL/MSSQL logic from previous step) ...
        elif Config.DB_TYPE == "mysql":
             sql = f"""SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{Config.DB_NAME}' ORDER BY TABLE_NAME, ORDINAL_POSITION"""
        else:
             sql = f"""SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_CATALOG = '{Config.DB_NAME}' AND TABLE_SCHEMA IN ('dbo', 'analytics_analytics') ORDER BY TABLE_SCHEMA DESC, TABLE_NAME, ORDINAL_POSITION"""

        try:
            class SimpleArgs:
                def __init__(self, s): self.sql = s
            return await _fetch_schema_async(db_tool, SimpleArgs(sql))
        except Exception as e:
            print(f"❌ Schema Fetch Error: {e}")
            return {"tables": [], "error": str(e)}

    # --- PREFERENCES ENDPOINTS ---
    class PrefRequest(BaseModel):
        key: str
        value: str

    @app.get("/api/preferences")
    def get_preferences(request: Request):
        # We can now use the user ID from the token if we wanted to isolate prefs
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

    return CustomVannaServer(app)