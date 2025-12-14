import os
import json
import asyncio
import inspect
from typing import Any, Dict, List
import urllib.parse

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from vanna_core.agent import agent_memory, vanna_agent
from vanna_core.config import Config

# ---------------- CONFIG ----------------
DDL_FILE_PATH = "database/script.sql"
JSON_FILE_PATH = "database/examples.json"
DDL_CHUNK_SIZE = 8000 

# ---------------- DB ENGINE (MS SQL) -------------
def get_sqlalchemy_engine() -> Engine:
    driver = Config.DB_DRIVER.replace(' ', '+')
    
    if not Config.DB_USER:
        # Windows Authentication
        url = (
            f"mssql+pyodbc://@"
            f"{Config.DB_HOST}/{Config.DB_NAME}"
            f"?driver={driver}"
            "&trusted_connection=yes"
            "&TrustServerCertificate=yes"
        )
    else:
        # SQL Authentication
        encoded_pwd = urllib.parse.quote_plus(Config.DB_PASSWORD)
        url = (
            f"mssql+pyodbc://{Config.DB_USER}:{encoded_pwd}"
            f"@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
            f"?driver={driver}"
            "&TrustServerCertificate=yes"
        )
        
    return create_engine(url)


# ---------------- MOCK CONTEXT ----------
class MockUser:
    id = "admin_trainer"
    email = "admin@mantrawise.com"
    group_memberships = ["admin"]

class MockContext:
    @property
    def user(self) -> MockUser:
        return MockUser()


# --------------- SMART CALL -------------
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
        if param == "self":
            continue
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


# --------------- TRAINING: TEXT (DDL + LIVE SCHEMA) ------------
async def train_ddl_and_docs(ctx: MockContext) -> None:
    text_method = getattr(agent_memory, "save_text_memory", None)
    if not text_method:
        return

    # 1. DDL (Loads raw DDL from file - usually just dbo)
    if os.path.exists(DDL_FILE_PATH):
        with open(DDL_FILE_PATH, "r", encoding="utf-8") as f:
            ddl = f.read()
        chunks = [ddl[i : i + DDL_CHUNK_SIZE] for i in range(0, len(ddl), DDL_CHUNK_SIZE)]
        for idx, chunk in enumerate(chunks, start=1):
            doc_text = f"-- MS SQL DDL chunk {idx}/{len(chunks)}\n{chunk}"
            try:
                await smart_call(text_method, text=doc_text, context=ctx)
            except Exception:
                pass
        print("✅ DDL chunks saved.")

    # 2. Introspection (Crucial Update for DBT)
    print("🔌 Introspecting live schema (dbo + analytics_analytics) ...")
    try:
        engine = get_sqlalchemy_engine()
        with engine.connect() as conn:
            # Query multiple schemas
            query = f"""
                SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_CATALOG = '{Config.DB_NAME}'
                  AND TABLE_SCHEMA IN ('dbo', 'analytics_analytics')
                ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION
            """
            df = pd.read_sql(query, conn)
    except Exception as e:
        print(f"❌ Schema fetch failed: {e}")
        return

    if df.empty:
        print("⚠ INFORMATION_SCHEMA returned no columns. Check DB_NAME/Permissions.")
        return

    # Group by Schema AND Table to differentiate 'dbo.profiles' from 'analytics.dim_guests'
    grouped = df.groupby(["TABLE_SCHEMA", "TABLE_NAME"])
    table_count = 0

    for (schema, table), group in grouped:
        columns = [(str(r["COLUMN_NAME"]), str(r["DATA_TYPE"])) for _, r in group.iterrows()]
        col_list = ", ".join([f"{c} ({t})" for c, t in columns])
        
        # Explicitly mention the schema in the documentation
        doc = f"Table '[{schema}].[{table}]' contains columns: {col_list}."
        
        try:
            await smart_call(text_method, text=doc, context=ctx)
            table_count += 1
        except Exception:
            pass

    print(f"✅ Semantic schema training complete ({table_count} tables).")


# --------------- TRAIN SQL EXAMPLES ----------------
async def train_sql_examples(ctx: MockContext) -> None:
    method = getattr(agent_memory, "save_tool_usage", None)
    if not method: return
    if not os.path.exists(JSON_FILE_PATH): return

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
        except Exception:
            pass
    print(f"✅ SQL examples trained. Success: {success_count}/{len(examples)}")


# ---------------- MAIN -----------------
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