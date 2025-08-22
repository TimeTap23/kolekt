#!/usr/bin/env python3
"""
Check Supabase Configuration Script
Helps diagnose and fix Supabase authentication issues
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.supabase import SupabaseService
from src.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_supabase_config():
    """Check Supabase configuration and authentication settings"""
    try:
        print("🔍 Checking Supabase Configuration...")
        
        # Initialize Supabase service
        supabase = SupabaseService()
        
        print(f"\n📋 Configuration:")
        print(f"   Supabase URL: {settings.SUPABASE_URL}")
        print(f"   Service Key: {'✅ Set' if settings.SUPABASE_KEY else '❌ Missing'}")
        print(f"   Anon Key: {'✅ Set' if settings.SUPABASE_ANON_KEY else '❌ Missing'}")
        
        # Test connection
        print(f"\n🔗 Testing Connection...")
        try:
            result = supabase.client.table('profiles').select('count').limit(1).execute()
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return
        
        # Check if auth.users table exists and has data
        print(f"\n👥 Checking Auth Tables...")
        try:
            # Try to get auth settings
            auth_settings = supabase.client.rpc('get_auth_settings').execute()
            print("✅ Auth settings accessible")
        except Exception as e:
            print(f"⚠️  Could not access auth settings: {e}")
        
        # Test email validation
        print(f"\n📧 Testing Email Validation...")
        test_emails = [
            "test@example.com",
            "test@gmail.com", 
            "test@outlook.com",
            "test@kolekt.io"
        ]
        
        for email in test_emails:
            try:
                # Try to sign up with each email
                response = await supabase.sign_up(email, "testpass123", {"name": "Test User"})
                if response.get("success"):
                    print(f"✅ {email} - Registration successful")
                    # Clean up - delete the test user
                    if response.get("user"):
                        await supabase.client.auth.admin.delete_user(response["user"].id)
                else:
                    print(f"❌ {email} - {response.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"❌ {email} - Exception: {e}")
        
        print(f"\n🔧 Recommended Fixes:")
        print(f"1. Check Supabase Dashboard > Authentication > Settings")
        print(f"2. Verify 'Enable email confirmations' is OFF for testing")
        print(f"3. Check 'Enable email change confirmations' is OFF")
        print(f"4. Verify 'Enable phone confirmations' is OFF")
        print(f"5. Check 'Enable phone change confirmations' is OFF")
        print(f"6. Under 'Site URL', make sure it includes your domain")
        print(f"7. Under 'Redirect URLs', add: http://localhost:8000/auth/callback")
        print(f"8. Under 'Additional redirect URLs', add your production URLs")
        
        print(f"\n📝 Next Steps:")
        print(f"1. Go to your Supabase Dashboard")
        print(f"2. Navigate to Authentication > Settings")
        print(f"3. Disable email confirmations temporarily")
        print(f"4. Add your redirect URLs")
        print(f"5. Test registration again")
        
    except Exception as e:
        logger.error(f"Configuration check failed: {e}")
        print(f"❌ Check failed: {e}")

if __name__ == "__main__":
    asyncio.run(check_supabase_config())
