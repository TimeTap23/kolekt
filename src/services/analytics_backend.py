"""
Analytics Backend Service
Handles real analytics data tracking and performance metrics
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class MetricType(Enum):
    CONTENT_CREATED = "content_created"
    POSTS_PUBLISHED = "posts_published"
    AI_CREDITS_USED = "ai_credits_used"
    ENGAGEMENT_RECEIVED = "engagement_received"
    PLATFORM_USAGE = "platform_usage"
    USER_ACTIVITY = "user_activity"
    ERROR_OCCURRED = "error_occurred"

@dataclass
class AnalyticsEvent:
    """Analytics event data"""
    user_id: str
    event_type: str
    metric_type: MetricType
    metadata: Dict[str, Any]
    timestamp: datetime
    platform: Optional[str] = None
    content_id: Optional[str] = None

@dataclass
class PerformanceMetrics:
    """Performance metrics data"""
    total_posts: int
    total_engagement: int
    avg_engagement_rate: float
    top_performing_content: List[Dict[str, Any]]
    platform_breakdown: Dict[str, int]
    daily_activity: List[Dict[str, Any]]
    weekly_growth: float

class AnalyticsBackendService:
    """Service for tracking and analyzing user activity and performance"""
    
    def __init__(self):
        self.metrics_store = {}  # In production, this would be a database
        self.events_buffer = []
        self.buffer_size = 100
        
    async def track_event(self, event: AnalyticsEvent):
        """Track an analytics event"""
        try:
            # Add to buffer
            self.events_buffer.append({
                'user_id': event.user_id,
                'event_type': event.event_type,
                'metric_type': event.metric_type.value,
                'metadata': event.metadata,
                'timestamp': event.timestamp.isoformat(),
                'platform': event.platform,
                'content_id': event.content_id
            })
            
            # Flush buffer if it's full
            if len(self.events_buffer) >= self.buffer_size:
                await self._flush_buffer()
                
            logger.info(f"Tracked event: {event.event_type} for user {event.user_id}")
            
        except Exception as e:
            logger.error(f"Error tracking event: {e}")
    
    async def _flush_buffer(self):
        """Flush events buffer to storage"""
        try:
            # In production, this would save to database
            for event in self.events_buffer:
                user_id = event['user_id']
                if user_id not in self.metrics_store:
                    self.metrics_store[user_id] = []
                
                self.metrics_store[user_id].append(event)
            
            self.events_buffer.clear()
            logger.info("Flushed analytics buffer")
            
        except Exception as e:
            logger.error(f"Error flushing buffer: {e}")
    
    async def get_user_metrics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive metrics for a user"""
        try:
            # Ensure buffer is flushed
            if self.events_buffer:
                await self._flush_buffer()
            
            user_events = self.metrics_store.get(user_id, [])
            
            # Filter events by date range
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            recent_events = [
                event for event in user_events
                if datetime.fromisoformat(event['timestamp']) >= cutoff_date
            ]
            
            # Calculate metrics
            metrics = {
                'total_posts': self._count_events(recent_events, 'posts_published'),
                'total_content_created': self._count_events(recent_events, 'content_created'),
                'ai_credits_used': self._sum_metadata(recent_events, 'ai_credits_used', 'credits'),
                'total_engagement': self._sum_metadata(recent_events, 'engagement_received', 'engagement'),
                'platform_usage': self._get_platform_usage(recent_events),
                'daily_activity': self._get_daily_activity(recent_events, days),
                'top_content': self._get_top_content(recent_events),
                'engagement_rate': self._calculate_engagement_rate(recent_events),
                'growth_metrics': self._calculate_growth_metrics(user_events, days)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting user metrics: {e}")
            return {}
    
    def _count_events(self, events: List[Dict], event_type: str) -> int:
        """Count events of a specific type"""
        return len([e for e in events if e['event_type'] == event_type])
    
    def _sum_metadata(self, events: List[Dict], event_type: str, key: str) -> int:
        """Sum metadata values for events of a specific type"""
        total = 0
        for event in events:
            if event['event_type'] == event_type:
                total += event['metadata'].get(key, 0)
        return total
    
    def _get_platform_usage(self, events: List[Dict]) -> Dict[str, int]:
        """Get platform usage breakdown"""
        platform_usage = {}
        for event in events:
            if event['event_type'] == 'posts_published' and event['platform']:
                platform = event['platform']
                platform_usage[platform] = platform_usage.get(platform, 0) + 1
        return platform_usage
    
    def _get_daily_activity(self, events: List[Dict], days: int) -> List[Dict[str, Any]]:
        """Get daily activity breakdown"""
        daily_activity = {}
        
        # Initialize all days
        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
            daily_activity[date] = {
                'date': date,
                'posts': 0,
                'engagement': 0,
                'ai_credits': 0
            }
        
        # Count events by day
        for event in events:
            event_date = datetime.fromisoformat(event['timestamp']).strftime('%Y-%m-%d')
            if event_date in daily_activity:
                if event['event_type'] == 'posts_published':
                    daily_activity[event_date]['posts'] += 1
                elif event['event_type'] == 'engagement_received':
                    daily_activity[event_date]['engagement'] += event['metadata'].get('engagement', 0)
                elif event['event_type'] == 'ai_credits_used':
                    daily_activity[event_date]['ai_credits'] += event['metadata'].get('credits', 0)
        
        return list(daily_activity.values())
    
    def _get_top_content(self, events: List[Dict]) -> List[Dict[str, Any]]:
        """Get top performing content"""
        content_performance = {}
        
        for event in events:
            if event['event_type'] == 'engagement_received' and event['content_id']:
                content_id = event['content_id']
                if content_id not in content_performance:
                    content_performance[content_id] = {
                        'content_id': content_id,
                        'engagement': 0,
                        'platform': event['platform'],
                        'timestamp': event['timestamp']
                    }
                content_performance[content_id]['engagement'] += event['metadata'].get('engagement', 0)
        
        # Sort by engagement and return top 5
        top_content = sorted(
            content_performance.values(),
            key=lambda x: x['engagement'],
            reverse=True
        )[:5]
        
        return top_content
    
    def _calculate_engagement_rate(self, events: List[Dict]) -> float:
        """Calculate average engagement rate"""
        posts = self._count_events(events, 'posts_published')
        total_engagement = self._sum_metadata(events, 'engagement_received', 'engagement')
        
        if posts == 0:
            return 0.0
        
        return round(total_engagement / posts, 2)
    
    def _calculate_growth_metrics(self, all_events: List[Dict], days: int) -> Dict[str, float]:
        """Calculate growth metrics"""
        if len(all_events) < 2:
            return {'posts_growth': 0.0, 'engagement_growth': 0.0}
        
        # Split events into two periods
        mid_point = len(all_events) // 2
        first_half = all_events[:mid_point]
        second_half = all_events[mid_point:]
        
        # Calculate metrics for each period
        first_posts = self._count_events(first_half, 'posts_published')
        second_posts = self._count_events(second_half, 'posts_published')
        
        first_engagement = self._sum_metadata(first_half, 'engagement_received', 'engagement')
        second_engagement = self._sum_metadata(second_half, 'engagement_received', 'engagement')
        
        # Calculate growth rates
        posts_growth = ((second_posts - first_posts) / max(first_posts, 1)) * 100
        engagement_growth = ((second_engagement - first_engagement) / max(first_engagement, 1)) * 100
        
        return {
            'posts_growth': round(posts_growth, 2),
            'engagement_growth': round(engagement_growth, 2)
        }
    
    async def get_platform_analytics(self, user_id: str, platform: str, days: int = 30) -> Dict[str, Any]:
        """Get analytics for a specific platform"""
        try:
            user_events = self.metrics_store.get(user_id, [])
            
            # Filter events by platform and date
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            platform_events = [
                event for event in user_events
                if event['platform'] == platform and 
                datetime.fromisoformat(event['timestamp']) >= cutoff_date
            ]
            
            metrics = {
                'platform': platform,
                'total_posts': self._count_events(platform_events, 'posts_published'),
                'total_engagement': self._sum_metadata(platform_events, 'engagement_received', 'engagement'),
                'avg_engagement_per_post': self._calculate_avg_engagement_per_post(platform_events),
                'best_performing_content': self._get_top_content(platform_events),
                'posting_frequency': self._calculate_posting_frequency(platform_events, days),
                'engagement_trends': self._get_engagement_trends(platform_events, days)
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting platform analytics: {e}")
            return {}
    
    def _calculate_avg_engagement_per_post(self, events: List[Dict]) -> float:
        """Calculate average engagement per post"""
        posts = self._count_events(events, 'posts_published')
        total_engagement = self._sum_metadata(events, 'engagement_received', 'engagement')
        
        if posts == 0:
            return 0.0
        
        return round(total_engagement / posts, 2)
    
    def _calculate_posting_frequency(self, events: List[Dict], days: int) -> float:
        """Calculate average posts per day"""
        posts = self._count_events(events, 'posts_published')
        return round(posts / days, 2)
    
    def _get_engagement_trends(self, events: List[Dict], days: int) -> List[Dict[str, Any]]:
        """Get engagement trends over time"""
        daily_engagement = {}
        
        # Initialize all days
        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
            daily_engagement[date] = {
                'date': date,
                'engagement': 0,
                'posts': 0
            }
        
        # Count engagement by day
        for event in events:
            event_date = datetime.fromisoformat(event['timestamp']).strftime('%Y-%m-%d')
            if event_date in daily_engagement:
                if event['event_type'] == 'engagement_received':
                    daily_engagement[event_date]['engagement'] += event['metadata'].get('engagement', 0)
                elif event['event_type'] == 'posts_published':
                    daily_engagement[event_date]['posts'] += 1
        
        return list(daily_engagement.values())
    
    async def get_content_performance(self, content_id: str) -> Dict[str, Any]:
        """Get performance metrics for specific content"""
        try:
            # Find all events related to this content
            content_events = []
            for user_events in self.metrics_store.values():
                for event in user_events:
                    if event.get('content_id') == content_id:
                        content_events.append(event)
            
            if not content_events:
                return {'error': 'Content not found'}
            
            # Calculate performance metrics
            performance = {
                'content_id': content_id,
                'total_engagement': self._sum_metadata(content_events, 'engagement_received', 'engagement'),
                'platforms_published': list(set(event['platform'] for event in content_events if event['platform'])),
                'publish_date': min(event['timestamp'] for event in content_events),
                'last_engagement': max(event['timestamp'] for event in content_events if event['event_type'] == 'engagement_received'),
                'engagement_breakdown': self._get_engagement_breakdown(content_events)
            }
            
            return performance
            
        except Exception as e:
            logger.error(f"Error getting content performance: {e}")
            return {}
    
    def _get_engagement_breakdown(self, events: List[Dict]) -> Dict[str, int]:
        """Get engagement breakdown by platform"""
        breakdown = {}
        for event in events:
            if event['event_type'] == 'engagement_received' and event['platform']:
                platform = event['platform']
                breakdown[platform] = breakdown.get(platform, 0) + event['metadata'].get('engagement', 0)
        return breakdown
    
    async def generate_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate actionable insights for the user"""
        try:
            metrics = await self.get_user_metrics(user_id, 30)
            insights = []
            
            # Engagement rate insight
            if metrics.get('engagement_rate', 0) < 10:
                insights.append({
                    'type': 'engagement',
                    'title': 'Low Engagement Rate',
                    'message': 'Your posts are getting low engagement. Try using more hashtags and engaging with your audience.',
                    'priority': 'high'
                })
            
            # Posting frequency insight
            daily_activity = metrics.get('daily_activity', [])
            total_posts = sum(day['posts'] for day in daily_activity)
            if total_posts < 10:
                insights.append({
                    'type': 'frequency',
                    'title': 'Low Posting Frequency',
                    'message': 'You\'re posting less than once every 3 days. Consistent posting can improve engagement.',
                    'priority': 'medium'
                })
            
            # Platform optimization insight
            platform_usage = metrics.get('platform_usage', {})
            if platform_usage:
                best_platform = max(platform_usage.items(), key=lambda x: x[1])[0]
                insights.append({
                    'type': 'platform',
                    'title': 'Platform Performance',
                    'message': f'{best_platform.title()} is your best performing platform. Consider focusing more content there.',
                    'priority': 'low'
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return []
    
    async def export_analytics_data(self, user_id: str, format: str = 'json') -> str:
        """Export analytics data for a user"""
        try:
            metrics = await self.get_user_metrics(user_id, 365)  # Full year
            
            if format == 'json':
                return json.dumps(metrics, indent=2, default=str)
            elif format == 'csv':
                # Convert to CSV format
                csv_lines = ['Date,Posts,Engagement,AI_Credits']
                for day in metrics.get('daily_activity', []):
                    csv_lines.append(f"{day['date']},{day['posts']},{day['engagement']},{day['ai_credits']}")
                return '\n'.join(csv_lines)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting analytics data: {e}")
            return ""
