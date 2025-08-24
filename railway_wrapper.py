#!/usr/bin/env python3
"""
Railway Wrapper Script
This script is called by Railway and handles the PORT environment variable
"""

import os
import sys
import subprocess

def main():
    # Get port from Railway environment
    port = os.getenv('PORT', '8000')
    
    # Validate port
    try:
        port_int = int(port)
        print(f"🚂 Railway: Starting on port {port_int}")
    except ValueError:
        print(f"⚠️  Invalid PORT: {port}, using 8000")
        port_int = 8000
    
    # Set environment variable
    os.environ['PORT'] = str(port_int)
    
    # Start the application using uvicorn directly
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'start_kolekt:app',
        '--host', '0.0.0.0',
        '--port', str(port_int)
    ]
    
    print(f"🚀 Starting: {' '.join(cmd)}")
    
    # Execute the command
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
