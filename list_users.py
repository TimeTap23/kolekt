#!/usr/bin/env python3
"""
Script to list existing users in the database
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.config import settings
from src.services.supabase import supabase_service

async def list_users():
    """List all users in the database"""
    print("👥 ThreadStorm User List")
    print("=" * 50)
    
    try:
        # List users from auth.users
        print("🔍 Checking auth.users table...")
        auth_response = supabase_service.client.auth.admin.list_users()
        
        if auth_response:
            print(f"✅ Found {len(auth_response)} users in auth system:")
            for user in auth_response:
                print(f"  - ID: {user.id}")
                print(f"    Email: {user.email}")
                print(f"    Created: {user.created_at}")
                print(f"    Confirmed: {user.email_confirmed_at is not None}")
                print()
        else:
            print("❌ No users found in auth system")
        
        # List users from profiles table
        print("🔍 Checking profiles table...")
        profiles_response = supabase_service.client.table("profiles").select("*").execute()
        
        if profiles_response.data:
            print(f"✅ Found {len(profiles_response.data)} users in profiles table:")
            for profile in profiles_response.data:
                print(f"  - ID: {profile.get('id')}")
                print(f"    Email: {profile.get('email', 'N/A')}")
                print(f"    Name: {profile.get('name', 'N/A')}")
                print(f"    Role: {profile.get('role', 'N/A')}")
                print(f"    Active: {profile.get('is_active', 'N/A')}")
                print()
        else:
            print("❌ No users found in profiles table")
        
    except Exception as e:
        print(f"❌ Error listing users: {e}")

def main():
    """Main function"""
    print("🚀 ThreadStorm User Management")
    print("=" * 50)
    
    # Check if required environment variables are set
    required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'SUPABASE_KEY']
    missing_vars = [var for var in required_vars if not getattr(settings, var, None)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Please run setup_supabase.py first to configure your environment")
        return
    
    # Run the async function
    asyncio.run(list_users())

if __name__ == "__main__":
    main()
