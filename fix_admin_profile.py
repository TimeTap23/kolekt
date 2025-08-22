#!/usr/bin/env python3
"""
Fix Admin Profile Script
Create the admin user profile in the profiles table
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.services.supabase import supabase_service

def fix_admin_profile():
    """Create admin user profile in the profiles table"""
    
    print("🔧 Fixing admin user profile...")
    
    try:
        # Get admin user from Supabase Auth
        auth_response = supabase_service.client.auth.admin.list_users()
        
        admin_user = None
        for user in auth_response:
            if user.email == "admin@kolekt.io":
                admin_user = user
                break
        
        if not admin_user:
            print("❌ Admin user not found in Supabase Auth")
            return False
        
        user_id = admin_user.id
        print(f"✅ Found admin user in Supabase Auth with ID: {user_id}")
        
        # Create profile data
        profile_data = {
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
        
        # Insert profile
        response = supabase_service.client.table("profiles").insert(profile_data).execute()
        
        if response.data:
            print("✅ Admin user profile created successfully!")
            print(f"   Profile ID: {response.data[0]['id']}")
            
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
        else:
            print("❌ Failed to create admin user profile")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing admin profile: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Fix Admin Profile")
    print("=" * 30)
    
    success = fix_admin_profile()
    
    if success:
        print("\n✅ Admin profile fixed successfully!")
        print("   You can now test admin functionality with:")
        print("   Email: admin@kolekt.io")
        print("   Password: admin123")
    else:
        print("\n❌ Failed to fix admin profile!")
    
    return success

if __name__ == "__main__":
    main()
