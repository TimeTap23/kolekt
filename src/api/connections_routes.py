#!/usr/bin/env python3
"""
Social Connections API Routes
Handles connecting and managing social media accounts
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import asyncio
import json

# Setup logging
logger = logging.getLogger(__name__)

# Create router
connections_router = APIRouter()

# Pydantic models
from pydantic import BaseModel

class ConnectionRequest(BaseModel):
    platform: str  # threads, instagram, facebook
    auth_code: Optional[str] = None
    access_token: Optional[str] = None

class DisconnectRequest(BaseModel):
    platform: str
    account_id: str

class ConnectionStatus(BaseModel):
    platform: str
    connected: bool
    account_id: Optional[str] = None
    username: Optional[str] = None
    display_name: Optional[str] = None
    profile_pic: Optional[str] = None
    followers_count: Optional[int] = None
    connected_at: Optional[str] = None
    last_sync: Optional[str] = None
    permissions: Optional[List[str]] = None

class ConnectionResponse(BaseModel):
    success: bool
    message: str
    connection: Optional[ConnectionStatus] = None
    error_message: Optional[str] = None

class AccountInfo(BaseModel):
    id: str
    platform: str
    username: str
    display_name: str
    profile_pic: str
    followers_count: int
    following_count: int
    bio: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    verified: bool = False
    private: bool = False
    connected_at: str
    last_sync: str
    permissions: List[str]

class UserConnectionsResponse(BaseModel):
    success: bool
    connections: List[ConnectionStatus]
    total_connected: int
    available_platforms: List[str]

# Dependency to get current user from JWT
from src.services.authentication import get_current_user, get_current_user_loose

async def get_current_user_id(current_user: Dict = Depends(get_current_user_loose)) -> str:
    """Get current user ID from JWT-authenticated request"""
    return current_user["user_id"]

@connections_router.post("/connect", response_model=ConnectionResponse)
async def connect_account(
    request: ConnectionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Connect a social media account"""
    try:
        logger.info(f"Connecting {request.platform} account for user {user_id}")
        
        # Validate platform
        if request.platform not in ["threads", "instagram", "facebook"]:
            raise HTTPException(status_code=400, detail="Unsupported platform")
        
        # Simulate OAuth flow
        await asyncio.sleep(2)
        
        # Simulate connection process
        connection = await _connect_social_account(request.platform, user_id, request.auth_code, request.access_token)
        
        return ConnectionResponse(
            success=True,
            message=f"Successfully connected {request.platform} account",
            connection=connection
        )
        
    except Exception as e:
        logger.error(f"Error connecting account: {e}")
        return ConnectionResponse(
            success=False,
            message="Failed to connect account",
            error_message=str(e)
        )

