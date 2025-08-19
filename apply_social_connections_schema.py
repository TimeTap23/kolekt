#!/usr/bin/env python3
"""
Apply Social Connections Schema
Applies the social_connections table and related functions to Supabase
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def apply_social_connections_schema():
    """Apply the social connections schema to Supabase"""
    try:
        from src.services.supabase import supabase_service
        
        print("🔗 Applying Social Connections Schema...")
        
        # Read the schema file
        schema_path = Path(__file__).parent / "supabase" / "social_connections_schema.sql"
        
        if not schema_path.exists():
            print(f"❌ Schema file not found: {schema_path}")
            return False
        
        with open(schema_path, 'r') as f:
            sql_content = f.read()
        
        print("📄 Schema content:")
        print("=" * 50)
        print(sql_content)
        print("=" * 50)
        
        # Split SQL into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        print(f"\n🔧 Executing {len(statements)} SQL statements...")
        
        for i, statement in enumerate(statements, 1):
            if statement:
                print(f"  {i}/{len(statements)}: {statement[:50]}...")
                try:
                    # Execute the statement
                    result = supabase_service.client.rpc('exec_sql', {'sql': statement}).execute()
                    print(f"    ✅ Success")
                except Exception as e:
                    print(f"    ⚠️  Warning: {e}")
                    # Try alternative method
                    try:
                        result = supabase_service.client.query(statement).execute()
                        print(f"    ✅ Success (alternative method)")
                    except Exception as e2:
                        print(f"    ❌ Failed: {e2}")
        
        print("\n✅ Schema application completed!")
        print("\n📝 Next Steps:")
        print("1. Verify the social_connections table was created")
        print("2. Test the OAuth flow with persistent connections")
        print("3. Check that connections persist across login sessions")
        
        return True
        
    except Exception as e:
        print(f"❌ Error applying schema: {e}")
        return False

def verify_schema():
    """Verify that the schema was applied correctly"""
    try:
        from src.services.supabase import supabase_service
        
        print("\n🔍 Verifying Schema...")
        
        # Check if social_connections table exists
        try:
            response = supabase_service.client.table("social_connections").select("count", count="exact").limit(1).execute()
            print("✅ social_connections table exists")
            
            # Check sample data
            response = supabase_service.client.table("social_connections").select("*").limit(5).execute()
            print(f"✅ Found {len(response.data)} connections in table")
            
            for conn in response.data:
                print(f"  - {conn['platform']}: {conn['username']} (Active: {conn['is_active']})")
                
        except Exception as e:
            print(f"❌ Error verifying table: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying schema: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Social Connections Schema Setup")
    print("=" * 50)
    
    # Check if .env exists
    if not Path(".env").exists():
        print("❌ .env file not found. Please run setup first.")
        return
    
    # Check required environment variables
    required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'SUPABASE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please run 'python setup_supabase.py' first.")
        return
    
    print("✅ Environment configuration verified")
    
    # Apply schema
    if apply_social_connections_schema():
        # Verify schema
        verify_schema()
    else:
        print("❌ Failed to apply schema")

if __name__ == "__main__":
    main()
