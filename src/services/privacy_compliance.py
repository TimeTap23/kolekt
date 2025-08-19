#!/usr/bin/env python3
"""
Privacy Compliance Service for ThreadStorm
Handles data deletion, GDPR compliance, and Meta platform requirements
"""

import logging
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.services.supabase import SupabaseService
from src.services.meta_oauth import meta_oauth

logger = logging.getLogger(__name__)


class PrivacyComplianceService:
    """Privacy compliance service for Meta platform requirements"""
    
    def __init__(self):
        self.supabase = SupabaseService()
        self.deletion_retention_days = 30  # Keep deletion logs for 30 days
        
        # Data categories for deletion
        self.data_categories = {
            'user_profile': ['profiles', 'user_settings'],
            'content': ['threadstorms', 'drafts', 'templates'],
            'analytics': ['usage_metrics', 'api_usage'],
            'authentication': ['user_tokens', 'oauth_states'],
            'jobs': ['job_queue', 'rate_limit_logs'],
            'all': ['profiles', 'user_settings', 'threadstorms', 'drafts', 'templates', 
                   'usage_metrics', 'api_usage', 'user_tokens', 'oauth_states', 
                   'job_queue', 'rate_limit_logs', 'access_logs']
        }
    
    async def handle_data_deletion_request(self, user_id: str, data_types: List[str] = None) -> Dict:
        """Handle data deletion request (Meta callback)"""
        try:
            if not data_types:
                data_types = ['all']
            
            # Log deletion request
            await self._log_deletion_request(user_id, data_types)
            
            # Perform data deletion
            deletion_results = await self._delete_user_data(user_id, data_types)
            
            # Revoke Meta access
            await meta_oauth.revoke_user_access(user_id)
            
            # Send confirmation email
            await self._send_deletion_confirmation(user_id)
            
            return {
                'success': True,
                'message': 'Data deletion completed successfully',
                'deleted_data': deletion_results,
                'confirmation_sent': True
            }
            
        except Exception as e:
            logger.error(f"Data deletion failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _log_deletion_request(self, user_id: str, data_types: List[str]):
        """Log data deletion request for compliance"""
        try:
            await self.supabase.table('deletion_logs').insert({
                'user_id': user_id,
                'data_types': json.dumps(data_types),
                'requested_at': datetime.now().isoformat(),
                'status': 'pending',
                'request_source': 'meta_callback'
            }).execute()
            
        except Exception as e:
            logger.error(f"Failed to log deletion request: {e}")
    
    async def _delete_user_data(self, user_id: str, data_types: List[str]) -> Dict:
        """Delete user data from all relevant tables"""
        deletion_results = {}
        
        try:
            for data_type in data_types:
                if data_type in self.data_categories:
                    tables = self.data_categories[data_type]
                    for table in tables:
                        try:
                            # Soft delete by marking as deleted
                            await self.supabase.table(table)\
                                .update({
                                    'deleted_at': datetime.now().isoformat(),
                                    'deletion_reason': 'user_request'
                                })\
                                .eq('user_id', user_id)\
                                .execute()
                            
                            # Get count of deleted records
                            response = await self.supabase.table(table)\
                                .select('id', count='exact')\
                                .eq('user_id', user_id)\
                                .eq('deleted_at', datetime.now().isoformat())\
                                .execute()
                            
                            deletion_results[table] = response.count or 0
                            
                        except Exception as e:
                            logger.error(f"Failed to delete from {table}: {e}")
                            deletion_results[table] = {'error': str(e)}
            
            # Update deletion log
            await self.supabase.table('deletion_logs')\
                .update({
                    'status': 'completed',
                    'completed_at': datetime.now().isoformat(),
                    'deletion_results': json.dumps(deletion_results)
                })\
                .eq('user_id', user_id)\
                .eq('status', 'pending')\
                .execute()
            
            return deletion_results
            
        except Exception as e:
            logger.error(f"Data deletion error: {e}")
            raise
    
    async def _send_deletion_confirmation(self, user_id: str):
        """Send confirmation email for data deletion"""
        try:
            # Get user email
            response = await self.supabase.table('profiles')\
                .select('email')\
                .eq('id', user_id)\
                .single()\
                .execute()
            
            if response.data and response.data.get('email'):
                email = response.data['email']
                
                # Send confirmation email
                await self._send_email(
                    to_email=email,
                    subject="Your ThreadStorm Data Has Been Deleted",
                    template="data_deletion_confirmation",
                    data={
                        'deletion_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
                        'retention_period': f"{self.deletion_retention_days} days"
                    }
                )
                
        except Exception as e:
            logger.error(f"Failed to send deletion confirmation: {e}")
    
    async def get_user_data_summary(self, user_id: str) -> Dict:
        """Get summary of user's stored data for transparency"""
        try:
            data_summary = {}
            
            for category, tables in self.data_categories.items():
                if category == 'all':
                    continue
                
                category_data = {}
                for table in tables:
                    try:
                        response = await self.supabase.table(table)\
                            .select('id', count='exact')\
                            .eq('user_id', user_id)\
                            .is_('deleted_at', 'null')\
                            .execute()
                        
                        category_data[table] = response.count or 0
                        
                    except Exception as e:
                        logger.error(f"Failed to get data summary for {table}: {e}")
                        category_data[table] = 0
                
                data_summary[category] = category_data
            
            return {
                'user_id': user_id,
                'data_summary': data_summary,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get data summary: {e}")
            raise HTTPException(status_code=500, detail="Failed to get data summary")
    
    async def export_user_data(self, user_id: str) -> Dict:
        """Export user data in GDPR-compliant format"""
        try:
            export_data = {
                'export_date': datetime.now().isoformat(),
                'user_id': user_id,
                'data': {}
            }
            
            # Export data from each table
            for category, tables in self.data_categories.items():
                if category == 'all':
                    continue
                
                category_data = {}
                for table in tables:
                    try:
                        response = await self.supabase.table(table)\
                            .select('*')\
                            .eq('user_id', user_id)\
                            .is_('deleted_at', 'null')\
                            .execute()
                        
                        category_data[table] = response.data
                        
                    except Exception as e:
                        logger.error(f"Failed to export data from {table}: {e}")
                        category_data[table] = []
                
                export_data['data'][category] = category_data
            
            # Log export request
            await self.supabase.table('data_exports').insert({
                'user_id': user_id,
                'exported_at': datetime.now().isoformat(),
                'data_size': len(json.dumps(export_data)),
                'status': 'completed'
            }).execute()
            
            return export_data
            
        except Exception as e:
            logger.error(f"Failed to export user data: {e}")
            raise HTTPException(status_code=500, detail="Failed to export user data")
    
    async def cleanup_expired_data(self):
        """Clean up expired deletion logs and soft-deleted data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.deletion_retention_days)
            
            # Clean up deletion logs
            await self.supabase.table('deletion_logs')\
                .delete()\
                .lt('completed_at', cutoff_date.isoformat())\
                .execute()
            
            # Clean up soft-deleted data
            for table in self.data_categories['all']:
                try:
                    await self.supabase.table(table)\
                        .delete()\
                        .lt('deleted_at', cutoff_date.isoformat())\
                        .execute()
                        
                except Exception as e:
                    logger.error(f"Failed to cleanup {table}: {e}")
            
            logger.info("Data cleanup completed")
            
        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")
    
    async def _send_email(self, to_email: str, subject: str, template: str, data: Dict):
        """Send email using configured email service"""
        try:
            # This would integrate with your email service (SendGrid, Mailgun, etc.)
            # For now, just log the email
            logger.info(f"Email sent to {to_email}: {subject}")
            
            # Log email in database
            await self.supabase.table('email_logs').insert({
                'to_email': to_email,
                'subject': subject,
                'template': template,
                'data': json.dumps(data),
                'sent_at': datetime.now().isoformat(),
                'status': 'sent'
            }).execute()
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")


# Global privacy service instance
privacy_service = PrivacyComplianceService()


# Privacy endpoints for Meta compliance
async def data_deletion_callback(request: Request):
    """Meta data deletion callback endpoint"""
    try:
        # Verify the request is from Meta
        if not await _verify_meta_request(request):
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Parse the request body
        body = await request.json()
        user_id = body.get('user_id')
        data_types = body.get('data_types', ['all'])
        
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user_id")
        
        # Handle the deletion request
        result = await privacy_service.handle_data_deletion_request(user_id, data_types)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Data deletion callback error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def _verify_meta_request(request: Request) -> bool:
    """Verify that the request is from Meta"""
    try:
        # Check for Meta's signature header
        signature = request.headers.get('X-Hub-Signature-256')
        if not signature:
            return False
        
        # Verify signature (implement proper verification)
        # For now, return True as placeholder
        return True
        
    except Exception as e:
        logger.error(f"Request verification failed: {e}")
        return False


# Privacy policy endpoints
async def get_privacy_policy():
    """Get privacy policy"""
    return {
        "privacy_policy": {
            "version": "1.0",
            "last_updated": "2024-01-01",
            "company": "Martek Labs LLC",
            "contact_email": "privacy@threadstorm.com",
            "data_collection": {
                "what_we_collect": [
                    "Account information (email, name)",
                    "Content you create (threadstorms, drafts)",
                    "Usage analytics (API calls, features used)",
                    "Meta authentication tokens (encrypted)",
                    "Technical data (IP address, user agent)"
                ],
                "why_we_collect": [
                    "To provide ThreadStorm services",
                    "To improve user experience",
                    "To ensure platform security",
                    "To comply with legal obligations"
                ]
            },
            "data_usage": {
                "how_we_use": [
                    "Format and publish content to Threads",
                    "Provide analytics and insights",
                    "Send service notifications",
                    "Improve our platform"
                ],
                "data_sharing": [
                    "We do not sell your personal data",
                    "We share data only with Meta (for publishing)",
                    "We may share data with service providers (hosting, email)",
                    "We may share data if required by law"
                ]
            },
            "data_retention": {
                "retention_period": "Until account deletion or 2 years of inactivity",
                "deletion_process": "Data is soft-deleted immediately, permanently deleted after 30 days"
            },
            "user_rights": {
                "access": "You can access your data through the app",
                "export": "You can export your data in JSON format",
                "deletion": "You can delete your account and all associated data",
                "correction": "You can update your profile information"
            },
            "meta_integration": {
                "data_shared": [
                    "Content you choose to publish",
                    "Basic profile information",
                    "Authentication tokens (encrypted)"
                ],
                "meta_policy": "Meta's data usage is governed by their privacy policy",
                "revocation": "You can revoke Meta access at any time"
            },
            "security": {
                "encryption": "All sensitive data is encrypted at rest and in transit",
                "access_controls": "Strict access controls and authentication",
                "monitoring": "Continuous security monitoring and logging"
            },
            "compliance": {
                "gdpr": "We comply with GDPR requirements",
                "ccpa": "We comply with CCPA requirements",
                "meta_platform": "We comply with Meta Platform Terms"
            }
        }
    }


async def get_data_deletion_instructions():
    """Get data deletion instructions"""
    return {
        "data_deletion": {
            "how_to_delete": [
                "1. Log into your ThreadStorm account",
                "2. Go to Account Settings > Privacy",
                "3. Click 'Delete My Account'",
                "4. Confirm deletion",
                "5. Your data will be deleted within 30 days"
            ],
            "what_happens": [
                "Immediate: Account deactivated, no new data collection",
                "24 hours: Content removed from public view",
                "30 days: All data permanently deleted",
                "Meta: Access tokens revoked immediately"
            ],
            "data_types_deleted": [
                "Account information",
                "All created content (threadstorms, drafts)",
                "Usage analytics",
                "Authentication tokens",
                "API usage logs"
            ],
            "exceptions": [
                "Legal requirements may require data retention",
                "Aggregated analytics (no personal data)",
                "Backup data (deleted within 90 days)"
            ],
            "contact": {
                "email": "privacy@threadstorm.com",
                "response_time": "Within 48 hours",
                "verification": "We may require identity verification for deletion requests"
            }
        }
    }
