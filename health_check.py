#!/usr/bin/env python3
"""
Health Check Script for Kolekt
Tests if the application can start properly
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_imports():
    """Test if all critical imports work"""
    try:
        print("🔍 Testing imports...")
        
        # Test main application
        import start_kolekt
        print("✅ start_kolekt imports successfully")
        
        # Test admin routes
        from src.api.admin_routes_new import admin_router_new
        print("✅ Admin routes work")
        
        # Test admin auth
        from src.services.admin_auth import admin_auth_service
        print("✅ Admin auth works")
        
        # Test Supabase service
        from src.services.supabase import SupabaseService
        print("✅ Supabase service works")
        
        # Test configuration
        from src.core.config_simple import settings
        print("✅ Configuration works")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_app_startup():
    """Test if the app can start"""
    try:
        print("🔍 Testing app startup...")
        
        from start_kolekt import app
        
        # Test basic routes
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        print(f"✅ Health endpoint: {response.status_code}")
        
        # Test root endpoint
        response = client.get("/")
        print(f"✅ Root endpoint: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ App startup error: {e}")
        return False

def main():
    """Run all health checks"""
    print("🏥 Kolekt Health Check")
    print("=" * 40)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test app startup
    startup_ok = test_app_startup()
    
    print("=" * 40)
    if imports_ok and startup_ok:
        print("✅ All health checks passed!")
        return 0
    else:
        print("❌ Health checks failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
