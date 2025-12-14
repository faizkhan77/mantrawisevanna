import asyncio
import pandas as pd
from vanna_core.agent import vanna_agent
from vanna.core.user import RequestContext

async def test():
    # 1. Create a Context (Admin)
    ctx = RequestContext(
        headers={"Authorization": "Bearer secret-admin-key-123"},
        cookies={},
        query_params={},
        remote_addr="127.0.0.1",
        metadata={}
    )

    print("⏳ Asking question: 'Show me the top 5 guests by spending'...")
    print("---------------------------------------------------------------")

    # 2. Stream the response
    async for ui_comp in vanna_agent.send_message(
        request_context=ctx,
        message="Show me the top 5 guests by spending",
        conversation_id="debug-session-1"
    ):
        # 3. Inspect the 'rich_component' inside the UiComponent
        rich = ui_comp.rich_component
        
        # Get the class name (e.g., 'RichTextComponent', 'StatusCardComponent')
        comp_type = rich.__class__.__name__

        # --- CASE A: Text / Markdown (The Final Answer) ---
        if comp_type == "RichTextComponent":
            print(f"\n📝 [Text]:\n{rich.content}")

        # --- CASE B: Status Updates (Internal "Thinking" Logs) ---
        elif comp_type in ["StatusBarUpdateComponent", "TaskTrackerUpdateComponent"]:
            # Uncomment below if you want to see "Thinking..." logs
            # print(f"🔄 [Status]: {getattr(rich, 'message', 'Updating task...')}")
            pass

        # --- CASE C: Tool Execution Status ---
        elif comp_type == "StatusCardComponent":
            print(f"⚙️ [Tool Status]: {rich.title} ({rich.status})")
            
        # --- CASE D: The SQL Code or Dataframe ---
        # Note: Since we don't know the exact class name for the SQL tool result yet
        # (it comes from the tool, not the agent file you sent), we inspect generic attributes.
        else:
            print(f"\n📦 [Unknown Component: {comp_type}]")
            
            # Try to find SQL code
            if hasattr(rich, 'code'):
                print(f"💻 SQL Found:\n{rich.code}")
            
            # Try to find Data
            if hasattr(rich, 'data'):
                data = rich.data
                if isinstance(data, pd.DataFrame):
                    print("📊 DataFrame Found:")
                    print(data.head())
                else:
                    print(f"📄 Data Content: {str(data)[:200]}...")

            # Fallback: Print all attributes to debug
            # print(vars(rich))

    print("\n---------------------------------------------------------------")
    print("✅ Test Complete.")

if __name__ == "__main__":
    asyncio.run(test())