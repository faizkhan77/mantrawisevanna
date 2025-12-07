import os
import json
import asyncio
import inspect
from typing import Any, Dict, List, Tuple

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from vanna_core.agent import agent_memory
from vanna_core.config import Config

# ---------------- CONFIG ----------------
DDL_FILE_PATH = "database/tables.sql"
JSON_FILE_PATH = "database/examples.json"
DDL_CHUNK_SIZE = 4000  # characters


# ---------------- DB ENGINE -------------
def get_sqlalchemy_engine() -> Engine:
    url = (
        f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}"
        f"@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
    )
    return create_engine(url)


# ---------------- MOCK CONTEXT ----------
class MockUser:
    id = "admin_trainer"
    email = "admin@localhost"
    group_memberships = ["admin"]


class MockContext:
    @property
    def user(self) -> MockUser:
        return MockUser()


# --------------- SMART CALL -------------
async def smart_call(method, **kwargs) -> Any:
    """
    Generic adapter that maps our kwargs into whatever signature the
    underlying tool method actually uses. Prevents 'unexpected kwarg'
    issues across Vanna versions.
    """
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


# --------------- SCHEMA CATEGORY MAPPING (BASED ON YOUR REAL SYSTEM) -------------
SCHEMA_CATEGORIES: Dict[str, List[str]] = {
    "Guest Profile": [
        "profiles",
        "profileassociations",
        "profileassociationrelationships",
        "preferences",
        "profilemonthlyspend",
        "profilevisitsperyear",
        "removedprofilemergecandidates",
        "vipcodes",
    ],
    "Hotel / PMS Stays": ["pmsstays", "pmsstayprofileassociations", "pmspreferences"],
    "Dining": ["restaurantreservations"],
    "Spa & Wellness": ["spabookings", "spapreferences"],
    "Recreation & Activities": [
        "courtbookings",
        "lessonbookings",
        "poolbeachamenityreservations",
        "otherreservations",
        "teetimebookings",
    ],
    "Transport": ["transportationreservations"],
    "System": ["settings", "sysdiagrams"],
}


def infer_category(table_name: str) -> str:
    for cat, tables in SCHEMA_CATEGORIES.items():
        if table_name.lower() in tables:
            return cat
    return "Uncategorized"


# --------------- DOMAIN-AWARE DESCRIPTIONS ----------------
def generate_domain_description(
    table_name: str, columns: List[Tuple[str, str]]
) -> str:
    """
    Creates a useful semantic description instead of:
    'The table X has columns Y'.
    """
    category = infer_category(table_name)
    col_list = ", ".join([f"{c} ({t})" for c, t in columns])

    descriptions: Dict[str, str] = {
        "profiles": "This table stores the master guest profile, including contact details, demographics, loyalty data, spend history, and VIP information.",
        "pmsstays": "This table stores hotel stay records: arrival, departure, room info, folio, rates, revenue, and PMS confirmation numbers.",
        "restaurantreservations": "Guest dining reservations, party size, dietary restrictions, restaurant info, spending, and cancellation data.",
        "spabookings": "Spa appointments including treatment type, provider info, guest notes, wellness forms, and cancellation info.",
        "courtbookings": "Court reservations (tennis, padel, etc.) including start/end time, court type, instructor, number of players and revenue.",
        "lessonbookings": "Lesson bookings (golf, fitness, sports) including instructor, facility, lesson type and sales value.",
        "teetimebookings": "Golf tee time bookings including course, holes, players, caddy selection, and booking status.",
        "poolbeachamenityreservations": "Pool and beach amenity bookings (cabanas, daybeds) with time, pricing, and guest details.",
        "otherreservations": "Misc non-categorized activity reservations linked to a guest profile.",
        "transportationreservations": "Transportation bookings including driver, destination, number of guests, and spend.",
    }

    if table_name in descriptions:
        base = descriptions[table_name]
    else:
        base = (
            f"This table belongs to category '{category}' and contains operational records."
        )

    return f"{base} Columns include: {col_list}"


