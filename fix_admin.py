#!/usr/bin/env python3
"""
Script to fix user profile and make them an admin
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

async def fix_user_profile():
    """Fix user profile and make them admin"""
    print("🔧 ThreadStorm Admin User Fix")
    print("=" * 50)
    
    user_id = "d917b37a-456d-440a-a7e6-488af7b5c0dc"
    email = "marcus@marteklabs.com"
    name = "Marcus"
    
    try:
        print(f"🔄 Fixing user profile for {email}...")
        
        # Update the user profile with missing information
        update_response = supabase_service.client.table("profiles").update({
            "email": email,
            "name": name,
            "role": "admin",
            "is_verified": True,
            "is_active": True,
            "plan": "business"
        }).eq("id", user_id).execute()
        
        if update_response.data:
            print("✅ User profile successfully updated!")
            print(f"User ID: {user_id}")
            print(f"Email: {email}")
            print(f"Name: {name}")
            print(f"Role: admin")
            print(f"Plan: business")
            print(f"Verified: True")
            print(f"Active: True")
            print("\n🔗 You can now access the admin panel at: http://127.0.0.1:8000/admin")
            print("📝 Login with your email and password")
        else:
            print("❌ Failed to update user profile")
        
    except Exception as e:
        print(f"❌ Error fixing user profile: {e}")

def main():
    """Main function"""
    print("🚀 ThreadStorm Admin Setup")
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
    asyncio.run(fix_user_profile())

if __name__ == "__main__":
    main()
