#!/usr/bin/env python3
"""
Threads API Routes
Handles posting to Threads via Meta Graph API
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import requests

# Setup logging
logger = logging.getLogger(__name__)

# Create router
threads_router = APIRouter()

# Pydantic models
from pydantic import BaseModel

class ThreadsPostRequest(BaseModel):
    content: str
    images: Optional[List[str]] = None
    scheduled_time: Optional[datetime] = None

class ThreadsThreadRequest(BaseModel):
    posts: List[str]
    images: Optional[List[List[str]]] = None
    scheduled_time: Optional[datetime] = None

class ThreadsResponse(BaseModel):
    success: bool
    post_id: Optional[str] = None
    error_message: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None

class ThreadsUserInfo(BaseModel):
    id: str
    username: str
    name: str
    profile_picture: Optional[str] = None
    followers_count: Optional[int] = None
    following_count: Optional[int] = None

from src.services.authentication import get_current_user

# Dependency to get current user (via JWT)
async def get_current_user_id(current_user: Dict = Depends(get_current_user)) -> str:
    """Get current user ID from JWT-authenticated request"""
    return current_user["user_id"]

@threads_router.post("/post", response_model=ThreadsResponse)
async def post_to_threads(
    request: ThreadsPostRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Post a single post to Threads"""
    try:
        # For now, simulate posting (since Threads API is not fully public)
        # In production, this would use the actual Threads API
        
        logger.info(f"Posting to Threads for user {user_id}: {request.content[:50]}...")
        
        # Simulate API call delay
        import asyncio
        await asyncio.sleep(1)
        
        # Simulate success response
        post_id = f"threads_post_{datetime.utcnow().timestamp()}"
        
        return ThreadsResponse(
            success=True,
            post_id=post_id,
            response_data={
                "content": request.content,
                "images": request.images or [],
                "posted_at": datetime.utcnow().isoformat(),
                "platform": "threads"
            }
        )
        
    except Exception as e:
        logger.error(f"Error posting to Threads: {e}")
        return ThreadsResponse(
            success=False,
            error_message=str(e)
        )

@threads_router.post("/thread", response_model=List[ThreadsResponse])
async def post_thread_to_threads(
    request: ThreadsThreadRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Post a thread (multiple posts) to Threads"""
    try:
        responses = []
        
        for i, post_content in enumerate(request.posts):
            logger.info(f"Posting thread part {i+1}/{len(request.posts)} for user {user_id}")
            
            # Get images for this post if available
            post_images = None
            if request.images and i < len(request.images):
                post_images = request.images[i]
            
            # Simulate posting each part
            import asyncio
            await asyncio.sleep(1)
            
            post_id = f"threads_thread_{datetime.utcnow().timestamp()}_{i}"
            
            responses.append(ThreadsResponse(
                success=True,
                post_id=post_id,
                response_data={
                    "content": post_content,
                    "images": post_images or [],
                    "post_number": i + 1,
                    "total_posts": len(request.posts),
                    "posted_at": datetime.utcnow().isoformat(),
                    "platform": "threads"
                }
            ))
        
        return responses
        
    except Exception as e:
        logger.error(f"Error posting thread to Threads: {e}")
        return [ThreadsResponse(
            success=False,
            error_message=str(e)
        )]

@threads_router.get("/user-info", response_model=ThreadsUserInfo)
async def get_threads_user_info(
    user_id: str = Depends(get_current_user_id)
):
    """Get Threads user information"""
    try:
        # For now, return mock data
        # In production, this would fetch from Threads API
        
        return ThreadsUserInfo(
            id="mock_threads_user_id",
            username="mockuser",
            name="Mock User",
            profile_picture="https://via.placeholder.com/150",
            followers_count=1234,
            following_count=567
        )
        
    except Exception as e:
        logger.error(f"Error getting Threads user info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user info")

@threads_router.get("/posts")
async def get_threads_posts(
    user_id: str = Depends(get_current_user_id),
    limit: int = 10
):
    """Get recent Threads posts"""
    try:
        # For now, return mock data
        # In production, this would fetch from Threads API
        
        mock_posts = []
        for i in range(min(limit, 5)):
            mock_posts.append({
                "id": f"mock_post_{i}",
                "content": f"This is mock post {i+1} from Threads",
                "posted_at": datetime.utcnow().isoformat(),
                "likes": 10 + i * 5,
                "replies": 2 + i,
                "reposts": 1 + i
            })
        
        return {
            "posts": mock_posts,
            "total": len(mock_posts),
            "has_more": False
        }
        
    except Exception as e:
        logger.error(f"Error getting Threads posts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get posts")

@threads_router.post("/schedule")
async def schedule_threads_post(
    request: ThreadsPostRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Schedule a post for Threads"""
    try:
        if not request.scheduled_time:
            raise HTTPException(status_code=400, detail="Scheduled time is required")
        
        # For now, simulate scheduling
        # In production, this would use a job queue
        
        schedule_id = f"threads_schedule_{datetime.utcnow().timestamp()}"
        
        logger.info(f"Scheduling Threads post for user {user_id} at {request.scheduled_time}")
        
        return {
            "success": True,
            "schedule_id": schedule_id,
            "scheduled_time": request.scheduled_time.isoformat(),
            "message": "Post scheduled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling Threads post: {e}")
        raise HTTPException(status_code=500, detail="Failed to schedule post")

@threads_router.get("/connection-status")
async def get_threads_connection_status(
    user_id: str = Depends(get_current_user_id)
):
    """Get Threads connection status"""
    try:
        # For now, return mock status
        # In production, this would check actual connection
        
        return {
            "connected": True,
            "username": "mockuser",
            "last_sync": datetime.utcnow().isoformat(),
            "permissions": ["read", "write"],
            "account_type": "business"
        }
        
    except Exception as e:
        logger.error(f"Error getting Threads connection status: {e}")
        return {
            "connected": False,
            "error": str(e)
        }
