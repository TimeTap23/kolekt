#!/usr/bin/env python3
"""
Debug OAuth Error
Helps identify the exact source of the OAuth connection error
"""

import requests
import json
import time
import os

def debug_oauth_error():
    """Debug the OAuth error step by step"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 Debugging OAuth Error")
    print("=" * 50)
    
    # Step 1: Check server health
    print("\n1. Checking server health...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Server is running")
        else:
            print(f"   ❌ Server health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Server not accessible: {e}")
        return
    
    # Step 2: Login to get token
    print("\n2. Logging in to get access token...")
    try:
        EMAIL = os.getenv("KOLEKT_TEST_EMAIL") or os.getenv("TEST_EMAIL") or ""
        PASSWORD = os.getenv("KOLEKT_TEST_PASSWORD") or os.getenv("TEST_PASSWORD") or ""
        if not EMAIL or not PASSWORD:
            print("   ❌ TEST_EMAIL/TEST_PASSWORD env vars not set (KOLEKT_TEST_* also supported)")
            return
        login_response = requests.post(f"{base_url}/api/v1/auth/login",
                                     headers={"Content-Type": "application/json"},
                                     json={
                                         "email": EMAIL,
                                         "password": PASSWORD
                                     })
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            access_token = login_data.get("access_token")
            print("   ✅ Login successful")
            print(f"   Token: {access_token[:20]}...")
        else:
            print(f"   ❌ Login failed: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return
    
    # Step 3: Test OAuth URL generation
    print("\n3. Testing OAuth URL generation...")
    try:
        oauth_response = requests.get(f"{base_url}/api/v1/connections/oauth/threads/url",
                                    headers={
                                        "Authorization": f"Bearer {access_token}"
                                    })
        
        print(f"   Status: {oauth_response.status_code}")
        
        if oauth_response.status_code == 200:
            oauth_data = oauth_response.json()
            print("   ✅ OAuth URL generated successfully")
            print(f"   URL: {oauth_data.get('oauth_url', 'N/A')}")
            
            # Extract the state parameter from the URL
            import urllib.parse
            parsed_url = urllib.parse.urlparse(oauth_data.get('oauth_url', ''))
            query_params = urllib.parse.parse_qs(parsed_url.query)
            state = query_params.get('state', [''])[0]
            print(f"   State: {state}")
            
        else:
            print(f"   ❌ OAuth URL generation failed")
            print(f"   Response: {oauth_response.text}")
            return
    except Exception as e:
        print(f"   ❌ OAuth URL error: {e}")
        return
    
    # Step 4: Test connection status before OAuth
    print("\n4. Testing connection status before OAuth...")
    try:
        status_response = requests.get(f"{base_url}/api/v1/connections/threads/status",
                                     headers={
                                         "Authorization": f"Bearer {access_token}"
                                     })
        
        print(f"   Status: {status_response.status_code}")
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            print("   ✅ Connection status retrieved")
            print(f"   Connected: {status_data.get('connection', {}).get('connected', 'N/A')}")
        else:
            print(f"   ❌ Connection status failed")
            print(f"   Response: {status_response.text}")
    except Exception as e:
        print(f"   ❌ Connection status error: {e}")
    
    # Step 5: Test OAuth callback with mock data
    print("\n5. Testing OAuth callback processing...")
    try:
        # Create a mock callback URL
        mock_callback_url = f"{base_url}/oauth/threads/callback?code=mock_code_123&state={state}"
        
        callback_response = requests.get(mock_callback_url)
        
        print(f"   Callback Status: {callback_response.status_code}")
        
        if callback_response.status_code == 200:
            print("   ✅ OAuth callback page served successfully")
            # Check if the page contains error handling
            content = callback_response.text
            if "error" in content.lower():
                print("   ⚠️  Callback page contains error handling")
            if "success" in content.lower():
                print("   ✅ Callback page contains success handling")
        else:
            print(f"   ❌ OAuth callback failed")
            print(f"   Response: {callback_response.text}")
    except Exception as e:
        print(f"   ❌ OAuth callback error: {e}")
    
    # Step 6: Test connection status after OAuth
    print("\n6. Testing connection status after OAuth...")
    try:
        time.sleep(1)  # Give some time for processing
        status_response = requests.get(f"{base_url}/api/v1/connections/threads/status",
                                     headers={
                                         "Authorization": f"Bearer {access_token}"
                                     })
        
        print(f"   Status: {status_response.status_code}")
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            print("   ✅ Connection status retrieved")
            print(f"   Connected: {status_data.get('connection', {}).get('connected', 'N/A')}")
        else:
            print(f"   ❌ Connection status failed")
            print(f"   Response: {status_response.text}")
    except Exception as e:
        print(f"   ❌ Connection status error: {e}")
    
    # Step 7: Check database for social connections
    print("\n7. Checking database for social connections...")
    try:
        # Test the connections endpoint
        connections_response = requests.get(f"{base_url}/api/v1/connections/status",
                                          headers={
                                              "Authorization": f"Bearer {access_token}"
                                          })
        
        print(f"   Status: {connections_response.status_code}")
        
        if connections_response.status_code == 200:
            connections_data = connections_response.json()
            print("   ✅ Connections status retrieved")
            print(f"   Total connected: {connections_data.get('total_connected', 'N/A')}")
            
            for conn in connections_data.get('connections', []):
                print(f"   - {conn.get('platform')}: {conn.get('connected')}")
        else:
            print(f"   ❌ Connections status failed")
            print(f"   Response: {connections_response.text}")
    except Exception as e:
        print(f"   ❌ Connections status error: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 Debug complete!")
    print("\n📝 Next Steps:")
    print("1. Open http://127.0.0.1:8000/dashboard")
    print("2. Open browser developer tools (F12)")
    print("3. Go to Console tab")
    print("4. Try connecting Threads account")
    print("5. Look for any JavaScript errors in the console")
    print("6. Check the Network tab for failed requests")

if __name__ == "__main__":
    debug_oauth_error()
