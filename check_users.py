#!/usr/bin/env python3
"""
Check Users
Lists all users in the profiles table
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def check_users():
    """Check what users exist in the profiles table"""
    
    print("👥 Checking Users in Profiles Table")
    print("=" * 50)
    
    # Get credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        return
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Get all users
        response = supabase.from_('profiles').select('*').execute()
        
        if response.data:
            print(f"✅ Found {len(response.data)} users:")
            for user in response.data:
                print(f"   - ID: {user.get('id')}")
                print(f"     Email: {user.get('email')}")
                print(f"     Name: {user.get('name')}")
                print(f"     Created: {user.get('created_at')}")
                print()
        else:
            print("ℹ️  No users found in profiles table")
            
    except Exception as e:
        print(f"❌ Error checking users: {e}")

if __name__ == "__main__":
    check_users()
