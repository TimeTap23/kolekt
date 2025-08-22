#!/usr/bin/env python3
"""
Check Admin User Script
Check if admin user exists in the database
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.services.supabase import supabase_service

def check_admin_user():
    """Check if admin user exists in the database"""
    
    print("🔍 Checking admin user in database...")
    
    try:
        # Check profiles table
        response = supabase_service.client.table("profiles").select("*").eq("email", "admin@kolekt.io").execute()
        
        if response.data:
            admin = response.data[0]
            print("✅ Admin user found in profiles table:")
            print(f"   ID: {admin['id']}")
            print(f"   Email: {admin['email']}")
            print(f"   Name: {admin['name']}")
            print(f"   Role: {admin['role']}")
            print(f"   Plan: {admin['plan']}")
            print(f"   Is Active: {admin['is_active']}")
            print(f"   Is Verified: {admin['is_verified']}")
            return True
        else:
            print("❌ Admin user not found in profiles table")
            return False
            
    except Exception as e:
        print(f"❌ Error checking admin user: {e}")
        return False

def check_supabase_auth():
    """Check if admin user exists in Supabase Auth"""
    
    print("\n🔍 Checking admin user in Supabase Auth...")
    
    try:
        # List all users
        auth_response = supabase_service.client.auth.admin.list_users()
        
        admin_user = None
        for user in auth_response:
            if user.email == "admin@kolekt.io":
                admin_user = user
                break
        
        if admin_user:
            print("✅ Admin user found in Supabase Auth:")
            print(f"   ID: {admin_user.id}")
            print(f"   Email: {admin_user.email}")
            print(f"   Email Confirmed: {admin_user.email_confirmed_at is not None}")
            print(f"   Created: {admin_user.created_at}")
            return True
        else:
            print("❌ Admin user not found in Supabase Auth")
            return False
            
    except Exception as e:
        print(f"❌ Error checking Supabase Auth: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Admin User Check")
    print("=" * 30)
    
    profiles_ok = check_admin_user()
    auth_ok = check_supabase_auth()
    
    print("\n" + "=" * 30)
    print("📊 SUMMARY")
    print("=" * 30)
    
    if profiles_ok and auth_ok:
        print("✅ Admin user is properly set up!")
        print("   Both profiles table and Supabase Auth have the admin user")
    elif profiles_ok:
        print("⚠️ Admin user exists in profiles but not in Supabase Auth")
    elif auth_ok:
        print("⚠️ Admin user exists in Supabase Auth but not in profiles")
    else:
        print("❌ Admin user is missing from both tables")
    
    return profiles_ok and auth_ok

if __name__ == "__main__":
    main()
