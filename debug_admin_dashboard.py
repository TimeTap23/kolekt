#!/usr/bin/env python3
"""
Debug Admin Dashboard
Direct test of the admin dashboard functionality
"""

import os
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

async def debug_admin_dashboard():
    """Debug the admin dashboard data collection"""
    
    print("🔍 Debugging Admin Dashboard Data Collection")
    print("=" * 50)
    
    # Get credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        return
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Test 1: Get users
        print("\n1. Testing users table...")
        try:
            users_response = supabase.table("profiles").select("id, created_at, last_login, plan").execute()
            print(f"   ✅ Users: {len(users_response.data)} found")
            for user in users_response.data[:3]:  # Show first 3
                print(f"      - ID: {user.get('id')}")
                print(f"        Created: {user.get('created_at')}")
                print(f"        Last Login: {user.get('last_login')}")
        except Exception as e:
            print(f"   ❌ Users error: {e}")
        
        # Test 2: Get content
        print("\n2. Testing content_items table...")
        try:
            content_response = supabase.table("content_items").select("id, created_at, status").execute()
            print(f"   ✅ Content: {len(content_response.data)} found")
            for item in content_response.data[:3]:  # Show first 3
                print(f"      - ID: {item.get('id')}")
                print(f"        Created: {item.get('created_at')}")
                print(f"        Status: {item.get('status')}")
        except Exception as e:
            print(f"   ❌ Content error: {e}")
        
        # Test 3: Get social connections
        print("\n3. Testing social_connections table...")
        try:
            connections_response = supabase.table("social_connections").select("id, platform, is_active, connected_at").execute()
            print(f"   ✅ Connections: {len(connections_response.data)} found")
            for conn in connections_response.data[:3]:  # Show first 3
                print(f"      - Platform: {conn.get('platform')}")
                print(f"        Active: {conn.get('is_active')}")
                print(f"        Connected: {conn.get('connected_at')}")
        except Exception as e:
            print(f"   ❌ Connections error: {e}")
        
        # Test 4: Test date parsing
        print("\n4. Testing date parsing...")
        try:
            thirty_days_ago = datetime.now() - timedelta(days=30)
            first_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            print(f"   📅 30 days ago: {thirty_days_ago}")
            print(f"   📅 First of month: {first_of_month}")
            
            # Test parsing a date
            test_date = "2024-01-15T10:30:00Z"
            parsed = datetime.fromisoformat(test_date.replace('Z', '+00:00'))
            print(f"   ✅ Date parsing works: {parsed}")
        except Exception as e:
            print(f"   ❌ Date parsing error: {e}")
        
        # Test 5: Build dashboard stats
        print("\n5. Building dashboard stats...")
        try:
            # Get basic counts
            total_users = len(users_response.data)
            total_content_items = len(content_response.data)
            social_connections = len(connections_response.data)
            
            # Calculate active users
            thirty_days_ago = datetime.now() - timedelta(days=30)
            active_users = 0
            for user in users_response.data:
                if user.get('last_login'):
                    try:
                        login_date = datetime.fromisoformat(user['last_login'].replace('Z', '+00:00'))
                        if login_date > thirty_days_ago:
                            active_users += 1
                    except:
                        continue
            
            # Calculate monthly posts
            first_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_posts = 0
            for item in content_response.data:
                if item.get('created_at'):
                    try:
                        created_date = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))
                        if created_date > first_of_month:
                            monthly_posts += 1
                    except:
                        continue
            
            stats = {
                "total_users": total_users,
                "active_users": active_users,
                "total_content_items": total_content_items,
                "social_connections": social_connections,
                "monthly_posts": monthly_posts,
                "total_api_calls": 0,
                "storage_used": 0.0,
                "revenue_monthly": 0.0
            }
            
            print("   ✅ Dashboard stats calculated:")
            for key, value in stats.items():
                print(f"      - {key}: {value}")
                
        except Exception as e:
            print(f"   ❌ Stats calculation error: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ General error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_admin_dashboard())
