#!/usr/bin/env python3
"""
Announcements Service
Provides comprehensive announcement management with scheduling, delivery tracking, and analytics
"""

import logging
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import uuid

from src.services.supabase import SupabaseService
from src.services.observability import observability_service
from src.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class DeliveryResult:
    success: bool
    channel: str
    recipient_count: int
    delivered_count: int
    failed_count: int
    error_message: Optional[str] = None


class AnnouncementsService:
    """Comprehensive announcements service with scheduling and analytics"""
    
    def __init__(self):
        self.supabase = SupabaseService()
        self.delivery_queue = asyncio.Queue()
        self.analytics_cache = {}
        
        # Delivery channels configuration
        self.delivery_channels = {
            "email": self._deliver_email,
            "in_app": self._deliver_in_app,
            "push": self._deliver_push,
            "sms": self._deliver_sms
        }
    
    async def create_announcement(
        self, 
        payload: Dict[str, Any], 
        created_by: str
    ) -> Dict[str, Any]:
        """Create a new announcement"""
        try:
            announcement_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            # Determine status based on schedule type
            status = "draft"
            if payload.get("schedule_type") == "immediate":
                status = "scheduled"
            elif payload.get("schedule_type") == "scheduled" and payload.get("scheduled_for"):
                status = "scheduled"
            
            announcement_data = {
                "id": announcement_id,
                "title": payload["title"],
                "content": payload["content"],
                "type": payload["type"],
                "audience": payload["audience"],
                "priority": payload.get("priority", 1),
                "tags": payload.get("tags", []),
                "metadata": payload.get("metadata", {}),
                "status": status,
                "created_at": now,
                "created_by": created_by,
                "scheduled_for": payload.get("scheduled_for"),
                "recurring_pattern": payload.get("recurring_pattern"),
                "notification_channels": payload.get("notification_channels", ["email", "in_app"]),
                "user_segments": payload.get("user_segments", []),
                "recipients_count": 0,
                "delivered_count": 0,
                "opened_count": 0,
                "clicked_count": 0,
                "delivery_stats": {}
            }
            
            # Store in database
            await self.supabase.table('announcements').insert(announcement_data).execute()
            
            await observability_service.log_event(
                "announcement_created",
                user_id=created_by,
                metadata={"announcement_id": announcement_id, "type": payload["type"]}
            )
            
            return announcement_data
            
        except Exception as e:
            logger.error(f"Failed to create announcement: {e}")
            raise
    
    async def get_announcements(
        self,
        status: Optional[str] = None,
        type: Optional[str] = None,
        audience: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get paginated list of announcements with filtering"""
        try:
            query = self.supabase.table('announcements').select('*')
            
            # Apply filters
            if status:
                query = query.eq('status', status)
            if type:
                query = query.eq('type', type)
            if audience:
                query = query.eq('audience', audience)
            
            # Apply pagination
            offset = (page - 1) * limit
            query = query.range(offset, offset + limit - 1)
            query = query.order('created_at', desc=True)
            
            response = await query.execute()
            announcements = response.data
            
            # Get total count for pagination
            count_query = self.supabase.table('announcements').select('id', count='exact')
            if status:
                count_query = count_query.eq('status', status)
            if type:
                count_query = count_query.eq('type', type)
            if audience:
                count_query = count_query.eq('audience', audience)
            
            count_response = await count_query.execute()
            total = count_response.count or 0
            
            return {
                "items": announcements,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                },
                "total": total
            }
            
        except Exception as e:
            logger.error(f"Failed to get announcements: {e}")
            return {"items": [], "pagination": {"page": 1, "limit": limit, "total": 0, "pages": 0}, "total": 0}
    
    async def get_announcement(self, announcement_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific announcement by ID"""
        try:
            response = await self.supabase.table('announcements')\
                .select('*')\
                .eq('id', announcement_id)\
                .single()\
                .execute()
            
            return response.data if response.data else None
            
        except Exception as e:
            logger.error(f"Failed to get announcement {announcement_id}: {e}")
            return None
    
    async def update_announcement(
        self,
        announcement_id: str,
        payload: Dict[str, Any],
        updated_by: str
    ) -> Optional[Dict[str, Any]]:
        """Update an existing announcement"""
        try:
            update_data = {
                "updated_at": datetime.now().isoformat(),
                "updated_by": updated_by
            }
            
            # Add fields that are present in payload
            for field in ["title", "content", "type", "audience", "priority", "tags", "metadata", "scheduled_for", "status"]:
                if field in payload and payload[field] is not None:
                    update_data[field] = payload[field]
            
            response = await self.supabase.table('announcements')\
                .update(update_data)\
                .eq('id', announcement_id)\
                .execute()
            
            if response.data:
                await observability_service.log_event(
                    "announcement_updated",
                    user_id=updated_by,
                    metadata={"announcement_id": announcement_id}
                )
                return response.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to update announcement {announcement_id}: {e}")
            return None
    
    async def delete_announcement(self, announcement_id: str) -> bool:
        """Delete an announcement"""
        try:
            await self.supabase.table('announcements')\
                .delete()\
                .eq('id', announcement_id)\
                .execute()
            
            await observability_service.log_event(
                "announcement_deleted",
                metadata={"announcement_id": announcement_id}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete announcement {announcement_id}: {e}")
            return False
    
    async def deliver_announcement(self, announcement_id: str) -> bool:
        """Deliver an announcement to all recipients"""
        try:
            # Get announcement
            announcement = await self.get_announcement(announcement_id)
            if not announcement:
                logger.error(f"Announcement {announcement_id} not found")
                return False
            
            # Update status to sending
            await self.update_announcement(
                announcement_id=announcement_id,
                payload={"status": "sending"},
                updated_by="system"
            )
            
            # Get recipients based on audience and segments
            recipients = await self._get_recipients(announcement)
            
            # Update recipients count
            await self.supabase.table('announcements')\
                .update({"recipients_count": len(recipients)})\
                .eq('id', announcement_id)\
                .execute()
            
            # Deliver to each channel
            delivery_results = []
            for channel in announcement.get("notification_channels", ["email", "in_app"]):
                if channel in self.delivery_channels:
                    result = await self.delivery_channels[channel](announcement, recipients)
                    delivery_results.append(result)
            
            # Calculate total delivery stats
            total_delivered = sum(r.delivered_count for r in delivery_results)
            total_failed = sum(r.failed_count for r in delivery_results)
            
            # Update delivery stats
            delivery_stats = {
                "total_recipients": len(recipients),
                "total_delivered": total_delivered,
                "total_failed": total_failed,
                "delivery_rate": total_delivered / len(recipients) if recipients else 0,
                "channel_results": [
                    {
                        "channel": r.channel,
                        "delivered": r.delivered_count,
                        "failed": r.failed_count,
                        "success": r.success
                    } for r in delivery_results
                ]
            }
            
            # Update announcement status and stats
            status = "sent" if total_failed == 0 else "failed"
            await self.supabase.table('announcements')\
                .update({
                    "status": status,
                    "delivered_count": total_delivered,
                    "delivery_stats": delivery_stats,
                    "sent_at": datetime.now().isoformat()
                })\
                .eq('id', announcement_id)\
                .execute()
            
            await observability_service.log_event(
                "announcement_delivered",
                metadata={
                    "announcement_id": announcement_id,
                    "recipients": len(recipients),
                    "delivered": total_delivered,
                    "failed": total_failed
                }
            )
            
            return total_failed == 0
            
        except Exception as e:
            logger.error(f"Failed to deliver announcement {announcement_id}: {e}")
            
            # Update status to failed
            await self.supabase.table('announcements')\
                .update({"status": "failed"})\
                .eq('id', announcement_id)\
                .execute()
            
            return False
    
    async def _get_recipients(self, announcement: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get list of recipients based on announcement audience and segments"""
        try:
            audience = announcement.get("audience", "all")
            user_segments = announcement.get("user_segments", [])
            
            query = self.supabase.table('profiles').select('id, email, name, role, plan')
            
            # Apply audience filter
            if audience == "admin":
                query = query.eq('role', 'admin')
            elif audience == "premium":
                query = query.eq('plan', 'premium')
            elif audience == "free":
                query = query.eq('plan', 'free')
            elif audience == "beta":
                query = query.eq('plan', 'beta')
            # "all" includes everyone
            
            # Apply user segments if specified
            if user_segments:
                # This would be more sophisticated in production
                # For now, we'll just get all users
                pass
            
            response = await query.execute()
            return response.data or []
            
        except Exception as e:
            logger.error(f"Failed to get recipients: {e}")
            return []
    
    async def _deliver_email(self, announcement: Dict[str, Any], recipients: List[Dict[str, Any]]) -> DeliveryResult:
        """Deliver announcement via email"""
        try:
            # Simulate email delivery
            delivered_count = len(recipients)
            failed_count = 0
            
            # In production, this would integrate with an email service
            # like SendGrid, Mailgun, or AWS SES
            
            return DeliveryResult(
                success=True,
                channel="email",
                recipient_count=len(recipients),
                delivered_count=delivered_count,
                failed_count=failed_count
            )
            
        except Exception as e:
            logger.error(f"Email delivery failed: {e}")
            return DeliveryResult(
                success=False,
                channel="email",
                recipient_count=len(recipients),
                delivered_count=0,
                failed_count=len(recipients),
                error_message=str(e)
            )
    
    async def _deliver_in_app(self, announcement: Dict[str, Any], recipients: List[Dict[str, Any]]) -> DeliveryResult:
        """Deliver announcement via in-app notification"""
        try:
            # Create in-app notifications for each recipient
            notifications = []
            for recipient in recipients:
                notification = {
                    "id": str(uuid.uuid4()),
                    "user_id": recipient["id"],
                    "announcement_id": announcement["id"],
                    "title": announcement["title"],
                    "content": announcement["content"],
                    "type": announcement["type"],
                    "read": False,
                    "created_at": datetime.now().isoformat()
                }
                notifications.append(notification)
            
            # Store notifications in database
            if notifications:
                await self.supabase.table('user_notifications').insert(notifications).execute()
            
            return DeliveryResult(
                success=True,
                channel="in_app",
                recipient_count=len(recipients),
                delivered_count=len(notifications),
                failed_count=0
            )
            
        except Exception as e:
            logger.error(f"In-app delivery failed: {e}")
            return DeliveryResult(
                success=False,
                channel="in_app",
                recipient_count=len(recipients),
                delivered_count=0,
                failed_count=len(recipients),
                error_message=str(e)
            )
    
    async def _deliver_push(self, announcement: Dict[str, Any], recipients: List[Dict[str, Any]]) -> DeliveryResult:
        """Deliver announcement via push notification"""
        try:
            # Simulate push notification delivery
            delivered_count = len(recipients)
            failed_count = 0
            
            # In production, this would integrate with push notification services
            # like Firebase Cloud Messaging, OneSignal, or AWS SNS
            
            return DeliveryResult(
                success=True,
                channel="push",
                recipient_count=len(recipients),
                delivered_count=delivered_count,
                failed_count=failed_count
            )
            
        except Exception as e:
            logger.error(f"Push delivery failed: {e}")
            return DeliveryResult(
                success=False,
                channel="push",
                recipient_count=len(recipients),
                delivered_count=0,
                failed_count=len(recipients),
                error_message=str(e)
            )
    
    async def _deliver_sms(self, announcement: Dict[str, Any], recipients: List[Dict[str, Any]]) -> DeliveryResult:
        """Deliver announcement via SMS"""
        try:
            # Simulate SMS delivery
            delivered_count = len(recipients)
            failed_count = 0
            
            # In production, this would integrate with SMS services
            # like Twilio, AWS SNS, or MessageBird
            
            return DeliveryResult(
                success=True,
                channel="sms",
                recipient_count=len(recipients),
                delivered_count=delivered_count,
                failed_count=failed_count
            )
            
        except Exception as e:
            logger.error(f"SMS delivery failed: {e}")
            return DeliveryResult(
                success=False,
                channel="sms",
                recipient_count=len(recipients),
                delivered_count=0,
                failed_count=len(recipients),
                error_message=str(e)
            )
    
    async def get_announcement_analytics(self, announcement_id: str) -> Dict[str, Any]:
        """Get analytics for a specific announcement"""
        try:
            announcement = await self.get_announcement(announcement_id)
            if not announcement:
                return {}
            
            # Get engagement data
            engagement_response = await self.supabase.table('announcement_events')\
                .select('*')\
                .eq('announcement_id', announcement_id)\
                .execute()
            
            events = engagement_response.data or []
            
            # Calculate metrics
            total_recipients = announcement.get("recipients_count", 0)
            delivered_count = announcement.get("delivered_count", 0)
            opened_count = len([e for e in events if e.get("event_type") == "opened"])
            clicked_count = len([e for e in events if e.get("event_type") == "clicked"])
            
            delivery_rate = delivered_count / total_recipients if total_recipients > 0 else 0
            open_rate = opened_count / delivered_count if delivered_count > 0 else 0
            click_rate = clicked_count / delivered_count if delivered_count > 0 else 0
            
            # Calculate engagement score (0-100)
            engagement_score = (
                (delivery_rate * 0.3) +
                (open_rate * 0.4) +
                (click_rate * 0.3)
            ) * 100
            
            # Channel performance
            delivery_stats = announcement.get("delivery_stats", {})
            channel_performance = delivery_stats.get("channel_results", [])
            
            # Time series data (last 7 days)
            time_series = []
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                day_events = [e for e in events if e.get("created_at", "").startswith(date)]
                time_series.append({
                    "date": date,
                    "opens": len([e for e in day_events if e.get("event_type") == "opened"]),
                    "clicks": len([e for e in day_events if e.get("event_type") == "clicked"])
                })
            
            return {
                "announcement_id": announcement_id,
                "total_recipients": total_recipients,
                "delivered_count": delivered_count,
                "opened_count": opened_count,
                "clicked_count": clicked_count,
                "delivery_rate": round(delivery_rate * 100, 2),
                "open_rate": round(open_rate * 100, 2),
                "click_rate": round(click_rate * 100, 2),
                "engagement_score": round(engagement_score, 2),
                "channel_performance": channel_performance,
                "time_series_data": time_series,
                "created_at": announcement.get("created_at"),
                "sent_at": announcement.get("sent_at")
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics for announcement {announcement_id}: {e}")
            return {}
    
    async def get_analytics_overview(self, days: int = 30) -> Dict[str, Any]:
        """Get overview analytics for all announcements"""
        try:
            # Get announcements from the last N days
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            response = await self.supabase.table('announcements')\
                .select('*')\
                .gte('created_at', start_date)\
                .execute()
            
            announcements = response.data or []
            
            # Calculate overview metrics
            total_announcements = len(announcements)
            sent_announcements = len([a for a in announcements if a.get("status") == "sent"])
            failed_announcements = len([a for a in announcements if a.get("status") == "failed"])
            
            total_recipients = sum(a.get("recipients_count", 0) for a in announcements)
            total_delivered = sum(a.get("delivered_count", 0) for a in announcements)
            total_opens = sum(a.get("opened_count", 0) for a in announcements)
            total_clicks = sum(a.get("clicked_count", 0) for a in announcements)
            
            avg_delivery_rate = total_delivered / total_recipients if total_recipients > 0 else 0
            avg_open_rate = total_opens / total_delivered if total_delivered > 0 else 0
            avg_click_rate = total_clicks / total_delivered if total_delivered > 0 else 0
            
            # Type distribution
            type_distribution = {}
            for announcement in announcements:
                announcement_type = announcement.get("type", "unknown")
                type_distribution[announcement_type] = type_distribution.get(announcement_type, 0) + 1
            
            # Audience distribution
            audience_distribution = {}
            for announcement in announcements:
                audience = announcement.get("audience", "unknown")
                audience_distribution[audience] = audience_distribution.get(audience, 0) + 1
            
            return {
                "period_days": days,
                "total_announcements": total_announcements,
                "sent_announcements": sent_announcements,
                "failed_announcements": failed_announcements,
                "success_rate": (sent_announcements / total_announcements * 100) if total_announcements > 0 else 0,
                "total_recipients": total_recipients,
                "total_delivered": total_delivered,
                "total_opens": total_opens,
                "total_clicks": total_clicks,
                "avg_delivery_rate": round(avg_delivery_rate * 100, 2),
                "avg_open_rate": round(avg_open_rate * 100, 2),
                "avg_click_rate": round(avg_click_rate * 100, 2),
                "type_distribution": type_distribution,
                "audience_distribution": audience_distribution
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics overview: {e}")
            return {}
    
    async def get_scheduled_announcements(self) -> List[Dict[str, Any]]:
        """Get all scheduled announcements"""
        try:
            response = await self.supabase.table('announcements')\
                .select('*')\
                .eq('status', 'scheduled')\
                .order('scheduled_for', asc=True)\
                .execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Failed to get scheduled announcements: {e}")
            return []
    
    async def cancel_scheduled_announcement(self, announcement_id: str) -> bool:
        """Cancel a scheduled announcement"""
        try:
            await self.supabase.table('announcements')\
                .update({"status": "cancelled"})\
                .eq('id', announcement_id)\
                .execute()
            
            await observability_service.log_event(
                "announcement_cancelled",
                metadata={"announcement_id": announcement_id}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel announcement {announcement_id}: {e}")
            return False
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user's notification preferences"""
        try:
            response = await self.supabase.table('user_notification_preferences')\
                .select('*')\
                .eq('user_id', user_id)\
                .single()\
                .execute()
            
            if response.data:
                return response.data
            
            # Return default preferences if none exist
            return {
                "user_id": user_id,
                "email_notifications": True,
                "in_app_notifications": True,
                "push_notifications": False,
                "announcement_types": ["info", "warning", "critical", "update"],
                "frequency": "immediate",
                "quiet_hours": {"start": "22:00", "end": "08:00"}
            }
            
        except Exception as e:
            logger.error(f"Failed to get user preferences for {user_id}: {e}")
            return {}
    
    async def update_user_preferences(
        self, 
        user_id: str, 
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user's notification preferences"""
        try:
            preferences["user_id"] = user_id
            preferences["updated_at"] = datetime.now().isoformat()
            
            # Upsert preferences
            response = await self.supabase.table('user_notification_preferences')\
                .upsert(preferences)\
                .execute()
            
            return response.data[0] if response.data else preferences
            
        except Exception as e:
            logger.error(f"Failed to update user preferences for {user_id}: {e}")
            return preferences
    
    async def track_event(
        self, 
        announcement_id: str, 
        user_id: str, 
        event_type: str
    ) -> bool:
        """Track user interaction with an announcement"""
        try:
            event_data = {
                "id": str(uuid.uuid4()),
                "announcement_id": announcement_id,
                "user_id": user_id,
                "event_type": event_type,
                "created_at": datetime.now().isoformat()
            }
            
            await self.supabase.table('announcement_events').insert(event_data).execute()
            
            # Update announcement stats
            if event_type == "opened":
                await self.supabase.table('announcements')\
                    .update({"opened_count": self.supabase.raw("opened_count + 1")})\
                    .eq('id', announcement_id)\
                    .execute()
            elif event_type == "clicked":
                await self.supabase.table('announcements')\
                    .update({"clicked_count": self.supabase.raw("clicked_count + 1")})\
                    .eq('id', announcement_id)\
                    .execute()
            
            await observability_service.log_event(
                "announcement_event_tracked",
                user_id=user_id,
                metadata={
                    "announcement_id": announcement_id,
                    "event_type": event_type
                }
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to track event: {e}")
            return False
    
    async def process_scheduled_announcements(self) -> None:
        """Process scheduled announcements (called by scheduler)"""
        try:
            now = datetime.now()
            
            # Get announcements scheduled for now or in the past
            response = await self.supabase.table('announcements')\
                .select('*')\
                .eq('status', 'scheduled')\
                .lte('scheduled_for', now.isoformat())\
                .execute()
            
            scheduled_announcements = response.data or []
            
            for announcement in scheduled_announcements:
                await self.deliver_announcement(announcement["id"])
                
        except Exception as e:
            logger.error(f"Failed to process scheduled announcements: {e}")
    
    async def cleanup_old_events(self, days: int = 90) -> int:
        """Clean up old announcement events"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            response = await self.supabase.table('announcement_events')\
                .delete()\
                .lt('created_at', cutoff_date)\
                .execute()
            
            deleted_count = len(response.data) if response.data else 0
            
            logger.info(f"Cleaned up {deleted_count} old announcement events")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old events: {e}")
            return 0
