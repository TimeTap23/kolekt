#!/usr/bin/env python3
"""
Threads API Integration Service for ThreadStorm
Uses Meta's official Threads API
"""

import logging
import asyncio
import httpx
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from src.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ThreadsPost:
    """Threads post data structure"""
    id: str
    text: str
    user_id: str
    created_at: datetime
    likes_count: int = 0
    replies_count: int = 0
    reposts_count: int = 0
    media_urls: List[str] = None
    reply_to: Optional[str] = None


@dataclass
class ThreadsThread:
    """Threads thread data structure"""
    id: str
    posts: List[ThreadsPost]
    user_id: str
    created_at: datetime
    total_posts: int
    engagement_score: float = 0.0


@dataclass
class ThreadsResponse:
    """Threads API response"""
    success: bool
    post_id: Optional[str] = None
    thread_id: Optional[str] = None
    error_message: Optional[str] = None
    response_time: float = 0.0


class ThreadsAPIClient:
    """Client for Meta's Threads API"""
    
    def __init__(self):
        self.base_url = "https://graph.instagram.com/v18.0"
        self.api_key = settings.THREADS_API_KEY
        self.api_secret = settings.THREADS_API_SECRET
        self.access_token = settings.THREADS_ACCESS_TOKEN
        self.access_token_secret = settings.THREADS_ACCESS_TOKEN_SECRET
        
        # API endpoints
        self.endpoints = {
            'post': f"{self.base_url}/me/media",
            'thread': f"{self.base_url}/me/media",
            'user_info': f"{self.base_url}/me",
            'recent_posts': f"{self.base_url}/me/media",
            'test_connection': f"{self.base_url}/me"
        }
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Dict[str, Any] = None,
        params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Threads API"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
                
                if method.upper() == "GET":
                    response = await client.get(endpoint, headers=headers, params=params)
                elif method.upper() == "POST":
                    response = await client.post(endpoint, headers=headers, json=data, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error in Threads API request: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error in Threads API: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Threads API request: {e}")
            raise
    
    async def post_single(self, text: str, user_id: str, media_urls: List[str] = None) -> ThreadsResponse:
        """Post a single thread to Threads"""
        try:
            start_time = datetime.now()
            
            # Prepare post data
            post_data = {
                "caption": text,
                "access_token": self.access_token
            }
            
            # Add media if provided
            if media_urls:
                post_data["media_type"] = "CAROUSEL_ALBUM"
                post_data["children"] = [{"media_type": "IMAGE", "image_url": url} for url in media_urls]
            else:
                post_data["media_type"] = "IMAGE"  # Required by API, but we'll post text-only
            
            # Make the API call
            response = await self._make_request("POST", self.endpoints['post'], data=post_data)
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            if response.get("id"):
                logger.info(f"Successfully posted to Threads: {response['id']}")
                return ThreadsResponse(
                    success=True,
                    post_id=response["id"],
                    response_time=response_time
                )
            else:
                logger.error(f"Failed to post to Threads: {response}")
                return ThreadsResponse(
                    success=False,
                    error_message="Failed to get post ID from response",
                    response_time=response_time
                )
                
        except Exception as e:
            logger.error(f"Error posting to Threads: {e}")
            return ThreadsResponse(
                success=False,
                error_message=str(e)
            )
    
    async def post_thread(self, posts: List[str], user_id: str, images: List[List[str]] = None) -> List[ThreadsResponse]:
        """Post a thread (multiple posts) to Threads"""
        try:
            responses = []
            
            for i, post_text in enumerate(posts):
                # Get images for this post if available
                post_images = images[i] if images and i < len(images) else None
                
                # Post the individual post
                response = await self.post_single(post_text, user_id, post_images)
                responses.append(response)
                
                # If this isn't the last post, add a small delay
                if i < len(posts) - 1:
                    await asyncio.sleep(2)  # 2-second delay between posts
            
            return responses
            
        except Exception as e:
            logger.error(f"Error posting thread to Threads: {e}")
            return [ThreadsResponse(success=False, error_message=str(e))]
    
    async def schedule_post(self, text: str, user_id: str, scheduled_time: datetime, media_urls: List[str] = None) -> ThreadsResponse:
        """Schedule a post for later (if supported by Threads API)"""
        try:
            # Note: Threads API may not support scheduling yet
            # This is a placeholder for when scheduling becomes available
            logger.warning("Scheduling not yet supported by Threads API")
            
            return ThreadsResponse(
                success=False,
                error_message="Scheduling not yet supported by Threads API"
            )
            
        except Exception as e:
            logger.error(f"Error scheduling post to Threads: {e}")
            return ThreadsResponse(success=False, error_message=str(e))
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get user information from Threads"""
        try:
            params = {
                "fields": "id,username,account_type,media_count,followers_count,follows_count",
                "access_token": self.access_token
            }
            
            response = await self._make_request("GET", self.endpoints['user_info'], params=params)
            
            return {
                "user_id": response.get("id"),
                "username": response.get("username"),
                "account_type": response.get("account_type"),
                "media_count": response.get("media_count", 0),
                "followers_count": response.get("followers_count", 0),
                "following_count": response.get("follows_count", 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting user info from Threads: {e}")
            return {
                "user_id": user_id,
                "username": f"user_{user_id}",
                "account_type": "unknown",
                "media_count": 0,
                "followers_count": 0,
                "following_count": 0,
                "error": str(e)
            }
    
    async def get_recent_posts(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent posts from Threads"""
        try:
            params = {
                "fields": "id,caption,media_type,media_url,thumbnail_url,timestamp,like_count,comments_count",
                "limit": limit,
                "access_token": self.access_token
            }
            
            response = await self._make_request("GET", self.endpoints['recent_posts'], params=params)
            
            posts = []
            for item in response.get("data", []):
                posts.append({
                    "id": item.get("id"),
                    "caption": item.get("caption"),
                    "media_type": item.get("media_type"),
                    "media_url": item.get("media_url"),
                    "thumbnail_url": item.get("thumbnail_url"),
                    "timestamp": item.get("timestamp"),
                    "like_count": item.get("like_count", 0),
                    "comments_count": item.get("comments_count", 0)
                })
            
            return posts
            
        except Exception as e:
            logger.error(f"Error getting recent posts from Threads: {e}")
            return []
    
    async def test_connection(self, user_id: str) -> bool:
        """Test connection to Threads API"""
        try:
            # Try to get user info as a connection test
            user_info = await self.get_user_info(user_id)
            return "error" not in user_info
            
        except Exception as e:
            logger.error(f"Threads API connection test failed: {e}")
            return False


class ThreadsIntegrationService:
    """Service for managing Threads API integration"""
    
    def __init__(self):
        self.clients: Dict[str, ThreadsAPIClient] = {}
    
    def get_client(self, user_id: str) -> ThreadsAPIClient:
        """Get or create a Threads API client for a user"""
        if user_id not in self.clients:
            self.clients[user_id] = ThreadsAPIClient()
        return self.clients[user_id]
    
    async def publish_threadstorm(
        self, 
        user_id: str, 
        posts: List[str], 
        images: List[List[str]] = None,
        scheduled_time: datetime = None
    ) -> List[ThreadsResponse]:
        """Publish a threadstorm to Threads"""
        try:
            client = self.get_client(user_id)
            
            if scheduled_time:
                # Schedule the posts
                responses = []
                for i, post in enumerate(posts):
                    post_images = images[i] if images and i < len(images) else None
                    response = await client.schedule_post(post, user_id, scheduled_time, post_images)
                    responses.append(response)
                return responses
            else:
                # Post immediately
                return await client.post_thread(posts, user_id, images)
                
        except Exception as e:
            logger.error(f"Error publishing threadstorm to Threads: {e}")
            return [ThreadsResponse(success=False, error_message=str(e))]
    
    async def test_connection(self, user_id: str) -> bool:
        """Test Threads API connection for a user"""
        try:
            client = self.get_client(user_id)
            return await client.test_connection(user_id)
        except Exception as e:
            logger.error(f"Error testing Threads connection: {e}")
            return False
    
    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get Threads user information"""
        try:
            client = self.get_client(user_id)
            return await client.get_user_info(user_id)
        except Exception as e:
            logger.error(f"Error getting Threads user info: {e}")
            return {"error": str(e)}
    
    async def get_recent_posts(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent Threads posts for a user"""
        try:
            client = self.get_client(user_id)
            return await client.get_recent_posts(user_id, limit)
        except Exception as e:
            logger.error(f"Error getting recent Threads posts: {e}")
            return []


# Global service instance
threads_service = ThreadsIntegrationService()
