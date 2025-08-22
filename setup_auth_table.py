#!/usr/bin/env python3
"""
Setup Authentication Table Script
Creates the user_auth table in Supabase for password storage
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.supabase import SupabaseService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_auth_table():
    """Create the user_auth table in Supabase"""
    try:
        print("🔧 Setting up authentication table...")
        
        # Initialize Supabase service
        supabase = SupabaseService()
        
        # SQL to create the auth table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS public.user_auth (
            user_id UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Create index
        create_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_user_auth_user_id ON public.user_auth(user_id);
        """
        
        # Enable RLS
        enable_rls_sql = """
        ALTER TABLE public.user_auth ENABLE ROW LEVEL SECURITY;
        """
        
        print("📝 Creating user_auth table...")
        result = await supabase.client.rpc('exec_sql', {'query': create_table_sql})
        print(f"Table creation result: {result}")
        
        print("📝 Creating index...")
        result = await supabase.client.rpc('exec_sql', {'query': create_index_sql})
        print(f"Index creation result: {result}")
        
        print("📝 Enabling RLS...")
        result = await supabase.client.rpc('exec_sql', {'query': enable_rls_sql})
        print(f"RLS enable result: {result}")
        
        print("✅ Authentication table setup complete!")
        
    except Exception as e:
        logger.error(f"Failed to setup auth table: {e}")
        print(f"❌ Setup failed: {e}")

if __name__ == "__main__":
    asyncio.run(setup_auth_table())
