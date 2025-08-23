#!/usr/bin/env python3
"""
User Cleanup Script
Removes test users and creates proper admin user
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

async def cleanup_users():
    """Remove test users and create admin user"""
    
    print("🧹 User Cleanup Script")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    try:
        from src.services.supabase import SupabaseService
        
        print("🔗 Connecting to Supabase...")
        supabase = SupabaseService()
        
        # Get all users
        print("\n📋 Getting all users...")
        response = supabase.table('profiles').select('*').execute()
        users = response.data
        
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  - {user.get('email', 'No email')} (ID: {user.get('id', 'No ID')})")
        
        # Remove test users
        print("\n🗑️ Removing test users...")
        test_emails = [
            'test@example.com',
            'admin@kolekt.io',  # Old test admin
            'user@test.com',
            'demo@test.com',
            'admin@threadstorm.com'  # Old test admin
        ]
        
        deleted_count = 0
        for user in users:
            email = user.get('email', '')
            if email is None:
                email = ''
            email = email.lower()
            
            # Delete users with no email or test emails
            if not email or any(test_email in email for test_email in test_emails):
                try:
                    supabase.table('profiles').delete().eq('id', user['id']).execute()
                    print(f"  ✅ Deleted test user: {email or 'No email'}")
                    deleted_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to delete {email or 'No email'}: {e}")
        
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
        else:
            # Create admin user in Supabase Auth
            auth_response = await supabase.sign_up(
                email="info@marteklabs.com",
                password="kolectio123",
                user_data={"name": "Admin User"}
            )
            
            if auth_response.get("success"):
                user = auth_response["user"]
                
                # Create admin profile
                profile_data = {
                    "id": user.id,
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
                print(f"  - ID: {user.id}")
            else:
                print(f"  ❌ Failed to create admin user: {auth_response.get('error')}")
        
        # Show final user list
        print("\n📋 Final user list:")
        final_response = supabase.table('profiles').select('*').execute()
        final_users = final_response.data
        
        for user in final_users:
            print(f"  - {user.get('email', 'No email')} (Role: {user.get('role', 'No role')})")
        
        print(f"\n✅ Cleanup completed! {len(final_users)} users remaining")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False
    
    return True

def main():
    """Main cleanup function"""
    async def run_cleanup():
        success = await cleanup_users()
        
        if success:
            print("\n🎉 User cleanup completed successfully!")
            print("\n📋 Admin Login Details:")
            print("  - Email: info@marteklabs.com")
            print("  - Password: kolectio123")
            print("  - URL: https://threadstorm-v6-kuo7e.ondigitalocean.app/admin-dashboard")
        else:
            print("\n⚠️ User cleanup failed. Please check the errors above.")
    
    # Run async cleanup
    asyncio.run(run_cleanup())

if __name__ == "__main__":
    main()
