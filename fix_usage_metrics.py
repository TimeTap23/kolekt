#!/usr/bin/env python3
"""
Fix missing usage_metrics table
"""

import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.services.supabase import SupabaseService

async def fix_usage_metrics():
    """Add the missing usage_metrics table"""
    
    print("🔧 Fixing missing usage_metrics table...")
    
    try:
        supabase = SupabaseService()
        
        # SQL to create the usage_metrics table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS public.usage_metrics (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
            metric_type VARCHAR(50) NOT NULL,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        -- Create indexes for usage_metrics
        CREATE INDEX IF NOT EXISTS idx_usage_metrics_user_id ON public.usage_metrics(user_id);
        CREATE INDEX IF NOT EXISTS idx_usage_metrics_metric_type ON public.usage_metrics(metric_type);
        CREATE INDEX IF NOT EXISTS idx_usage_metrics_created_at ON public.usage_metrics(created_at);
        
        -- RLS Policies for usage_metrics (users can view their own)
        DROP POLICY IF EXISTS "Users can view their own usage metrics" ON public.usage_metrics;
        CREATE POLICY "Users can view their own usage metrics" ON public.usage_metrics
            FOR SELECT USING (auth.uid() = user_id);
        
        DROP POLICY IF EXISTS "Users can insert their own usage metrics" ON public.usage_metrics;
        CREATE POLICY "Users can insert their own usage metrics" ON public.usage_metrics
            FOR INSERT WITH CHECK (auth.uid() = user_id);
        
        -- Enable RLS
        ALTER TABLE public.usage_metrics ENABLE ROW LEVEL SECURITY;
        
        -- Grant permissions
        GRANT ALL ON public.usage_metrics TO anon, authenticated;
        """
        
        # Execute the SQL
        print("📝 Creating usage_metrics table...")
        result = supabase.client.rpc('exec_sql', {'query': create_table_sql}).execute()
        
        print("✅ usage_metrics table created successfully!")
        
        # Test the table
        print("🧪 Testing table access...")
        test_result = supabase.client.table('usage_metrics').select('*').limit(1).execute()
        print(f"✅ Table access test successful: {len(test_result.data)} records found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating usage_metrics table: {e}")
        return False

def main():
    """Main function"""
    import asyncio
    
    print("🚀 ThreadStorm Database Fix")
    print("=" * 40)
    
    success = asyncio.run(fix_usage_metrics())
    
    if success:
        print("\n🎉 Database fix completed successfully!")
        print("✅ usage_metrics table is now available")
        print("✅ Analytics and usage tracking will work properly")
    else:
        print("\n❌ Database fix failed")
        print("Please check the error messages above")

if __name__ == "__main__":
    main()
