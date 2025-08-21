#!/usr/bin/env python3
"""
Local Development Server for Kolekt
Simple script to run the app locally for development
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import and run the app
from start_kolekt_simple import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Kolekt Local Development Server")
    print("📍 Local URL: http://localhost:8000")
    print("📝 API Docs: http://localhost:8000/docs")
    print("🔧 Press Ctrl+C to stop the server")
    print()
    
    # Run the development server
    uvicorn.run(
        "start_kolekt_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
