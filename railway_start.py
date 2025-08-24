#!/usr/bin/env python3
"""
Railway Startup Script for Kolekt
Handles Railway's PORT environment variable correctly
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Get port from Railway environment
port = int(os.getenv('PORT', 8000))
host = os.getenv('HOST', '0.0.0.0')

print(f"🚂 Railway: Starting Kolekt on {host}:{port}")
print(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'production')}")

# Import and run the application
import uvicorn
from start_kolekt import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
