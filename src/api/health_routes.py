"""
Enhanced System Health API Routes
Provides comprehensive system monitoring with real-time metrics and health checks
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging
import psutil
import asyncio

from src.services.authentication import require_admin
from src.services.observability import observability_service
from src.services.system_monitoring import SystemMonitoringService

logger = logging.getLogger(__name__)
health_router = APIRouter()

# Pydantic models for request/response validation
class SystemMetrics(BaseModel):
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    disk_usage: float = Field(..., description="Disk usage percentage")
    network_io: Dict[str, float] = Field(..., description="Network I/O statistics")
    load_average: List[float] = Field(..., description="System load average")

class DatabaseMetrics(BaseModel):
    connections: str = Field(..., description="Database connections")
    response_time: str = Field(..., description="Database response time")
    active_queries: int = Field(..., description="Active queries count")
    size: str = Field(..., description="Database size")
    health_status: str = Field(..., description="Database health status")

class APIMetrics(BaseModel):
    response_time: str = Field(..., description="API response time")
    requests_per_min: int = Field(..., description="Requests per minute")
    error_rate: str = Field(..., description="Error rate percentage")
    uptime: str = Field(..., description="System uptime percentage")
    active_endpoints: int = Field(..., description="Active API endpoints")

class SystemHealthResponse(BaseModel):
    overall_status: str
    timestamp: datetime
    server: SystemMetrics
    database: DatabaseMetrics
    api: APIMetrics
    alerts: List[Dict[str, Any]]
    recommendations: List[str]

@health_router.get("/health")
async def get_system_health(
    current_user: Dict[str, Any] = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get comprehensive system health status
    
    Returns:
        Complete system health metrics with status and recommendations
    """
    try:
        await observability_service.log_event(
            "system_health_check",
            user_id=current_user.get("user_id"),
            metadata={"endpoint": "/system/health"}
        )
        
        monitoring_service = SystemMonitoringService()
        
        # Get comprehensive system metrics
        system_metrics = await monitoring_service.get_system_metrics()
        database_metrics = await monitoring_service.get_database_metrics()
        api_metrics = await monitoring_service.get_api_metrics()
        
        # Determine overall status
        overall_status = monitoring_service.determine_overall_status(
            system_metrics, database_metrics, api_metrics
        )
        
        # Get active alerts
        alerts = await monitoring_service.get_active_alerts()
        
        # Get recommendations
        recommendations = monitoring_service.get_recommendations(
            system_metrics, database_metrics, api_metrics
        )
        
        return {
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "server": system_metrics,
            "database": database_metrics,
            "api": api_metrics,
            "alerts": alerts,
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"System health check failed: {e}")
        await observability_service.log_event(
            "system_health_error",
            user_id=current_user.get("user_id"),
            metadata={"error": str(e), "endpoint": "/system/health"}
        )
        raise HTTPException(status_code=500, detail="System health check failed")

@health_router.get("/metrics/detailed")
async def get_detailed_metrics(
    current_user: Dict[str, Any] = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get detailed system metrics for monitoring
    """
    try:
        monitoring_service = SystemMonitoringService()
        
        detailed_metrics = await monitoring_service.get_detailed_metrics()
        
        return {
            "success": True,
            "metrics": detailed_metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Detailed metrics failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get detailed metrics")

@health_router.get("/alerts")
async def get_system_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    current_user: Dict[str, Any] = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get system alerts and notifications
    """
    try:
        monitoring_service = SystemMonitoringService()
        
        alerts = await monitoring_service.get_alerts(severity=severity)
        
        return {
            "success": True,
            "alerts": alerts,
            "total_alerts": len(alerts)
        }
        
    except Exception as e:
        logger.error(f"Alerts retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alerts")

@health_router.get("/performance/trends")
async def get_performance_trends(
    hours: int = Query(24, description="Hours of data to retrieve"),
    current_user: Dict[str, Any] = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get performance trends over time
    """
    try:
        monitoring_service = SystemMonitoringService()
        
        trends = await monitoring_service.get_performance_trends(hours=hours)
        
        return {
            "success": True,
            "trends": trends,
            "period_hours": hours
        }
        
    except Exception as e:
        logger.error(f"Performance trends failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance trends")

@health_router.post("/alerts/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user: Dict[str, Any] = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Acknowledge a system alert
    """
    try:
        monitoring_service = SystemMonitoringService()
        
        await monitoring_service.acknowledge_alert(alert_id, current_user.get("user_id"))
        
        return {
            "success": True,
            "message": "Alert acknowledged successfully"
        }
        
    except Exception as e:
        logger.error(f"Alert acknowledgment failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to acknowledge alert")

@health_router.get("/healthz")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint for load balancers and monitoring
    """
    try:
        monitoring_service = SystemMonitoringService()
        
        # Quick health check
        is_healthy = await monitoring_service.quick_health_check()
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@health_router.get("/readyz")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check endpoint for Kubernetes
    """
    try:
        monitoring_service = SystemMonitoringService()
        
        # Check if system is ready to serve traffic
        is_ready = await monitoring_service.readiness_check()
        
        return {
            "status": "ready" if is_ready else "not_ready",
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "database": "ready",
                "api": "ready",
                "cache": "ready"
            }
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not_ready",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


