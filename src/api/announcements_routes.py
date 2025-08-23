"""
Enhanced Announcements System
Provides comprehensive announcement management with scheduling, delivery tracking, and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json

from src.services.authentication import get_current_user, require_admin
from src.services.observability import observability_service
from src.services.announcements import AnnouncementsService

announcements_router = APIRouter()

# Enums for type safety
class AnnouncementType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    UPDATE = "update"
    MAINTENANCE = "maintenance"
    FEATURE = "feature"

class AnnouncementAudience(str, Enum):
    ALL = "all"
    ADMIN = "admin"
    PREMIUM = "premium"
    FREE = "free"
    BETA = "beta"

class AnnouncementStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Pydantic models for request/response validation
class AnnouncementBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Announcement title")
    content: str = Field(..., min_length=1, max_length=5000, description="Announcement content")
    type: AnnouncementType = Field(..., description="Announcement type")
    audience: AnnouncementAudience = Field(..., description="Target audience")
    priority: int = Field(default=1, ge=1, le=5, description="Priority level (1-5)")
    tags: List[str] = Field(default=[], description="Tags for categorization")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")

class AnnouncementCreate(AnnouncementBase):
    schedule_type: str = Field(default="immediate", description="Schedule type: immediate, scheduled, recurring")
    scheduled_for: Optional[datetime] = Field(None, description="Scheduled send time")
    recurring_pattern: Optional[str] = Field(None, description="Recurring pattern (cron-like)")
    notification_channels: List[str] = Field(default=["email", "in_app"], description="Delivery channels")
    user_segments: List[str] = Field(default=[], description="Specific user segments to target")

class AnnouncementUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    type: Optional[AnnouncementType] = None
    audience: Optional[AnnouncementAudience] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    scheduled_for: Optional[datetime] = None
    status: Optional[AnnouncementStatus] = None

class AnnouncementResponse(AnnouncementBase):
    id: str
    status: AnnouncementStatus
    created_at: datetime
    created_by: str
    scheduled_for: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    recipients_count: int = 0
    delivered_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    delivery_stats: Dict[str, Any] = Field(default_factory=dict)

class UserNotificationPreferences(BaseModel):
    email_notifications: bool = True
    in_app_notifications: bool = True
    push_notifications: bool = False
    announcement_types: List[AnnouncementType] = Field(default_factory=list)
    frequency: str = Field(default="immediate", description="immediate, daily, weekly")
    quiet_hours: Dict[str, str] = Field(default_factory=dict, description="Start and end times for quiet hours")

class AnnouncementAnalytics(BaseModel):
    announcement_id: str
    total_recipients: int
    delivered_count: int
    opened_count: int
    clicked_count: int
    delivery_rate: float
    open_rate: float
    click_rate: float
    delivery_time: Optional[float] = None
    engagement_score: float
    channel_performance: Dict[str, Any]
    user_segment_performance: Dict[str, Any]
    time_series_data: List[Dict[str, Any]]


# Initialize announcements service
announcements_service = AnnouncementsService()

@announcements_router.get("")
async def list_announcements(
    status: Optional[AnnouncementStatus] = Query(None, description="Filter by status"),
    type: Optional[AnnouncementType] = Query(None, description="Filter by type"),
    audience: Optional[AnnouncementAudience] = Query(None, description="Filter by audience"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: Dict[str, Any] = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get paginated list of announcements with filtering
    """
    try:
        await observability_service.log_event(
            "announcements_list",
            user_id=current_user.get("user_id"),
            metadata={"action": "list_announcements", "filters": {"status": status, "type": type, "audience": audience}}
        )
        
        announcements = await announcements_service.get_announcements(
            status=status,
            type=type,
            audience=audience,
            page=page,
            limit=limit
        )
        
        return {
            "success": True,
            "announcements": announcements["items"],
            "pagination": announcements["pagination"],
            "total": announcements["total"]
        }
        
    except Exception as e:
        await observability_service.log_event(
            "announcements_error",
            user_id=current_user.get("user_id"),
            metadata={"error": str(e), "action": "list_announcements"}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve announcements")

@announcements_router.post("")
async def create_announcement(
    payload: AnnouncementCreate, 
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Create a new announcement with scheduling and delivery options
    """
    try:
        await observability_service.log_event(
            "announcement_create",
            user_id=current_user.get("user_id"),
            metadata={"action": "create_announcement", "type": payload.type, "audience": payload.audience}
        )
        
        announcement = await announcements_service.create_announcement(
            payload=payload,
            created_by=current_user.get("user_id")
        )
        
        # Schedule delivery if immediate
        if payload.schedule_type == "immediate":
            background_tasks.add_task(
                announcements_service.deliver_announcement,
                announcement_id=announcement["id"]
            )
        
        return {
            "success": True,
            "announcement": announcement,
            "message": "Announcement created successfully"
        }
        
    except Exception as e:
        await observability_service.log_event(
            "announcement_error",
            user_id=current_user.get("user_id"),
            metadata={"error": str(e), "action": "create_announcement"}
        )
        raise HTTPException(status_code=500, detail="Failed to create announcement")

@announcements_router.get("/{announcement_id}")
async def get_announcement(
    announcement_id: str,
    current_user: Dict[str, Any] = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get a specific announcement by ID
    """
    try:
        announcement = await announcements_service.get_announcement(announcement_id)
        
        if not announcement:
            raise HTTPException(status_code=404, detail="Announcement not found")
        
        return {
            "success": True,
            "announcement": announcement
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await observability_service.log_event(
            "announcement_error",
            user_id=current_user.get("user_id"),
            metadata={"error": str(e), "action": "get_announcement", "announcement_id": announcement_id}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve announcement")

@announcements_router.put("/{announcement_id}")
async def update_announcement(
    announcement_id: str,
    payload: AnnouncementUpdate,
    current_user: Dict[str, Any] = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Update an existing announcement
    """
    try:
        announcement = await announcements_service.update_announcement(
            announcement_id=announcement_id,
            payload=payload,
            updated_by=current_user.get("user_id")
        )
        
        return {
            "success": True,
            "announcement": announcement,
            "message": "Announcement updated successfully"
        }
        
    except Exception as e:
        await observability_service.log_event(
            "announcement_error",
            user_id=current_user.get("user_id"),
            metadata={"error": str(e), "action": "update_announcement", "announcement_id": announcement_id}
        )
        raise HTTPException(status_code=500, detail="Failed to update announcement")

@announcements_router.delete("/{announcement_id}")
async def delete_announcement(
    announcement_id: str,
    current_user: Dict[str, Any] = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Delete an announcement
    """
    try:
        await announcements_service.delete_announcement(announcement_id)
        
        return {
            "success": True,
            "message": "Announcement deleted successfully"
        }
        
    except Exception as e:
        await observability_service.log_event(
            "announcement_error",
            user_id=current_user.get("user_id"),
            metadata={"error": str(e), "action": "delete_announcement", "announcement_id": announcement_id}
        )
        raise HTTPException(status_code=500, detail="Failed to delete announcement")

@announcements_router.post("/{announcement_id}/send")
async def send_announcement(
    announcement_id: str,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Manually trigger announcement delivery
    """
    try:
        background_tasks.add_task(
            announcements_service.deliver_announcement,
            announcement_id=announcement_id
        )
        
        return {
            "success": True,
            "message": "Announcement delivery initiated"
        }
        
    except Exception as e:
        await observability_service.log_event(
            "announcement_error",
            user_id=current_user.get("user_id"),
            metadata={"error": str(e), "action": "send_announcement", "announcement_id": announcement_id}
        )
        raise HTTPException(status_code=500, detail="Failed to send announcement")

@announcements_router.get("/{announcement_id}/analytics")
async def get_announcement_analytics(
    announcement_id: str,
    current_user: Dict[str, Any] = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get analytics for a specific announcement
    """
    try:
        analytics = await announcements_service.get_announcement_analytics(announcement_id)
        
        return {
            "success": True,
            "analytics": analytics
        }
        
    except Exception as e:
        await observability_service.log_event(
            "announcement_error",
            user_id=current_user.get("user_id"),
            metadata={"error": str(e), "action": "get_analytics", "announcement_id": announcement_id}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")

@announcements_router.get("/analytics/overview")
async def get_analytics_overview(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: Dict[str, Any] = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get overview analytics for all announcements
    """
    try:
        analytics = await announcements_service.get_analytics_overview(days)
        
        return {
            "success": True,
            "analytics": analytics
        }
        
    except Exception as e:
        await observability_service.log_event(
            "announcement_error",
            user_id=current_user.get("user_id"),
            metadata={"error": str(e), "action": "get_analytics_overview"}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics overview")

@announcements_router.get("/scheduled")
async def get_scheduled_announcements(
    current_user: Dict[str, Any] = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get all scheduled announcements
    """
    try:
        scheduled = await announcements_service.get_scheduled_announcements()
        
        return {
            "success": True,
            "scheduled_announcements": scheduled
        }
        
    except Exception as e:
        await observability_service.log_event(
            "announcement_error",
            user_id=current_user.get("user_id"),
            metadata={"error": str(e), "action": "get_scheduled_announcements"}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve scheduled announcements")

@announcements_router.post("/{announcement_id}/cancel")
async def cancel_scheduled_announcement(
    announcement_id: str,
    current_user: Dict[str, Any] = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Cancel a scheduled announcement
    """
    try:
        await announcements_service.cancel_scheduled_announcement(announcement_id)
        
        return {
            "success": True,
            "message": "Scheduled announcement cancelled successfully"
        }
        
    except Exception as e:
        await observability_service.log_event(
            "announcement_error",
            user_id=current_user.get("user_id"),
            metadata={"error": str(e), "action": "cancel_announcement", "announcement_id": announcement_id}
        )
        raise HTTPException(status_code=500, detail="Failed to cancel announcement")

@announcements_router.get("/user/preferences")
async def get_user_preferences(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current user's notification preferences
    """
    try:
        preferences = await announcements_service.get_user_preferences(current_user.get("user_id"))
        
        return {
            "success": True,
            "preferences": preferences
        }
        
    except Exception as e:
        await observability_service.log_event(
            "announcement_error",
            user_id=current_user.get("user_id"),
            metadata={"error": str(e), "action": "get_user_preferences"}
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve user preferences")

@announcements_router.put("/user/preferences")
async def update_user_preferences(
    preferences: UserNotificationPreferences,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Update current user's notification preferences
    """
    try:
        updated_preferences = await announcements_service.update_user_preferences(
            user_id=current_user.get("user_id"),
            preferences=preferences
        )
        
        return {
            "success": True,
            "preferences": updated_preferences,
            "message": "Preferences updated successfully"
        }
        
    except Exception as e:
        await observability_service.log_event(
            "announcement_error",
            user_id=current_user.get("user_id"),
            metadata={"error": str(e), "action": "update_user_preferences"}
        )
        raise HTTPException(status_code=500, detail="Failed to update user preferences")

@announcements_router.post("/{announcement_id}/track")
async def track_announcement_event(
    announcement_id: str,
    event_type: str = Query(..., description="Event type: opened, clicked, dismissed"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Track user interaction with an announcement
    """
    try:
        await announcements_service.track_event(
            announcement_id=announcement_id,
            user_id=current_user.get("user_id"),
            event_type=event_type
        )
        
        return {
            "success": True,
            "message": "Event tracked successfully"
        }
        
    except Exception as e:
        await observability_service.log_event(
            "announcement_error",
            user_id=current_user.get("user_id"),
            metadata={"error": str(e), "action": "track_event", "announcement_id": announcement_id}
        )
        raise HTTPException(status_code=500, detail="Failed to track event")


