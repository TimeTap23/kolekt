#!/usr/bin/env python3
"""
Verify Social Connections Schema
Checks if the social_connections table and related objects were created successfully.
"""

import os
import sys
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def verify_social_connections_schema():
    """Verify that the social connections schema was applied correctly."""
    
    print("🔍 Verifying Social Connections Schema...")
    print("=" * 50)
    
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in .env file")
        print("Please ensure SUPABASE_URL and SUPABASE_ANON_KEY are set")
        return False
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
        
        # Check if social_connections table exists
        print("\n📋 Checking social_connections table...")
        try:
            result = supabase.table("social_connections").select("count", count="exact").execute()
            print(f"✅ social_connections table exists with {result.count} records")
        except Exception as e:
            print(f"❌ social_connections table not found: {e}")
            return False
        
        # Check table structure
        print("\n🏗️  Checking table structure...")
        try:
            # Try to select all columns to verify structure
            result = supabase.table("social_connections").select("*").limit(1).execute()
            columns = list(result.data[0].keys()) if result.data else []
            
            expected_columns = [
                'id', 'user_id', 'platform', 'account_id', 'username', 
                'display_name', 'profile_pic_url', 'access_token', 'refresh_token',
                'token_expires_at', 'scopes', 'followers_count', 'following_count',
                'is_active', 'last_sync_at', 'connected_at', 'updated_at'
            ]
            
            missing_columns = [col for col in expected_columns if col not in columns]
            if missing_columns:
                print(f"❌ Missing columns: {missing_columns}")
                return False
            else:
                print(f"✅ All expected columns present: {len(columns)} columns")
                
        except Exception as e:
            print(f"❌ Error checking table structure: {e}")
            return False
        
        # Check sample data
        print("\n📊 Checking sample data...")
        try:
            result = supabase.table("social_connections").select("*").execute()
            
            if result.data:
                print(f"✅ Found {len(result.data)} connection records")
                
                # Check for our test user's connections
                test_user_connections = [
                    conn for conn in result.data 
                    if conn.get('user_id') == '550e8400-e29b-41d4-a716-446655440000'
                ]
                
                if test_user_connections:
                    print(f"✅ Found {len(test_user_connections)} connections for test user")
                    for conn in test_user_connections:
                        print(f"   - {conn['platform']}: @{conn['username']} ({conn['display_name']})")
                else:
                    print("⚠️  No connections found for test user")
            else:
                print("⚠️  No connection records found")
                
        except Exception as e:
            print(f"❌ Error checking sample data: {e}")
            return False
        
        # Test encryption functions
        print("\n🔐 Testing encryption functions...")
        try:
            # Test encrypt function
            result = supabase.rpc('encrypt_social_token', {'token': 'test_token_123'}).execute()
            if result.data:
                print("✅ encrypt_social_token function works")
            else:
                print("❌ encrypt_social_token function failed")
                return False
                
            # Test decrypt function
            result = supabase.rpc('decrypt_social_token', {'encrypted_token': 'test_token_123'}).execute()
            if result.data:
                print("✅ decrypt_social_token function works")
            else:
                print("❌ decrypt_social_token function failed")
                return False
                
        except Exception as e:
            print(f"❌ Error testing encryption functions: {e}")
            return False
        
        # Test constraints
        print("\n🔒 Testing constraints...")
        try:
            # Try to insert duplicate connection (should fail)
            duplicate_data = {
                'user_id': '550e8400-e29b-41d4-a716-446655440000',
                'platform': 'threads',  # Already exists
                'account_id': 'duplicate_test',
                'username': 'duplicate_user',
                'display_name': 'Duplicate User',
                'access_token': 'duplicate_token'
            }
            
            result = supabase.table("social_connections").insert(duplicate_data).execute()
            print("❌ Duplicate constraint not working - should have failed")
            return False
            
        except Exception as e:
            if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
                print("✅ Unique constraint working correctly")
            else:
                print(f"⚠️  Unexpected error testing constraint: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Social Connections Schema Verification Complete!")
        print("✅ All checks passed - schema is ready for use")
        
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")
        return False

async def test_api_endpoints():
    """Test the social connections API endpoints."""
    
    print("\n🌐 Testing API Endpoints...")
    print("=" * 50)
    
    import requests
    
    base_url = "http://127.0.0.1:8000"
    test_user_id = "550e8400-e29b-41d4-a716-446655440000"
    
    endpoints_to_test = [
        f"/api/v1/connections/{test_user_id}",
        f"/api/v1/connections/{test_user_id}/status",
        f"/api/v1/connections/{test_user_id}/threads",
        f"/api/v1/connections/{test_user_id}/facebook",
        f"/api/v1/connections/{test_user_id}/instagram"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                print(f"✅ {endpoint} - {response.status_code}")
                data = response.json()
                if isinstance(data, dict) and 'connections' in data:
                    print(f"   Found {len(data['connections'])} connections")
            else:
                print(f"⚠️  {endpoint} - {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint} - Server not running")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

if __name__ == "__main__":
    print("🚀 Social Connections Schema Verification")
    print("=" * 50)
    
    # Run schema verification
    success = asyncio.run(verify_social_connections_schema())
    
    if success:
        # Test API endpoints if server is running
        try:
            asyncio.run(test_api_endpoints())
        except Exception as e:
            print(f"\n⚠️  API testing skipped: {e}")
            print("   Start the server with 'python start_kolekt.py' to test API endpoints")
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Verification complete! Your social connections are ready.")
        print("\nNext steps:")
        print("1. Start the server: python start_kolekt.py")
        print("2. Open the dashboard: http://127.0.0.1:8000/dashboard")
        print("3. Test the OAuth flow with real social media platforms")
    else:
        print("❌ Verification failed. Please check the manual setup guide.")
        print("   See: MANUAL_SOCIAL_CONNECTIONS_SETUP.md")
