"""
Announcements CRUD to support announcements.html
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from src.services.authentication import get_current_user, require_admin
from src.services.observability import observability_service

announcements_router = APIRouter()

class Announcement(BaseModel):
    id: str
    title: str
    content: str
    type: str
    audience: str
    status: str
    created_at: datetime
    scheduled_for: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    recipients: Optional[int] = None
    delivered: Optional[int] = None


class AnnouncementCreate(BaseModel):
    title: str
    content: str
    type: str
    audience: str
    schedule: Optional[str] = "now"
    scheduleDateTime: Optional[str] = None


_ANNOUNCEMENTS_MEM: List[Dict[str, Any]] = []


@announcements_router.get("")
async def list_announcements(current_user: Dict[str, Any] = Depends(require_admin)):
    try:
        await observability_service.log_event(
            "announcements_list",
            user_id=current_user.get("user_id"),
            metadata={"action": "list_announcements"}
        )
        return _ANNOUNCEMENTS_MEM
    except Exception as e:
        await observability_service.log_event(
            "announcements_error",
            user_id=current_user.get("user_id"),
            metadata={"error": str(e), "action": "list_announcements"}
        )
        raise


@announcements_router.post("")
async def create_announcement(payload: AnnouncementCreate, current_user: Dict[str, Any] = Depends(require_admin)):
    try:
        await observability_service.log_event(
            "announcement_create",
            user_id=current_user.get("user_id"),
            metadata={"action": "create_announcement", "type": payload.type, "audience": payload.audience}
        )
        
        now = datetime.utcnow().isoformat()
        item = {
            "id": str(uuid.uuid4()),
            "title": payload.title,
            "content": payload.content,
            "type": payload.type,
            "audience": payload.audience,
            "status": "scheduled" if payload.schedule == "scheduled" else "draft",
            "created_at": now,
            "scheduled_for": payload.scheduleDateTime,
        }
        _ANNOUNCEMENTS_MEM.append(item)
        return item
    except Exception as e:
        await observability_service.log_event(
            "announcement_error",
            user_id=current_user.get("user_id"),
            metadata={"error": str(e), "action": "create_announcement"}
        )
        raise


