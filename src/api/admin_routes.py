from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import logging
import asyncio

from src.services.authentication import require_admin, get_current_user
from src.services.supabase import supabase_service
from src.services.observability import observability_service

# Configure logging
logger = logging.getLogger(__name__)

admin_router = APIRouter(tags=["admin"])

# Pydantic Models
class UserUpdate(BaseModel):
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    plan: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None

class AnnouncementCreate(BaseModel):
    title: str
    content: str
    priority: str = "normal"  # low, normal, high, critical
    is_active: bool = True
    expires_at: Optional[datetime] = None

class AnnouncementUpdate(BaseModel):
    announcement_id: str
    title: Optional[str] = None
    content: Optional[str] = None
    priority: Optional[str] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None

class KolektStats(BaseModel):
    total_users: int
    active_users: int
    total_content_items: int
    social_connections: int
    monthly_posts: int
    total_api_calls: int
    storage_used: float
    revenue_monthly: float

class SocialConnectionStats(BaseModel):
    total_connections: int
    threads_connections: int
    instagram_connections: int
    facebook_connections: int
    active_connections: int
    failed_connections: int

class ContentStats(BaseModel):
    total_content: int
    published_content: int
    draft_content: int
    scheduled_content: int
    this_month_content: int

# Simple admin authentication (for development)
@admin_router.post("/login")
async def admin_login(email: str, password: str):
    """Simple admin login for development"""
    try:
        # Check if user exists and is admin
        response = supabase_service.client.table("profiles").select("*").eq("email", email).eq("role", "admin").execute()
        
        if not response.data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = response.data[0]
        
        # For development, accept any password for admin users
        # In production, you'd verify the password properly
        
        return {
            "success": True,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

# Enhanced Kolekt Admin Dashboard
@admin_router.get("/dashboard")
async def get_kolekt_admin_dashboard():
    """Get comprehensive Kolekt admin dashboard statistics"""
    try:
        # Get user statistics
        users_response = supabase_service.client.table("profiles").select("id, created_at, last_login, plan").execute()
        total_users = len(users_response.data)
        
        # Get active users (logged in within last 30 days)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        active_users = 0
        for user in users_response.data:
            if user.get('last_login'):
                try:
                    login_date = datetime.fromisoformat(user['last_login'].replace('Z', '+00:00'))
                    if login_date > thirty_days_ago:
                        active_users += 1
                except:
                    continue
        
        # Get content statistics
        content_response = supabase_service.client.table("content_items").select("id, added_at").execute()
        total_content_items = len(content_response.data)
        
        # Get monthly content count
        try:
            first_of_month = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_posts = 0
            for item in content_response.data:
                if item.get('added_at'):
                    try:
                        created_date = datetime.fromisoformat(item['added_at'].replace('Z', '+00:00'))
                        if created_date > first_of_month:
                            monthly_posts += 1
                    except:
                        continue
        except:
            monthly_posts = 0
        
        # Get social connections statistics
        connections_response = supabase_service.client.table("social_connections").select("id, platform, is_active").execute()
        social_connections = len(connections_response.data)
        
        # Get API usage statistics (fallback if table doesn't exist)
        try:
            api_usage_response = supabase_service.client.table("api_usage").select("calls_count").execute()
            total_api_calls = sum(usage.get('calls_count', 0) for usage in api_usage_response.data)
        except:
            total_api_calls = 0
        
        # Get storage usage (placeholder - would need actual storage calculation)
        storage_used = 0.0  # MB
        
        # Get revenue (placeholder - would need payment integration)
        revenue_monthly = 0.0
        
        stats = KolektStats(
            total_users=total_users,
            active_users=active_users,
            total_content_items=total_content_items,
            social_connections=social_connections,
            monthly_posts=monthly_posts,
            total_api_calls=total_api_calls,
            storage_used=storage_used,
            revenue_monthly=revenue_monthly
        )
        
        return {
            "success": True,
            "stats": stats.dict(),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting Kolekt admin dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard statistics")

# User Management
@admin_router.get("/users")
async def get_users(
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    plan: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user = Depends(require_admin)
):
    """Get paginated list of users with filtering"""
    try:
        offset = (page - 1) * limit
        
        # Build query
        query = supabase_service.client.table("profiles").select("*")
        
        if search:
            query = query.or_(f"email.ilike.%{search}%,name.ilike.%{search}%")
        
        if plan:
            query = query.eq("plan", plan)
            
        if is_active is not None:
            query = query.eq("is_active", is_active)
        
        # Get total count
        count_response = query.execute()
        total_count = len(count_response.data)
        
        # Get paginated results
        users_response = query.range(offset, offset + limit - 1).execute()
        
        await observability_service.log_event(
            category="admin",
            action="view_users",
            description=f"Admin viewed users list (page {page}, limit {limit})",
            metadata={"page": page, "limit": limit, "search": search},
            user_id=current_user.id,
            severity="info"
        )
        
        return {
            "success": True,
            "users": users_response.data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail="Failed to get users")

@admin_router.get("/users/{user_id}")
async def get_user(user_id: str, current_user = Depends(require_admin)):
    """Get detailed user information"""
    try:
        user_response = supabase_service.client.table("profiles").select("*").eq("id", user_id).execute()
        
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user's threadstorms
        threadstorms_response = supabase_service.client.table("threadstorms").select("*").eq("user_id", user_id).execute()
        
        # Get user's API usage
        api_usage_response = supabase_service.client.table("api_usage").select("*").eq("user_id", user_id).execute()
        
        user_data = user_response.data[0]
        user_data["threadstorms"] = threadstorms_response.data
        user_data["api_usage"] = api_usage_response.data
        
        await observability_service.log_event(
            category="admin",
            action="view_user",
            description=f"Admin viewed user details for {user_id}",
            metadata={"target_user_id": user_id},
            user_id=current_user.id,
            severity="info"
        )
        
        return {"success": True, "user": user_data}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user")

@admin_router.put("/users/{user_id}")
async def update_user(user_id: str, user_update: UserUpdate, current_user = Depends(require_admin)):
    """Update user information"""
    try:
        update_data = {}
        if user_update.email is not None:
            update_data["email"] = user_update.email
        if user_update.name is not None:
            update_data["name"] = user_update.name
        if user_update.plan is not None:
            update_data["plan"] = user_update.plan
        if user_update.is_active is not None:
            update_data["is_active"] = user_update.is_active
        if user_update.is_verified is not None:
            update_data["is_verified"] = user_update.is_verified
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        response = supabase_service.client.table("profiles").update(update_data).eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        await observability_service.log_event(
            category="admin",
            action="update_user",
            description=f"Admin updated user {user_id}",
            metadata={"target_user_id": user_id, "updates": update_data},
            user_id=current_user.id,
            severity="info"
        )
        
        return {"success": True, "user": response.data[0]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user")

@admin_router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user = Depends(require_admin)):
    """Delete user (soft delete)"""
    try:
        # Soft delete by setting is_active to False
        response = supabase_service.client.table("profiles").update({"is_active": False}).eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        await observability_service.log_event(
            category="admin",
            action="delete_user",
            description=f"Admin deactivated user {user_id}",
            metadata={"target_user_id": user_id},
            user_id=current_user.id,
            severity="warning"
        )
        
        return {"success": True, "message": "User deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user")

# Social Connections Management
@admin_router.get("/social-connections")
async def get_social_connections_stats():
    """Get social connections statistics"""
    try:
        connections_response = supabase_service.client.table("social_connections").select("*").execute()
        connections = connections_response.data
        
        total_connections = len(connections)
        threads_connections = sum(1 for conn in connections if conn.get('platform') == 'threads')
        instagram_connections = sum(1 for conn in connections if conn.get('platform') == 'instagram')
        facebook_connections = sum(1 for conn in connections if conn.get('platform') == 'facebook')
        active_connections = sum(1 for conn in connections if conn.get('is_active', False))
        failed_connections = total_connections - active_connections
        
        stats = SocialConnectionStats(
            total_connections=total_connections,
            threads_connections=threads_connections,
            instagram_connections=instagram_connections,
            facebook_connections=facebook_connections,
            active_connections=active_connections,
            failed_connections=failed_connections
        )
        
        return {
            "success": True,
            "stats": stats.dict(),
            "connections": connections
        }
        
    except Exception as e:
        logger.error(f"Error getting social connections stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get social connections statistics")

@admin_router.get("/social-connections/{user_id}")
async def get_user_social_connections(user_id: str):
    """Get social connections for a specific user"""
    try:
        connections_response = supabase_service.client.table("social_connections").select("*").eq("user_id", user_id).execute()
        
        return {
            "success": True,
            "user_id": user_id,
            "connections": connections_response.data
        }
        
    except Exception as e:
        logger.error(f"Error getting user social connections: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user social connections")

@admin_router.delete("/social-connections/{connection_id}")
async def remove_social_connection(connection_id: str):
    """Remove a social connection"""
    try:
        response = supabase_service.client.table("social_connections").delete().eq("id", connection_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        return {"success": True, "message": "Social connection removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing social connection: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove social connection")

# Content Management
@admin_router.get("/content")
async def get_content_stats():
    """Get content statistics"""
    try:
        content_response = supabase_service.client.table("content_items").select("*").execute()
        content_items = content_response.data
        
        total_content = len(content_items)
        # Note: content_items table doesn't have status field, so we'll use placeholders
        published_content = 0  # Placeholder
        draft_content = 0  # Placeholder
        scheduled_content = 0  # Placeholder
        
        # Get this month's content
        first_of_month = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        this_month_content = 0
        for item in content_items:
            if item.get('added_at'):
                try:
                    added_date = datetime.fromisoformat(item['added_at'].replace('Z', '+00:00'))
                    if added_date > first_of_month:
                        this_month_content += 1
                except:
                    continue
        
        stats = ContentStats(
            total_content=total_content,
            published_content=published_content,
            draft_content=draft_content,
            scheduled_content=scheduled_content,
            this_month_content=this_month_content
        )
        
        return {
            "success": True,
            "stats": stats.dict(),
            "recent_content": sorted(content_items, key=lambda x: x.get('added_at', ''), reverse=True)[:10]
        }
        
    except Exception as e:
        logger.error(f"Error getting content stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get content statistics")

@admin_router.get("/content/{content_id}")
async def get_content_item(content_id: str):
    """Get specific content item details"""
    try:
        content_response = supabase_service.client.table("content_items").select("*").eq("id", content_id).execute()
        
        if not content_response.data:
            raise HTTPException(status_code=404, detail="Content not found")
        
        return {
            "success": True,
            "content": content_response.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content item: {e}")
        raise HTTPException(status_code=500, detail="Failed to get content item")

@admin_router.delete("/content/{content_id}")
async def delete_content_item(content_id: str):
    """Delete a content item"""
    try:
        response = supabase_service.client.table("content_items").delete().eq("id", content_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Content not found")
        
        return {"success": True, "message": "Content item deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting content item: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete content item")

# Platform Analytics
@admin_router.get("/analytics/overview")
async def get_platform_analytics():
    """Get comprehensive platform analytics"""
    try:
        # Get user growth (last 30 days)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        users_response = supabase_service.client.table("profiles").select("id, created_at").execute()
        
        # Get user growth with error handling
        new_users_30d = 0
        for user in users_response.data:
            if user.get('created_at'):
                try:
                    created_date = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
                    if created_date > thirty_days_ago:
                        new_users_30d += 1
                except:
                    continue
        
        # Get content growth (last 30 days)
        content_response = supabase_service.client.table("content_items").select("id, added_at").execute()
        new_content_30d = 0
        for item in content_response.data:
            if item.get('added_at'):
                try:
                    created_date = datetime.fromisoformat(item['added_at'].replace('Z', '+00:00'))
                    if created_date > thirty_days_ago:
                        new_content_30d += 1
                except:
                    continue
        
        # Get connections growth (last 30 days)
        connections_response = supabase_service.client.table("social_connections").select("id, connected_at").execute()
        new_connections_30d = 0
        for conn in connections_response.data:
            if conn.get('connected_at'):
                try:
                    connected_date = datetime.fromisoformat(conn['connected_at'].replace('Z', '+00:00'))
                    if connected_date > thirty_days_ago:
                        new_connections_30d += 1
                except:
                    continue
        
        return {
            "success": True,
            "analytics": {
                "user_growth_30d": new_users_30d,
                "content_growth_30d": new_content_30d,
                "connections_growth_30d": new_connections_30d,
                "total_users": len(users_response.data),
                "total_content": len(content_response.data),
                "total_connections": len(connections_response.data),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting platform analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get platform analytics")

# Announcement Management
@admin_router.get("/announcements")
async def get_announcements(current_user = Depends(require_admin)):
    """Get all announcements"""
    try:
        response = supabase_service.client.table("announcements").select("*").order("created_at", desc=True).execute()
        
        return {"success": True, "announcements": response.data}
        
    except Exception as e:
        logger.error(f"Error getting announcements: {e}")
        raise HTTPException(status_code=500, detail="Failed to get announcements")

@admin_router.post("/announcements")
async def create_announcement(announcement: AnnouncementCreate, current_user = Depends(require_admin)):
    """Create a new announcement"""
    try:
        announcement_data = {
            "title": announcement.title,
            "content": announcement.content,
            "priority": announcement.priority,
            "is_active": announcement.is_active,
            "created_by": current_user.id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        if announcement.expires_at:
            announcement_data["expires_at"] = announcement.expires_at.isoformat()
        
        response = supabase_service.client.table("announcements").insert(announcement_data).execute()
        
        await observability_service.log_event(
            category="admin",
            action="create_announcement",
            description=f"Admin created announcement {response.data[0]['id']}",
            metadata={"announcement_id": response.data[0]["id"]},
            user_id=current_user.id,
            severity="info"
        )
        
        return {"success": True, "announcement": response.data[0]}
        
    except Exception as e:
        logger.error(f"Error creating announcement: {e}")
        raise HTTPException(status_code=500, detail="Failed to create announcement")

@admin_router.put("/announcements/{announcement_id}")
async def update_announcement(announcement_id: str, announcement: AnnouncementUpdate, current_user = Depends(require_admin)):
    """Update an announcement"""
    try:
        update_data = {}
        if announcement.title is not None:
            update_data["title"] = announcement.title
        if announcement.content is not None:
            update_data["content"] = announcement.content
        if announcement.priority is not None:
            update_data["priority"] = announcement.priority
        if announcement.is_active is not None:
            update_data["is_active"] = announcement.is_active
        if announcement.expires_at is not None:
            update_data["expires_at"] = announcement.expires_at.isoformat()
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        response = supabase_service.client.table("announcements").update(update_data).eq("id", announcement_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Announcement not found")
        
        await observability_service.log_event(
            category="admin",
            action="update_announcement",
            description=f"Admin updated announcement {announcement_id}",
            metadata={"announcement_id": announcement_id},
            user_id=current_user.id,
            severity="info"
        )
        
        return {"success": True, "announcement": response.data[0]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating announcement {announcement_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update announcement")

@admin_router.delete("/announcements/{announcement_id}")
async def delete_announcement(announcement_id: str, current_user = Depends(require_admin)):
    """Delete an announcement"""
    try:
        response = supabase_service.client.table("announcements").delete().eq("id", announcement_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Announcement not found")
        
        await observability_service.log_event(
            category="admin",
            action="delete_announcement",
            description=f"Admin deleted announcement {announcement_id}",
            metadata={"announcement_id": announcement_id},
            user_id=current_user.id,
            severity="warning"
        )
        
        return {"success": True, "message": "Announcement deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting announcement {announcement_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete announcement")

# System Management
@admin_router.get("/system/health")
async def get_system_health():
    """Get system health status"""
    try:
        # Check database connection
        db_health = "healthy"
        try:
            supabase_service.client.table("profiles").select("id").limit(1).execute()
        except Exception:
            db_health = "unhealthy"
        
        # Check Redis connection (if available)
        redis_health = "unknown"
        
        # Check API endpoints
        api_health = "healthy"
        
        # await observability_service.log_event(
        #     category="admin",
        #     action="check_system_health",
        #     description="Admin checked system health",
        #     metadata={"db_health": db_health, "redis_health": redis_health, "api_health": api_health},
        #     user_id=current_user.id,
        #     severity="info"
        # )
        
        return {
            "success": True,
            "health": {
                "database": db_health,
                "redis": redis_health,
                "api": api_health,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error checking system health: {e}")
        raise HTTPException(status_code=500, detail="Failed to check system health")

@admin_router.post("/system/maintenance")
async def toggle_maintenance_mode(
    enabled: bool,
    message: Optional[str] = None,
    current_user = Depends(require_admin)
):
    """Toggle maintenance mode"""
    try:
        # This would typically update a system settings table
        # For now, we'll just log the action
        
        await observability_service.log_event(
            category="admin",
            action="toggle_maintenance",
            description=f"Admin toggled maintenance mode: {enabled}",
            metadata={"enabled": enabled, "message": message},
            user_id=current_user.id,
            severity="warning"
        )
        
        return {
            "success": True,
            "maintenance_mode": enabled,
            "message": message or "Maintenance mode updated"
        }
        
    except Exception as e:
        logger.error(f"Error toggling maintenance mode: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle maintenance mode")
