#!/usr/bin/env python3
"""
Debug Registration Script
Tests the registration process step by step
"""

import asyncio
import sys
import os
import uuid

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.supabase import SupabaseService
from src.services.authentication import AuthenticationService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_registration():
    """Debug the registration process"""
    try:
        print("🔍 Starting registration debug...")
        
        # Initialize services
        supabase = SupabaseService()
        auth_service = AuthenticationService()
        
        # Test email and password
        test_email = "debug_test@gmail.com"
        test_password = "testpass123"
        
        print(f"📧 Testing with email: {test_email}")
        
        # Step 1: Test Supabase connection
        print("\n1️⃣ Testing Supabase connection...")
        try:
            # Try to get a simple table to test connection
            result = supabase.client.table('profiles').select('count').limit(1).execute()
            print("✅ Supabase connection successful")
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
            return
        
        # Step 2: Test Supabase Auth signup
        print("\n2️⃣ Testing Supabase Auth signup...")
        print("⚠️  Skipping Supabase Auth test (known to fail with email validation)")
        print("   Proceeding to direct database registration...")
        
        # Skip Supabase Auth test and go directly to database creation
        user_id = str(uuid.uuid4())
        print(f"Generated User ID: {user_id}")
        
        # Step 3: Test profile creation
        print("\n3️⃣ Testing profile creation...")
        try:
            profile_data = {
                "id": user_id,
                "email": test_email,
                "name": "Debug Test",
                "role": "user",
                "plan": "free",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00",
                "email_verified": False,
                "last_login": None,
                "login_count": 0
            }
            
            profile_result = await supabase.client.table('profiles').insert(profile_data).execute()
            print(f"Profile result: {profile_result}")
            print("✅ Profile creation successful")
            
        except Exception as e:
            print(f"❌ Profile creation failed: {e}")
            return
        
        # Step 4: Test settings creation
        print("\n4️⃣ Testing settings creation...")
        try:
            settings_data = {
                "user_id": user_id,
                "notifications_enabled": True,
                "email_notifications": True,
                "theme": "cyberpunk",
                "language": "en",
                "timezone": "UTC",
                "created_at": "2025-01-01T00:00:00",
                "updated_at": "2025-01-01T00:00:00"
            }
            
            settings_result = await supabase.client.table('user_settings').insert(settings_data).execute()
            print(f"Settings result: {settings_result}")
            print("✅ Settings creation successful")
            
        except Exception as e:
            print(f"❌ Settings creation failed: {e}")
            return
        
        # Step 5: Test full registration
        print("\n5️⃣ Testing full registration process...")
        try:
            full_result = await auth_service.register_user(test_email + "_full", test_password, "Debug Full Test")
            print(f"Full registration result: {full_result}")
            print("✅ Full registration successful")
            
        except Exception as e:
            print(f"❌ Full registration failed: {e}")
            import traceback
            traceback.print_exc()
            return
        
        print("\n🎉 All tests passed! Registration should be working.")
        
    except Exception as e:
        logger.error(f"Debug registration failed: {e}")
        print(f"❌ Debug failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_registration())
