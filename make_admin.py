#!/usr/bin/env python3
"""
Script to make an existing user an admin
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

async def make_user_admin():
    """Make an existing user an admin"""
    print("🔧 ThreadStorm Admin User Setup")
    print("=" * 50)
    
    # Get user input
    email = input("Enter the email of the user to make admin: ").strip()
    if not email:
        print("❌ Email is required")
        return
    
    try:
        print(f"\n🔄 Making user {email} an admin...")
        
        # First, find the user by email
        response = supabase_service.client.table("profiles").select("*").eq("email", email).execute()
        
        if not response.data:
            print(f"❌ User with email {email} not found")
            return
        
        user = response.data[0]
        user_id = user["id"]
        
        print(f"✅ Found user: {user.get('name', email)}")
        
        # Update the user to be an admin
        update_response = supabase_service.client.table("profiles").update({
            "role": "admin",
            "is_verified": True,
            "is_active": True
        }).eq("id", user_id).execute()
        
        if update_response.data:
            print("✅ User successfully made admin!")
            print(f"User ID: {user_id}")
            print(f"Email: {email}")
            print(f"Role: admin")
            print("\n🔗 You can now access the admin panel at: http://127.0.0.1:8000/admin")
            print("📝 Login with your email and password")
        else:
            print("❌ Failed to update user")
        
    except Exception as e:
        print(f"❌ Error making user admin: {e}")

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
    asyncio.run(make_user_admin())

if __name__ == "__main__":
    main()
