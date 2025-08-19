#!/usr/bin/env python3
"""
Observability Service for ThreadStorm
Handles centralized logging, metrics, and alerting
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio

from src.core.config import settings
from src.services.supabase import SupabaseService
from src.services.security import security_service

logger = logging.getLogger(__name__)


@dataclass
class Metric:
    name: str
    value: float
    tags: Dict[str, str]
    timestamp: datetime


@dataclass
class Alert:
    severity: str
    message: str
    metric: str
    value: float
    threshold: float
    timestamp: datetime


class ObservabilityService:
    """Comprehensive observability service"""
    
    def __init__(self):
        self.supabase = SupabaseService()
        self.metrics_buffer = []
        self.alerts_buffer = []
        self.last_cleanup = datetime.now()
        
        # Alert thresholds
        self.alert_thresholds = {
            'error_rate': 0.05,  # 5% error rate
            'latency_p95': 2000,  # 2 seconds
            'rate_limit_exceeded': 10,  # 10 rate limit errors per hour
            'token_refresh_failures': 5,  # 5 token refresh failures per hour
            'publish_failures': 20,  # 20 publish failures per hour
        }
    
    async def log_event(self, category: str, action: str, description: str, 
                       metadata: Dict = None, user_id: str = None, 
                       profile_id: str = None, severity: str = "info"):
        """Log event to centralized logging"""
        try:
            log_data = {
                'category': category,
                'action': action,
                'description': description,
                'metadata': json.dumps(metadata) if metadata else None,
                'user_id': user_id,
                'profile_id': profile_id,
                'severity': severity,
                'timestamp': datetime.now().isoformat(),
                'service': 'threadstorm',
                'version': settings.APP_VERSION
            }
            
            await self.supabase.table('centralized_logs').insert(log_data).execute()
            
            # Also log to standard logging
            log_level = getattr(logging, severity.upper(), logging.INFO)
            logger.log(log_level, f"{category}:{action} - {description}")
            
        except Exception as e:
            logger.error(f"Failed to log event: {e}")
    
    async def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record metric for monitoring"""
        try:
            metric = Metric(
                name=name,
                value=value,
                tags=tags or {},
                timestamp=datetime.now()
            )
            
            self.metrics_buffer.append(metric)
            
            # Flush buffer if it gets too large
            if len(self.metrics_buffer) >= 100:
                await self._flush_metrics()
                
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
    
    async def _flush_metrics(self):
        """Flush metrics buffer to database"""
        try:
            if not self.metrics_buffer:
                return
            
            metrics_data = []
            for metric in self.metrics_buffer:
                metrics_data.append({
                    'name': metric.name,
                    'value': metric.value,
                    'tags': json.dumps(metric.tags),
                    'timestamp': metric.timestamp.isoformat()
                })
            
            await self.supabase.table('metrics').insert(metrics_data).execute()
            self.metrics_buffer.clear()
            
        except Exception as e:
            logger.error(f"Failed to flush metrics: {e}")
    
    async def check_alerts(self):
        """Check for alert conditions"""
        try:
            # Check error rate
            await self._check_error_rate()
            
            # Check latency
            await self._check_latency()
            
            # Check rate limit violations
            await self._check_rate_limit_violations()
            
            # Check token refresh failures
            await self._check_token_refresh_failures()
            
            # Check publish failures
            await self._check_publish_failures()
            
        except Exception as e:
            logger.error(f"Alert checking failed: {e}")
    
    async def _check_error_rate(self):
        """Check error rate and alert if too high"""
        try:
            # Get error rate for last hour
            one_hour_ago = datetime.now() - timedelta(hours=1)
            
            # Count total requests
            total_response = await self.supabase.table('centralized_logs')\
                .select('id', count='exact')\
                .eq('category', 'response')\
                .gte('timestamp', one_hour_ago.isoformat())\
                .execute()
            
            # Count errors
            error_response = await self.supabase.table('centralized_logs')\
                .select('id', count='exact')\
                .eq('category', 'error')\
                .gte('timestamp', one_hour_ago.isoformat())\
                .execute()
            
            total_requests = total_response.count or 0
            total_errors = error_response.count or 0
            
            if total_requests > 0:
                error_rate = total_errors / total_requests
                
                if error_rate > self.alert_thresholds['error_rate']:
                    await self._create_alert(
                        'error_rate',
                        f"High error rate: {error_rate:.2%}",
                        error_rate,
                        self.alert_thresholds['error_rate'],
                        'high'
                    )
                
                # Record metric
                await self.record_metric('error_rate', error_rate)
                
        except Exception as e:
            logger.error(f"Error rate check failed: {e}")
    
    async def _check_latency(self):
        """Check latency and alert if too high"""
        try:
            # Get recent response times
            one_hour_ago = datetime.now() - timedelta(hours=1)
            
            response = await self.supabase.table('centralized_logs')\
                .select('metadata')\
                .eq('category', 'response')\
                .gte('timestamp', one_hour_ago.isoformat())\
                .execute()
            
            response_times = []
            for log in response.data:
                try:
                    metadata = json.loads(log['metadata'])
                    if 'response_time' in metadata:
                        response_times.append(metadata['response_time'])
                except:
                    continue
            
            if response_times:
                # Calculate P95 latency
                response_times.sort()
                p95_index = int(len(response_times) * 0.95)
                p95_latency = response_times[p95_index] * 1000  # Convert to milliseconds
                
                if p95_latency > self.alert_thresholds['latency_p95']:
                    await self._create_alert(
                        'latency_p95',
                        f"High P95 latency: {p95_latency:.0f}ms",
                        p95_latency,
                        self.alert_thresholds['latency_p95'],
                        'medium'
                    )
                
                # Record metric
                await self.record_metric('latency_p95', p95_latency)
                
        except Exception as e:
            logger.error(f"Latency check failed: {e}")
    
    async def _check_rate_limit_violations(self):
        """Check rate limit violations"""
        try:
            one_hour_ago = datetime.now() - timedelta(hours=1)
            
            response = await self.supabase.table('centralized_logs')\
                .select('id', count='exact')\
                .eq('category', 'rate_limit')\
                .gte('timestamp', one_hour_ago.isoformat())\
                .execute()
            
            rate_limit_violations = response.count or 0
            
            if rate_limit_violations > self.alert_thresholds['rate_limit_exceeded']:
                await self._create_alert(
                    'rate_limit_violations',
                    f"High rate limit violations: {rate_limit_violations}",
                    rate_limit_violations,
                    self.alert_thresholds['rate_limit_exceeded'],
                    'medium'
                )
            
            # Record metric
            await self.record_metric('rate_limit_violations', rate_limit_violations)
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
    
    async def _check_token_refresh_failures(self):
        """Check token refresh failures"""
        try:
            one_hour_ago = datetime.now() - timedelta(hours=1)
            
            response = await self.supabase.table('centralized_logs')\
                .select('id', count='exact')\
                .eq('action', 'token_refresh_failed')\
                .gte('timestamp', one_hour_ago.isoformat())\
                .execute()
            
            token_failures = response.count or 0
            
            if token_failures > self.alert_thresholds['token_refresh_failures']:
                await self._create_alert(
                    'token_refresh_failures',
                    f"High token refresh failures: {token_failures}",
                    token_failures,
                    self.alert_thresholds['token_refresh_failures'],
                    'high'
                )
            
            # Record metric
            await self.record_metric('token_refresh_failures', token_failures)
            
        except Exception as e:
            logger.error(f"Token refresh check failed: {e}")
    
    async def _check_publish_failures(self):
        """Check publish failures"""
        try:
            one_hour_ago = datetime.now() - timedelta(hours=1)
            
            response = await self.supabase.table('centralized_logs')\
                .select('id', count='exact')\
                .eq('action', 'publish_failed')\
                .gte('timestamp', one_hour_ago.isoformat())\
                .execute()
            
            publish_failures = response.count or 0
            
            if publish_failures > self.alert_thresholds['publish_failures']:
                await self._create_alert(
                    'publish_failures',
                    f"High publish failures: {publish_failures}",
                    publish_failures,
                    self.alert_thresholds['publish_failures'],
                    'high'
                )
            
            # Record metric
            await self.record_metric('publish_failures', publish_failures)
            
        except Exception as e:
            logger.error(f"Publish failure check failed: {e}")
    
    async def _create_alert(self, metric: str, message: str, value: float, 
                          threshold: float, severity: str):
        """Create and store alert"""
        try:
            alert = Alert(
                severity=severity,
                message=message,
                metric=metric,
                value=value,
                threshold=threshold,
                timestamp=datetime.now()
            )
            
            alert_data = {
                'severity': alert.severity,
                'message': alert.message,
                'metric': alert.metric,
                'value': alert.value,
                'threshold': alert.threshold,
                'timestamp': alert.timestamp.isoformat(),
                'acknowledged': False
            }
            
            await self.supabase.table('alerts').insert(alert_data).execute()
            
            # Send alert notification
            await self._send_alert_notification(alert)
            
            # Log alert
            await self.log_event(
                'alert',
                'alert_created',
                message,
                {'metric': metric, 'value': value, 'threshold': threshold},
                severity='warning'
            )
            
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
    
    async def _send_alert_notification(self, alert: Alert):
        """Send alert notification"""
        try:
            if not settings.ALERT_EMAIL:
                return
            
            # This would integrate with your notification service
            # For now, just log the alert
            logger.warning(f"ALERT [{alert.severity.upper()}]: {alert.message}")
            
            # Log notification attempt
            await self.log_event(
                'notification',
                'alert_sent',
                f"Alert notification sent: {alert.message}",
                {'alert_id': alert.metric, 'severity': alert.severity}
            )
            
        except Exception as e:
            logger.error(f"Failed to send alert notification: {e}")
    
    async def get_metrics(self, metric_name: str = None, start_time: datetime = None, 
                         end_time: datetime = None, tags: Dict[str, str] = None) -> List[Dict]:
        """Get metrics with filtering"""
        try:
            query = self.supabase.table('metrics').select('*')
            
            if metric_name:
                query = query.eq('name', metric_name)
            if start_time:
                query = query.gte('timestamp', start_time.isoformat())
            if end_time:
                query = query.lte('timestamp', end_time.isoformat())
            
            response = await query.order('timestamp', desc=True).execute()
            
            # Filter by tags if provided
            metrics = response.data
            if tags:
                filtered_metrics = []
                for metric in metrics:
                    metric_tags = json.loads(metric['tags'])
                    if all(metric_tags.get(k) == v for k, v in tags.items()):
                        filtered_metrics.append(metric)
                metrics = filtered_metrics
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return []
    
    async def get_alerts(self, severity: str = None, acknowledged: bool = None, 
                        start_time: datetime = None) -> List[Dict]:
        """Get alerts with filtering"""
        try:
            query = self.supabase.table('alerts').select('*')
            
            if severity:
                query = query.eq('severity', severity)
            if acknowledged is not None:
                query = query.eq('acknowledged', acknowledged)
            if start_time:
                query = query.gte('timestamp', start_time.isoformat())
            
            response = await query.order('timestamp', desc=True).execute()
            return response.data
            
        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            return []
    
    async def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert"""
        try:
            await self.supabase.table('alerts')\
                .update({'acknowledged': True})\
                .eq('id', alert_id)\
                .execute()
            
            await self.log_event(
                'alert',
                'alert_acknowledged',
                f"Alert {alert_id} acknowledged",
                {'alert_id': alert_id}
            )
            
        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
    
    async def cleanup_old_data(self):
        """Clean up old logs, metrics, and alerts"""
        try:
            # Clean up old logs (keep 30 days)
            log_cutoff = datetime.now() - timedelta(days=30)
            await self.supabase.table('centralized_logs')\
                .delete()\
                .lt('timestamp', log_cutoff.isoformat())\
                .execute()
            
            # Clean up old metrics (keep 7 days)
            metric_cutoff = datetime.now() - timedelta(days=7)
            await self.supabase.table('metrics')\
                .delete()\
                .lt('timestamp', metric_cutoff.isoformat())\
                .execute()
            
            # Clean up old alerts (keep 90 days)
            alert_cutoff = datetime.now() - timedelta(days=90)
            await self.supabase.table('alerts')\
                .delete()\
                .lt('timestamp', alert_cutoff.isoformat())\
                .execute()
            
            logger.info("Old observability data cleaned up")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")


# Global observability service instance
observability_service = ObservabilityService()


# Observability middleware
async def observability_middleware(request, call_next):
    """Observability middleware for request monitoring"""
    start_time = time.time()
    
    try:
        # Process request
        response = await call_next(request)
        
        # Record response time
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Record metrics
        await observability_service.record_metric(
            'request_duration_ms',
            response_time,
            {
                'method': request.method,
                'path': request.url.path,
                'status_code': str(response.status_code)
            }
        )
        
        await observability_service.record_metric(
            'request_count',
            1,
            {
                'method': request.method,
                'path': request.url.path,
                'status_code': str(response.status_code)
            }
        )
        
        # Log successful request
        await observability_service.log_event(
            'request',
            'api_request',
            f"{request.method} {request.url.path} - {response.status_code}",
            {
                'method': request.method,
                'path': request.url.path,
                'status_code': response.status_code,
                'response_time_ms': response_time
            }
        )
        
        return response
        
    except Exception as e:
        # Record error metrics
        await observability_service.record_metric(
            'request_errors',
            1,
            {
                'method': request.method,
                'path': request.url.path,
                'error_type': type(e).__name__
            }
        )
        
        # Log error
        await observability_service.log_event(
            'error',
            'api_error',
            f"Request failed: {str(e)}",
            {
                'method': request.method,
                'path': request.url.path,
                'error': str(e)
            },
            severity='error'
        )
        
        raise


# Background tasks for observability
async def observability_background_tasks():
    """Background tasks for observability"""
    while True:
        try:
            # Flush metrics buffer
            await observability_service._flush_metrics()
            
            # Check for alerts
            await observability_service.check_alerts()
            
            # Cleanup old data (once per day)
            now = datetime.now()
            if (now - observability_service.last_cleanup).days >= 1:
                await observability_service.cleanup_old_data()
                observability_service.last_cleanup = now
            
            # Wait before next iteration
            await asyncio.sleep(60)  # Check every minute
            
        except Exception as e:
            logger.error(f"Observability background task error: {e}")
            await asyncio.sleep(60)
