#!/usr/bin/env python3
"""
Social Media API Routes
Handles Instagram and Facebook integration
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import requests

# Setup logging
logger = logging.getLogger(__name__)

# Create router
social_router = APIRouter()

# Pydantic models
from pydantic import BaseModel
from src.api.threads_routes import ThreadsPostRequest, ThreadsResponse

class SocialPostRequest(BaseModel):
    content: str
    images: Optional[List[str]] = None
    scheduled_time: Optional[datetime] = None

class SocialResponse(BaseModel):
    success: bool
    post_id: Optional[str] = None
    error_message: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None

class SocialUserInfo(BaseModel):
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

# Instagram Endpoints
@social_router.post("/instagram/post", response_model=SocialResponse)
async def post_to_instagram(
    request: SocialPostRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Post to Instagram"""
    try:
        logger.info(f"Posting to Instagram for user {user_id}: {request.content[:50]}...")
        
        # Simulate API call delay
        import asyncio
        await asyncio.sleep(1)
        
        # Simulate success response
        post_id = f"instagram_post_{datetime.utcnow().timestamp()}"
        
        return SocialResponse(
            success=True,
            post_id=post_id,
            response_data={
                "content": request.content,
                "images": request.images or [],
                "posted_at": datetime.utcnow().isoformat(),
                "platform": "instagram"
            }
        )
        
    except Exception as e:
        logger.error(f"Error posting to Instagram: {e}")
        return SocialResponse(
            success=False,
            error_message=str(e)
        )

@social_router.get("/instagram/user-info", response_model=SocialUserInfo)
async def get_instagram_user_info(
    user_id: str = Depends(get_current_user_id)
):
    """Get Instagram user information"""
    try:
        return SocialUserInfo(
            id="mock_instagram_user_id",
            username="mockinstagramuser",
            name="Mock Instagram User",
            profile_picture="https://via.placeholder.com/150",
            followers_count=5678,
            following_count=1234
        )
        
    except Exception as e:
        logger.error(f"Error getting Instagram user info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user info")

@social_router.get("/instagram/connection-status")
async def get_instagram_connection_status(
    user_id: str = Depends(get_current_user_id)
):
    """Get Instagram connection status"""
    try:
        return {
            "connected": True,
            "username": "mockinstagramuser",
            "last_sync": datetime.utcnow().isoformat(),
            "permissions": ["read", "write"],
            "account_type": "business"
        }
        
    except Exception as e:
        logger.error(f"Error getting Instagram connection status: {e}")
        return {
            "connected": False,
            "error": str(e)
        }

# Facebook Endpoints
@social_router.post("/facebook/post", response_model=SocialResponse)
async def post_to_facebook(
    request: SocialPostRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Post to Facebook"""
    try:
        logger.info(f"Posting to Facebook for user {user_id}: {request.content[:50]}...")
        
        # Simulate API call delay
        import asyncio
        await asyncio.sleep(1)
        
        # Simulate success response
        post_id = f"facebook_post_{datetime.utcnow().timestamp()}"
        
        return SocialResponse(
            success=True,
            post_id=post_id,
            response_data={
                "content": request.content,
                "images": request.images or [],
                "posted_at": datetime.utcnow().isoformat(),
                "platform": "facebook"
            }
        )
        
    except Exception as e:
        logger.error(f"Error posting to Facebook: {e}")
        return SocialResponse(
            success=False,
            error_message=str(e)
        )

@social_router.get("/facebook/user-info", response_model=SocialUserInfo)
async def get_facebook_user_info(
    user_id: str = Depends(get_current_user_id)
):
    """Get Facebook user information"""
    try:
        return SocialUserInfo(
            id="mock_facebook_user_id",
            username="mockfacebookuser",
            name="Mock Facebook User",
            profile_picture="https://via.placeholder.com/150",
            followers_count=8901,
            following_count=2345
        )
        
    except Exception as e:
        logger.error(f"Error getting Facebook user info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user info")

@social_router.get("/facebook/connection-status")
async def get_facebook_connection_status(
    user_id: str = Depends(get_current_user_id)
):
    """Get Facebook connection status"""
    try:
        return {
            "connected": True,
            "username": "mockfacebookuser",
            "last_sync": datetime.utcnow().isoformat(),
            "permissions": ["read", "write"],
            "account_type": "business"
        }
        
    except Exception as e:
        logger.error(f"Error getting Facebook connection status: {e}")
        return {
            "connected": False,
            "error": str(e)
        }

class CrossPlatformPostRequest(BaseModel):
    content: str
    platforms: Optional[List[str]] = ["threads", "instagram", "facebook"]
    images: Optional[List[str]] = None
    scheduled_time: Optional[datetime] = None

# Cross-platform posting
@social_router.post("/cross-platform/post")
async def post_to_all_platforms(
    request: CrossPlatformPostRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Post to multiple platforms simultaneously"""
    try:
        results = {}
        platforms = request.platforms or ["threads", "instagram", "facebook"]

        for platform in platforms:
            logger.info(f"Posting to {platform} for user {user_id}")
            # Simulate posting
            import asyncio
            await asyncio.sleep(0.3)
            post_id = f"{platform}_post_{datetime.utcnow().timestamp()}"
            results[platform] = {
                "success": True,
                "post_id": post_id,
                "posted_at": datetime.utcnow().isoformat()
            }

        return {
            "success": True,
            "results": results,
            "message": f"Posted to {len(platforms)} platforms successfully"
        }
    except Exception as e:
        logger.error(f"Error posting to multiple platforms: {e}")
        return {"success": False, "error": str(e)}

# Threads wrapper under social namespace for consistency
@social_router.post("/threads/post", response_model=ThreadsResponse)
async def post_threads_via_social(
    request: ThreadsPostRequest,
    user_id: str = Depends(get_current_user_id)
):
    try:
        logger.info(f"[Social] Posting to Threads for user {user_id}")
        # Simulate success similarly to threads route
        import asyncio
        await asyncio.sleep(0.3)
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
        logger.error(f"Error in social threads post: {e}")
        return ThreadsResponse(success=False, error_message=str(e))
