#!/usr/bin/env python3
"""
Apply centralized_logs table
Create the missing centralized_logs table for observability
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.supabase import supabase_service

async def create_centralized_logs():
    """Create the centralized_logs table"""
    print("📝 Creating centralized_logs table...")
    
    # Read the SQL file
    with open('create_centralized_logs.sql', 'r') as f:
        sql_content = f.read()
    
    try:
        # Execute the SQL using exec_sql function
        response = supabase_service.client.rpc('exec_sql', {'sql': sql_content}).execute()
        print("✅ centralized_logs table created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating centralized_logs table: {e}")
        return False

async def main():
    print("🔧 Applying centralized_logs table...")
    print("=" * 50)
    
    success = await create_centralized_logs()
    
    if success:
        print("\n🎉 centralized_logs table applied successfully!")
        print("📊 Observability logging should now work properly")
    else:
        print("\n⚠️ Failed to create centralized_logs table")
        print("🔧 Check the error message above")

if __name__ == "__main__":
    asyncio.run(main())
