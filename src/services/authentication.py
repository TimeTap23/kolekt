#!/usr/bin/env python3
"""
Authentication Service for ThreadStorm
Handles user authentication, authorization, and session management
"""

import logging
import jwt
from jwt import InvalidTokenError, ExpiredSignatureError
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import uuid

from src.core.config import settings
from src.services.supabase import SupabaseService
from src.services.security import security_service
from src.services.observability import observability_service

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()


class AuthenticationService:
    """Comprehensive authentication service with Supabase integration"""
    
    def __init__(self):
        self.supabase = SupabaseService()
        self.jwt_secret = settings.SECRET_KEY
        self.jwt_algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        
        # Role-based permissions
        self.role_permissions = {
            "user": {
                "threadstorms": ["read", "write_own", "delete_own"],
                "templates": ["read", "write_own"],
                "analytics": ["read_own"],
                "api_usage": ["read_own"]
            },
            "pro": {
                "threadstorms": ["read", "write_own", "delete_own", "bulk_operations"],
                "templates": ["read", "write_own", "share"],
                "analytics": ["read_own", "export"],
                "api_usage": ["read_own", "advanced_metrics"]
            },
            "business": {
                "threadstorms": ["read", "write_own", "delete_own", "bulk_operations", "team_access"],
                "templates": ["read", "write_own", "share", "team_templates"],
                "analytics": ["read_own", "export", "team_analytics"],
                "api_usage": ["read_own", "advanced_metrics", "team_usage"]
            },
            "admin": {
                "threadstorms": ["read", "write", "delete", "manage_all"],
                "templates": ["read", "write", "delete", "manage_all"],
                "analytics": ["read", "write", "delete", "manage_all"],
                "api_usage": ["read", "write", "delete", "manage_all"],
                "users": ["read", "write", "delete", "manage_all"],
                "system": ["read", "write", "delete", "manage_all"]
            }
        }
    
    async def register_user(self, email: str, password: str, name: str = None) -> Dict:
        """Register a new user with Supabase Auth"""
        try:
            # Validate input
            if not email or not password:
                raise HTTPException(status_code=400, detail="Email and password are required")
            
            if len(password) < 8:
                raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
            
            # Check if user already exists
            existing_user = await self._get_user_by_email(email)
            if existing_user:
                raise HTTPException(status_code=400, detail="User already exists")
            
            # Create user in Supabase Auth
            auth_response = await self.supabase.sign_up(email, password, {"name": name or email.split('@')[0]})
            
            if auth_response.get("success") and auth_response.get("user"):
                user_id = auth_response["user"].id
                
                # Create user profile
                profile_data = {
                    "id": user_id,
                    "email": email,
                    "name": name or email.split('@')[0],
                    "role": "user",
                    "plan": "free",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "is_verified": auth_response["user"].email_confirmed_at is not None,
                    "last_login": None,
                    "login_count": 0
                }
                
                await self.supabase.client.table('profiles').insert(profile_data).execute()
            
                # Create user settings
                settings_data = {
                    "id": user_id,  # Use id instead of user_id for user_settings
                    "notifications_enabled": True,
                    "theme": "cyberpunk",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                await self.supabase.client.table('user_settings').insert(settings_data).execute()
                
                # Create default permissions for new user
                try:
                    await self._create_default_permissions(user_id)
                except Exception as e:
                    logger.warning(f"Could not create default permissions: {e}")
                
                # Log registration
                try:
                    await observability_service.log_event(
                        'auth',
                        'user_registered',
                        f"New user registered: {email}",
                        {'user_id': user_id, 'email': email},
                        user_id=user_id
                    )
                except Exception as e:
                    logger.warning(f"Could not log registration event: {e}")
                
                # Send welcome email (placeholder)
                try:
                    await self._send_welcome_email(email, name)
                except Exception as e:
                    logger.warning(f"Could not send welcome email: {e}")
                
                return {
                    "success": True,
                    "user_id": user_id,
                    "email": email,
                    "message": "User registered successfully. Please check your email to verify your account."
                }
            else:
                error_msg = auth_response.get("error", "Failed to create user")
                raise HTTPException(status_code=400, detail=error_msg)
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"User registration failed: {e}")
            raise HTTPException(status_code=500, detail="Registration failed")
    
    async def login_user(self, email: str, password: str) -> Dict:
        """Authenticate user and return access tokens"""
        try:
            # Authenticate with Supabase
            auth_response = await self.supabase.sign_in(email, password)
            
            if auth_response.get("success") and auth_response.get("user"):
                user_id = auth_response["user"].id
                
                # Get user profile
                profile = await self._get_user_profile(user_id)
                if not profile:
                    raise HTTPException(status_code=404, detail="User profile not found")
                
                # Update last login
                await self._update_last_login(user_id)
                
                # Generate JWT tokens
                access_token = self._create_access_token(
                    data={"sub": user_id, "email": email, "role": profile.get('role', 'user')}
                )
                refresh_token = self._create_refresh_token(
                    data={"sub": user_id}
                )
                
                # Store refresh token securely
                await self._store_refresh_token(user_id, refresh_token)
                
                # Log successful login
                await observability_service.log_event(
                    'auth',
                    'user_login',
                    f"User logged in: {email}",
                    {'user_id': user_id, 'email': email, 'role': profile.get('role')},
                    user_id=user_id
                )
                
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "expires_in": self.access_token_expire_minutes * 60,
                    "user": {
                        "id": user_id,
                        "email": email,
                        "name": profile.get('name'),
                        "role": profile.get('role', 'user'),
                        "plan": profile.get('plan', 'free'),
                        "email_verified": profile.get('email_verified', False)
                    }
                }
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"User login failed: {e}")
            raise HTTPException(status_code=500, detail="Login failed")
    
    async def refresh_token(self, refresh_token: str) -> Dict:
        """Refresh access token using refresh token"""
        try:
            # Verify refresh token
            payload = jwt.decode(refresh_token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            
            # Check if refresh token exists in database
            stored_token = await self._get_refresh_token(user_id, refresh_token)
            if not stored_token:
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            
            # Get user profile
            profile = await self._get_user_profile(user_id)
            if not profile:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Generate new access token
            access_token = self._create_access_token(
                data={"sub": user_id, "email": profile.get('email'), "role": profile.get('role', 'user')}
            )
            
            # Log token refresh
            await observability_service.log_event(
                'auth',
                'token_refreshed',
                f"Access token refreshed for user: {user_id}",
                {'user_id': user_id},
                user_id=user_id
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60
            }
            
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token expired")
        except InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    async def logout_user(self, user_id: str, refresh_token: str = None) -> Dict:
        """Logout user and invalidate tokens"""
        try:
            # Invalidate refresh token if provided
            if refresh_token:
                await self._invalidate_refresh_token(user_id, refresh_token)
            
            # Log logout
            await observability_service.log_event(
                'auth',
                'user_logout',
                f"User logged out: {user_id}",
                {'user_id': user_id},
                user_id=user_id
            )
            
            return {"success": True, "message": "Logged out successfully"}
            
        except Exception as e:
            logger.error(f"User logout failed: {e}")
            raise HTTPException(status_code=500, detail="Logout failed")
    
    async def verify_token(self, token: str) -> Dict:
        """Verify JWT token and return user info"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            # Get user profile
            profile = await self._get_user_profile(user_id)
            if not profile:
                raise HTTPException(status_code=404, detail="User not found")
            
            return {
                "user_id": user_id,
                "email": profile.get('email'),
                "role": profile.get('role', 'user'),
                "plan": profile.get('plan', 'free')
            }
            
        except ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """Check if user has permission for specific resource and action"""
        try:
            # Get user profile
            profile = await self._get_user_profile(user_id)
            if not profile:
                return False
            
            role = profile.get('role', 'user')
            
            # Check if role has permission
            role_perms = self.role_permissions.get(role, {})
            resource_perms = role_perms.get(resource, [])
            
            # Admin has all permissions
            if role == 'admin':
                return True
            
            # Check specific permission
            return action in resource_perms
            
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return False
    
    async def update_user_profile(self, user_id: str, updates: Dict) -> Dict:
        """Update user profile"""
        try:
            # Validate updates
            allowed_fields = ['name', 'timezone', 'language', 'theme']
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
            
            if not filtered_updates:
                raise HTTPException(status_code=400, detail="No valid fields to update")
            
            filtered_updates['updated_at'] = datetime.now().isoformat()
            
            # Update profile
            self.supabase.client.table('profiles')\
                .update(filtered_updates)\
                .eq('id', user_id)\
                .execute()
            
            # Log profile update
            await observability_service.log_event(
                'user',
                'profile_updated',
                f"User profile updated: {user_id}",
                {'user_id': user_id, 'updates': filtered_updates},
                user_id=user_id
            )
            
            return {"success": True, "message": "Profile updated successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Profile update failed: {e}")
            raise HTTPException(status_code=500, detail="Profile update failed")
    
    async def change_password(self, user_id: str, current_password: str, new_password: str) -> Dict:
        """Change user password"""
        try:
            # Validate new password
            if len(new_password) < 8:
                raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
            
            # Get user email
            profile = await self._get_user_profile(user_id)
            if not profile:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Update password in Supabase Auth
            self.supabase.client.auth.update_user({
                "password": new_password
            })
            
            # Log password change
            await observability_service.log_event(
                'auth',
                'password_changed',
                f"Password changed for user: {user_id}",
                {'user_id': user_id},
                user_id=user_id
            )
            
            return {"success": True, "message": "Password changed successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Password change failed: {e}")
            raise HTTPException(status_code=500, detail="Password change failed")
    
    # Helper methods
    def _create_access_token(self, data: Dict) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def _create_refresh_token(self, data: Dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    async def _get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            response = await self.supabase.client.table('profiles')\
                .select('*')\
                .eq('email', email)\
                .single()\
                .execute()
            
            return response.data if response.data else None
            
        except Exception:
            return None
    
    async def _get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile"""
        try:
            response = await self.supabase.client.table('profiles')\
                .select('*')\
                .eq('id', user_id)\
                .single()\
                .execute()
            
            return response.data if response.data else None
            
        except Exception:
            return None
    
    async def _update_last_login(self, user_id: str):
        """Update user's last login time"""
        try:
            await self.supabase.client.table('profiles')\
                .update({
                    'last_login': datetime.now().isoformat(),
                    'login_count': self.supabase.client.raw('login_count + 1')
                })\
                .eq('id', user_id)\
                .execute()
                
        except Exception as e:
            logger.error(f"Failed to update last login: {e}")
    
    async def _store_refresh_token(self, user_id: str, refresh_token: str):
        """Store refresh token securely"""
        try:
            # Hash the refresh token before storing
            token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            
            self.supabase.client.table('refresh_tokens').insert({
                'user_id': user_id,
                'token_hash': token_hash,
                'expires_at': (datetime.now() + timedelta(days=self.refresh_token_expire_days)).isoformat(),
                'created_at': datetime.now().isoformat()
            }).execute()
            
        except Exception as e:
            logger.error(f"Failed to store refresh token: {e}")
    
    async def _get_refresh_token(self, user_id: str, refresh_token: str) -> Optional[Dict]:
        """Get stored refresh token"""
        try:
            token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            
            response = self.supabase.client.table('refresh_tokens')\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('token_hash', token_hash)\
                .eq('expires_at', datetime.now().isoformat(), 'gt')\
                .single()\
                .execute()
            
            return response.data if response.data else None
            
        except Exception:
            return None
    
    async def _invalidate_refresh_token(self, user_id: str, refresh_token: str):
        """Invalidate refresh token"""
        try:
            token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            
            self.supabase.client.table('refresh_tokens')\
                .delete()\
                .eq('user_id', user_id)\
                .eq('token_hash', token_hash)\
                .execute()
                
        except Exception as e:
            logger.error(f"Failed to invalidate refresh token: {e}")
    
    async def _create_default_permissions(self, user_id: str):
        """Create default permissions for new users"""
        try:
            # Default permissions for regular users
            default_permissions = [
                # Profile management
                {"user_id": user_id, "resource": "profile", "action": "read", "granted": True},
                {"user_id": user_id, "resource": "profile", "action": "update", "granted": True},
                
                # Password management
                {"user_id": user_id, "resource": "password", "action": "change", "granted": True},
                
                # Threadstorm creation and management
                {"user_id": user_id, "resource": "threadstorms", "action": "create", "granted": True},
                {"user_id": user_id, "resource": "threadstorms", "action": "read", "granted": True},
                {"user_id": user_id, "resource": "threadstorms", "action": "update", "granted": True},
                {"user_id": user_id, "resource": "threadstorms", "action": "delete", "granted": True},
                
                # Templates
                {"user_id": user_id, "resource": "templates", "action": "read", "granted": True},
                {"user_id": user_id, "resource": "templates", "action": "create", "granted": True},
                {"user_id": user_id, "resource": "templates", "action": "update", "granted": True},
                {"user_id": user_id, "resource": "templates", "action": "delete", "granted": True},
                
                # API usage
                {"user_id": user_id, "resource": "api", "action": "format", "granted": True},
                {"user_id": user_id, "resource": "api", "action": "publish", "granted": True},
                
                # User data
                {"user_id": user_id, "resource": "data", "action": "export", "granted": True},
                {"user_id": user_id, "resource": "data", "action": "delete", "granted": True},
            ]
            
            # Insert permissions into database
            for permission in default_permissions:
                self.supabase.client.table('user_permissions').insert(permission).execute()
            
            logger.info(f"Default permissions created for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to create default permissions for user {user_id}: {e}")
    
    async def _assign_custom_permissions(self, user_id: str, permissions: list):
        """Assign custom permissions to a user (admin function)"""
        try:
            # Clear existing permissions for this user
            self.supabase.client.table('user_permissions').delete().eq('user_id', user_id).execute()
            
            # Insert new permissions
            for permission in permissions:
                permission_data = {
                    "user_id": user_id,
                    "resource": permission["resource"],
                    "action": permission["action"],
                    "granted": permission.get("granted", True)
                }
                self.supabase.client.table('user_permissions').insert(permission_data).execute()
            
            logger.info(f"Custom permissions assigned to user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to assign custom permissions to user {user_id}: {e}")
    
    async def _send_welcome_email(self, email: str, name: str):
        """Send welcome email to new user (placeholder)"""
        try:
            # TODO: Implement actual email sending
            logger.info(f"Welcome email sent to {email}")
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")

    async def login_user_oauth(self, email: str, provider: str, user_info: Dict) -> Dict:
        """Login user via OAuth provider"""
        try:
            # Get user profile
            user_profile = await self._get_user_by_email(email)
            if not user_profile:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Update last login
            await self._update_last_login(user_profile['id'])
            
            # Generate tokens
            access_token = await self._generate_access_token(user_profile['id'])
            refresh_token = await self._generate_refresh_token(user_profile['id'])
            
            # Log OAuth login
            await observability_service.log_event(
                'auth',
                'oauth_login_success',
                f"OAuth login successful: {email} via {provider}",
                {'email': email, 'provider': provider, 'user_id': user_profile['id']}
            )
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60,
                "user": {
                    "id": user_profile['id'],
                    "email": user_profile['email'],
                    "name": user_profile['name'],
                    "role": user_profile['role'],
                    "plan": user_profile['plan'],
                    "email_verified": user_profile.get('email_verified', False),
                    "created_at": user_profile['created_at'],
                    "last_login": user_profile.get('last_login'),
                    "login_count": user_profile.get('login_count', 0)
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"OAuth login error: {e}")
            raise HTTPException(status_code=500, detail="OAuth login failed")

    async def register_user_oauth(self, email: str, name: str, provider: str, provider_user_id: str) -> Dict:
        """Register new user via OAuth provider"""
        try:
            # Check if user already exists
            existing_user = await self._get_user_by_email(email)
            if existing_user:
                # User exists, log them in instead
                return await self.login_user_oauth(email, provider, {"email": email})
            
            # Create user profile
            user_id = str(uuid.uuid4())
            profile_data = {
                "id": user_id,
                "email": email,
                "name": name,
                "role": "user",
                "plan": "free",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "email_verified": True,  # OAuth users are pre-verified
                "last_login": datetime.now().isoformat(),
                "login_count": 1,
                "oauth_provider": provider,
                "oauth_provider_id": provider_user_id
            }
            
            # Insert profile
            await self.supabase.client.table('profiles').insert(profile_data).execute()
            
            # Create user settings
            settings_data = {
                "user_id": user_id,
                "notifications_enabled": True,
                "email_notifications": True,
                "theme": "cyberpunk",
                "language": "en",
                "timezone": "UTC",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            await self.supabase.client.table('user_settings').insert(settings_data).execute()
            
            # Create default permissions
            await self._create_default_permissions(user_id)
            
            # Generate tokens
            access_token = await self._generate_access_token(user_id)
            refresh_token = await self._generate_refresh_token(user_id)
            
            # Log OAuth registration
            await observability_service.log_event(
                'auth',
                'oauth_registration_success',
                f"OAuth registration successful: {email} via {provider}",
                {'email': email, 'provider': provider, 'user_id': user_id}
            )
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60,
                "user": {
                    "id": user_id,
                    "email": email,
                    "name": name,
                    "role": "user",
                    "plan": "free",
                    "email_verified": True,
                    "created_at": profile_data['created_at'],
                    "last_login": profile_data['last_login'],
                    "login_count": 1
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"OAuth registration error: {e}")
            raise HTTPException(status_code=500, detail="OAuth registration failed")


# Global authentication service instance
auth_service = AuthenticationService()


# Dependency for getting current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Get current authenticated user"""
    try:
        token = credentials.credentials

        # Development token fallback: accept tokens like "dev-access-token-<user_id>"
        if token.startswith("dev-access-token-"):
            user_id = token.replace("dev-access-token-", "", 1)
            try:
                profile = await auth_service._get_user_profile(user_id)
                if not profile:
                    raise HTTPException(status_code=401, detail="Invalid authentication")
                return {
                    "user_id": user_id,
                    "email": profile.get('email'),
                    "role": profile.get('role', 'user'),
                    "plan": profile.get('plan', 'free')
                }
            except Exception as e:
                logger.error(f"Dev token profile lookup failed: {e}")
                raise HTTPException(status_code=401, detail="Invalid authentication")

        # Production JWT verification
        user_info = await auth_service.verify_token(token)
        return user_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get current user: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication")


# Looser dependency that accepts Authorization or X-Dev-Access-Token headers
async def get_current_user_loose(request: Request) -> Dict:
    """Get current user, accepting dev tokens from custom headers as fallback."""
    # Try standard Authorization header first
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "", 1)

    # Fallbacks for dev/local flows
    if not token:
        token = request.headers.get("X-Dev-Access-Token") or request.headers.get("X-Access-Token")

    if not token:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    # Dev token support
    if token.startswith("dev-access-token-"):
        user_id = token.replace("dev-access-token-", "", 1)
        profile = await auth_service._get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return {
            "user_id": user_id,
            "email": profile.get('email'),
            "role": profile.get('role', 'user'),
            "plan": profile.get('plan', 'free')
        }

    # Otherwise verify JWT
    return await auth_service.verify_token(token)


# Dependency for checking permissions
async def require_permission(resource: str, action: str):
    """Dependency to require specific permission"""
    async def permission_checker(current_user: Dict = Depends(get_current_user)):
        has_permission = await auth_service.check_permission(
            current_user["user_id"], resource, action
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=403, 
                detail=f"Insufficient permissions for {action} on {resource}"
            )
        
        return current_user
    
    return permission_checker


# Dependency for admin access
async def require_admin(current_user: Dict = Depends(get_current_user)) -> Dict:
    """Require admin role"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
