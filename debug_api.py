#!/usr/bin/env python3
"""
Debug script to see exact API errors
"""

import requests
import json

def debug_api():
    """Debug the API endpoints to see exact errors"""
    
    print("🔍 Debugging API Endpoints")
    print("=" * 40)
    
    BASE_URL = "http://127.0.0.1:8000"
    TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440000"  # Valid UUID
    
    # Test 1: Health endpoint
    print("1. Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 2: Manual ingestion with detailed error
    print("2. Testing Manual Ingestion...")
    test_items = [
        {
            "title": "Test Article",
            "url": "https://example.com/test",
            "raw": "This is a test article for debugging purposes."
        }
    ]
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/curation/ingest/manual?user_id={TEST_USER_ID}",
            json=test_items,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Response: {response.text}")
        
        if response.status_code != 200:
            print(f"   Error Details:")
            try:
                error_data = response.json()
                print(f"   JSON Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Raw Error: {response.text}")
                
    except Exception as e:
        print(f"   Request Error: {e}")
    
    print()
    
    # Test 3: Check if server is running
    print("3. Checking Server Status...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Root Status: {response.status_code}")
    except Exception as e:
        print(f"   Server Error: {e}")

if __name__ == "__main__":
    debug_api()
