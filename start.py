#!/usr/bin/env python3
"""
Railway Startup Script for Kolekt
Handles Railway's PORT environment variable and startup requirements
"""

import os
import sys
import uvicorn
from pathlib import Path

def main():
    """Main startup function"""
    # Add src to Python path
    src_path = Path(__file__).parent / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
    
    # Get Railway environment variables
    port_str = os.getenv('PORT', '8000')
    host = os.getenv('HOST', '0.0.0.0')
    
    # Handle port conversion with error handling
    try:
        port = int(port_str)
        print(f"🚂 Railway: Starting Kolekt on {host}:{port}")
    except ValueError:
        print(f"⚠️  Invalid PORT value: {port_str}, using default 8000")
        port = 8000
    
    # Print environment info
    print(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'production')}")
    print(f"🔗 Host: {host}")
    print(f"🚪 Port: {port}")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Check if required files exist
    if not Path("start_kolekt.py").exists():
        print("❌ Error: start_kolekt.py not found!")
        sys.exit(1)
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    if not logs_dir.exists():
        logs_dir.mkdir(exist_ok=True)
        print(f"📁 Created logs directory: {logs_dir}")
    
    try:
        # Start the application
        print("🚀 Starting Kolekt application...")
        uvicorn.run(
            "start_kolekt:app",
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            reload=False  # Disable reload in production
        )
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
