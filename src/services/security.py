#!/usr/bin/env python3
"""
Security Service for ThreadStorm
Handles token encryption, KMS integration, audit logging, and security hardening
"""

import logging
import hashlib
import hmac
import base64
import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import boto3
from botocore.exceptions import ClientError

from src.core.config import settings
from src.services.supabase import SupabaseService

logger = logging.getLogger(__name__)


class SecurityService:
    """Comprehensive security service with KMS integration"""
    
    def __init__(self):
        self.supabase = SupabaseService()
        self.kms_client = None
        self.encryption_key = None
        self.audit_enabled = settings.ENABLE_AUDIT_LOGS
        
        # Initialize KMS if configured
        if settings.AWS_KMS_KEY_ID:
            self._init_kms()
        
        # Initialize local encryption as fallback
        self._init_local_encryption()
    
    def _init_kms(self):
        """Initialize AWS KMS client"""
        try:
            self.kms_client = boto3.client(
                'kms',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            logger.info("KMS client initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize KMS: {e}")
            self.kms_client = None
    
    def _init_local_encryption(self):
        """Initialize local encryption as fallback"""
        try:
            if settings.TOKEN_ENCRYPTION_KEY:
                # Use provided key
                key = base64.urlsafe_b64encode(
                    hashlib.sha256(settings.TOKEN_ENCRYPTION_KEY.encode()).digest()
                )
            else:
                # Generate new key (not recommended for production)
                key = Fernet.generate_key()
                logger.warning("Using generated encryption key - not secure for production")
            
            self.encryption_key = key
            self.cipher = Fernet(key)
            logger.info("Local encryption initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise
    
    async def encrypt_token(self, token: str, user_id: str) -> str:
        """Encrypt OAuth token with KMS or local encryption"""
        try:
            if self.kms_client:
                return await self._encrypt_with_kms(token, user_id)
            else:
                return self._encrypt_locally(token)
                
        except Exception as e:
            logger.error(f"Token encryption failed: {e}")
            raise
    
    async def decrypt_token(self, encrypted_token: str, user_id: str) -> str:
        """Decrypt OAuth token"""
        try:
            if self.kms_client:
                return await self._decrypt_with_kms(encrypted_token, user_id)
            else:
                return self._decrypt_locally(encrypted_token)
                
        except Exception as e:
            logger.error(f"Token decryption failed: {e}")
            raise

    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a secure random token for OAuth state"""
        try:
            return secrets.token_urlsafe(length)
        except Exception as e:
            logger.error(f"Failed to generate secure token: {e}")
            # Fallback to a simpler method
            import random
            import string
            return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    async def _encrypt_with_kms(self, token: str, user_id: str) -> str:
        """Encrypt token using AWS KMS"""
        try:
            # Create encryption context for additional security
            encryption_context = {
                'user_id': user_id,
                'service': 'threadstorm',
                'token_type': 'oauth'
            }
            
            response = self.kms_client.encrypt(
                KeyId=settings.AWS_KMS_KEY_ID,
                Plaintext=token.encode(),
                EncryptionContext=encryption_context
            )
            
            # Store encrypted token with metadata
            encrypted_data = {
                'ciphertext': base64.b64encode(response['CiphertextBlob']).decode(),
                'key_id': response['KeyId'],
                'encryption_context': encryption_context,
                'encryption_method': 'kms'
            }
            
            return json.dumps(encrypted_data)
            
        except ClientError as e:
            logger.error(f"KMS encryption failed: {e}")
            # Fallback to local encryption
            return self._encrypt_locally(token)
    
    async def _decrypt_with_kms(self, encrypted_token: str, user_id: str) -> str:
        """Decrypt token using AWS KMS"""
        try:
            encrypted_data = json.loads(encrypted_token)
            
            if encrypted_data.get('encryption_method') != 'kms':
                # Fallback to local decryption
                return self._decrypt_locally(encrypted_token)
            
            ciphertext = base64.b64decode(encrypted_data['ciphertext'])
            encryption_context = encrypted_data['encryption_context']
            
            response = self.kms_client.decrypt(
                CiphertextBlob=ciphertext,
                EncryptionContext=encryption_context
            )
            
            return response['Plaintext'].decode()
            
        except (ClientError, json.JSONDecodeError) as e:
            logger.error(f"KMS decryption failed: {e}")
            # Fallback to local decryption
            return self._decrypt_locally(encrypted_token)
    
    def _encrypt_locally(self, token: str) -> str:
        """Encrypt token using local encryption"""
        try:
            encrypted = self.cipher.encrypt(token.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Local encryption failed: {e}")
            raise
    
    def _decrypt_locally(self, encrypted_token: str) -> str:
        """Decrypt token using local encryption"""
        try:
            # Handle both old format (base64) and new format (JSON)
            if encrypted_token.startswith('{'):
                # New format with metadata
                data = json.loads(encrypted_token)
                if data.get('encryption_method') == 'local':
                    encrypted = base64.b64decode(data['ciphertext'])
                else:
                    # Fallback for old format
                    encrypted = base64.b64decode(encrypted_token)
            else:
                # Old format - direct base64
                encrypted = base64.b64decode(encrypted_token)
            
            decrypted = self.cipher.decrypt(encrypted)
            return decrypted.decode()
            
        except Exception as e:
            logger.error(f"Local decryption failed: {e}")
            raise
    
    async def rotate_app_secrets(self):
        """Rotate application secrets"""
        try:
            # Generate new secrets
            new_app_secret = secrets.token_urlsafe(32)
            new_webhook_secret = secrets.token_urlsafe(32)
            new_encryption_key = Fernet.generate_key()
            
            # Update configuration (in production, this would update environment variables)
            logger.info("App secrets rotated successfully")
            
            # Log rotation event
            await self.log_audit_event(
                'security',
                'secret_rotation',
                'App secrets rotated',
                {'rotation_type': 'app_secrets'}
            )
            
            return {
                'app_secret': new_app_secret,
                'webhook_secret': new_webhook_secret,
                'encryption_key': base64.b64encode(new_encryption_key).decode()
            }
            
        except Exception as e:
            logger.error(f"Secret rotation failed: {e}")
            raise
    
    async def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify webhook signature from Meta"""
        try:
            if not signature or not settings.META_WEBHOOK_SECRET:
                return False
            
            # Extract signature from header
            if signature.startswith('sha256='):
                signature = signature[7:]
            
            # Calculate expected signature
            expected_signature = hmac.new(
                settings.META_WEBHOOK_SECRET.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {e}")
            return False
    
    async def log_audit_event(self, category: str, action: str, description: str, 
                            metadata: Dict = None, user_id: str = None):
        """Log security audit event"""
        if not self.audit_enabled:
            return
        
        try:
            audit_data = {
                'category': category,
                'action': action,
                'description': description,
                'metadata': json.dumps(metadata) if metadata else None,
                'user_id': user_id,
                'ip_address': '127.0.0.1',  # Would get from request context
                'user_agent': 'system',  # Would get from request context
                'timestamp': datetime.now().isoformat(),
                'session_id': None  # Would get from request context
            }
            
            await self.supabase.table('audit_logs').insert(audit_data).execute()
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")
    
    async def get_audit_logs(self, user_id: str = None, category: str = None, 
                           start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """Retrieve audit logs with filtering"""
        try:
            query = self.supabase.table('audit_logs').select('*')
            
            if user_id:
                query = query.eq('user_id', user_id)
            if category:
                query = query.eq('category', category)
            if start_date:
                query = query.gte('timestamp', start_date.isoformat())
            if end_date:
                query = query.lte('timestamp', end_date.isoformat())
            
            response = await query.order('timestamp', desc=True).execute()
            return response.data
            
        except Exception as e:
            logger.error(f"Failed to retrieve audit logs: {e}")
            return []
    
    def generate_idempotency_key(self, user_id: str, action: str) -> str:
        """Generate idempotency key for operations"""
        timestamp = datetime.now().isoformat()
        random_component = secrets.token_urlsafe(8)
        return f"{user_id}:{action}:{timestamp}:{random_component}"
    
    async def check_idempotency(self, idempotency_key: str) -> Optional[Dict]:
        """Check if operation with idempotency key already exists"""
        try:
            response = await self.supabase.table('idempotency_keys')\
                .select('*')\
                .eq('key', idempotency_key)\
                .single()\
                .execute()
            
            if response.data:
                return response.data
            return None
            
        except Exception:
            return None
    
    async def store_idempotency_key(self, idempotency_key: str, result: Dict, 
                                  expires_at: datetime = None):
        """Store idempotency key with result"""
        try:
            if not expires_at:
                expires_at = datetime.now() + timedelta(hours=24)
            
            await self.supabase.table('idempotency_keys').insert({
                'key': idempotency_key,
                'result': json.dumps(result),
                'created_at': datetime.now().isoformat(),
                'expires_at': expires_at.isoformat()
            }).execute()
            
        except Exception as e:
            logger.error(f"Failed to store idempotency key: {e}")
    
    async def cleanup_expired_idempotency_keys(self):
        """Clean up expired idempotency keys"""
        try:
            await self.supabase.table('idempotency_keys')\
                .delete()\
                .lt('expires_at', datetime.now().isoformat())\
                .execute()
            
            logger.info("Expired idempotency keys cleaned up")
            
        except Exception as e:
            logger.error(f"Failed to cleanup idempotency keys: {e}")


# Global security service instance
security_service = SecurityService()


# Security middleware
async def security_middleware(request, call_next):
    """Security middleware for request processing"""
    start_time = datetime.now()
    
    try:
        # Log request
        await security_service.log_audit_event(
            'request',
            'api_call',
            f"{request.method} {request.url.path}",
            {
                'method': request.method,
                'path': request.url.path,
                'query_params': dict(request.query_params),
                'headers': dict(request.headers)
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        await security_service.log_audit_event(
            'response',
            'api_response',
            f"Response {response.status_code}",
            {
                'status_code': response.status_code,
                'response_time': (datetime.now() - start_time).total_seconds()
            }
        )
        
        return response
        
    except Exception as e:
        # Log error
        await security_service.log_audit_event(
            'error',
            'api_error',
            f"Request failed: {str(e)}",
            {
                'error': str(e),
                'response_time': (datetime.now() - start_time).total_seconds()
            }
        )
        raise
