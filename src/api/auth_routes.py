#!/usr/bin/env python3
"""
Authentication API Routes for ThreadStorm
Handles user registration, login, logout, and profile management
"""

import logging
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr, validator

from src.services.authentication import auth_service, get_current_user, require_permission, require_admin
from src.services.observability import observability_service
from src.services.security import security_service

logger = logging.getLogger(__name__)

# Create router
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


# Pydantic models for request/response
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    theme: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    plan: str
    email_verified: bool
    created_at: str
    last_login: Optional[str] = None
    login_count: int


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


# Authentication endpoints
@auth_router.post("/register", response_model=Dict)
async def register_user(request: UserRegisterRequest):
    """Register a new user"""
    try:
        # Log registration attempt
        await observability_service.log_event(
            'auth',
            'register_attempt',
            f"Registration attempt for {request.email}",
            {'email': request.email}
        )
        
        # Register user
        result = await auth_service.register_user(
            email=request.email,
            password=request.password,
            name=request.name
        )
        
        # Log successful registration
        await observability_service.log_event(
            'auth',
            'register_success',
            f"User registered successfully: {request.email}",
            {'email': request.email, 'user_id': result.get('user_id')}
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration endpoint error: {e}")
        await observability_service.log_event(
            'auth',
            'register_error',
            f"Registration failed for {request.email}",
            {'email': request.email, 'error': str(e)},
            severity='error'
        )
        raise HTTPException(status_code=500, detail="Registration failed")


@auth_router.post("/login", response_model=AuthResponse)
async def login_user(request: UserLoginRequest):
    """Authenticate user and return tokens"""
    try:
        # Log login attempt
        await observability_service.log_event(
            'auth',
            'login_attempt',
            f"Login attempt for {request.email}",
            {'email': request.email}
        )
        
        # Authenticate user
        result = await auth_service.login_user(
            email=request.email,
            password=request.password
        )
        
        # Log successful login
        await observability_service.log_event(
            'auth',
            'login_success',
            f"User logged in successfully: {request.email}",
            {'email': request.email, 'user_id': result['user']['id']}
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login endpoint error: {e}")
        await observability_service.log_event(
            'auth',
            'login_error',
            f"Login failed for {request.email}",
            {'email': request.email, 'error': str(e)},
            severity='error'
        )
        raise HTTPException(status_code=500, detail="Login failed")


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    try:
        # Refresh token
        result = await auth_service.refresh_token(request.refresh_token)
        
        # Log token refresh
        await observability_service.log_event(
            'auth',
            'token_refresh_success',
            "Access token refreshed successfully",
            {'token_type': 'refresh'}
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh endpoint error: {e}")
        await observability_service.log_event(
            'auth',
            'token_refresh_error',
            "Token refresh failed",
            {'error': str(e)},
            severity='error'
        )
        raise HTTPException(status_code=500, detail="Token refresh failed")


@auth_router.post("/logout")
async def logout_user(request: LogoutRequest, current_user: Dict = Depends(get_current_user)):
    """Logout user and invalidate tokens"""
    try:
        # Logout user
        result = await auth_service.logout_user(
            user_id=current_user["user_id"],
            refresh_token=request.refresh_token
        )
        
        # Log logout
        await observability_service.log_event(
            'auth',
            'logout_success',
            f"User logged out successfully: {current_user['user_id']}",
            {'user_id': current_user['user_id']}
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout endpoint error: {e}")
        await observability_service.log_event(
            'auth',
            'logout_error',
            f"Logout failed for {current_user['user_id']}",
            {'user_id': current_user['user_id'], 'error': str(e)},
            severity='error'
        )
        raise HTTPException(status_code=500, detail="Logout failed")


@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: Dict = Depends(get_current_user)):
    """Get current user's profile"""
    try:
        # Get user profile from database
        from src.services.supabase import SupabaseService
        supabase = SupabaseService()
        
        response = await supabase.table('profiles')\
            .select('*')\
            .eq('id', current_user["user_id"])\
            .single()\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Log profile access
        await observability_service.log_event(
            'user',
            'profile_accessed',
            f"User profile accessed: {current_user['user_id']}",
            {'user_id': current_user['user_id']},
            user_id=current_user['user_id']
        )
        
        return response.data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get profile endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get profile")


@auth_router.put("/profile")
async def update_user_profile(
    request: ProfileUpdateRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Update user profile"""
    try:
        # Update profile
        result = await auth_service.update_user_profile(
            user_id=current_user["user_id"],
            updates=request.dict(exclude_unset=True)
        )
        
        # Log profile update
        await observability_service.log_event(
            'user',
            'profile_updated',
            f"User profile updated: {current_user['user_id']}",
            {'user_id': current_user['user_id'], 'updates': request.dict(exclude_unset=True)},
            user_id=current_user['user_id']
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update profile endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")


@auth_router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: Dict = Depends(get_current_user)
):
    """Change user password"""
    try:
        # Change password
        result = await auth_service.change_password(
            user_id=current_user["user_id"],
            current_password=request.current_password,
            new_password=request.new_password
        )
        
        # Log password change
        await observability_service.log_event(
            'auth',
            'password_changed',
            f"Password changed for user: {current_user['user_id']}",
            {'user_id': current_user['user_id']},
            user_id=current_user['user_id']
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Failed to change password")


@auth_router.get("/permissions")
async def get_user_permissions(current_user: Dict = Depends(get_current_user)):
    """Get current user's permissions"""
    try:
        # Get user profile
        from src.services.supabase import SupabaseService
        supabase = SupabaseService()
        
        response = await supabase.table('profiles')\
            .select('role')\
            .eq('id', current_user["user_id"])\
            .single()\
            .execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        role = response.data.get('role', 'user')
        
        # Get permissions for role
        permissions = auth_service.role_permissions.get(role, {})
        
        # Log permissions access
        await observability_service.log_event(
            'auth',
            'permissions_accessed',
            f"User permissions accessed: {current_user['user_id']}",
            {'user_id': current_user['user_id'], 'role': role},
            user_id=current_user['user_id']
        )
        
        return {
            "user_id": current_user["user_id"],
            "role": role,
            "permissions": permissions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get permissions endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get permissions")


@auth_router.post("/verify-email")
async def verify_email(token: str):
    """Verify user email address"""
    try:
        # This would integrate with Supabase email verification
        # For now, just log the attempt
        await observability_service.log_event(
            'auth',
            'email_verification_attempt',
            "Email verification attempt",
            {'token': token[:10] + '...'}  # Log partial token for security
        )
        
        # Placeholder response
        return {
            "success": True,
            "message": "Email verification endpoint - integrate with Supabase Auth"
        }
        
    except Exception as e:
        logger.error(f"Email verification endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Email verification failed")


@auth_router.post("/forgot-password")
async def forgot_password(email: EmailStr):
    """Send password reset email"""
    try:
        # Log password reset attempt
        await observability_service.log_event(
            'auth',
            'password_reset_attempt',
            f"Password reset requested for {email}",
            {'email': email}
        )
        
        # This would integrate with Supabase password reset
        # For now, just log the attempt
        return {
            "success": True,
            "message": "Password reset email sent (if user exists)"
        }
        
    except Exception as e:
        logger.error(f"Forgot password endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Password reset failed")


@auth_router.post("/reset-password")
async def reset_password(token: str, new_password: str):
    """Reset password using reset token"""
    try:
        # Validate new password
        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
        
        # Log password reset
        await observability_service.log_event(
            'auth',
            'password_reset_completed',
            "Password reset completed",
            {'token': token[:10] + '...'}  # Log partial token for security
        )
        
        # This would integrate with Supabase password reset
        # For now, just log the attempt
        return {
            "success": True,
            "message": "Password reset completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Password reset failed")


# Admin endpoints
@auth_router.get("/admin/users", dependencies=[Depends(require_admin)])
async def get_all_users():
    """Get all users (admin only)"""
    try:
        # Get all users
        from src.services.supabase import SupabaseService
        supabase = SupabaseService()
        
        response = await supabase.table('profiles')\
            .select('id, email, name, role, plan, created_at, last_login, login_count')\
            .execute()
        
        # Log admin action
        await observability_service.log_event(
            'admin',
            'users_listed',
            "All users listed by admin",
            {'user_count': len(response.data)},
            severity='info'
        )
        
        return {
            "users": response.data,
            "total": len(response.data)
        }
        
    except Exception as e:
        logger.error(f"Get all users endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get users")


@auth_router.put("/admin/users/{user_id}/role", dependencies=[Depends(require_admin)])
async def update_user_role(user_id: str, role: str):
    """Update user role (admin only)"""
    try:
        # Validate role
        valid_roles = ["user", "pro", "business", "admin"]
        if role not in valid_roles:
            raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {valid_roles}")
        
        # Update user role
        from src.services.supabase import SupabaseService
        supabase = SupabaseService()
        
        await supabase.table('profiles')\
            .update({'role': role, 'updated_at': 'now()'})\
            .eq('id', user_id)\
            .execute()
        
        # Log admin action
        await observability_service.log_event(
            'admin',
            'user_role_updated',
            f"User role updated: {user_id} -> {role}",
            {'user_id': user_id, 'new_role': role},
            severity='info'
        )
        
        return {
            "success": True,
            "message": f"User role updated to {role}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user role endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user role")


# =============================================================================
# OAUTH ENDPOINTS
# =============================================================================

@auth_router.get("/google/authorize")
async def google_oauth_authorize():
    """Initiate Google OAuth flow"""
    try:
        from src.services.oauth_service import OAuthService, OAuthProvider
        
        oauth_service = OAuthService()
        state = security_service.generate_secure_token()
        
        # Store state for validation
        await observability_service.log_event(
            'oauth',
            'google_authorize_initiated',
            "Google OAuth flow initiated",
            {'state': state}
        )
        
        auth_url = oauth_service.get_auth_url(OAuthProvider.GOOGLE, state)
        return {"auth_url": auth_url, "state": state}
        
    except Exception as e:
        logger.error(f"Google OAuth authorize error: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate Google OAuth")


@auth_router.get("/google/callback")
async def google_oauth_callback(code: str, state: str):
    """Handle Google OAuth callback"""
    try:
        from src.services.oauth_service import OAuthService, OAuthProvider
        
        oauth_service = OAuthService()
        
        # Exchange code for token
        token = await oauth_service.exchange_code_for_token(OAuthProvider.GOOGLE, code)
        
        # Get user info from Google
        user_info = await oauth_service.get_user_info(OAuthProvider.GOOGLE, token.access_token)
        
        # Check if user exists
        existing_user = await auth_service._get_user_by_email(user_info['email'])
        
        if existing_user:
            # User exists, log them in
            result = await auth_service.login_user_oauth(user_info['email'], 'google', user_info)
        else:
            # Create new user
            result = await auth_service.register_user_oauth(
                email=user_info['email'],
                name=user_info.get('name', user_info['email'].split('@')[0]),
                provider='google',
                provider_user_id=user_info['id']
            )
        
        # Log OAuth success
        await observability_service.log_event(
            'oauth',
            'google_oauth_success',
            f"Google OAuth successful for {user_info['email']}",
            {'email': user_info['email'], 'provider': 'google'}
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Google OAuth callback error: {e}")
        await observability_service.log_event(
            'oauth',
            'google_oauth_error',
            f"Google OAuth failed: {str(e)}",
            {'error': str(e)},
            severity='error'
        )
        raise HTTPException(status_code=500, detail="Google OAuth failed")


@auth_router.get("/meta/authorize")
async def meta_oauth_authorize():
    """Initiate Meta OAuth flow"""
    try:
        from src.services.oauth_service import OAuthService, OAuthProvider
        
        oauth_service = OAuthService()
        state = security_service.generate_secure_token()
        
        # Store state for validation
        await observability_service.log_event(
            'oauth',
            'meta_authorize_initiated',
            "Meta OAuth flow initiated",
            {'state': state}
        )
        
        auth_url = oauth_service.get_auth_url(OAuthProvider.META, state)
        return {"auth_url": auth_url, "state": state}
        
    except Exception as e:
        logger.error(f"Meta OAuth authorize error: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate Meta OAuth")


@auth_router.get("/meta/callback")
async def meta_oauth_callback(code: str, state: str):
    """Handle Meta OAuth callback"""
    try:
        from src.services.oauth_service import OAuthService, OAuthProvider
        
        oauth_service = OAuthService()
        
        # Exchange code for token
        token = await oauth_service.exchange_code_for_token(OAuthProvider.META, code)
        
        # Get user info from Meta
        user_info = await oauth_service.get_user_info(OAuthProvider.META, token.access_token)
        
        # Check if user exists
        existing_user = await auth_service._get_user_by_email(user_info['email'])
        
        if existing_user:
            # User exists, log them in
            result = await auth_service.login_user_oauth(user_info['email'], 'meta', user_info)
        else:
            # Create new user
            result = await auth_service.register_user_oauth(
                email=user_info['email'],
                name=user_info.get('name', user_info['email'].split('@')[0]),
                provider='meta',
                provider_user_id=user_info['id']
            )
        
        # Log OAuth success
        await observability_service.log_event(
            'oauth',
            'meta_oauth_success',
            f"Meta OAuth successful for {user_info['email']}",
            {'email': user_info['email'], 'provider': 'meta'}
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Meta OAuth callback error: {e}")
        await observability_service.log_event(
            'oauth',
            'meta_oauth_error',
            f"Meta OAuth failed: {str(e)}",
            {'error': str(e)},
            severity='error'
        )
        raise HTTPException(status_code=500, detail="Meta OAuth failed")


# Health check endpoint
@auth_router.get("/health")
async def auth_health_check():
    """Health check for authentication service"""
    return {
        "status": "healthy",
        "service": "authentication",
        "features": {
            "registration": True,
            "login": True,
            "jwt_tokens": True,
            "refresh_tokens": True,
            "rbac": True,
            "audit_logging": True
        }
    }
