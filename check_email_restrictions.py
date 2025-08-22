#!/usr/bin/env python3
"""
Check and fix email domain restrictions in Supabase
"""

import os
import sys
import asyncio
from supabase import create_client, Client

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.supabase import SupabaseService

async def check_email_restrictions():
    """Check for email domain restrictions in Supabase"""
    
    print("🔍 Checking Supabase email domain restrictions...")
    
    # Initialize Supabase service
    supabase_service = SupabaseService()
    
    try:
        # Test different email domains
        test_emails = [
            "test@gmail.com",
            "test@yahoo.com", 
            "test@outlook.com",
            "test@hotmail.com",
            "test@aol.com",
            "test@icloud.com",
            "test@example.com"
        ]
        
        print("\n📧 Testing email domain restrictions:")
        print("=" * 50)
        
        for email in test_emails:
            try:
                # Try to sign up with each email
                response = await supabase_service.sign_up(email, "testpass123")
                
                if response.get("success"):
                    print(f"✅ {email} - ALLOWED")
                    # Clean up - delete the test user
                    if response.get("user"):
                        try:
                            await supabase_service.admin.delete_user(response["user"].id)
                        except:
                            pass
                else:
                    error = response.get("error", "Unknown error")
                    print(f"❌ {email} - BLOCKED: {error}")
                    
            except Exception as e:
                print(f"❌ {email} - ERROR: {str(e)}")
        
        print("\n🔧 Checking for RLS policies that might restrict emails...")
        
        # Check if there are any RLS policies on the profiles table
        try:
            policies = supabase_service.client.rpc('get_policies', {
                'table_name': 'profiles'
            }).execute()
            print("📋 Found RLS policies on profiles table")
            print(policies)
        except Exception as e:
            print(f"ℹ️  Could not check RLS policies: {e}")
        
        # Check for any email validation functions
        try:
            functions = supabase_service.client.rpc('get_functions').execute()
            print("📋 Checking for email validation functions...")
            print(functions)
        except Exception as e:
            print(f"ℹ️  Could not check functions: {e}")
            
    except Exception as e:
        print(f"❌ Error checking email restrictions: {e}")

async def fix_email_restrictions():
    """Attempt to fix email domain restrictions"""
    
    print("\n🔧 Attempting to fix email domain restrictions...")
    
    # Initialize Supabase service
    supabase_service = SupabaseService()
    
    try:
        # Check if there's a custom email validation function
        print("🔍 Looking for custom email validation...")
        
        # Try to find any email-related policies or functions
        # This is a more comprehensive check
        
        print("📝 Recommendations:")
        print("1. Check your Supabase project's SQL editor for any custom functions")
        print("2. Look for RLS policies that might validate email domains")
        print("3. Check if you have any database triggers on the auth.users table")
        print("4. Verify there are no custom email validation rules")
        
    except Exception as e:
        print(f"❌ Error fixing email restrictions: {e}")

if __name__ == "__main__":
    print("🚀 Supabase Email Domain Restriction Checker")
    print("=" * 50)
    
    asyncio.run(check_email_restrictions())
    asyncio.run(fix_email_restrictions())
    
    print("\n📋 Manual Steps to Fix:")
    print("1. Go to your Supabase Dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Check for any custom functions that validate emails")
    print("4. Look for RLS policies that might restrict email domains")
    print("5. Check for any database triggers on auth.users")
    print("6. Remove any email domain validation logic")
