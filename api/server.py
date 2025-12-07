from vanna.servers.fastapi import VannaFastAPIServer
from vanna_core.agent import vanna_agent

def create_server():
    # Vanna 2.0 Server Configuration
    config = {
        "cors": {
            "enabled": True,
            "allow_origins": ["*"],  # CRITICAL: Allows Streamlit to talk to FastAPI
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }
    }

    # Initialize the server
    server = VannaFastAPIServer(agent=vanna_agent, config=config)
    
    return server