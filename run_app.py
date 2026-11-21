"""Convenient entrypoint to run the PlantGuard AI web application."""
import sys
import subprocess
from pathlib import Path
import uvicorn

if __name__ == "__main__":
    current_dir = Path(__file__).parent.resolve()
    print("=" * 65)
    print("🌱 PlantGuard AI - Crop Disease Detection & Diagnosis Platform")
    print("=" * 65)
    print("🚀 Starting web server at: http://127.0.0.1:8000")
    print("📖 API Documentation at:  http://127.0.0.1:8000/docs")
    print("💡 Press Ctrl+C to stop the server.")
    print("=" * 65)
    
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
