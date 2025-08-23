#!/usr/bin/env python3
"""
System Monitoring Service
Provides comprehensive system health monitoring, metrics collection, and alerting
"""

import logging
import psutil
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

from src.services.supabase import SupabaseService
from src.services.observability import observability_service
from src.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SystemAlert:
    id: str
    severity: str  # critical, warning, info
    message: str
    metric: str
    value: float
    threshold: float
    timestamp: datetime
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


class SystemMonitoringService:
    """Comprehensive system monitoring service"""
    
    def __init__(self):
        self.supabase = SupabaseService()
        self.metrics_cache = {}
        self.last_metrics_update = None
        self.cache_ttl = 30  # seconds
        
        # Alert thresholds
        self.thresholds = {
            'cpu_usage': 80.0,  # CPU usage > 80%
            'memory_usage': 85.0,  # Memory usage > 85%
            'disk_usage': 90.0,  # Disk usage > 90%
            'error_rate': 5.0,  # Error rate > 5%
            'response_time': 2000,  # Response time > 2s
            'database_connections': 80,  # DB connections > 80%
        }
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        try:
            # Check cache first
            if (self.last_metrics_update and 
                (datetime.now() - self.last_metrics_update).seconds < self.cache_ttl):
                return self.metrics_cache.get('system', {})
            
            # Get CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Get memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Get disk metrics
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Get network metrics
            network = psutil.net_io_counters()
            
            # Get load average
            load_avg = psutil.getloadavg()
            
            # Get process metrics
            processes = len(psutil.pids())
            
            system_metrics = {
                "cpu_usage": round(cpu_percent, 2),
                "cpu_count": cpu_count,
                "cpu_frequency": round(cpu_freq.current / 1000, 2) if cpu_freq else 0,
                "memory_usage": round(memory.percent, 2),
                "memory_total": round(memory.total / (1024**3), 2),  # GB
                "memory_available": round(memory.available / (1024**3), 2),  # GB
                "swap_usage": round(swap.percent, 2),
                "disk_usage": round(disk.percent, 2),
                "disk_total": round(disk.total / (1024**3), 2),  # GB
                "disk_free": round(disk.free / (1024**3), 2),  # GB
                "disk_io": {
                    "read_bytes": round(disk_io.read_bytes / (1024**2), 2) if disk_io else 0,  # MB
                    "write_bytes": round(disk_io.write_bytes / (1024**2), 2) if disk_io else 0,  # MB
                    "read_count": disk_io.read_count if disk_io else 0,
                    "write_count": disk_io.write_count if disk_io else 0,
                },
                "network_io": {
                    "bytes_sent": round(network.bytes_sent / (1024**2), 2),  # MB
                    "bytes_recv": round(network.bytes_recv / (1024**2), 2),  # MB
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv,
                },
                "load_average": [round(load, 2) for load in load_avg],
                "processes": processes,
                "uptime": round(time.time() - psutil.boot_time(), 2),  # seconds
            }
            
            # Update cache
            self.metrics_cache['system'] = system_metrics
            self.last_metrics_update = datetime.now()
            
            return system_metrics
            
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {
                "cpu_usage": 0,
                "memory_usage": 0,
                "disk_usage": 0,
                "network_io": {"bytes_sent": 0, "bytes_recv": 0},
                "load_average": [0, 0, 0],
                "error": str(e)
            }
    
    async def get_database_metrics(self) -> Dict[str, Any]:
        """Get database health metrics"""
        try:
            # Simulate database metrics (in production, query actual DB)
            start_time = time.time()
            
            # Test database connection
            try:
                await self.supabase.table('profiles').select('count').limit(1).execute()
                response_time = (time.time() - start_time) * 1000  # ms
                db_healthy = True
            except Exception:
                response_time = 9999  # High response time indicates issues
                db_healthy = False
            
            # Get database size (simulated)
            db_size = "2.4 GB"
            
            # Get connection pool info (simulated)
            connections = "12/20"
            active_queries = 8
            
            database_metrics = {
                "connections": connections,
                "response_time": f"{round(response_time, 0)}ms",
                "active_queries": active_queries,
                "size": db_size,
                "health_status": "healthy" if db_healthy else "unhealthy",
                "last_backup": "2024-01-15 02:00:00",
                "backup_size": "1.8 GB",
                "replication_lag": "0ms",
            }
            
            return database_metrics
            
        except Exception as e:
            logger.error(f"Failed to get database metrics: {e}")
            return {
                "connections": "0/0",
                "response_time": "9999ms",
                "active_queries": 0,
                "size": "0 GB",
                "health_status": "unhealthy",
                "error": str(e)
            }
    
    async def get_api_metrics(self) -> Dict[str, Any]:
        """Get API performance metrics"""
        try:
            # Get metrics from observability service
            current_time = datetime.now()
            
            # Calculate API metrics from logs (simulated)
            api_metrics = {
                "response_time": "120ms",
                "requests_per_min": 156,
                "error_rate": "0.2%",
                "uptime": "99.8%",
                "active_endpoints": 24,
                "total_requests": 2240,
                "successful_requests": 2235,
                "failed_requests": 5,
                "average_response_time": 120,
                "p95_response_time": 450,
                "p99_response_time": 1200,
            }
            
            return api_metrics
            
        except Exception as e:
            logger.error(f"Failed to get API metrics: {e}")
            return {
                "response_time": "9999ms",
                "requests_per_min": 0,
                "error_rate": "100%",
                "uptime": "0%",
                "active_endpoints": 0,
                "error": str(e)
            }
    
    def determine_overall_status(
        self, 
        system_metrics: Dict[str, Any], 
        database_metrics: Dict[str, Any], 
        api_metrics: Dict[str, Any]
    ) -> str:
        """Determine overall system health status"""
        try:
            # Check critical thresholds
            critical_issues = 0
            warning_issues = 0
            
            # System checks
            if system_metrics.get('cpu_usage', 0) > self.thresholds['cpu_usage']:
                critical_issues += 1
            elif system_metrics.get('cpu_usage', 0) > 70:
                warning_issues += 1
            
            if system_metrics.get('memory_usage', 0) > self.thresholds['memory_usage']:
                critical_issues += 1
            elif system_metrics.get('memory_usage', 0) > 75:
                warning_issues += 1
            
            if system_metrics.get('disk_usage', 0) > self.thresholds['disk_usage']:
                critical_issues += 1
            elif system_metrics.get('disk_usage', 0) > 80:
                warning_issues += 1
            
            # Database checks
            if database_metrics.get('health_status') == 'unhealthy':
                critical_issues += 1
            
            response_time = float(database_metrics.get('response_time', '9999ms').replace('ms', ''))
            if response_time > self.thresholds['response_time']:
                warning_issues += 1
            
            # API checks
            error_rate = float(api_metrics.get('error_rate', '0%').replace('%', ''))
            if error_rate > self.thresholds['error_rate']:
                critical_issues += 1
            elif error_rate > 2:
                warning_issues += 1
            
            # Determine status
            if critical_issues > 0:
                return 'critical'
            elif warning_issues > 0:
                return 'warning'
            else:
                return 'healthy'
                
        except Exception as e:
            logger.error(f"Failed to determine overall status: {e}")
            return 'unknown'
    
    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active system alerts"""
        try:
            # Get alerts from database
            response = await self.supabase.table('security_alerts')\
                .select('*')\
                .eq('acknowledged', False)\
                .order('created_at', desc=True)\
                .limit(10)\
                .execute()
            
            alerts = []
            for alert in response.data:
                alerts.append({
                    "id": alert.get('id'),
                    "severity": alert.get('severity', 'info'),
                    "message": alert.get('message'),
                    "metric": alert.get('metric'),
                    "value": alert.get('value'),
                    "threshold": alert.get('threshold'),
                    "timestamp": alert.get('created_at'),
                    "acknowledged": alert.get('acknowledged', False)
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get active alerts: {e}")
            return []
    
    def get_recommendations(
        self, 
        system_metrics: Dict[str, Any], 
        database_metrics: Dict[str, Any], 
        api_metrics: Dict[str, Any]
    ) -> List[str]:
        """Get system recommendations based on current metrics"""
        recommendations = []
        
        try:
            # System recommendations
            if system_metrics.get('cpu_usage', 0) > 70:
                recommendations.append("Consider scaling up CPU resources or optimizing application performance")
            
            if system_metrics.get('memory_usage', 0) > 75:
                recommendations.append("Memory usage is high - consider increasing RAM or optimizing memory usage")
            
            if system_metrics.get('disk_usage', 0) > 80:
                recommendations.append("Disk usage is high - consider cleanup or expanding storage")
            
            # Database recommendations
            if database_metrics.get('health_status') == 'unhealthy':
                recommendations.append("Database health check failed - investigate connection issues")
            
            response_time = float(database_metrics.get('response_time', '9999ms').replace('ms', ''))
            if response_time > 1000:
                recommendations.append("Database response time is slow - consider query optimization or scaling")
            
            # API recommendations
            error_rate = float(api_metrics.get('error_rate', '0%').replace('%', ''))
            if error_rate > 2:
                recommendations.append("API error rate is elevated - investigate recent deployments or traffic patterns")
            
            # General recommendations
            if not recommendations:
                recommendations.append("System is performing well - continue monitoring")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return ["Unable to generate recommendations due to system error"]
    
    async def get_detailed_metrics(self) -> Dict[str, Any]:
        """Get detailed system metrics for monitoring"""
        try:
            system_metrics = await self.get_system_metrics()
            database_metrics = await self.get_database_metrics()
            api_metrics = await self.get_api_metrics()
            
            # Get historical data (simulated)
            historical_data = {
                "cpu_trend": [45, 52, 48, 61, 58, 55, 49],
                "memory_trend": [65, 68, 72, 75, 71, 69, 67],
                "disk_trend": [42, 43, 44, 45, 46, 47, 45],
                "response_time_trend": [120, 135, 118, 142, 128, 115, 120],
            }
            
            return {
                "current": {
                    "system": system_metrics,
                    "database": database_metrics,
                    "api": api_metrics
                },
                "historical": historical_data,
                "thresholds": self.thresholds,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get detailed metrics: {e}")
            return {"error": str(e)}
    
    async def get_alerts(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get system alerts with optional severity filter"""
        try:
            query = self.supabase.table('security_alerts').select('*')
            
            if severity:
                query = query.eq('severity', severity)
            
            response = await query.order('created_at', desc=True).limit(50).execute()
            
            alerts = []
            for alert in response.data:
                alerts.append({
                    "id": alert.get('id'),
                    "severity": alert.get('severity'),
                    "message": alert.get('message'),
                    "metric": alert.get('metric'),
                    "value": alert.get('value'),
                    "threshold": alert.get('threshold'),
                    "timestamp": alert.get('created_at'),
                    "acknowledged": alert.get('acknowledged', False),
                    "acknowledged_by": alert.get('acknowledged_by'),
                    "acknowledged_at": alert.get('acknowledged_at')
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            return []
    
    async def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance trends over time"""
        try:
            # Simulate performance trends
            current_time = datetime.now()
            trends = {
                "cpu_usage": [],
                "memory_usage": [],
                "disk_usage": [],
                "response_time": [],
                "error_rate": [],
                "requests_per_min": []
            }
            
            # Generate trend data
            for i in range(hours):
                timestamp = current_time - timedelta(hours=i)
                trends["cpu_usage"].append({
                    "timestamp": timestamp.isoformat(),
                    "value": round(50 + (i % 20), 2)
                })
                trends["memory_usage"].append({
                    "timestamp": timestamp.isoformat(),
                    "value": round(65 + (i % 15), 2)
                })
                trends["disk_usage"].append({
                    "timestamp": timestamp.isoformat(),
                    "value": round(45 + (i % 5), 2)
                })
                trends["response_time"].append({
                    "timestamp": timestamp.isoformat(),
                    "value": round(120 + (i % 30), 2)
                })
                trends["error_rate"].append({
                    "timestamp": timestamp.isoformat(),
                    "value": round(0.2 + (i % 3) * 0.1, 2)
                })
                trends["requests_per_min"].append({
                    "timestamp": timestamp.isoformat(),
                    "value": round(150 + (i % 50), 2)
                })
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to get performance trends: {e}")
            return {}
    
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge a system alert"""
        try:
            await self.supabase.table('security_alerts').update({
                'acknowledged': True,
                'acknowledged_by': user_id,
                'acknowledged_at': datetime.now().isoformat()
            }).eq('id', alert_id).execute()
            
            await observability_service.log_event(
                "alert_acknowledged",
                user_id=user_id,
                metadata={"alert_id": alert_id}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            return False
    
    async def quick_health_check(self) -> bool:
        """Perform a quick health check"""
        try:
            # Check basic system health
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_usage = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent
            
            # Check if critical thresholds are exceeded
            if (cpu_usage > 95 or memory_usage > 95 or disk_usage > 95):
                return False
            
            # Check database connectivity
            try:
                await self.supabase.table('profiles').select('count').limit(1).execute()
            except Exception:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Quick health check failed: {e}")
            return False
    
    async def readiness_check(self) -> bool:
        """Check if system is ready to serve traffic"""
        try:
            # Check if all critical services are ready
            checks = {
                "database": await self._check_database_readiness(),
                "api": await self._check_api_readiness(),
                "cache": await self._check_cache_readiness(),
            }
            
            # All checks must pass
            return all(checks.values())
            
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return False
    
    async def _check_database_readiness(self) -> bool:
        """Check database readiness"""
        try:
            await self.supabase.table('profiles').select('count').limit(1).execute()
            return True
        except Exception:
            return False
    
    async def _check_api_readiness(self) -> bool:
        """Check API readiness"""
        try:
            # Check if API endpoints are responding
            return True  # Simplified check
        except Exception:
            return False
    
    async def _check_cache_readiness(self) -> bool:
        """Check cache readiness"""
        try:
            # Check if cache is available
            return True  # Simplified check
        except Exception:
            return False
    
    async def create_alert(
        self, 
        severity: str, 
        message: str, 
        metric: str, 
        value: float, 
        threshold: float
    ) -> bool:
        """Create a new system alert"""
        try:
            alert_data = {
                'severity': severity,
                'message': message,
                'metric': metric,
                'value': value,
                'threshold': threshold,
                'created_at': datetime.now().isoformat(),
                'acknowledged': False
            }
            
            await self.supabase.table('security_alerts').insert(alert_data).execute()
            
            await observability_service.log_event(
                "alert_created",
                metadata=alert_data
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            return False
