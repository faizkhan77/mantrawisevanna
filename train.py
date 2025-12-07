import os
import json
import asyncio
import inspect
import pandas as pd
from sqlalchemy import create_engine
from vanna_core.agent import agent_memory
from vanna_core.config import Config

# ---------------- CONFIG ----------------
DDL_FILE_PATH = "database/tables.sql"
JSON_FILE_PATH = "database/examples.json"

# ---------------- DB ENGINE -------------
def get_sqlalchemy_engine():
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
    def user(self):
        return MockUser()

# --------------- SMART CALL -------------
async def smart_call(method, **kwargs):
    sig = inspect.signature(method)
    bound_args = {}

    arg_mapping = {
        'text': ['text', 'content', 'doc', 'memory', 'input_text'],
        'context': ['context', 'request_context', 'user'],
        'question': ['question', 'input'],
        'tool_name': ['tool_name', 'name'],
        'args': ['args', 'tool_args', 'arguments'],
        'success': ['success', 'is_success']
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
SCHEMA_CATEGORIES = {
    "Guest Profile": [
        "profiles", "profileassociations", "profileassociationrelationships",
        "preferences", "profilemonthlyspend", "profilevisitsperyear",
        "removedprofilemergecandidates", "vipcodes"
    ],
    "Hotel / PMS Stays": [
        "pmsstays", "pmsstayprofileassociations", "pmspreferences"
    ],
    "Dining": ["restaurantreservations"],
    "Spa & Wellness": ["spabookings", "spapreferences"],
    "Recreation & Activities": [
        "courtbookings", "lessonbookings", "poolbeachamenityreservations",
        "otherreservations", "teetimebookings"
    ],
    "Transport": ["transportationreservations"],
    "System": ["settings", "sysdiagrams"]
}

def infer_category(table_name):
    for cat, tables in SCHEMA_CATEGORIES.items():
        if table_name.lower() in tables:
            return cat
    return "Uncategorized"

# --------------- DOMAIN-AWARE DESCRIPTIONS ----------------
def generate_domain_description(table_name, columns):
    """
    Creates a useful semantic description instead of 'table x has columns y'.
    """
    category = infer_category(table_name)

    col_list = ", ".join([f"{c} ({t})" for c, t in columns])

    descriptions = {
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
        base = f"This table belongs to category '{category}' and contains operational records."

    return f"{base} Columns include: {col_list}"

# --------------- TRAINING: TEXT (DDL + LIVE SCHEMA + DOMAIN SEMANTICS) ------------
async def train_ddl_and_docs(ctx):
    text_method = getattr(agent_memory, "save_text_memory", None)

    if not text_method:
        print("❌ Missing 'save_text_memory'")
        return

    # ---- 1. Train DDL raw ----
    if os.path.exists(DDL_FILE_PATH):
        with open(DDL_FILE_PATH, "r", encoding="utf-8") as f:
            ddl = f.read()

        await smart_call(text_method, text=ddl, context=ctx)
        print("✅ DDL saved.")

    # ---- 2. Train schema with semantic docs ----
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
                conn
            )
    except Exception as e:
        print("❌ schema fetch failed:", e)
        return

    grouped = df.groupby("TABLE_NAME")
    count = 0

    for table, group in grouped:
        columns = [(r["COLUMN_NAME"], r["DATA_TYPE"]) for _, r in group.iterrows()]
        doc = generate_domain_description(table, columns)

        await smart_call(text_method, text=doc, context=ctx)
        count += 1

    print(f"✅ Semantic schema training complete ({count} tables).")

# --------------- TRAIN SQL EXAMPLES ----------------
async def train_sql_examples(ctx):
    method = getattr(agent_memory, "save_tool_usage", None)
    if not method:
        print("⚠ No save_tool_usage found.")
        return

    if not os.path.exists(JSON_FILE_PATH):
        print("⚠ Missing examples.json")
        return

    with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
        examples = json.load(f)

    for ex in examples:
        q = ex.get("input")
        sql = ex.get("query")
        if not q or not sql:
            continue

        await smart_call(
            method,
            question=q,
            tool_name="run_sql",
            args={"sql": sql},
            context=ctx,
            success=True
        )

    print("✅ SQL examples trained.")

# ---------------- MAIN -----------------
async def main():
    ctx = MockContext()
    print("🚀 Starting training (domain aware)...")

    await train_ddl_and_docs(ctx)
    await train_sql_examples(ctx)

    print("🎉 Training done. Run: streamlit run streamlit/app.py")

if __name__ == "__main__":
    asyncio.run(main())
