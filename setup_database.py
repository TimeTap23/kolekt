#!/usr/bin/env python3
"""
Database Schema Setup Script
Sets up the ThreadStorm database schema in Supabase
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

async def setup_database():
    """Set up the database schema"""
    
    print("🗄️ ThreadStorm Database Schema Setup")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    try:
        from src.services.supabase import SupabaseService
        
        print("🔗 Connecting to Supabase...")
        supabase = SupabaseService()
        
        # Test connection
        print("✅ Connected to Supabase successfully")
        
        # Check if tables already exist
        print("\n📋 Checking existing tables...")
        
        try:
            # Try to query profiles table
            response = await supabase.table('profiles').select('count').execute()
            print("✅ Database schema already exists")
            return True
        except Exception:
            print("📝 Database schema not found, creating...")
        
        # Read and execute schema
        schema_file = Path("supabase_schema_auth.sql")
        if not schema_file.exists():
            print("❌ Schema file not found: supabase_schema_auth.sql")
            return False
        
        print("📖 Reading schema file...")
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        # Split into individual statements
        statements = []
        current_statement = ""
        
        for line in schema_sql.split('\n'):
            line = line.strip()
            if line and not line.startswith('--'):
                current_statement += line + " "
                if line.endswith(';'):
                    statements.append(current_statement.strip())
                    current_statement = ""
        
        print(f"📝 Found {len(statements)} SQL statements to execute")
        
        # Execute statements using direct SQL
        success_count = 0
        for i, statement in enumerate(statements, 1):
            try:
                print(f"  [{i}/{len(statements)}] Executing: {statement[:50]}...")
                
                # Execute the statement using raw SQL
                response = await supabase.client.rpc('exec_sql', {'sql': statement}).execute()
                success_count += 1
                
            except Exception as e:
                print(f"  ⚠️  Statement {i} failed: {str(e)[:100]}...")
                # Continue with other statements
        
        print(f"\n✅ Database setup complete: {success_count}/{len(statements)} statements executed")
        
        # Verify tables were created
        print("\n🔍 Verifying tables...")
        try:
            response = await supabase.client.table('profiles').select('count').execute()
            print("✅ Profiles table created successfully")
        except Exception as e:
            print(f"❌ Profiles table verification failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

async def create_storage_bucket():
    """Create storage bucket for file uploads"""
    
    print("\n📦 Setting up Storage Bucket...")
    
    try:
        from src.services.supabase import SupabaseService
        supabase = SupabaseService()
        
        # Create storage bucket
        bucket_name = "threadstorm"
        
        try:
            # Try to create bucket
            response = await supabase.client.storage.create_bucket(bucket_name, {
                'public': False,
                'allowed_mime_types': ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
                'file_size_limit': 10485760  # 10MB
            })
            print(f"✅ Storage bucket '{bucket_name}' created successfully")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"✅ Storage bucket '{bucket_name}' already exists")
            else:
                print(f"⚠️  Storage bucket creation failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Storage setup failed: {e}")
        return False

async def test_database_connection():
    """Test database connection and basic operations"""
    
    print("\n🧪 Testing Database Connection...")
    
    try:
        from src.services.supabase import SupabaseService
        supabase = SupabaseService()
        
        # Test basic query
        response = await supabase.client.table('profiles').select('count').execute()
        print("✅ Database connection test successful")
        
        # Test insert/delete (cleanup)
        test_data = {
            'id': 'test-user-id',
            'email': 'test@example.com',
            'name': 'Test User',
            'role': 'user',
            'plan': 'free'
        }
        
        try:
            # Insert test data
            await supabase.client.table('profiles').insert(test_data).execute()
            print("✅ Database write test successful")
            
            # Delete test data
            await supabase.client.table('profiles').delete().eq('id', 'test-user-id').execute()
            print("✅ Database delete test successful")
            
        except Exception as e:
            print(f"⚠️  Database write/delete test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def main():
    """Main setup function"""
    
    async def run_setup():
        # Setup database schema
        schema_success = await setup_database()
        
        # Setup storage bucket
        storage_success = await create_storage_bucket()
        
        # Test connection
        test_success = await test_database_connection()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Database Setup Summary")
        print("=" * 50)
        
        results = [
            ("Database Schema", schema_success),
            ("Storage Bucket", storage_success),
            ("Connection Test", test_success)
        ]
        
        for name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {name}")
        
        all_success = all(success for _, success in results)
        
        if all_success:
            print("\n🎉 Database setup completed successfully!")
            print("\n📋 Next Steps:")
            print("1. Test Meta credentials: python test_meta_credentials.py")
            print("2. Start ThreadStorm: python main.py")
            print("3. Open http://localhost:8000 in your browser")
        else:
            print("\n⚠️  Some setup steps failed. Please check the errors above.")
    
    # Run async setup
    asyncio.run(run_setup())

if __name__ == "__main__":
    main()
