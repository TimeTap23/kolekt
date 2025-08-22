"""
System health endpoint used by system-health.html
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
from src.services.authentication import require_admin
from src.services.observability import observability_service

health_router = APIRouter()

@health_router.get("/health")
async def system_health(current_user: Dict[str, Any] = Depends(require_admin)):
    """System health endpoint - admin only"""
    try:
        await observability_service.log_event(
            "system_health_check",
            user_id=current_user.get("user_id"),
            metadata={"endpoint": "/system/health"}
        )
        
        # Stub values; replace with real checks later
        return {
            "overall_status": "healthy",
            "server": {"cpu": 23, "memory": 67, "disk": 45, "network": "2.3 MB/s"},
            "database": {"connections": "12/20", "response_time": "45ms", "active_queries": 8, "size": "2.4 GB"},
            "api": {"response_time": "120ms", "requests_per_min": 156, "error_rate": "0.2%", "uptime": "99.8%"},
        }
    except Exception as e:
        await observability_service.log_event(
            "system_health_error",
            user_id=current_user.get("user_id"),
            metadata={"error": str(e), "endpoint": "/system/health"}
        )
        raise
    # Stub values; replace with real checks later
    return {
        "overall_status": "healthy",
        "server": {"cpu": 23, "memory": 67, "disk": 45, "network": "2.3 MB/s"},
        "database": {"connections": "12/20", "response_time": "45ms", "active_queries": 8, "size": "2.4 GB"},
        "api": {"response_time": "120ms", "requests_per_min": 156, "error_rate": "0.2%", "uptime": "99.8%"},
    }


