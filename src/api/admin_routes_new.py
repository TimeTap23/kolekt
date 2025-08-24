from fastapi import APIRouter, Depends, HTTPException, status, Form
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from pydantic import BaseModel
from src.services.authentication import require_admin
from src.services.cache_service import cache_service, cached, invalidate_cache
from supabase import create_client, Client
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create a simple admin router
admin_router_new = APIRouter(tags=["admin"])

# Initialize Supabase client
supabase_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Pydantic models for request/response
class UserCreateRequest(BaseModel):
    email: str
    password: str
    name: str
    role: str = "user"
    plan: str = "free"

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    plan: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    role: str
    plan: str
    is_active: bool
    created_at: str

@admin_router_new.get("/test")
async def admin_test(current_user = Depends(require_admin)):
    """Simple test endpoint - requires admin authentication"""
    return {"message": "Admin router is working", "status": "ok", "user": current_user}

@admin_router_new.get("/dashboard")
@cached("dashboard", ttl=300)  # Cache for 5 minutes
async def get_admin_dashboard(current_user = Depends(require_admin)):
    """Get admin dashboard statistics - requires admin authentication"""
    try:
        # Get real statistics from database
        users_response = supabase_client.table('profiles').select('*').execute()
        total_users = len(users_response.data) if users_response.data else 0
        
        # Get active users (users with recent activity)
        active_users = 0
        if users_response.data:
            # Count users with recent login (last 30 days)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            active_users = sum(1 for user in users_response.data 
                             if user.get('last_login') and user['last_login'] > thirty_days_ago)
        
        return {
            "success": True,
            "stats": {
                "total_users": total_users,
                "active_users": active_users,
                "total_content_items": 12,  # TODO: Get from database
                "social_connections": 8,    # TODO: Get from database
                "monthly_posts": 25,        # TODO: Get from database
                "total_api_calls": 150,     # TODO: Get from database
                "storage_used": 2.5,        # TODO: Calculate from database
                "revenue_monthly": 0.0      # TODO: Get from billing system
            },
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")

@admin_router_new.post("/login")
async def admin_login(email: str = Form(...), password: str = Form(...)):
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

@admin_router_new.get("/users", response_model=List[UserResponse])
@cached("admin", ttl=60)  # Cache for 1 minute
async def get_users(current_user = Depends(require_admin)):
    """Get all users - requires admin authentication"""
    try:
        response = supabase_client.table('profiles').select('*').order('created_at', desc=True).execute()
        
        users = []
        if response.data:
            for user in response.data:
                users.append(UserResponse(
                    id=user.get('id', ''),
                    email=user.get('email', ''),
                    name=user.get('name'),
                    role=user.get('role', 'user'),
                    plan=user.get('plan', 'free'),
                    is_active=user.get('is_active', True),
                    created_at=user.get('created_at', '')
                ))
        
        return users
    except Exception as e:
        logger.error(f"Get users error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get users")

@admin_router_new.get("/users/{user_id}", response_model=UserResponse)
@cached("user", ttl=300)  # Cache for 5 minutes
async def get_user(user_id: str, current_user = Depends(require_admin)):
    """Get specific user - requires admin authentication"""
    try:
        response = supabase_client.table('profiles').select('*').eq('id', user_id).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = response.data
        return UserResponse(
            id=user.get('id', ''),
            email=user.get('email', ''),
            name=user.get('name'),
            role=user.get('role', 'user'),
            plan=user.get('plan', 'free'),
            is_active=user.get('is_active', True),
            created_at=user.get('created_at', '')
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user")

@admin_router_new.post("/users", response_model=UserResponse)
@invalidate_cache("admin")  # Invalidate admin cache after user creation
async def create_user(user_data: UserCreateRequest, current_user = Depends(require_admin)):
    """Create a new user - requires admin authentication"""
    try:
        # Create user in Supabase Auth
        auth_response = supabase_client.auth.admin.create_user({
            "email": user_data.email,
            "password": user_data.password,
            "email_confirm": True,
            "user_metadata": {
                "name": user_data.name
            }
        })
        
        if not auth_response or not hasattr(auth_response, 'user'):
            raise HTTPException(status_code=400, detail="Failed to create user in auth system")
        
        user_id = auth_response.user.id
        
        # Create user profile
        profile_data = {
            "id": user_id,
            "email": user_data.email,
            "name": user_data.name,
            "role": user_data.role,
            "plan": user_data.plan,
            "email_verified": True,
            "is_active": True
        }
        
        supabase_client.table('profiles').insert(profile_data).execute()
        
        # Invalidate user-specific cache
        await cache_service.invalidate_user_cache(user_id)
        
        return UserResponse(
            id=user_id,
            email=user_data.email,
            name=user_data.name,
            role=user_data.role,
            plan=user_data.plan,
            is_active=True,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create user error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@admin_router_new.put("/users/{user_id}", response_model=UserResponse)
@invalidate_cache("user")  # Invalidate user cache after update
async def update_user(user_id: str, user_data: UserUpdateRequest, current_user = Depends(require_admin)):
    """Update a user - requires admin authentication"""
    try:
        # Build update data
        update_data = {}
        if user_data.name is not None:
            update_data["name"] = user_data.name
        if user_data.role is not None:
            update_data["role"] = user_data.role
        if user_data.plan is not None:
            update_data["plan"] = user_data.plan
        if user_data.is_active is not None:
            update_data["is_active"] = user_data.is_active
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Update user profile
        response = supabase_client.table('profiles').update(update_data).eq('id', user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = response.data[0]
        
        # Invalidate user-specific cache
        await cache_service.invalidate_user_cache(user_id)
        
        return UserResponse(
            id=user.get('id', ''),
            email=user.get('email', ''),
            name=user.get('name'),
            role=user.get('role', 'user'),
            plan=user.get('plan', 'free'),
            is_active=user.get('is_active', True),
            created_at=user.get('created_at', '')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user")

@admin_router_new.delete("/users/{user_id}")
@invalidate_cache("admin")  # Invalidate admin cache after user deletion
async def delete_user(user_id: str, current_user = Depends(require_admin)):
    """Delete a user - requires admin authentication"""
    try:
        # Check if user exists
        user_response = supabase_client.table('profiles').select('*').eq('id', user_id).single().execute()
        
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Delete from profiles table
        supabase_client.table('profiles').delete().eq('id', user_id).execute()
        
        # Invalidate user-specific cache
        await cache_service.invalidate_user_cache(user_id)
        
        # Note: Supabase Auth user deletion would require admin API
        # For now, we just delete from profiles table
        
        return {
            "success": True,
            "message": f"User {user_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete user error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user")

@admin_router_new.post("/users/create-admin")
@invalidate_cache("admin")  # Invalidate admin cache after admin creation
async def create_admin_user(current_user = Depends(require_admin)):
    """Create admin user - requires admin authentication"""
    try:
        # Check if admin user already exists
        admin_response = supabase_client.table('profiles').select('*').eq('email', 'info@marteklabs.com').execute()
        
        if admin_response.data:
            return {
                "success": True,
                "message": "Admin user already exists",
                "user_id": admin_response.data[0]['id']
            }
        
        # Create admin user in Supabase Auth
        auth_response = supabase_client.auth.admin.create_user({
            "email": "info@marteklabs.com",
            "password": "kolectio123",
            "email_confirm": True,
            "user_metadata": {
                "name": "Admin User"
            }
        })
        
        if not auth_response or not hasattr(auth_response, 'user'):
            raise HTTPException(status_code=400, detail="Failed to create admin user in auth system")
        
        user_id = auth_response.user.id
        
        # Create admin profile
        profile_data = {
            "id": user_id,
            "email": "info@marteklabs.com",
            "name": "Admin User",
            "role": "admin",
            "plan": "business",
            "email_verified": True,
            "is_active": True
        }
        
        supabase_client.table('profiles').insert(profile_data).execute()
        
        # Invalidate user-specific cache
        await cache_service.invalidate_user_cache(user_id)
        
        return {
            "success": True,
            "message": "Admin user created successfully",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create admin user error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create admin user")

@admin_router_new.post("/users/bulk-delete")
@invalidate_cache("admin")  # Invalidate admin cache after bulk deletion
async def bulk_delete_users(user_ids: List[str], current_user = Depends(require_admin)):
    """Bulk delete users - requires admin authentication"""
    try:
        deleted_count = 0
        failed_deletions = []
        
        for user_id in user_ids:
            try:
                supabase_client.table('profiles').delete().eq('id', user_id).execute()
                deleted_count += 1
                
                # Invalidate user-specific cache
                await cache_service.invalidate_user_cache(user_id)
                
            except Exception as e:
                failed_deletions.append({"user_id": user_id, "error": str(e)})
        
        return {
            "success": True,
            "message": f"Bulk deletion completed",
            "deleted_count": deleted_count,
            "failed_deletions": failed_deletions
        }
        
    except Exception as e:
        logger.error(f"Bulk delete users error: {e}")
        raise HTTPException(status_code=500, detail="Failed to bulk delete users")

@admin_router_new.get("/cache/stats")
async def get_cache_stats(current_user = Depends(require_admin)):
    """Get cache statistics - requires admin authentication"""
    try:
        stats = await cache_service.get_cache_stats()
        return {
            "success": True,
            "cache_stats": stats
        }
    except Exception as e:
        logger.error(f"Get cache stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get cache stats")

@admin_router_new.post("/cache/clear")
async def clear_cache(current_user = Depends(require_admin)):
    """Clear all cache - requires admin authentication"""
    try:
        # Clear all cache patterns
        patterns = [
            "user:*",
            "profile:*",
            "dashboard:*",
            "analytics:*",
            "content:*",
            "template:*",
            "api:*",
            "admin:*"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            deleted = await cache_service.delete_pattern(pattern)
            total_deleted += deleted
        
        return {
            "success": True,
            "message": f"Cache cleared successfully",
            "deleted_keys": total_deleted
        }
    except Exception as e:
        logger.error(f"Clear cache error: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")
