#!/usr/bin/env python3
"""
Content Management API Routes
Handles content creation, retrieval, updating, and deletion
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging

from src.services.supabase import supabase_service
from src.services.authentication import get_current_user

# Setup logging
logger = logging.getLogger(__name__)

# Create router
content_router = APIRouter()

# Pydantic models for request/response
from pydantic import BaseModel

class ContentCreateRequest(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []
    status: str = "draft"  # draft, published, scheduled
    scheduled_for: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = {}

class ContentUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class ContentResponse(BaseModel):
    id: str
    user_id: str
    title: str
    content: str
    tags: List[str]
    status: str
    scheduled_for: Optional[datetime]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class ContentListResponse(BaseModel):
    items: List[ContentResponse]
    total: int
    page: int
    per_page: int
    has_more: bool

class ContentStatsResponse(BaseModel):
    total: int
    published: int
    drafts: int
    scheduled: int
    this_month: int

# Dependency to get current user (via JWT)
async def get_current_user_id(current_user: Dict = Depends(get_current_user)) -> str:
    """Get current user ID from JWT-authenticated request"""
    return current_user["user_id"]

@content_router.post("/create")
async def create_content(
    request: ContentCreateRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Create new content"""
    try:
        content_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        # Create content item
        content_data = {
            "id": content_id,
            "user_id": user_id,
            "title": request.title,
            "content": request.content,
            "tags": request.tags,
            "status": request.status,
            "scheduled_for": request.scheduled_for.isoformat() if request.scheduled_for else None,
            "metadata": request.metadata,
            "created_at": now,
            "updated_at": now
        }
        
        # Insert into content_items table
        response = supabase_service.client.table("content_items").insert({
            "id": content_id,
            "user_id": user_id,
            "title": request.title,
            "raw": request.content,
            "normalized": request.content,
            "metadata": {
                "tags": request.tags,
                "status": request.status,
                "scheduled_for": request.scheduled_for.isoformat() if request.scheduled_for else None,
                **request.metadata
            }
        }).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create content")
        
        return {
            "success": True,
            "content_id": content_id,
            "message": "Content created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating content: {e}")
        raise HTTPException(status_code=500, detail="Failed to create content")

@content_router.get("/list")
async def list_content(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id)
):
    """List user's content with pagination"""
    try:
        # Build query
        query = supabase_service.client.table("content_items").select("*").eq("user_id", user_id)
        
        # Add status filter if provided
        if status:
            query = query.eq("metadata->status", status)
        
        # Add pagination
        offset = (page - 1) * per_page
        query = query.range(offset, offset + per_page - 1).order("added_at", desc=True)
        
        response = query.execute()
        
        if not response.data:
            return {
                "success": True,
                "items": [],
                "total": 0,
                "page": page,
                "per_page": per_page,
                "has_more": False
            }
        
        # Convert to response format
        items = []
        for item in response.data:
            metadata = item.get("metadata", {})
            items.append(ContentResponse(
                id=item["id"],
                user_id=item["user_id"],
                title=item.get("title", "Untitled"),
                content=item.get("normalized", item.get("raw", "")),
                tags=metadata.get("tags", []),
                status=metadata.get("status", "draft"),
                scheduled_for=datetime.fromisoformat(metadata["scheduled_for"]) if metadata.get("scheduled_for") else None,
                metadata=metadata,
                created_at=datetime.fromisoformat(item["added_at"]),
                updated_at=datetime.fromisoformat(item["added_at"])
            ))
        
        # Get total count
        count_query = supabase_service.client.table("content_items").select("id", count="exact").eq("user_id", user_id)
        if status:
            count_query = count_query.eq("metadata->status", status)
        count_response = count_query.execute()
        total = count_response.count if hasattr(count_response, 'count') else len(response.data)
        
        return {
            "success": True,
            "items": [item.dict() for item in items],
            "total": total,
            "page": page,
            "per_page": per_page,
            "has_more": offset + per_page < total
        }
        
    except Exception as e:
        logger.error(f"Error listing content: {e}")
        raise HTTPException(status_code=500, detail="Failed to list content")

