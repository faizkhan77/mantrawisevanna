# main.py
import os

from dotenv import load_dotenv

from api.server import create_server

load_dotenv()

server = create_server()

if __name__ == "__main__":
    print("🚀 Starting Vanna AI Server...")
    print("📄 Docs available at: http://localhost:8000/docs")

    # Run the FastAPI server (VannaFastAPIServer wraps uvicorn under the hood)
    server.run(host=os.getenv("SERVER_HOST", "0.0.0.0"), port=int(os.getenv("SERVER_PORT", 8000)))
