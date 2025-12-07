# main.py
from api.server import create_server
import os
from dotenv import load_dotenv

load_dotenv()

server = create_server()

if __name__ == "__main__":
    print("🚀 Starting Vanna AI Server...")
    print(f"📄 Docs available at: http://localhost:8000/docs")
    
    # Run the server
    server.run(host="0.0.0.0", port=8000)