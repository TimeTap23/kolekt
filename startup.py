#!/usr/bin/env python3
"""
Startup script for Kolekt with Supabase integration
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run the main application
from main import app
import uvicorn

if __name__ == "__main__":
    print("🎮 Starting Kolekt with Supabase Integration...")
    print("⚡ Server will be available at: http://127.0.0.1:8000")
    print("🌐 Open your browser and navigate to the URL above")
    print("🚀 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )
