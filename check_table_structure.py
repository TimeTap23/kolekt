#!/usr/bin/env python3
"""
Check Social Connections Table Structure
Examines the actual structure of the social_connections table.
"""

import os
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def check_table_structure():
    """Check the structure of the social_connections table."""
    
    print("🔍 Checking Social Connections Table Structure...")
    print("=" * 50)
    
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in .env file")
        return
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
        
        # Try to get table info by selecting all columns
        print("\n📋 Checking table structure...")
        try:
            result = supabase.table("social_connections").select("*").limit(1).execute()
            
            if hasattr(result, 'data') and result.data is not None:
                if len(result.data) > 0:
                    columns = list(result.data[0].keys())
                    print(f"✅ Table exists with {len(columns)} columns:")
                    for col in columns:
                        print(f"   - {col}")
                else:
                    print("✅ Table exists but is empty")
                    # Try to get column info from a different approach
                    print("   (Empty table - columns will be created when first record is inserted)")
            else:
                print("❌ Could not determine table structure")
                
        except Exception as e:
            print(f"❌ Error checking table structure: {e}")
            
        # Check if table exists by trying to count
        print("\n📊 Checking if table exists...")
        try:
            result = supabase.table("social_connections").select("count", count="exact").execute()
            print(f"✅ Table exists with {result.count} records")
        except Exception as e:
            print(f"❌ Table does not exist or error: {e}")
            
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")

if __name__ == "__main__":
    asyncio.run(check_table_structure())
