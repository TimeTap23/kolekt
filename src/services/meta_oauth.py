#!/usr/bin/env python3
"""
Meta OAuth Service
Handles real OAuth flows for Instagram and Facebook
"""

import logging
import httpx
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import urlencode

from src.core.config import settings

logger = logging.getLogger(__name__)

class MetaOAuthService:
    """Handles Meta OAuth flows for Instagram and Facebook"""
    
    def __init__(self):
        self.meta_app_id = settings.META_APP_ID
        self.meta_app_secret = settings.META_APP_SECRET
        self.threads_app_id = settings.THREADS_APP_ID
        self.threads_app_secret = settings.THREADS_APP_SECRET
        self.redirect_base = getattr(settings, 'OAUTH_REDIRECT_BASE', 'http://127.0.0.1:8000')
        
        # Check if credentials are configured
        self.meta_configured = bool(self.meta_app_id and self.meta_app_secret)
        self.threads_configured = bool(self.threads_app_id and self.threads_app_secret)
        
        if not self.meta_configured:
            logger.warning("Meta OAuth credentials not configured. Using mock OAuth for Instagram and Facebook.")
        else:
            logger.info("Meta OAuth credentials configured. Real OAuth available for Instagram and Facebook.")
            
        if not self.threads_configured:
            logger.warning("Threads OAuth credentials not configured. Using mock OAuth for Threads.")
        else:
            logger.info("Threads OAuth credentials configured. Real OAuth available for Threads.")
        
        # Platform-specific configurations
        self.platform_configs = {
            "threads": {
                "auth_url": "https://threads.net/oauth/authorize",
                "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",  # Threads uses Facebook Graph API
                "graph_url": "https://graph.facebook.com",
                "scopes": ["threads_basic", "threads_content_publish"],
                "api_version": "v18.0",
                "deauthorize_url": f"{self.redirect_base}/oauth/threads/uninstall",
                "data_deletion_url": f"{self.redirect_base}/oauth/threads/delete"
            },
            "instagram": {
                "auth_url": "https://api.instagram.com/oauth/authorize",
                "token_url": "https://api.instagram.com/oauth/access_token",
                "graph_url": "https://graph.instagram.com",
                "scopes": ["user_profile", "user_media"],
                "api_version": "v18.0"
            },
            "facebook": {
                "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
                "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
                "graph_url": "https://graph.facebook.com",
                "scopes": ["pages_show_list", "pages_read_engagement", "pages_manage_posts"],
                "api_version": "v18.0"
            }
        }
    
    def generate_oauth_url(self, platform: str, user_id: str, state: Optional[str] = None) -> str:
        """Generate OAuth URL for platform"""
        if platform not in self.platform_configs:
            raise ValueError(f"Unsupported platform: {platform}")
        
        config = self.platform_configs[platform]
        state = state or f"{user_id}_{platform}_{datetime.utcnow().timestamp()}"
        
        # Determine which credentials to use
        if platform == "threads" and self.threads_configured:
            # Use Threads credentials
            client_id = self.threads_app_id
            is_configured = True
        elif platform in ["instagram", "facebook"] and self.meta_configured:
            # Use Meta credentials for Instagram and Facebook
            client_id = self.meta_app_id
            is_configured = True
        else:
            # Use mock credentials
            client_id = "kolekt_app_id"
            is_configured = False
        
        # If not configured, return mock URL
        if not is_configured:
            params = {
                "client_id": client_id,
                "redirect_uri": f"{self.redirect_base}/oauth/{platform}/callback",
                "scope": ",".join(config["scopes"]),
                "state": state,
                "response_type": "code"
            }
            param_string = urlencode(params)
            return f"{config['auth_url']}?{param_string}"
        
        params = {
            "client_id": client_id,
            "redirect_uri": f"{self.redirect_base}/oauth/{platform}/callback",
            "scope": ",".join(config["scopes"]),
            "state": state,
            "response_type": "code"
        }
        
        # Add platform-specific parameters
        if platform == "instagram":
            params["app_id"] = self.meta_app_id
        elif platform == "threads":
            params["app_id"] = self.threads_app_id
        
        # Build URL
        param_string = urlencode(params)
        return f"{config['auth_url']}?{param_string}"
    
    async def exchange_code_for_token(self, platform: str, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        if platform not in self.platform_configs:
            raise ValueError(f"Unsupported platform: {platform}")
        
        # Determine which credentials to use
        if platform == "threads" and self.threads_configured:
            client_id = self.threads_app_id
            client_secret = self.threads_app_secret
            is_configured = True
        elif platform in ["instagram", "facebook"] and self.meta_configured:
            client_id = self.meta_app_id
            client_secret = self.meta_app_secret
            is_configured = True
        else:
            is_configured = False
        
        # If not configured, return mock token
        if not is_configured:
            logger.info(f"Using mock token exchange for {platform}")
            return {
                "access_token": f"mock_access_token_{platform}_{datetime.utcnow().timestamp()}",
                "user_id": f"mock_user_{platform}",
                "expires_in": 5184000  # 60 days
            }
        
        config = self.platform_configs[platform]
        
        # Prepare token exchange request
        token_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": f"{self.redirect_base}/oauth/{platform}/callback"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    config["token_url"],
                    data=token_data,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Token exchange failed for {platform}: {response.status_code} - {response.text}")
                    raise Exception(f"Token exchange failed: {response.status_code}")
                
                token_response = response.json()
                
                # Handle different response formats
                if platform == "instagram":
                    return {
                        "access_token": token_response.get("access_token"),
                        "user_id": token_response.get("user_id"),
                        "expires_in": token_response.get("expires_in", 0)
                    }
                elif platform == "facebook":
                    return {
                        "access_token": token_response.get("access_token"),
                        "token_type": token_response.get("token_type", "bearer"),
                        "expires_in": token_response.get("expires_in", 0)
                    }
                
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            raise
    
    async def get_user_profile(self, platform: str, access_token: str) -> Dict[str, Any]:
        """Get user profile information"""
        if platform not in self.platform_configs:
            raise ValueError(f"Unsupported platform: {platform}")
        
        # If not configured, return mock profile
        if platform == "threads" and not self.threads_configured:
            logger.info(f"Using mock profile for {platform}")
            return {
                "account_id": "mock_threads_user_id",
                "username": "mockthreadsuser",
                "display_name": "Mock Threads User",
                "account_type": "personal"
            }
        elif platform in ["instagram", "facebook"] and not self.meta_configured:
            logger.info(f"Using mock profile for {platform}")
            if platform == "instagram":
                return {
                    "account_id": "mock_instagram_user_id",
                    "username": "mockinstagramuser",
                    "display_name": "Mock Instagram User",
                    "account_type": "personal"
                }
            elif platform == "facebook":
                return {
                    "account_id": "mock_facebook_user_id",
                    "username": "Mock Facebook User",
                    "display_name": "Mock Facebook User",
                    "email": "mock@facebook.com"
                }
            elif platform == "threads":
                return {
                    "account_id": "mock_threads_user_id",
                    "username": "mockthreadsuser",
                    "display_name": "Mock Threads User",
                    "account_type": "personal"
                }
        
        config = self.platform_configs[platform]
        
        try:
            async with httpx.AsyncClient() as client:
                if platform == "instagram":
                    # Instagram Basic Display API
                    response = await client.get(
                        f"{config['graph_url']}/me",
                        params={
                            "fields": "id,username,account_type",
                            "access_token": access_token
                        },
                        timeout=30.0
                    )
                elif platform == "facebook":
                    # Facebook Graph API
                    response = await client.get(
                        f"{config['graph_url']}/me",
                        params={
                            "fields": "id,name,email",
                            "access_token": access_token
                        },
                        timeout=30.0
                    )
                
                if response.status_code != 200:
                    logger.error(f"Profile fetch failed for {platform}: {response.status_code} - {response.text}")
                    raise Exception(f"Profile fetch failed: {response.status_code}")
                
                profile_data = response.json()
                
                # Format profile data consistently
                if platform == "instagram":
                    return {
                        "account_id": profile_data.get("id"),
                        "username": profile_data.get("username"),
                        "display_name": profile_data.get("username"),
                        "account_type": profile_data.get("account_type", "personal")
                    }
                elif platform == "facebook":
                    return {
                        "account_id": profile_data.get("id"),
                        "username": profile_data.get("name"),
                        "display_name": profile_data.get("name"),
                        "email": profile_data.get("email")
                    }
                
        except Exception as e:
            logger.error(f"Error fetching user profile: {e}")
            raise
    
    async def get_pages(self, access_token: str) -> list:
        """Get Facebook pages for the user"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://graph.facebook.com/v18.0/me/accounts",
                    params={
                        "access_token": access_token,
                        "fields": "id,name,access_token,category"
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Pages fetch failed: {response.status_code} - {response.text}")
                    return []
                
                data = response.json()
                return data.get("data", [])
                
        except Exception as e:
            logger.error(f"Error fetching pages: {e}")
            return []
    
    def validate_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Validate Meta webhook"""
        if mode == "subscribe" and token == settings.META_WEBHOOK_VERIFY_TOKEN:
            return challenge
        return None
    
    async def refresh_token(self, platform: str, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        if platform not in self.platform_configs:
            raise ValueError(f"Unsupported platform: {platform}")
        
        config = self.platform_configs[platform]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    config["token_url"],
                    data={
                        "client_id": self.meta_app_id,
                        "client_secret": self.meta_app_secret,
                        "grant_type": "fb_exchange_token",
                        "fb_exchange_token": refresh_token
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Token refresh failed for {platform}: {response.status_code} - {response.text}")
                    raise Exception(f"Token refresh failed: {response.status_code}")
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise

# Global instance
meta_oauth_service = MetaOAuthService()
