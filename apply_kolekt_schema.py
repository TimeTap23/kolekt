#!/usr/bin/env python3
"""
Apply Kolekt schema to Supabase database
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def apply_kolekt_schema():
    """Apply the Kolekt schema to Supabase"""
    
    print("🗄️ Applying Kolekt Schema to Supabase")
    print("=" * 40)
    
    # Check if Supabase credentials are configured
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found in .env file")
        print("Please run 'python setup_supabase.py' first")
        return False
    
    try:
        from supabase import create_client
        
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        
        # Read the schema file
        schema_file = Path("supabase/kolekt_schema.sql")
        if not schema_file.exists():
            print(f"❌ Schema file not found: {schema_file}")
            return False
        
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        print("📄 Schema SQL loaded successfully")
        print(f"📊 Tables to create:")
        print("  - content_sources")
        print("  - content_items") 
        print("  - content_embeddings")
        print("  - review_queue")
        print("  - channel_drafts")
        print("  - post_schedules")
        print("  - channel_posts")
        print("  - engagement_metrics")
        
        # Execute the schema
        print("\n🚀 Applying schema...")
        result = supabase.rpc('exec_sql', {'query': schema_sql}).execute()
        
        print("✅ Schema applied successfully!")
        print("\n📋 Next steps:")
        print("1. Test the API endpoints")
        print("2. Add some test content")
        print("3. Create the review queue UI")
        
        return True
        
    except Exception as e:
        print(f"❌ Error applying schema: {e}")
        print("\n💡 Alternative: Apply manually in Supabase Dashboard")
        print("1. Go to your Supabase project dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Copy the contents of supabase/kolekt_schema.sql")
        print("4. Paste and execute")
        return False

if __name__ == "__main__":
    success = apply_kolekt_schema()
    if success:
        print("\n🎉 Schema applied! You can now test the API endpoints.")
    else:
        print("\n⚠️  Please apply the schema manually in Supabase Dashboard")
        sys.exit(1)