@connections_router.post("/disconnect", response_model=ConnectionResponse)
async def disconnect_account(
    request: DisconnectRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Disconnect a social media account"""
    try:
        logger.info(f"Disconnecting {request.platform} account {request.account_id} for user {user_id}")
        
        # Simulate disconnection process
        await asyncio.sleep(1)
        
        # Simulate disconnection
        await _disconnect_social_account(request.platform, request.account_id, user_id)
        
        return ConnectionResponse(
            success=True,
            message=f"Successfully disconnected {request.platform} account"
        )
        
    except Exception as e:
        logger.error(f"Error disconnecting account: {e}")
        return ConnectionResponse(
            success=False,
            message="Failed to disconnect account",
            error_message=str(e)
        )

@connections_router.get("/status", response_model=UserConnectionsResponse)
async def get_connection_status(
    user_id: str = Depends(get_current_user_id)
):
    """Get status of all social media connections"""
    try:
        logger.info(f"Getting connection status for user {user_id}")
        
        # Simulate fetching connection status
        await asyncio.sleep(0.5)
        
        # Get all connections
        connections = await _get_user_connections(user_id)
        
        # Count connected platforms
        total_connected = sum(1 for conn in connections if conn.connected)
        
        return UserConnectionsResponse(
            success=True,
            connections=connections,
            total_connected=total_connected,
            available_platforms=["threads", "instagram", "facebook"]
        )
        
    except Exception as e:
        logger.error(f"Error getting connection status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@connections_router.get("/{platform}/status")
async def get_platform_status(
    platform: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get connection status for specific platform"""
    try:
        logger.info(f"Getting {platform} connection status for user {user_id}")
        
        # Validate platform
        if platform not in ["threads", "instagram", "facebook"]:
            raise HTTPException(status_code=400, detail="Unsupported platform")
        
        # Simulate fetching platform status
        await asyncio.sleep(0.5)
        
        # Get platform connection status
        connection = await _get_platform_connection(platform, user_id)
        
        return {
            "success": True,
            "connection": connection.dict()
        }
        
    except Exception as e:
        logger.error(f"Error getting platform status: {e}")
        return {
            "success": False,
            "error_message": str(e)
        }

@connections_router.get("/{platform}/account", response_model=AccountInfo)
async def get_account_info(
    platform: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get detailed account information for connected platform"""
    try:
        logger.info(f"Getting {platform} account info for user {user_id}")
        
        # Validate platform
        if platform not in ["threads", "instagram", "facebook"]:
            raise HTTPException(status_code=400, detail="Unsupported platform")
        
        # Simulate fetching account info
        await asyncio.sleep(1)
        
        # Get account information
        account_info = await _get_account_info(platform, user_id)
        
        if not account_info:
            raise HTTPException(status_code=404, detail="Account not connected")
        
        return account_info
        
    except Exception as e:
        logger.error(f"Error getting account info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@connections_router.post("/{platform}/refresh", response_model=ConnectionResponse)
async def refresh_connection(
    platform: str,
    user_id: str = Depends(get_current_user_id)
):
    """Refresh connection and sync latest data"""
    try:
        logger.info(f"Refreshing {platform} connection for user {user_id}")
        
        # Validate platform
        if platform not in ["threads", "instagram", "facebook"]:
            raise HTTPException(status_code=400, detail="Unsupported platform")
        
        # Simulate refresh process
        await asyncio.sleep(2)
        
        # Refresh connection
        connection = await _refresh_connection(platform, user_id)
        
        return ConnectionResponse(
            success=True,
            message=f"Successfully refreshed {platform} connection",
            connection=connection
        )
        
    except Exception as e:
        logger.error(f"Error refreshing connection: {e}")
        return ConnectionResponse(
            success=False,
            message="Failed to refresh connection",
            error_message=str(e)
        )

@connections_router.get("/oauth/{platform}/url")
async def get_oauth_url(
    platform: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get OAuth URL for platform connection"""
    try:
        logger.info(f"Getting OAuth URL for {platform} for user {user_id}")
        
        # Validate platform
        if platform not in ["threads", "instagram", "facebook"]:
            raise HTTPException(status_code=400, detail="Unsupported platform")
        
        # Generate OAuth URL
        oauth_url = await _generate_oauth_url(platform, user_id)
        
        return {
            "success": True,
            "oauth_url": oauth_url,
            "platform": platform
        }
        
    except Exception as e:
        logger.error(f"Error generating OAuth URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@connections_router.get("/permissions/{platform}")
async def get_platform_permissions(
    platform: str
):
    """Get required permissions for platform connection"""
    try:
        logger.info(f"Getting permissions for {platform}")
        
        # Validate platform
        if platform not in ["threads", "instagram", "facebook"]:
            raise HTTPException(status_code=400, detail="Unsupported platform")
        
        # Get platform permissions
        permissions = _get_platform_permissions(platform)
        
        return {
            "success": True,
            "platform": platform,
            "permissions": permissions,
            "description": f"Required permissions for connecting {platform.title()} account"
        }
        
    except Exception as e:
        logger.error(f"Error getting permissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
async def _connect_social_account(platform: str, user_id: str, auth_code: Optional[str], access_token: Optional[str]) -> ConnectionStatus:
    """Connect social media account and store in database"""
    try:
        from src.services.supabase import supabase_service
        
        # In a real implementation, you would:
        # 1. Exchange auth_code for access_token with the platform's OAuth endpoint
        # 2. Fetch user profile information from the platform
        # 3. Store the connection in the database
        
        # For now, we'll simulate the OAuth exchange and profile fetch
        if auth_code:
            # Simulate OAuth token exchange
            access_token = f"access_token_{platform}_{user_id}_{datetime.utcnow().timestamp()}"
        
        # Simulate fetching user profile from platform
        profile_data = await _fetch_platform_profile(platform, access_token)
        
        # Store connection in database
        connection_data = {
            "user_id": user_id,
            "platform": platform,
            "account_id": profile_data["account_id"],
            "username": profile_data["username"],
            "display_name": profile_data["display_name"],
            "profile_pic_url": profile_data["profile_pic_url"],
            "access_token": access_token,  # In production, encrypt this
            "refresh_token": profile_data.get("refresh_token"),
            "token_expires_at": profile_data.get("token_expires_at"),
            "scopes": profile_data["scopes"],
            "followers_count": profile_data["followers_count"],
            "following_count": profile_data["following_count"],
            "is_active": True,
            "connected_at": datetime.utcnow().isoformat(),
            "last_sync_at": datetime.utcnow().isoformat()
        }
        
        # Upsert connection (insert or update if exists)
        response = supabase_service.client.table("social_connections").upsert(connection_data).execute()
        
        if not response.data:
            raise Exception("Failed to store connection in database")
        
        # Return connection status
        return ConnectionStatus(
            platform=platform,
            connected=True,
            account_id=profile_data["account_id"],
            username=profile_data["username"],
            display_name=profile_data["display_name"],
            profile_pic=profile_data["profile_pic_url"],
            followers_count=profile_data["followers_count"],
            connected_at=connection_data["connected_at"],
            last_sync=connection_data["last_sync_at"],
            permissions=profile_data["scopes"]
        )
        
    except Exception as e:
        logger.error(f"Error connecting {platform} account: {e}")
        raise Exception(f"Failed to connect {platform} account: {str(e)}")

async def _fetch_platform_profile(platform: str, access_token: str) -> dict:
    """Fetch user profile from platform (simulated)"""
    # In a real implementation, this would make API calls to the platform
    # For now, we'll return simulated data
    
    timestamp = int(datetime.utcnow().timestamp())
    
    profiles = {
        "threads": {
            "account_id": f"threads_{timestamp}",
            "username": "kolekt_user",
            "display_name": "Kolekt User",
            "profile_pic_url": "https://via.placeholder.com/150x150?text=TU",
            "scopes": ["read_posts", "write_posts", "read_profile"],
            "followers_count": 1250,
            "following_count": 625,
            "refresh_token": f"refresh_token_threads_{timestamp}",
            "token_expires_at": (datetime.utcnow() + timedelta(days=60)).isoformat()
        },
        "instagram": {
            "account_id": f"instagram_{timestamp}",
            "username": "kolekt_insta",
            "display_name": "Kolekt Instagram",
            "profile_pic_url": "https://via.placeholder.com/150x150?text=KI",
            "scopes": ["read_posts", "write_posts", "read_profile", "read_insights"],
            "followers_count": 3400,
            "following_count": 1700,
            "refresh_token": f"refresh_token_instagram_{timestamp}",
            "token_expires_at": (datetime.utcnow() + timedelta(days=60)).isoformat()
        },
        "facebook": {
            "account_id": f"facebook_{timestamp}",
            "username": "kolekt.fb",
            "display_name": "Kolekt Facebook",
            "profile_pic_url": "https://via.placeholder.com/150x150?text=KF",
            "scopes": ["read_posts", "write_posts", "read_profile", "manage_pages"],
            "followers_count": 2100,
            "following_count": 1050,
            "refresh_token": f"refresh_token_facebook_{timestamp}",
            "token_expires_at": (datetime.utcnow() + timedelta(days=60)).isoformat()
        }
    }
    
    return profiles.get(platform, {})

def _get_platform_profile(platform: str) -> dict:
    """Non-async profile fetch for OAuth callback path (simulated)."""
    timestamp = int(datetime.utcnow().timestamp())
    profiles = {
        "threads": {
            "account_id": f"threads_{timestamp}",
            "username": "kolekt_user",
            "display_name": "Kolekt User",
            "profile_pic_url": "https://via.placeholder.com/150x150?text=TU",
            "scopes": ["read_posts", "write_posts", "read_profile"],
            "followers_count": 1250,
            "following_count": 625,
            "token_expires_at": (datetime.utcnow() + timedelta(days=60)).isoformat()
        },
        "instagram": {
            "account_id": f"instagram_{timestamp}",
            "username": "kolekt_insta",
            "display_name": "Kolekt Instagram",
            "profile_pic_url": "https://via.placeholder.com/150x150?text=KI",
            "scopes": ["read_posts", "write_posts", "read_profile", "read_insights"],
            "followers_count": 3400,
            "following_count": 1700,
            "token_expires_at": (datetime.utcnow() + timedelta(days=60)).isoformat()
        },
        "facebook": {
            "account_id": f"facebook_{timestamp}",
            "username": "kolekt.fb",
            "display_name": "Kolekt Facebook",
            "profile_pic_url": "https://via.placeholder.com/150x150?text=KF",
            "scopes": ["read_posts", "write_posts", "read_profile", "manage_pages"],
            "followers_count": 2100,
            "following_count": 1050,
            "token_expires_at": (datetime.utcnow() + timedelta(days=60)).isoformat()
        }
    }
    return profiles.get(platform, {})

async def _disconnect_social_account(platform: str, account_id: str, user_id: str):
    """Disconnect social media account and update database"""
    try:
        from src.services.supabase import supabase_service
        
        # In a real implementation, you would:
        # 1. Revoke the access token with the platform's API
        # 2. Mark the connection as inactive in the database
        # 3. Update any related data
        
        # For now, we'll just mark the connection as inactive
        response = supabase_service.client.table("social_connections").update({
            "is_active": False,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("user_id", user_id).eq("platform", platform).execute()
        
        if not response.data:
            raise Exception("Failed to disconnect account")
        
        logger.info(f"Disconnected {platform} account {account_id} for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error disconnecting {platform} account: {e}")
        raise Exception(f"Failed to disconnect {platform} account: {str(e)}")

async def _get_user_connections(user_id: str) -> List[ConnectionStatus]:
    """Get all social connections for a user from database"""
    try:
        from src.services.supabase import supabase_service
        
        # Fetch active connections from database
        response = supabase_service.client.table("social_connections").select("*").eq("user_id", user_id).eq("is_active", True).execute()
        
        connections = []
        for conn in response.data:
            connections.append(ConnectionStatus(
                platform=conn["platform"],
                connected=True,
                account_id=conn["account_id"],
                username=conn["username"],
                display_name=conn["display_name"],
                profile_pic=conn["profile_pic_url"],
                followers_count=conn["followers_count"],
                connected_at=conn["connected_at"],
                last_sync=conn["last_sync_at"],
                permissions=conn["scopes"]
            ))
        
        # Add disconnected platforms
        connected_platforms = {conn.platform for conn in connections}
        all_platforms = {"threads", "instagram", "facebook"}
        
        for platform in all_platforms - connected_platforms:
            connections.append(ConnectionStatus(
                platform=platform,
                connected=False,
                connected_at=None,
                last_sync=None
            ))
        
        return connections
        
    except Exception as e:
        logger.error(f"Error fetching user connections: {e}")
        # Return empty list on error
        return [
            ConnectionStatus(platform="threads", connected=False),
            ConnectionStatus(platform="instagram", connected=False),
            ConnectionStatus(platform="facebook", connected=False)
        ]
    
    return connections

async def _get_platform_connection(platform: str, user_id: str) -> ConnectionStatus:
    """Get connection status for specific platform"""
    connections = await _get_user_connections(user_id)
    
    for connection in connections:
        if connection.platform == platform:
            return connection
    
    # Return disconnected status
    return ConnectionStatus(
        platform=platform,
        connected=False,
        connected_at=None,
        last_sync=None
    )

async def _get_account_info(platform: str, user_id: str) -> Optional[AccountInfo]:
    """Get detailed account information"""
    connections = await _get_user_connections(user_id)
    
    for connection in connections:
        if connection.platform == platform and connection.connected:
            return AccountInfo(
                id=connection.account_id,
                platform=connection.platform,
                username=connection.username,
                display_name=connection.display_name,
                profile_pic=connection.profile_pic,
                followers_count=connection.followers_count,
                following_count=connection.followers_count // 2,  # Simulate following count
                bio=f"Professional content creator using Kolekt for {platform.title()}",
                website="https://kolekt.io",
                location="San Francisco, CA",
                verified=True,
                private=False,
                connected_at=connection.connected_at,
                last_sync=connection.last_sync,
                permissions=connection.permissions
            )
    
    return None

async def _refresh_connection(platform: str, user_id: str) -> ConnectionStatus:
    """Refresh connection and sync latest data"""
    # Simulate refresh process
    connection = await _get_platform_connection(platform, user_id)
    
    if connection.connected:
        # Update last sync time
        connection.last_sync = datetime.utcnow().isoformat()
        
        # Simulate updated follower count
        if platform == "threads":
            connection.followers_count = 1250 + 25  # Simulate growth
        elif platform == "instagram":
            connection.followers_count = 3400 + 50
        elif platform == "facebook":
            connection.followers_count = 2100 + 30
    
    return connection

async def _generate_oauth_url(platform: str, user_id: str) -> str:
    """Generate OAuth URL for platform"""
    # Use real OAuth for all platforms via Meta OAuth service
    if platform in ["threads", "instagram", "facebook"]:
        from src.services.meta_oauth import meta_oauth_service
        return meta_oauth_service.generate_oauth_url(platform, user_id)
    else:
        raise ValueError(f"Unsupported platform: {platform}")

def _get_platform_permissions(platform: str) -> List[str]:
    """Get required permissions for platform"""
    permissions = {
        "threads": [
            "read_posts",
            "write_posts", 
            "read_profile",
            "read_insights"
        ],
        "instagram": [
            "read_posts",
            "write_posts",
            "read_profile", 
            "read_insights",
            "manage_comments"
        ],
        "facebook": [
            "read_posts",
            "write_posts",
            "read_profile",
            "manage_pages",
            "publish_pages"
        ]
    }
    
    return permissions.get(platform, [])

async def _process_oauth_callback(platform: str, code: str, state: str, user_id: str) -> Dict[str, Any]:
    """Process OAuth callback and store connection"""
    try:
        logger.info(f"Processing OAuth callback for {platform} user {user_id}")
        
        # Use real OAuth for all platforms via Meta OAuth service
        if platform in ["threads", "instagram", "facebook"]:
            from src.services.meta_oauth import meta_oauth_service
            
            # Exchange code for access token
            token_data = await meta_oauth_service.exchange_code_for_token(platform, code)
            access_token = token_data["access_token"]
            
            # Get user profile
            profile_data = await meta_oauth_service.get_user_profile(platform, access_token)
            
            # For Facebook, also get pages if available
            pages = []
            if platform == "facebook":
                pages = await meta_oauth_service.get_pages(access_token)
            
            # Calculate token expiration
            expires_in = token_data.get("expires_in", 0)
            token_expires_at = None
            if expires_in > 0:
                token_expires_at = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()
            
            # Prepare connection data
            connection_data = {
                "user_id": user_id,
                "platform": platform,
                "account_id": profile_data["account_id"],
                "username": profile_data["username"],
                "display_name": profile_data["display_name"],
                "profile_pic_url": f"https://graph.facebook.com/{profile_data['account_id']}/picture?type=large" if platform in ["facebook", "threads"] else None,
                "access_token": access_token,  # In production, encrypt this
                "refresh_token": None,  # Meta doesn't provide refresh tokens for basic flows
                "token_expires_at": token_expires_at,
                "scopes": ",".join(meta_oauth_service.platform_configs[platform]["scopes"]),
                "followers_count": 0,  # Would need additional API call
                "following_count": 0,  # Would need additional API call
                "is_active": True,
                "connected_at": datetime.utcnow().isoformat(),
                "last_sync_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "metadata": {
                    "pages": pages if platform == "facebook" else None,
                    "account_type": profile_data.get("account_type", "personal")
                }
            }
        else:
            raise ValueError(f"Unsupported platform: {platform}")
        
        # Store in database
        from src.services.supabase import supabase_service
        
        # Check if connection already exists
        existing = supabase_service.client.table("social_connections").select("*").eq("user_id", user_id).eq("platform", platform).execute()
        
        if existing.data:
            # Update existing connection
            response = supabase_service.client.table("social_connections").update(connection_data).eq("user_id", user_id).eq("platform", platform).execute()
        else:
            # Create new connection
            response = supabase_service.client.table("social_connections").insert(connection_data).execute()
        
        if not response.data:
            raise Exception("Failed to store connection in database")
        
        logger.info(f"Successfully processed OAuth callback for {platform} user {user_id}")
        
        return {
            "success": True,
            "platform": platform,
            "account_id": connection_data["account_id"],
            "username": connection_data["username"]
        }
        
    except Exception as e:
        logger.error(f"Error processing OAuth callback: {e}")
        raise Exception(f"Failed to process OAuth callback: {str(e)}")
