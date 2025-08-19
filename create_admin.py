#!/usr/bin/env python3
"""
Script to create an admin user for ThreadStorm
Run this script to create your first admin user
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
from src.services.authentication import auth_service

async def create_admin_user():
    """Create an admin user interactively"""
    print("🔧 ThreadStorm Admin User Creation")
    print("=" * 50)
    
    # Get user input
    email = input("Enter admin email: ").strip()
    if not email:
        print("❌ Email is required")
        return
    
    password = input("Enter admin password (min 8 characters): ").strip()
    if len(password) < 8:
        print("❌ Password must be at least 8 characters")
        return
    
    name = input("Enter admin name: ").strip()
    if not name:
        print("❌ Name is required")
        return
    
    # Confirm
    print(f"\n📋 Admin User Details:")
    print(f"Email: {email}")
    print(f"Name: {name}")
    print(f"Role: admin")
    
    confirm = input("\nCreate this admin user? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Admin user creation cancelled")
        return
    
    try:
        print("\n🔄 Creating admin user...")
        
        # Register the user
        user = await auth_service.register_user(email, password, name)
        
        # Update the user's role to admin
        await supabase_service.client.table("profiles").update({
            "role": "admin",
            "is_verified": True
        }).eq("id", user["id"]).execute()
        
        print("✅ Admin user created successfully!")
        print(f"User ID: {user['id']}")
        print(f"Email: {email}")
        print(f"Role: admin")
        print("\n🔗 You can now access the admin panel at: http://127.0.0.1:8000/admin")
        print("📝 Login with your email and password")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        print("💡 Make sure your Supabase configuration is correct")

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
    asyncio.run(create_admin_user())

if __name__ == "__main__":
    main()
