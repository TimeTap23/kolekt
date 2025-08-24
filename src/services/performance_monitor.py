#!/usr/bin/env python3
"""
Performance Monitoring Service for ThreadStorm
Tracks system performance metrics and provides insights
"""

import time
import logging
import psutil
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from src.services.cache_service import cache_service

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    category: str
    severity: str = "normal"  # normal, warning, critical


class PerformanceMonitor:
    """Performance monitoring service"""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetric] = []
        self.max_history_size = 1000
        self.monitoring_enabled = True
        
        # Performance thresholds
        self.thresholds = {
            'cpu_usage': {'warning': 70.0, 'critical': 90.0},
            'memory_usage': {'warning': 80.0, 'critical': 95.0},
            'disk_usage': {'warning': 85.0, 'critical': 95.0},
            'response_time': {'warning': 1000.0, 'critical': 3000.0},  # milliseconds
            'error_rate': {'warning': 5.0, 'critical': 10.0},  # percentage
            'cache_hit_rate': {'warning': 70.0, 'critical': 50.0}  # percentage
        }
    
    async def collect_system_metrics(self) -> Dict[str, PerformanceMetric]:
        """Collect current system performance metrics"""
        metrics = {}
        
        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics['cpu_usage'] = PerformanceMetric(
                name="CPU Usage",
                value=cpu_percent,
                unit="%",
                timestamp=datetime.now(),
                category="system",
                severity=self._get_severity('cpu_usage', cpu_percent)
            )
            
            # Memory Usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            metrics['memory_usage'] = PerformanceMetric(
                name="Memory Usage",
                value=memory_percent,
                unit="%",
                timestamp=datetime.now(),
                category="system",
                severity=self._get_severity('memory_usage', memory_percent)
            )
            
            # Disk Usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            metrics['disk_usage'] = PerformanceMetric(
                name="Disk Usage",
                value=disk_percent,
                unit="%",
                timestamp=datetime.now(),
                category="system",
                severity=self._get_severity('disk_usage', disk_percent)
            )
            
            # Network I/O
            network = psutil.net_io_counters()
            metrics['network_bytes_sent'] = PerformanceMetric(
                name="Network Bytes Sent",
                value=network.bytes_sent,
                unit="bytes",
                timestamp=datetime.now(),
                category="network"
            )
            
            metrics['network_bytes_recv'] = PerformanceMetric(
                name="Network Bytes Received",
                value=network.bytes_recv,
                unit="bytes",
                timestamp=datetime.now(),
                category="network"
            )
            
            # Cache Performance
            cache_stats = await cache_service.get_cache_stats()
            if cache_stats.get('enabled'):
                hit_rate = cache_stats.get('hit_rate', 0.0)
                metrics['cache_hit_rate'] = PerformanceMetric(
                    name="Cache Hit Rate",
                    value=hit_rate,
                    unit="%",
                    timestamp=datetime.now(),
                    category="cache",
                    severity=self._get_severity('cache_hit_rate', hit_rate)
                )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
        
        return metrics
    
    def _get_severity(self, metric_name: str, value: float) -> str:
        """Determine severity level based on thresholds"""
        if metric_name not in self.thresholds:
            return "normal"
        
        thresholds = self.thresholds[metric_name]
        
        if value >= thresholds.get('critical', float('inf')):
            return "critical"
        elif value >= thresholds.get('warning', float('inf')):
            return "warning"
        else:
            return "normal"
    
    async def record_request_metric(self, endpoint: str, method: str, 
                                  response_time: float, status_code: int):
        """Record request performance metric"""
        try:
            metric = PerformanceMetric(
                name=f"{method} {endpoint}",
                value=response_time,
                unit="ms",
                timestamp=datetime.now(),
                category="api",
                severity=self._get_severity('response_time', response_time)
            )
            
            # Store in cache for quick access
            cache_key = f"request_metric:{endpoint}:{method}"
            await cache_service.set("performance", cache_key, {
                'response_time': response_time,
                'status_code': status_code,
                'timestamp': metric.timestamp.isoformat(),
                'severity': metric.severity
            }, ttl=3600)  # Cache for 1 hour
            
            # Add to history
            self.metrics_history.append(metric)
            
            # Trim history if too large
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history = self.metrics_history[-self.max_history_size:]
                
        except Exception as e:
            logger.error(f"Error recording request metric: {e}")
    
    async def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance summary for the last N hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filter recent metrics
            recent_metrics = [
                m for m in self.metrics_history 
                if m.timestamp >= cutoff_time
            ]
            
            # Group by category
            categories = {}
            for metric in recent_metrics:
                if metric.category not in categories:
                    categories[metric.category] = []
                categories[metric.category].append(metric)
            
            # Calculate statistics
            summary = {
                'period_hours': hours,
                'total_metrics': len(recent_metrics),
                'categories': {},
                'alerts': []
            }
            
            for category, metrics in categories.items():
                if not metrics:
                    continue
                
                values = [m.value for m in metrics]
                summary['categories'][category] = {
                    'count': len(metrics),
                    'avg': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'critical_count': len([m for m in metrics if m.severity == 'critical']),
                    'warning_count': len([m for m in metrics if m.severity == 'warning'])
                }
                
                # Add alerts for critical metrics
                critical_metrics = [m for m in metrics if m.severity == 'critical']
                for metric in critical_metrics:
                    summary['alerts'].append({
                        'metric': metric.name,
                        'value': f"{metric.value}{metric.unit}",
                        'severity': metric.severity,
                        'timestamp': metric.timestamp.isoformat()
                    })
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {'error': str(e)}
    
    async def get_endpoint_performance(self, endpoint: str = None) -> Dict[str, Any]:
        """Get performance metrics for specific endpoints"""
        try:
            # Get from cache first
            if endpoint:
                cache_key = f"endpoint_performance:{endpoint}"
                cached_data = await cache_service.get("performance", cache_key)
                if cached_data:
                    return cached_data
            
            # Get all endpoint metrics from cache
            pattern = "request_metric:*"
            # Note: This would require Redis SCAN command for production
            # For now, we'll return a simplified version
            
            return {
                'endpoint': endpoint or 'all',
                'metrics': {
                    'avg_response_time': 150.0,  # Mock data
                    'total_requests': 1000,
                    'error_rate': 2.5,
                    'status_codes': {
                        '200': 950,
                        '404': 30,
                        '500': 20
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting endpoint performance: {e}")
            return {'error': str(e)}
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        try:
            # Collect current metrics
            current_metrics = await self.collect_system_metrics()
            
            # Determine overall health
            critical_count = len([m for m in current_metrics.values() if m.severity == 'critical'])
            warning_count = len([m for m in current_metrics.values() if m.severity == 'warning'])
            
            if critical_count > 0:
                overall_status = "critical"
            elif warning_count > 0:
                overall_status = "warning"
            else:
                overall_status = "healthy"
            
            return {
                'status': overall_status,
                'timestamp': datetime.now().isoformat(),
                'metrics': {
                    name: {
                        'value': metric.value,
                        'unit': metric.unit,
                        'severity': metric.severity
                    }
                    for name, metric in current_metrics.items()
                },
                'alerts': {
                    'critical': critical_count,
                    'warning': warning_count
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                'status': 'unknown',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous performance monitoring"""
        logger.info(f"Starting performance monitoring (interval: {interval_seconds}s)")
        
        while self.monitoring_enabled:
            try:
                # Collect metrics
                metrics = await self.collect_system_metrics()
                
                # Store in cache
                await cache_service.set("performance", "current_metrics", {
                    name: {
                        'value': metric.value,
                        'unit': metric.unit,
                        'severity': metric.severity,
                        'timestamp': metric.timestamp.isoformat()
                    }
                    for name, metric in metrics.items()
                }, ttl=300)  # Cache for 5 minutes
                
                # Log critical alerts
                critical_metrics = [m for m in metrics.values() if m.severity == 'critical']
                for metric in critical_metrics:
                    logger.critical(f"CRITICAL: {metric.name} = {metric.value}{metric.unit}")
                
                # Wait for next interval
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(interval_seconds)
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_enabled = False
        logger.info("Performance monitoring stopped")


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
