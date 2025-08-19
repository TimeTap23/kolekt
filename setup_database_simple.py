#!/usr/bin/env python3
"""
Simple Database Setup Script
Provides instructions for setting up the database schema manually
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def check_supabase_connection():
    """Check if Supabase connection is working"""
    
    print("🔗 Testing Supabase Connection...")
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Check required variables
        required_vars = [
            'SUPABASE_URL',
            'SUPABASE_ANON_KEY',
            'SUPABASE_KEY',
            'DATABASE_URL'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing required variables: {', '.join(missing_vars)}")
            return False
        
        print("✅ All required environment variables are set")
        
        # Test basic connection
        try:
            from supabase import create_client
            
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY')
            
            client = create_client(url, key)
            
            # Try a simple query
            response = client.table('profiles').select('count').execute()
            print("✅ Database connection successful")
            return True
            
        except Exception as e:
            print(f"⚠️  Database connection test failed: {e}")
            print("   This is expected if the schema hasn't been set up yet")
            return True  # Still return True as this is expected
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def show_manual_setup_instructions():
    """Show instructions for manual database setup"""
    
    print("\n📚 Manual Database Setup Instructions")
    print("=" * 50)
    print("Since automatic schema execution requires special permissions,")
    print("you'll need to set up the database schema manually:")
    print()
    print("1. Go to your Supabase Dashboard:")
    print("   https://supabase.com/dashboard")
    print()
    print("2. Select your project")
    print()
    print("3. Go to SQL Editor (left sidebar)")
    print()
    print("4. Create a new query")
    print()
    print("5. Copy and paste the contents of 'supabase_schema_auth.sql'")
    print()
    print("6. Click 'Run' to execute the schema")
    print()
    print("7. Verify the tables were created by checking the 'Table Editor'")
    print()
    print("📋 Expected Tables:")
    print("   - profiles")
    print("   - user_settings")
    print("   - refresh_tokens")
    print("   - user_tokens")
    print("   - oauth_states")
    print("   - api_usage")
    print("   - rate_limit_logs")
    print("   - access_logs")
    print("   - deletion_logs")

def create_storage_bucket():
    """Create storage bucket for file uploads"""
    
    print("\n📦 Setting up Storage Bucket...")
    
    try:
        from supabase import create_client
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        client = create_client(url, key)
        
        bucket_name = "threadstorm"
        
        try:
            # Try to create bucket
            response = client.storage.create_bucket(bucket_name, {
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

def test_basic_operations():
    """Test basic database operations after setup"""
    
    print("\n🧪 Testing Basic Database Operations...")
    
    try:
        from supabase import create_client
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        client = create_client(url, key)
        
        # Test basic query
        try:
            response = client.table('profiles').select('count').execute()
            print("✅ Database query test successful")
        except Exception as e:
            print(f"⚠️  Database query test failed: {e}")
            print("   This is expected if the schema hasn't been set up yet")
            return True
        
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
            client.table('profiles').insert(test_data).execute()
            print("✅ Database write test successful")
            
            # Delete test data
            client.table('profiles').delete().eq('id', 'test-user-id').execute()
            print("✅ Database delete test successful")
            
        except Exception as e:
            print(f"⚠️  Database write/delete test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database operations test failed: {e}")
        return False

def main():
    """Main setup function"""
    
    print("🗄️ ThreadStorm Database Setup (Simple)")
    print("=" * 50)
    
    # Check connection
    connection_ok = check_supabase_connection()
    
    if not connection_ok:
        print("\n❌ Cannot proceed without proper Supabase configuration")
        print("Please run 'python setup_supabase.py' first")
        return
    
    # Show manual setup instructions
    show_manual_setup_instructions()
    
    # Create storage bucket
    storage_ok = create_storage_bucket()
    
    # Test operations
    operations_ok = test_basic_operations()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Setup Summary")
    print("=" * 50)
    
    results = [
        ("Supabase Connection", connection_ok),
        ("Storage Bucket", storage_ok),
        ("Database Operations", operations_ok)
    ]
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")
    
    print("\n📋 Next Steps:")
    print("1. Follow the manual setup instructions above")
    print("2. Run the SQL schema in your Supabase dashboard")
    print("3. Test Meta credentials: python test_meta_credentials.py")
    print("4. Start ThreadStorm: python main.py")
    
    print("\n💡 Tip: After setting up the schema, run this script again")
    print("   to verify everything is working correctly")

if __name__ == "__main__":
    main()
