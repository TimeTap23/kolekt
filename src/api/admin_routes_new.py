from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timezone
from src.services.authentication import require_admin
from src.services.supabase import SupabaseService
import logging

logger = logging.getLogger(__name__)

# Create a simple admin router
admin_router_new = APIRouter(tags=["admin"])

@admin_router_new.get("/test")
async def admin_test(current_user = Depends(require_admin)):
    """Simple test endpoint - requires admin authentication"""
    return {"message": "Admin router is working", "status": "ok", "user": current_user}

@admin_router_new.get("/dashboard")
async def get_admin_dashboard(current_user = Depends(require_admin)):
    """Get admin dashboard statistics - requires admin authentication"""
    return {
        "success": True,
        "stats": {
            "total_users": 5,
            "active_users": 3,
            "total_content_items": 12,
            "social_connections": 8,
            "monthly_posts": 25,
            "total_api_calls": 150,
            "storage_used": 2.5,
            "revenue_monthly": 0.0
        },
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "note": "Demo data - database integration in progress"
    }

@admin_router_new.post("/login")
async def admin_login(email: str, password: str):
    """Admin login endpoint - no authentication required"""
    try:
        # Simple hardcoded credentials for now
        if (email == "admin@kolekt.io" and password == "admin123") or \
           (email == "info@marteklabs.com" and password == "kolectio123"):
            return {
                "success": True,
                "user": {
                    "id": "admin-user-id",
                    "email": email,
                    "name": "Admin User",
                    "role": "admin"
                },
                "access_token": "admin_token_mock",  # Mock token for development
                "token_type": "bearer"
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@admin_router_new.get("/users")
async def get_users(current_user = Depends(require_admin)):
    """Get all users - requires admin authentication"""
    try:
        supabase = SupabaseService()
        response = await supabase.table('profiles').select('*').execute()
        
        return {
            "success": True,
            "users": response.data,
            "total": len(response.data)
        }
    except Exception as e:
        logger.error(f"Get users error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get users")

@admin_router_new.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user = Depends(require_admin)):
    """Delete a user - requires admin authentication"""
    try:
        supabase = SupabaseService()
        
        # Delete from profiles table
        await supabase.table('profiles').delete().eq('id', user_id).execute()
        
        # Note: Supabase Auth user deletion would require admin API
        # For now, we just delete from profiles table
        
        return {
            "success": True,
            "message": f"User {user_id} deleted successfully"
        }
    except Exception as e:
        logger.error(f"Delete user error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user")

@admin_router_new.post("/users/create-admin")
async def create_admin_user(current_user = Depends(require_admin)):
    """Create admin user - requires admin authentication"""
    try:
        supabase = SupabaseService()
        
        # Create admin user in Supabase Auth
        admin_data = {
            "email": "info@marteklabs.com",
            "password": "kolectio123",
            "user_metadata": {
                "name": "Admin User"
            }
        }
        
        auth_response = await supabase.sign_up(
            email=admin_data["email"],
            password=admin_data["password"],
            user_data=admin_data["user_metadata"]
        )
        
        if auth_response.get("success"):
            user = auth_response["user"]
            
            # Create admin profile
            profile_data = {
                "id": user.id,
                "email": admin_data["email"],
                "name": "Admin User",
                "role": "admin",
                "plan": "business",
                "email_verified": True
            }
            
            await supabase.table('profiles').insert(profile_data).execute()
            
            return {
                "success": True,
                "message": "Admin user created successfully",
                "user_id": user.id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to create admin user")
            
    except Exception as e:
        logger.error(f"Create admin user error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create admin user")
