#!/usr/bin/env python3
"""
Create Admin User Script
Creates an admin user in the database for testing purposes
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import uuid

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.services.supabase import supabase_service

def create_admin_user():
    """Create an admin user in the database"""
    
    print("🔧 Creating admin user...")
    print(f"   Email: admin@kolekt.io")
    print(f"   Name: Admin User")
    print(f"   Role: admin")
    
    try:
        # First, try to create user in Supabase Auth
        try:
            auth_response = supabase_service.client.auth.admin.create_user({
                "email": "admin@kolekt.io",
                "password": "admin123",
                "email_confirm": True
            })
            
            if not auth_response.user:
                print("❌ Failed to create user in Supabase Auth")
                return False
            
            user_id = auth_response.user.id
            print(f"   ✅ Created in Supabase Auth with ID: {user_id}")
            
        except Exception as e:
            if "already been registered" in str(e):
                print("   ⚠️ Admin user already exists in Supabase Auth, getting existing user...")
                # Get existing user
                auth_response = supabase_service.client.auth.admin.list_users()
                admin_user = None
                for user in auth_response:
                    if user.email == "admin@kolekt.io":
                        admin_user = user
                        break
                
                if admin_user:
                    user_id = admin_user.id
                    print(f"   ✅ Found existing admin user with ID: {user_id}")
                else:
                    print("❌ Could not find existing admin user")
                    return False
            else:
                print(f"❌ Error creating admin user in Supabase Auth: {e}")
                return False
        
        # Now create profile
        admin_data = {
            "id": user_id,
            "email": "admin@kolekt.io",
            "name": "Admin User",
            "role": "admin",
            "plan": "pro",
            "is_active": True,
            "is_verified": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Try to insert admin user into profiles table
        try:
            response = supabase_service.client.table("profiles").insert(admin_data).execute()
            print("✅ Admin user profile created successfully!")
        except Exception as e:
            if "duplicate key" in str(e):
                print("⚠️ Admin user profile already exists, updating...")
                # Update existing profile to admin role
                response = supabase_service.client.table("profiles").update({
                    "role": "admin",
                    "name": "Admin User",
                    "plan": "pro",
                    "is_active": True,
                    "is_verified": True,
                    "updated_at": datetime.now().isoformat()
                }).eq("id", user_id).execute()
                print("✅ Admin user profile updated successfully!")
            else:
                print(f"❌ Error creating admin user profile: {e}")
                return False
        
        # Also create user settings
        settings_data = {
            "id": user_id,
            "notifications_enabled": True,
            "theme": "cyberpunk",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        try:
            settings_response = supabase_service.client.table("user_settings").insert(settings_data).execute()
            print("✅ Admin user settings created successfully!")
        except Exception as e:
            if "duplicate key" in str(e):
                print("⚠️ Admin user settings already exist")
            else:
                print(f"⚠️ Warning: Could not create user settings: {e}")
        
        return True
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def check_admin_user():
    """Check if admin user already exists"""
    try:
        response = supabase_service.client.table("profiles").select("*").eq("email", "admin@kolekt.io").eq("role", "admin").execute()
        
        if response.data:
            admin = response.data[0]
            print("✅ Admin user already exists!")
            print(f"   Email: {admin['email']}")
            print(f"   Name: {admin['name']}")
            print(f"   ID: {admin['id']}")
            return True
        else:
            print("❌ Admin user not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking admin user: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Admin User Setup")
    print("=" * 30)
    
    # Check if admin user already exists
    if check_admin_user():
        print("\n✅ Admin user is ready for testing!")
        return True
    
    # Create admin user
    print("\n🔧 Creating new admin user...")
    success = create_admin_user()
    
    if success:
        print("\n✅ Admin user setup complete!")
        print("   You can now test admin functionality with:")
        print("   Email: admin@kolekt.io")
        print("   Password: admin123")
    else:
        print("\n❌ Admin user setup failed!")
    
    return success

if __name__ == "__main__":
    main()
