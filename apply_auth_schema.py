#!/usr/bin/env python3
"""
Apply authentication schema to Supabase
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def show_schema_instructions():
    """Show instructions for applying the schema"""
    print("🔐 Authentication Schema Setup")
    print("=" * 40)
    print()
    print("To set up authentication, please follow these steps:")
    print()
    print("1. Go to your Supabase project dashboard")
    print("2. Navigate to the SQL Editor")
    print("3. Copy and paste the following SQL:")
    print()
    print("-" * 40)
    
    # Read and display the schema
    with open('create_auth_schema.sql', 'r') as f:
        schema_content = f.read()
        print(schema_content)
    
    print("-" * 40)
    print()
    print("4. Click 'Run' to execute the SQL")
    print("5. This will create the profiles table and add test users")
    print()
    print("Test users created:")
    print("- Email: test@example.com, Password: 123")
    print("- Email: admin@example.com, Password: 123")
    print()
    print("After applying the schema, you can test authentication with:")
    print("python test_auth.py")

if __name__ == "__main__":
    show_schema_instructions()
