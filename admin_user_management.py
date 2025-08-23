#!/usr/bin/env python3
"""
Admin User Management Script
Removes test users and creates proper admin user
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def cleanup_users():
    """Remove test users and create admin user - synchronous version"""
    
    print("🧹 User Cleanup Script")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    try:
        from supabase import create_client, Client
        
        # Get Supabase credentials
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Use service role for admin operations
        
        if not url or not key:
            print("❌ Missing Supabase credentials")
            return False
        
        print("🔗 Connecting to Supabase...")
        supabase: Client = create_client(url, key)
        
        # Get all users from profiles table
        print("\n📋 Getting all users...")
        response = supabase.table('profiles').select('*').execute()
        users = response.data
        
        print(f"Found {len(users)} users:")
        for user in users:
            email = user.get('email') or 'No email'
            user_id = user.get('id') or 'No ID'
            print(f"  - {email} (ID: {user_id})")
        
        # Remove test users and users with no email
        print("\n🗑️ Removing test users...")
        test_emails = [
            'test@example.com',
            'admin@kolekt.io',  # Old test admin
            'user@test.com',
            'demo@test.com',
            'admin@threadstorm.com',  # Old test admin
            'local_test_',  # Any local test users
            'login_local_'  # Any login test users
        ]
        
        deleted_count = 0
        for user in users:
            email = user.get('email', '')
            if not email:  # Delete users with no email
                try:
                    supabase.table('profiles').delete().eq('id', user['id']).execute()
                    print(f"  ✅ Deleted user with no email (ID: {user.get('id')})")
                    deleted_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to delete user with no email: {e}")
            else:
                # Check if it's a test email
                email_lower = email.lower()
                if any(test_email in email_lower for test_email in test_emails):
                    try:
                        supabase.table('profiles').delete().eq('id', user['id']).execute()
                        print(f"  ✅ Deleted test user: {email}")
                        deleted_count += 1
                    except Exception as e:
                        print(f"  ❌ Failed to delete {email}: {e}")
        
        print(f"\n🗑️ Deleted {deleted_count} test users")
        
        # Create admin user
        print("\n👤 Creating admin user...")
        
        # Check if admin user already exists
        admin_response = supabase.table('profiles').select('*').eq('email', 'info@marteklabs.com').execute()
        
        if admin_response.data:
            print("  ⚠️ Admin user already exists")
            admin_user = admin_response.data[0]
            print(f"  - Email: {admin_user.get('email')}")
            print(f"  - Role: {admin_user.get('role')}")
            print(f"  - ID: {admin_user.get('id')}")
            
            # Update to ensure admin role
            if admin_user.get('role') != 'admin':
                print("  🔧 Updating user role to admin...")
                supabase.table('profiles').update({'role': 'admin', 'plan': 'business'}).eq('id', admin_user['id']).execute()
                print("  ✅ Role updated to admin")
        else:
            # Check if user exists in auth but not in profiles
            print("  🔧 Checking if admin user exists in auth system...")
            
            # Try to get users by email from auth
            try:
                auth_users = supabase.auth.admin.list_users()
                admin_auth_user = None
                
                for user in auth_users:
                    if user.email == "info@marteklabs.com":
                        admin_auth_user = user
                        break
                
                if admin_auth_user:
                    print(f"  ✅ Found existing auth user: {admin_auth_user.id}")
                    
                    # Create profile for existing auth user
                    profile_data = {
                        "id": admin_auth_user.id,
                        "email": "info@marteklabs.com",
                        "name": "Admin User",
                        "role": "admin",
                        "plan": "business",
                        "email_verified": True
                    }
                    
                    supabase.table('profiles').insert(profile_data).execute()
                    print("  ✅ Admin profile created for existing auth user")
                    print(f"  - Email: info@marteklabs.com")
                    print(f"  - Password: kolectio123")
                    print(f"  - ID: {admin_auth_user.id}")
                else:
                    # Create new user in auth
                    print("  🔧 Creating new admin user in auth...")
                    
                    auth_response = supabase.auth.admin.create_user({
                        "email": "info@marteklabs.com",
                        "password": "kolectio123",
                        "email_confirm": True,
                        "user_metadata": {
                            "name": "Admin User"
                        }
                    })
                    
                    if auth_response.user:
                        user_id = auth_response.user.id
                        
                        # Create admin profile
                        profile_data = {
                            "id": user_id,
                            "email": "info@marteklabs.com",
                            "name": "Admin User",
                            "role": "admin",
                            "plan": "business",
                            "email_verified": True
                        }
                        
                        supabase.table('profiles').insert(profile_data).execute()
                        print("  ✅ Admin user created successfully")
                        print(f"  - Email: info@marteklabs.com")
                        print(f"  - Password: kolectio123")
                        print(f"  - ID: {user_id}")
                    else:
                        print(f"  ❌ Failed to create admin user in auth system")
                        return False
                        
            except Exception as e:
                print(f"  ❌ Error handling admin user creation: {e}")
                return False
        
        # Show final user list
        print("\n📋 Final user list:")
        final_response = supabase.table('profiles').select('*').execute()
        final_users = final_response.data
        
        for user in final_users:
            email = user.get('email', 'No email')
            role = user.get('role', 'No role')
            print(f"  - {email} (Role: {role})")
        
        print(f"\n✅ Cleanup completed! {len(final_users)} users remaining")
        return True
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main cleanup function"""
    success = cleanup_users()
    
    if success:
        print("\n🎉 User cleanup completed successfully!")
        print("\n📋 Admin Login Details:")
        print("  - Email: info@marteklabs.com")
        print("  - Password: kolectio123")
        print("  - URL: https://threadstorm-v6-kuo7e.ondigitalocean.app/admin-dashboard")
    else:
        print("\n⚠️ User cleanup failed. Please check the errors above.")

if __name__ == "__main__":
    main()
