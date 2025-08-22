#!/usr/bin/env python3
"""
Fix Security Issues Properly
This script creates the missing exec_sql function and then applies RLS security fixes
"""

import asyncio
import sys
import os
import httpx

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.supabase import supabase_service

async def create_exec_sql_function():
    """Create the missing exec_sql function"""
    print("🔧 Creating exec_sql function...")
    print("==================================================")
    
    # Read the SQL function definition
    try:
        with open('create_exec_sql_function.sql', 'r') as f:
            sql_function = f.read()
    except FileNotFoundError:
        print("❌ create_exec_sql_function.sql not found!")
        return False
    
    try:
        # Execute the function creation using direct SQL
        # We'll use the Supabase REST API to execute this directly
        response = supabase_service.client.rpc(
            'exec_sql', 
            {'sql': sql_function}
        ).execute()
        
        print("✅ exec_sql function created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create exec_sql function: {e}")
        print("   This is expected since the function doesn't exist yet.")
        print("   We need to create it manually in Supabase Dashboard.")
        return False

async def apply_rls_fix_with_exec_sql():
    """Apply RLS fix using the exec_sql function"""
    print("\n🔒 Applying RLS Security Fix...")
    print("==================================================")
    
    # Read the RLS fix SQL
    try:
        with open('fix_rls_security.sql', 'r') as f:
            rls_sql = f.read()
    except FileNotFoundError:
        print("❌ fix_rls_security.sql not found!")
        return False
    
    # Split into individual statements
    statements = [stmt.strip() for stmt in rls_sql.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
    
    success_count = 0
    total_statements = len(statements)
    
    for i, statement in enumerate(statements, 1):
        if not statement:
            continue
            
        try:
            print(f"📝 Executing statement {i}/{total_statements}...")
            
            # Execute using exec_sql function
            response = supabase_service.client.rpc(
                'exec_sql', 
                {'sql': statement}
            ).execute()
            
            print(f"✅ Statement {i} executed successfully")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Statement {i} failed: {e}")
            print(f"   Statement: {statement[:100]}...")
    
    print("==================================================")
    print(f"📊 Results: {success_count}/{total_statements} statements executed successfully")
    
    return success_count == total_statements

async def verify_rls_fix():
    """Verify that RLS is properly enabled"""
    print("\n🔍 Verifying RLS Security Fix...")
    print("==================================================")
    
    verification_sql = """
    SELECT 
        schemaname,
        tablename,
        rowsecurity
    FROM pg_tables 
    WHERE schemaname = 'public' 
        AND tablename IN (
            'content_sources',
            'content_items', 
            'content_embeddings',
            'post_schedules',
            'channel_posts',
            'review_queue',
            'channel_drafts',
            'engagement_metrics',
            'social_connections'
        );
    """
    
    try:
        response = supabase_service.client.rpc(
            'exec_sql', 
            {'sql': verification_sql}
        ).execute()
        
        if response.data:
            print("📋 RLS Status Report:")
            all_enabled = True
            for row in response.data:
                status = "✅ ENABLED" if row['rowsecurity'] else "❌ DISABLED"
                print(f"   {row['tablename']}: {status}")
                if not row['rowsecurity']:
                    all_enabled = False
            
            if all_enabled:
                print("\n🎉 All tables have RLS enabled!")
                return True
            else:
                print("\n⚠️ Some tables still have RLS disabled!")
                return False
        else:
            print("❌ No data returned from verification query")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def print_manual_instructions():
    """Print manual instructions for creating the exec_sql function"""
    print("\n📋 MANUAL SETUP REQUIRED")
    print("==================================================")
    print("🚨 The exec_sql function needs to be created manually in Supabase Dashboard")
    print("")
    print("1. Go to your Supabase Dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Copy and paste this SQL:")
    print("")
    print("-- Create the exec_sql function")
    print("CREATE OR REPLACE FUNCTION exec_sql(sql text)")
    print("RETURNS json AS $$")
    print("BEGIN")
    print("  -- Only allow service role to execute this function")
    print("  IF auth.role() != 'service_role' THEN")
    print("    RAISE EXCEPTION 'Only service role can execute this function';")
    print("  END IF;")
    print("  ")
    print("  -- Execute the SQL and return results as JSON")
    print("  RETURN (SELECT json_agg(row_to_json(t)) FROM (SELECT * FROM (EXECUTE sql) t) t);")
    print("EXCEPTION")
    print("  WHEN OTHERS THEN")
    print("    -- Return error information as JSON")
    print("    RETURN json_build_object(")
    print("      'error', SQLERRM,")
    print("      'detail', SQLSTATE")
    print("    );")
    print("END;")
    print("$$ LANGUAGE plpgsql SECURITY DEFINER;")
    print("")
    print("-- Grant execute permission to service role only")
    print("GRANT EXECUTE ON FUNCTION exec_sql(text) TO service_role;")
    print("REVOKE EXECUTE ON FUNCTION exec_sql(text) FROM authenticated;")
    print("REVOKE EXECUTE ON FUNCTION exec_sql(text) FROM anon;")
    print("")
    print("4. Click 'Run' to execute the SQL")
    print("5. Then run this script again to apply the RLS fixes")

if __name__ == "__main__":
    async def main():
        print("🔧 Fixing Security Issues Properly")
        print("==================================================")
        print("This script will:")
        print("1. Create the missing exec_sql function")
        print("2. Apply RLS security fixes to all tables")
        print("3. Verify the fixes are working")
        print("")
        
        # Try to create the exec_sql function
        exec_sql_created = await create_exec_sql_function()
        
        if not exec_sql_created:
            print_manual_instructions()
            return
        
        # Apply RLS fixes
        rls_fixed = await apply_rls_fix_with_exec_sql()
        
        if rls_fixed:
            # Verify the fix
            await verify_rls_fix()
            print("\n🎉 Security issues fixed properly!")
        else:
            print("\n⚠️ Some RLS fixes failed. Check the output above.")
    
    asyncio.run(main())