@content_router.get("/{content_id}")
async def get_content(
    content_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get specific content by ID"""
    try:
        response = supabase_service.client.table("content_items").select("*").eq("id", content_id).eq("user_id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Content not found")
        
        item = response.data[0]
        metadata = item.get("metadata", {})
        
        return {
            "success": True,
            "content": {
                "id": item["id"],
                "user_id": item["user_id"],
                "title": item.get("title", "Untitled"),
                "content": item.get("normalized", item.get("raw", "")),
                "tags": metadata.get("tags", []),
                "status": metadata.get("status", "draft"),
                "scheduled_for": metadata.get("scheduled_for"),
                "metadata": metadata,
                "created_at": item["added_at"],
                "updated_at": item["added_at"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content: {e}")
        raise HTTPException(status_code=500, detail="Failed to get content")

@content_router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: str,
    request: ContentUpdateRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Update content"""
    try:
        # First, get the existing content
        get_response = supabase_service.client.table("content_items").select("*").eq("id", content_id).eq("user_id", user_id).execute()
        
        if not get_response.data:
            raise HTTPException(status_code=404, detail="Content not found")
        
        existing_item = get_response.data[0]
        existing_metadata = existing_item.get("metadata", {})
        
        # Prepare update data
        update_data = {}
        new_metadata = existing_metadata.copy()
        
        if request.title is not None:
            update_data["title"] = request.title
        
        if request.content is not None:
            update_data["raw"] = request.content
            update_data["normalized"] = request.content
        
        if request.tags is not None:
            new_metadata["tags"] = request.tags
        
        if request.status is not None:
            new_metadata["status"] = request.status
        
        if request.scheduled_for is not None:
            new_metadata["scheduled_for"] = request.scheduled_for.isoformat()
        
        if request.metadata is not None:
            new_metadata.update(request.metadata)
        
        update_data["metadata"] = new_metadata
        
        # Update the content
        response = supabase_service.client.table("content_items").update(update_data).eq("id", content_id).eq("user_id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to update content")
        
        updated_item = response.data[0]
        
        return ContentResponse(
            id=updated_item["id"],
            user_id=updated_item["user_id"],
            title=updated_item.get("title", "Untitled"),
            content=updated_item.get("normalized", updated_item.get("raw", "")),
            tags=new_metadata.get("tags", []),
            status=new_metadata.get("status", "draft"),
            scheduled_for=datetime.fromisoformat(new_metadata["scheduled_for"]) if new_metadata.get("scheduled_for") else None,
            metadata=new_metadata,
            created_at=datetime.fromisoformat(updated_item["added_at"]),
            updated_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating content: {e}")
        raise HTTPException(status_code=500, detail="Failed to update content")

@content_router.delete("/{content_id}")
async def delete_content(
    content_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete content"""
    try:
        response = supabase_service.client.table("content_items").delete().eq("id", content_id).eq("user_id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Content not found")
        
        return {"success": True, "message": "Content deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting content: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete content")

@content_router.get("/stats/overview")
async def get_content_stats(
    user_id: str = Depends(get_current_user_id)
):
    """Get content statistics"""
    try:
        # Get total content count
        total_response = supabase_service.client.table("content_items").select("id", count="exact").eq("user_id", user_id).execute()
        total = total_response.count if hasattr(total_response, 'count') else 0
        
        # Get content by status
        all_content = supabase_service.client.table("content_items").select("metadata").eq("user_id", user_id).execute()
        
        published = 0
        drafts = 0
        scheduled = 0
        
        for item in all_content.data:
            status = item.get("metadata", {}).get("status", "draft")
            if status == "published":
                published += 1
            elif status == "draft":
                drafts += 1
            elif status == "scheduled":
                scheduled += 1
        
        # Get this month's content
        this_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        this_month_response = supabase_service.client.table("content_items").select("id", count="exact").eq("user_id", user_id).gte("added_at", this_month_start.isoformat()).execute()
        this_month = this_month_response.count if hasattr(this_month_response, 'count') else 0
        
        return {
            "success": True,
            "stats": {
                "total": total,
                "published": published,
                "drafts": drafts,
                "scheduled": scheduled,
                "this_month": this_month
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting content stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get content statistics")

@content_router.post("/{content_id}/publish")
async def publish_content(
    content_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Publish content (change status to published)"""
    try:
        # Update status to published
        response = supabase_service.client.table("content_items").update({
            "metadata": {"status": "published"}
        }).eq("id", content_id).eq("user_id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Content not found")
        
        return {"success": True, "message": "Content published successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing content: {e}")
        raise HTTPException(status_code=500, detail="Failed to publish content")

@content_router.post("/{content_id}/schedule")
async def schedule_content(
    content_id: str,
    scheduled_for: datetime = Body(...),
    user_id: str = Depends(get_current_user_id)
):
    """Schedule content for later posting"""
    try:
        # Update status to scheduled and set scheduled_for
        response = supabase_service.client.table("content_items").update({
            "metadata": {
                "status": "scheduled",
                "scheduled_for": scheduled_for.isoformat()
            }
        }).eq("id", content_id).eq("user_id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Content not found")
        
        return {"success": True, "message": "Content scheduled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling content: {e}")
        raise HTTPException(status_code=500, detail="Failed to schedule content")