# --------------- TRAINING: TEXT (DDL + LIVE SCHEMA + DOMAIN SEMANTICS) ------------
async def train_ddl_and_docs(ctx: MockContext) -> None:
    """
    1) Load and chunk the DDL from tables.sql into memory.
    2) Introspect INFORMATION_SCHEMA and store semantic docs per table.
    """
    text_method = getattr(agent_memory, "save_text_memory", None)

    if not text_method:
        print("❌ Missing 'save_text_memory' on agent_memory. Aborting text training.")
        return

    # ---- 1. Train DDL raw (chunked) ----
    if os.path.exists(DDL_FILE_PATH):
        print(f"📜 Loading DDL from {DDL_FILE_PATH} ...")
        with open(DDL_FILE_PATH, "r", encoding="utf-8") as f:
            ddl = f.read()

        chunks: List[str] = [
            ddl[i : i + DDL_CHUNK_SIZE] for i in range(0, len(ddl), DDL_CHUNK_SIZE)
        ]
        print(f"🧩 DDL size = {len(ddl)} chars, split into {len(chunks)} chunks.")

        for idx, chunk in enumerate(chunks, start=1):
            doc_text = f"-- DDL chunk {idx}/{len(chunks)}\n{chunk}"
            try:
                await smart_call(text_method, text=doc_text, context=ctx)
            except Exception as e:
                print(f"❌ Error saving DDL chunk {idx}: {e}")
                # Keep going; one failed chunk is not fatal

        print("✅ DDL chunks saved.")
    else:
        print(f"⚠ No DDL file found at {DDL_FILE_PATH}; skipping DDL training.")

    # ---- 2. Train schema with semantic docs ----
    print("🔌 Introspecting live schema via INFORMATION_SCHEMA ...")
    try:
        engine = get_sqlalchemy_engine()
        with engine.connect() as conn:
            df = pd.read_sql(
                f"""
                SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = '{Config.DB_NAME}'
                ORDER BY TABLE_NAME, ORDINAL_POSITION
                """,
                conn,
            )
    except Exception as e:
        print(f"❌ Schema fetch failed: {e}")
        return

    if df.empty:
        print("⚠ INFORMATION_SCHEMA returned no columns for this DB. Check permissions.")
        return

    grouped = df.groupby("TABLE_NAME")
    table_count = 0

    for table, group in grouped:
        columns = [(str(r["COLUMN_NAME"]), str(r["DATA_TYPE"])) for _, r in group.iterrows()]
        doc = generate_domain_description(table, columns)

        try:
            await smart_call(text_method, text=doc, context=ctx)
            table_count += 1
        except Exception as e:
            print(f"❌ Error saving schema doc for table '{table}': {e}")

    print(f"✅ Semantic schema training complete ({table_count} tables).")


# --------------- TRAIN SQL EXAMPLES ----------------
async def train_sql_examples(ctx: MockContext) -> None:
    """
    Train question → tool_usage mappings from examples.json.
    """
    method = getattr(agent_memory, "save_tool_usage", None)
    if not method:
        print("⚠ No 'save_tool_usage' method found on agent_memory. Skipping SQL examples.")
        return

    if not os.path.exists(JSON_FILE_PATH):
        print(f"⚠ No examples.json found at {JSON_FILE_PATH}. Skipping SQL examples.")
        return

    with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
        try:
            examples = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse {JSON_FILE_PATH}: {e}")
            return

    if not isinstance(examples, list):
        print("⚠ examples.json is not a list. Skipping.")
        return

    print(f"💡 Training {len(examples)} SQL examples from {JSON_FILE_PATH} ...")
    success_count = 0
    error_count = 0

    for idx, ex in enumerate(examples, start=1):
        q = ex.get("input")
        sql = ex.get("query")

        if not q or not sql:
            print(f"⚠ Example #{idx} missing 'input' or 'query'; skipping.")
            continue

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
        except Exception as e:
            error_count += 1
            print(f"❌ Error saving SQL example #{idx}: {e}")

    print(f"✅ SQL examples trained. OK={success_count}, Failed={error_count}")


# ---------------- MAIN -----------------
async def main() -> None:
    ctx = MockContext()
    print("🚀 Starting domain-aware Vanna training...")

    await train_ddl_and_docs(ctx)
    await train_sql_examples(ctx)

    print("🎉 Training completed. You can now query the agent.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⏹ Training interrupted by user.")
