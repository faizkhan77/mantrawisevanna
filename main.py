import os
from dotenv import load_dotenv

# 1. LOAD ENV BEFORE IMPORTS
load_dotenv()

# 2. NOW IMPORT SERVER
from api.server import create_server

server = create_server()

if __name__ == "__main__":
    print("🚀 Starting Vanna AI Server...")
    print("📄 Docs available at: http://localhost:8000/docs")
    
    # Run the FastAPI server
    server.run(host=os.getenv("SERVER_HOST", "0.0.0.0"), port=int(os.getenv("SERVER_PORT", 8000)))