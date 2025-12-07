import streamlit as st
import streamlit.components.v1 as components

# Page Configuration
st.set_page_config(
    page_title="Mantra Wise Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Optional: Add a clean header for the demo
st.title("🤖 Enterprise Data Agent")
st.caption("Powered by Vanna AI 2.0 & Groq")

# --- VANNA WEB COMPONENT CONFIGURATION ---
# We embed the Vanna Web Component using an iframe.
# It connects directly to your FastAPI backend running on port 8000.

vanna_component_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vanna Chat</title>
    
    <!-- Load the Vanna web component from CDN -->
    <script type="module" src="https://img.vanna.ai/vanna-components.js"></script>
    
    <style>
        /* Ensure the component takes up the full iframe space */
        body, html {
            margin: 0;
            padding: 0;
            height: 100%;
            width: 100%;
            background-color: transparent;
            font-family: sans-serif;
        }
        vanna-chat {
            width: 100%;
            height: 100vh;
            display: block;
        }
    </style>
</head>
<body>
    <!-- 
      CONFIGURATION:
      api-base: The URL of your running main.py (FastAPI)
      endpoints: The Vanna 2.0 standard endpoints
    -->
    <vanna-chat
        api-base="http://localhost:8000"
        sse-endpoint="http://localhost:8000/api/vanna/v2/chat_sse"
        ws-endpoint="http://localhost:8000/api/vanna/v2/chat_websocket"
        poll-endpoint="http://localhost:8000/api/vanna/v2/chat_poll"
        theme="light"
        debug="true"
    ></vanna-chat>
</body>
</html>
"""

# Render the component
# Height=800 ensures enough space for tables and charts
components.html(vanna_component_html, height=800, scrolling=False)

# Footer / Instructions
st.divider()
st.info("💡 **Note:** Ensure `python main.py` is running in a separate terminal on port 8000.")