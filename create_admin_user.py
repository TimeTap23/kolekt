#!/usr/bin/env python3
"""
Create Admin User Script
Creates an admin user for testing the Kolekt admin dashboard
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.supabase import SupabaseService
from src.services.authentication import AuthenticationService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_admin_user():
    """Create an admin user for testing"""
    try:
        supabase = SupabaseService()
        auth_service = AuthenticationService()
        
        # Admin user details
        admin_email = "admin@kolekt.io"
        admin_password = "admin123456"  # Change this in production!
        admin_name = "Kolekt Admin"
        
        logger.info(f"Creating admin user: {admin_email}")
        
        # Check if admin user already exists
        existing_user = supabase.client.table("profiles").select("*").eq("email", admin_email).execute()
        
        if existing_user.data:
            logger.info(f"Admin user {admin_email} already exists")
            user = existing_user.data[0]
            
            # Update user to admin role if not already
            if user.get('role') != 'admin':
                logger.info("Updating user to admin role")
                supabase.client.table("profiles").update({
                    "role": "admin",
                    "is_active": True,
                    "is_verified": True
                }).eq("id", user['id']).execute()
                logger.info("User updated to admin role")
            else:
                logger.info("User is already an admin")
            
            return user
        else:
            # Create new admin user
            logger.info("Creating new admin user")
            
            # Register the user
            user_data = await auth_service.register_user(
                email=admin_email,
                password=admin_password,
                name=admin_name
            )
            
            # Update user to admin role
            supabase.client.table("profiles").update({
                "role": "admin",
                "is_active": True,
                "is_verified": True
            }).eq("id", user_data['user_id']).execute()
            
            logger.info(f"Admin user created successfully: {user_data['user_id']}")
            return user_data
            
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        raise

async def main():
    """Main function"""
    try:
        user = await create_admin_user()
        print("\n" + "="*50)
        print("ADMIN USER CREATED SUCCESSFULLY")
        print("="*50)
        print(f"Email: {user.get('email', 'admin@kolekt.io')}")
        print(f"Password: admin123456")
        print(f"User ID: {user.get('user_id', user.get('id'))}")
        print("\nYou can now:")
        print("1. Visit http://localhost:8000/admin")
        print("2. Use the admin dashboard to manage Kolekt")
        print("\n⚠️  IMPORTANT: Change the password in production!")
        print("="*50)
        
    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
