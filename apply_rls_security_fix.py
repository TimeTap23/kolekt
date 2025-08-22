#!/usr/bin/env python3
"""
Apply RLS Security Fix
This script fixes the critical security vulnerabilities by enabling RLS on all public tables
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.supabase import supabase_service

async def apply_rls_security_fix():
    """Apply RLS security fix to all vulnerable tables"""
    print("🔒 Applying RLS Security Fix...")
    print("==================================================")
    
    # Read the SQL script
    try:
        with open('fix_rls_security.sql', 'r') as f:
            sql_script = f.read()
    except FileNotFoundError:
        print("❌ fix_rls_security.sql not found!")
        return False
    
    # Split the script into individual statements
    statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
    
    success_count = 0
    total_statements = len(statements)
    
    for i, statement in enumerate(statements, 1):
        if not statement or statement.startswith('--'):
            continue
            
        try:
            print(f"📝 Executing statement {i}/{total_statements}...")
            
            # Execute the SQL statement
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
    
    if success_count == total_statements:
        print("🎉 RLS Security Fix applied successfully!")
        print("🔒 All tables now have proper Row Level Security enabled")
        return True
    else:
        print("⚠️ Some statements failed. Check the output above for details.")
        return False

async def verify_rls_fix():
    """Verify that RLS is properly enabled on all tables"""
    print("\n🔍 Verifying RLS Security Fix...")
    print("==================================================")
    
    # Check which tables have RLS enabled
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
            for row in response.data:
                status = "✅ ENABLED" if row['rowsecurity'] else "❌ DISABLED"
                print(f"   {row['tablename']}: {status}")
            
            # Check if all tables have RLS enabled
            all_enabled = all(row['rowsecurity'] for row in response.data)
            
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

if __name__ == "__main__":
    async def main():
        print("🚨 CRITICAL SECURITY FIX REQUIRED")
        print("Supabase has identified RLS vulnerabilities on public tables.")
        print("This script will fix these security issues.\n")
        
        # Apply the fix
        success = await apply_rls_security_fix()
        
        if success:
            # Verify the fix
            await verify_rls_fix()
        
        print("\n🔒 Security fix process completed!")
    
    asyncio.run(main())
