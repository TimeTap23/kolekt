"""
OAuth Service
Handles social media OAuth integrations
"""

import logging
import asyncio
from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum
import os
import httpx

logger = logging.getLogger(__name__)

class OAuthProvider(Enum):
    GOOGLE = "google"
    META = "meta"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"

@dataclass
class OAuthConfig:
    """OAuth configuration for a provider"""
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: str
    auth_url: str
    token_url: str

@dataclass
class OAuthToken:
    """OAuth token data"""
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    token_type: str = "Bearer"

class OAuthService:
    """Service for handling OAuth integrations"""
    
    def __init__(self):
        self.providers = {
            OAuthProvider.GOOGLE: OAuthConfig(
                client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
                client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
                redirect_uri=os.getenv("GOOGLE_REDIRECT_URI", ""),
                scope="openid email profile",
                auth_url="https://accounts.google.com/o/oauth2/v2/auth",
                token_url="https://oauth2.googleapis.com/token"
            ),
            OAuthProvider.META: OAuthConfig(
                client_id=os.getenv("META_CLIENT_ID", ""),
                client_secret=os.getenv("META_CLIENT_SECRET", ""),
                redirect_uri=os.getenv("META_REDIRECT_URI", ""),
                scope="email public_profile",
                auth_url="https://www.facebook.com/v12.0/dialog/oauth",
                token_url="https://graph.facebook.com/v12.0/oauth/access_token"
            ),
            OAuthProvider.TWITTER: OAuthConfig(
                client_id=os.getenv("TWITTER_CLIENT_ID", ""),
                client_secret=os.getenv("TWITTER_CLIENT_SECRET", ""),
                redirect_uri=os.getenv("TWITTER_REDIRECT_URI", ""),
                scope="tweet.read users.read",
                auth_url="https://twitter.com/i/oauth2/authorize",
                token_url="https://api.twitter.com/2/oauth2/token"
            ),
            OAuthProvider.LINKEDIN: OAuthConfig(
                client_id=os.getenv("LINKEDIN_CLIENT_ID", ""),
                client_secret=os.getenv("LINKEDIN_CLIENT_SECRET", ""),
                redirect_uri=os.getenv("LINKEDIN_REDIRECT_URI", ""),
                scope="r_liteprofile r_emailaddress",
                auth_url="https://www.linkedin.com/oauth/v2/authorization",
                token_url="https://www.linkedin.com/oauth/v2/accessToken"
            )
        }
    
    def get_auth_url(self, provider: OAuthProvider, state: str = None) -> str:
        """Generate OAuth authorization URL"""
        try:
            config = self.providers.get(provider)
            if not config:
                raise ValueError(f"Unsupported OAuth provider: {provider}")
            
            params = {
                'client_id': config.client_id,
                'redirect_uri': config.redirect_uri,
                'scope': config.scope,
                'response_type': 'code'
            }
            
            if state:
                params['state'] = state
            
            # Add provider-specific parameters
            if provider == OAuthProvider.GOOGLE:
                params['access_type'] = 'offline'
                params['prompt'] = 'consent'
            elif provider == OAuthProvider.META:
                params['response_type'] = 'code'
            elif provider == OAuthProvider.TWITTER:
                params['code_challenge_method'] = 'S256'
                params['code_challenge'] = self._generate_code_challenge()
            
            # Build URL with parameters
            param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            return f"{config.auth_url}?{param_string}"
            
        except Exception as e:
            logger.error(f"Error generating auth URL for {provider}: {e}")
            raise
    
    async def exchange_code_for_token(self, provider: OAuthProvider, code: str) -> OAuthToken:
        """Exchange authorization code for access token"""
        try:
            config = self.providers.get(provider)
            if not config:
                raise ValueError(f"Unsupported OAuth provider: {provider}")
            
            # Prepare token request data
            data = {
                'client_id': config.client_id,
                'client_secret': config.client_secret,
                'redirect_uri': config.redirect_uri,
                'code': code,
                'grant_type': 'authorization_code'
            }
            
            # Add provider-specific parameters
            if provider == OAuthProvider.GOOGLE:
                pass  # Google uses standard OAuth2
            elif provider == OAuthProvider.META:
                pass  # Meta uses standard OAuth2
            elif provider == OAuthProvider.TWITTER:
                data['code_verifier'] = self._get_code_verifier()
            
            # Make token request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    config.token_url,
                    data=data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                
                if response.status_code != 200:
                    raise Exception(f"Token exchange failed: {response.text}")
                
                token_data = response.json()
                
                return OAuthToken(
                    access_token=token_data.get('access_token'),
                    refresh_token=token_data.get('refresh_token'),
                    expires_in=token_data.get('expires_in'),
                    token_type=token_data.get('token_type', 'Bearer')
                )
                
        except Exception as e:
            logger.error(f"Error exchanging code for token with {provider}: {e}")
            raise
    
    async def get_user_info(self, provider: OAuthProvider, access_token: str) -> Dict[str, Any]:
        """Get user information from OAuth provider"""
        try:
            user_info_urls = {
                OAuthProvider.GOOGLE: "https://www.googleapis.com/oauth2/v2/userinfo",
                OAuthProvider.META: "https://graph.facebook.com/me?fields=id,name,email",
                OAuthProvider.TWITTER: "https://api.twitter.com/2/users/me",
                OAuthProvider.LINKEDIN: "https://api.linkedin.com/v2/me"
            }
            
            url = user_info_urls.get(provider)
            if not url:
                raise ValueError(f"Unsupported OAuth provider: {provider}")
            
            headers = {'Authorization': f'Bearer {access_token}'}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code != 200:
                    raise Exception(f"Failed to get user info: {response.text}")
                
                user_data = response.json()
                
                # Normalize user data across providers
                return self._normalize_user_data(provider, user_data)
                
        except Exception as e:
            logger.error(f"Error getting user info from {provider}: {e}")
            raise
    
    def _normalize_user_data(self, provider: OAuthProvider, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize user data across different OAuth providers"""
        normalized = {
            'provider': provider.value,
            'provider_user_id': None,
            'email': None,
            'name': None,
            'picture': None
        }
        
        if provider == OAuthProvider.GOOGLE:
            normalized.update({
                'provider_user_id': user_data.get('id'),
                'email': user_data.get('email'),
                'name': user_data.get('name'),
                'picture': user_data.get('picture')
            })
        elif provider == OAuthProvider.META:
            normalized.update({
                'provider_user_id': user_data.get('id'),
                'email': user_data.get('email'),
                'name': user_data.get('name'),
                'picture': f"https://graph.facebook.com/{user_data.get('id')}/picture"
            })
        elif provider == OAuthProvider.TWITTER:
            normalized.update({
                'provider_user_id': user_data.get('data', {}).get('id'),
                'email': None,  # Twitter doesn't provide email by default
                'name': user_data.get('data', {}).get('name'),
                'picture': None  # Would need additional API call
            })
        elif provider == OAuthProvider.LINKEDIN:
            normalized.update({
                'provider_user_id': user_data.get('id'),
                'email': None,  # Would need additional API call
                'name': f"{user_data.get('localizedFirstName', '')} {user_data.get('localizedLastName', '')}".strip(),
                'picture': None  # Would need additional API call
            })
        
        return normalized
    
    def _generate_code_challenge(self) -> str:
        """Generate PKCE code challenge for OAuth2"""
        # This is a simplified implementation
        # In production, you'd use proper PKCE generation
        import secrets
        code_verifier = secrets.token_urlsafe(32)
        # Store code_verifier for later use
        return code_verifier
    
    def _get_code_verifier(self) -> str:
        """Get stored code verifier for PKCE"""
        # In production, you'd retrieve this from storage
        return "stored_code_verifier"
    
    async def refresh_token(self, provider: OAuthProvider, refresh_token: str) -> OAuthToken:
        """Refresh OAuth access token"""
        try:
            config = self.providers.get(provider)
            if not config:
                raise ValueError(f"Unsupported OAuth provider: {provider}")
            
            data = {
                'client_id': config.client_id,
                'client_secret': config.client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    config.token_url,
                    data=data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                
                if response.status_code != 200:
                    raise Exception(f"Token refresh failed: {response.text}")
                
                token_data = response.json()
                
                return OAuthToken(
                    access_token=token_data.get('access_token'),
                    refresh_token=token_data.get('refresh_token', refresh_token),
                    expires_in=token_data.get('expires_in'),
                    token_type=token_data.get('token_type', 'Bearer')
                )
                
        except Exception as e:
            logger.error(f"Error refreshing token with {provider}: {e}")
            raise
    
    async def revoke_token(self, provider: OAuthProvider, access_token: str) -> bool:
        """Revoke OAuth access token"""
        try:
            revoke_urls = {
                OAuthProvider.GOOGLE: "https://oauth2.googleapis.com/revoke",
                OAuthProvider.META: "https://graph.facebook.com/me/permissions",
                OAuthProvider.TWITTER: "https://api.twitter.com/2/oauth2/revoke",
                OAuthProvider.LINKEDIN: "https://www.linkedin.com/oauth/v2/revoke"
            }
            
            url = revoke_urls.get(provider)
            if not url:
                raise ValueError(f"Unsupported OAuth provider: {provider}")
            
            data = {'token': access_token}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=data)
                
                return response.status_code in [200, 204]
                
        except Exception as e:
            logger.error(f"Error revoking token with {provider}: {e}")
            return False
