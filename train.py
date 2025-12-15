import os
import json
import asyncio
import inspect
from typing import Any, Dict, List
import urllib.parse

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from vanna_core.agent import agent_memory, vanna_agent
from vanna_core.config import Config

# ---------------- CONFIG ----------------
DDL_FILE_PATH = Config.get_ddl_path()
JSON_FILE_PATH = Config.get_examples_path()
DDL_CHUNK_SIZE = 8000 

# ---------------- DB ENGINE FACTORY ----------------
def get_training_engine() -> Engine:
    user = Config.DB_USER
    password = urllib.parse.quote_plus(Config.DB_PASSWORD) if Config.DB_PASSWORD else ""
    host = Config.DB_HOST
    port = Config.DB_PORT
    db_name = Config.DB_NAME
    db_type = Config.DB_TYPE

    url = ""
    if db_type == "postgres":
        url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"
    elif db_type == "mysql":
        url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
    elif db_type == "mssql":
        driver = Config.DB_DRIVER.replace(' ', '+')
        if not user:
            url = f"mssql+pyodbc://@{host}/{db_name}?driver={driver}&trusted_connection=yes&TrustServerCertificate=yes"
        else:
            url = f"mssql+pyodbc://{user}:{password}@{host}:{port}/{db_name}?driver={driver}&TrustServerCertificate=yes"
    else:
        raise ValueError(f"Unsupported DB_TYPE for training: {db_type}")

    return create_engine(url)

# ---------------- MOCK CONTEXT ----------------
class MockUser:
    id = "admin_trainer"
    email = "admin@mantrawise.com"
    group_memberships = ["admin"]

class MockContext:
    @property
    def user(self) -> MockUser:
        return MockUser()

# --------------- SMART CALL ----------------
async def smart_call(method, **kwargs) -> Any:
    sig = inspect.signature(method)
    bound_args: Dict[str, Any] = {}
    arg_mapping: Dict[str, List[str]] = {
        "text": ["text", "content", "doc", "memory", "input_text", "document"],
        "context": ["context", "request_context", "user"],
        "question": ["question", "input", "prompt"],
        "tool_name": ["tool_name", "name"],
        "args": ["args", "tool_args", "arguments", "tool_arguments"],
        "success": ["success", "is_success"],
    }
    for param in sig.parameters:
        if param == "self": continue
        if param in kwargs:
            bound_args[param] = kwargs[param]
            continue
        found = False
        for key, aliases in arg_mapping.items():
            if param in aliases and key in kwargs:
                bound_args[param] = kwargs[key]
                found = True
                break
        if not found and param == "context":
            bound_args["context"] = kwargs.get("context")

    if asyncio.iscoroutinefunction(method):
        return await method(**bound_args)
    return method(**bound_args)

# --------------- TRAINING ----------------
async def train_ddl_and_docs(ctx: MockContext) -> None:
    text_method = getattr(agent_memory, "save_text_memory", None)
    if not text_method: return

    print(f"\n🔎 [DEBUG] Loading DDL from: {os.path.abspath(DDL_FILE_PATH)}")
    
    if os.path.exists(DDL_FILE_PATH):
        with open(DDL_FILE_PATH, "r", encoding="utf-8") as f:
            ddl = f.read()
        chunks = [ddl[i : i + DDL_CHUNK_SIZE] for i in range(0, len(ddl), DDL_CHUNK_SIZE)]
        for idx, chunk in enumerate(chunks, start=1):
            doc_text = f"-- {Config.DB_TYPE.upper()} DDL chunk {idx}/{len(chunks)}\n{chunk}"
            try:
                await smart_call(text_method, text=doc_text, context=ctx)
            except Exception: pass
        print("✅ DDL chunks saved.")
    else:
        print(f"❌ ERROR: DDL File not found at {DDL_FILE_PATH}")

    # 2. Introspection
    print(f"🔌 Introspecting live schema for {Config.DB_TYPE}...")
    
    sql = ""
    # FIX: Removed table_catalog check for Postgres
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

    try:
        engine = get_training_engine()
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)
    except Exception as e:
        print(f"❌ Schema fetch failed: {e}")
        return

    if df.empty:
        print("⚠ INFORMATION_SCHEMA returned no columns. Check DB_NAME/Permissions.")
        return

    df.columns = [c.lower() for c in df.columns]

    # --- DEBUGGING OUTPUT FOR USER ---
    print("\n🧐 [DEBUG] INSPECTING ACTUAL DATABASE COLUMNS:")
    print("-" * 50)
    debug_tables = ['pmsstays', 'profiles', 'dim_guests'] 
    for index, row in df.iterrows():
        t_name = row['table_name'].lower()
        if t_name in debug_tables and row['column_name'].lower() in ['arrivalwhen', 'arrival_when', 'firstname', 'first_name', 'pid', 'profile_id']:
            print(f"   Table: {row['table_schema']}.{t_name} | Column: {row['column_name']}")
    print("-" * 50 + "\n")
    # ---------------------------------

    grouped = df.groupby(["table_schema", "table_name"])
    table_count = 0

    for (schema, table), group in grouped:
        columns = [(str(r["column_name"]), str(r["data_type"])) for _, r in group.iterrows()]
        col_list = ", ".join([f"{c} ({t})" for c, t in columns])
        
        if Config.DB_TYPE == "mssql":
            tbl_str = f"[{schema}].[{table}]"
        else:
            tbl_str = f"{schema}.{table}"

        doc = f"Table '{tbl_str}' contains columns: {col_list}."
        
        try:
            await smart_call(text_method, text=doc, context=ctx)
            table_count += 1
        except Exception: pass

    print(f"✅ Semantic schema training complete ({table_count} tables).")

async def train_sql_examples(ctx: MockContext) -> None:
    method = getattr(agent_memory, "save_tool_usage", None)
    if not method: return
    
    print(f"\n🔎 [DEBUG] Loading SQL Examples from: {os.path.abspath(JSON_FILE_PATH)}")
    
    if not os.path.exists(JSON_FILE_PATH): 
        print(f"❌ ERROR: Examples file not found at {JSON_FILE_PATH}")
        return

    with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
        examples = json.load(f)

    print(f"💡 Training {len(examples)} SQL examples ...")
    success_count = 0
    for ex in examples:
        q = ex.get("input")
        sql = ex.get("query")
        if not q or not sql: continue
        try:
            await smart_call(
                method,
                question=q,
                tool_name="run_sql",
                args={"sql": sql},
                context=ctx,
                success=True,
            )
            success_count += 1
        except Exception: pass
    print(f"✅ SQL examples trained. Success: {success_count}/{len(examples)}")

async def main() -> None:
    ctx = MockContext()
    await train_ddl_and_docs(ctx)
    await train_sql_examples(ctx)
    print("🎉 Training completed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass