import os
from typing import Any, Dict

from vanna.servers.fastapi import VannaFastAPIServer
from vanna_core.agent import vanna_agent


def _build_cors_config() -> Dict[str, Any]:
    """
    Build CORS settings, allowing override via environment if needed.
    """
    allow_origins_env = os.getenv("CORS_ALLOW_ORIGINS", "*")
    allow_origins = [o.strip() for o in allow_origins_env.split(",") if o.strip()]

    return {
        "enabled": True,
        "allow_origins": allow_origins,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }


def create_server() -> VannaFastAPIServer:
    """
    Create and configure the Vanna FastAPI server.
    """
    config = {
        "cors": _build_cors_config(),
    }

    server = VannaFastAPIServer(agent=vanna_agent, config=config)
    return server
