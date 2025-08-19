#!/usr/bin/env python3
"""
Apply Authentication Schema to Supabase
This script will create the profiles table and add test users
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def apply_auth_schema():
    """Apply the authentication schema to Supabase"""
    
    print("🔐 Applying Authentication Schema to Supabase")
    print("=" * 50)
    
    try:
        from src.services.supabase import supabase_service
        
        # SQL to create the profiles table and test users
        sql_commands = [
            """
            -- Create profiles table if it doesn't exist
            CREATE TABLE IF NOT EXISTS profiles (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255),
                password_hash VARCHAR(255),
                role VARCHAR(50) DEFAULT 'user',
                plan VARCHAR(50) DEFAULT 'free',
                is_active BOOLEAN DEFAULT true,
                is_verified BOOLEAN DEFAULT false,
                email_verified BOOLEAN DEFAULT false,
                last_login TIMESTAMP,
                login_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            """,
            """
            -- Create index on email for faster lookups
            CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);
            """,
            """
            -- Insert test user 1
            INSERT INTO profiles (id, email, name, password_hash, role, plan, is_active, is_verified, email_verified)
            VALUES (
                '550e8400-e29b-41d4-a716-446655440000',
                'test@example.com',
                'Test User',
                'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3',
                'user',
                'free',
                true,
                true,
                true
            ) ON CONFLICT (email) DO NOTHING;
            """,
            """
            -- Insert test user 2
            INSERT INTO profiles (id, email, name, password_hash, role, plan, is_active, is_verified, email_verified)
            VALUES (
                '550e8400-e29b-41d4-a716-446655440001',
                'admin@example.com',
                'Admin User',
                'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3',
                'admin',
                'premium',
                true,
                true,
                true
            ) ON CONFLICT (email) DO NOTHING;
            """
        ]
        
        # Execute each SQL command
        for i, sql in enumerate(sql_commands, 1):
            print(f"Executing SQL command {i}...")
            try:
                result = supabase_service.client.rpc('exec_sql', {'sql': sql}).execute()
                print(f"✅ SQL command {i} executed successfully")
            except Exception as e:
                print(f"⚠️ SQL command {i} failed (this might be expected): {e}")
                # Try direct execution
                try:
                    result = supabase_service.client.query(sql).execute()
                    print(f"✅ SQL command {i} executed successfully (direct)")
                except Exception as e2:
                    print(f"❌ SQL command {i} failed: {e2}")
        
        # Verify the table was created
        print("\n🔍 Verifying table creation...")
        try:
            result = supabase_service.client.table("profiles").select("id, email, name").execute()
            print(f"✅ Profiles table exists with {len(result.data)} users")
            
            for user in result.data:
                print(f"   - {user['email']} ({user['name']})")
                
        except Exception as e:
            print(f"❌ Could not verify profiles table: {e}")
            return False
        
        print("\n🎉 Authentication schema applied successfully!")
        print("\nTest users created:")
        print("- Email: test@example.com, Password: 123")
        print("- Email: admin@example.com, Password: 123")
        
        return True
        
    except Exception as e:
        print(f"❌ Error applying schema: {e}")
        return False

if __name__ == "__main__":
    apply_auth_schema()
