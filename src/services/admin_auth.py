#!/usr/bin/env python3
"""
Admin Authentication Service for Kolekt
Handles secure admin authentication and session management
"""

import logging
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from supabase import create_client, Client
from src.core.config import settings

logger = logging.getLogger(__name__)


class AdminAuthService:
    """Secure admin authentication service"""
    
    def __init__(self):
        self.supabase_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.admin_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Admin credentials (should be moved to environment variables)
        self.admin_credentials = {
            "info@marteklabs.com": {
                "password_hash": self._hash_password("kolectio123"),
                "name": "Admin User",
                "role": "admin"
            }
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return self._hash_password(password) == password_hash
    
    def _generate_session_token(self) -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(32)
    
    def authenticate_admin(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate admin user"""
        try:
            if email not in self.admin_credentials:
                logger.warning(f"Failed admin login attempt for unknown email: {email}")
                return None
            
            admin_data = self.admin_credentials[email]
            
            if not self._verify_password(password, admin_data["password_hash"]):
                logger.warning(f"Failed admin login attempt for email: {email}")
                return None
            
            # Generate session token
            session_token = self._generate_session_token()
            session_data = {
                "email": email,
                "name": admin_data["name"],
                "role": admin_data["role"],
                "created_at": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc) + timedelta(hours=24)
            }
            
            # Store session
            self.admin_sessions[session_token] = session_data
            
            logger.info(f"Successful admin login for: {email}")
            
            return {
                "success": True,
                "user": {
                    "id": "admin-user-id",
                    "email": email,
                    "name": admin_data["name"],
                    "role": admin_data["role"]
                },
                "access_token": session_token,
                "token_type": "bearer",
                "expires_in": 86400  # 24 hours
            }
            
        except Exception as e:
            logger.error(f"Admin authentication error: {e}")
            return None
    
    def verify_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Verify admin session token"""
        try:
            if session_token not in self.admin_sessions:
                return None
            
            session_data = self.admin_sessions[session_token]
            
            # Check if session has expired
            if datetime.now(timezone.utc) > session_data["expires_at"]:
                # Remove expired session
                del self.admin_sessions[session_token]
                return None
            
            return session_data
            
        except Exception as e:
            logger.error(f"Session verification error: {e}")
            return None
    
    def logout_admin(self, session_token: str) -> bool:
        """Logout admin user"""
        try:
            if session_token in self.admin_sessions:
                del self.admin_sessions[session_token]
                logger.info("Admin session terminated")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Admin logout error: {e}")
            return False
    
    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active admin sessions"""
        return self.admin_sessions.copy()
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            current_time = datetime.now(timezone.utc)
            expired_tokens = [
                token for token, session in self.admin_sessions.items()
                if current_time > session["expires_at"]
            ]
            
            for token in expired_tokens:
                del self.admin_sessions[token]
            
            if expired_tokens:
                logger.info(f"Cleaned up {len(expired_tokens)} expired admin sessions")
                
        except Exception as e:
            logger.error(f"Session cleanup error: {e}")


# Global admin auth service instance
admin_auth_service = AdminAuthService()
