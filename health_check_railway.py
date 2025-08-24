#!/usr/bin/env python3
"""
Railway Health Check Script
Simple script to verify the application is running
"""

import os
import sys
import requests
import time
from pathlib import Path

def check_health():
    """Check if the application is healthy"""
    try:
        # Get the port from environment
        port = os.getenv('PORT', '8000')
        host = os.getenv('HOST', '0.0.0.0')
        
        # Try to connect to the health endpoint
        url = f"http://{host}:{port}/health"
        print(f"🔍 Checking health at: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed!")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Version: {data.get('version', 'unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    """Main health check function"""
    print("🏥 Railway Health Check")
    print("=" * 30)
    
    # Wait a bit for the app to start
    print("⏳ Waiting for application to start...")
    time.sleep(5)
    
    # Try multiple times
    max_attempts = 3
    for attempt in range(max_attempts):
        print(f"\n🔄 Attempt {attempt + 1}/{max_attempts}")
        
        if check_health():
            print("🎉 Application is healthy!")
            return 0
        else:
            if attempt < max_attempts - 1:
                print("⏳ Retrying in 5 seconds...")
                time.sleep(5)
    
    print("❌ Health check failed after all attempts")
    return 1

if __name__ == "__main__":
    sys.exit(main())
