#!/usr/bin/env python3
"""
Check what tables exist in the Supabase database
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_tables():
    """Check what tables exist in the database"""
    
    print("🔍 Checking Supabase Database Tables")
    print("=" * 40)
    
    # Check if Supabase credentials are configured
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found!")
        print("Please run: python setup_supabase.py")
        return
    
    try:
        from supabase import create_client
        
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        
        # Try to query each table to see if it exists
        tables_to_check = [
            "content_sources",
            "content_items", 
            "content_embeddings",
            "review_queue",
            "channel_drafts",
            "post_schedules",
            "channel_posts",
            "engagement_metrics"
        ]
        
        print("📊 Checking table existence:")
        print("-" * 30)
        
        for table in tables_to_check:
            try:
                # Try to select from the table
                result = supabase.table(table).select("count", count="exact").limit(1).execute()
                print(f"✅ {table} - EXISTS")
            except Exception as e:
                if "Could not find the table" in str(e):
                    print(f"❌ {table} - NOT FOUND")
                else:
                    print(f"⚠️  {table} - ERROR: {str(e)[:50]}...")
        
        print("\n" + "=" * 40)
        print("📋 If tables are missing, you need to:")
        print("1. Go to Supabase Dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Run the schema SQL")
        print("4. Check Table Editor to verify")
        
    except Exception as e:
        print(f"❌ Error checking tables: {e}")

if __name__ == "__main__":
    check_tables()
