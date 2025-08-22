"""
System health endpoint used by system-health.html
"""

from fastapi import APIRouter

health_router = APIRouter()

@health_router.get("/health")
async def system_health():
    # Stub values; replace with real checks later
    return {
        "overall_status": "healthy",
        "server": {"cpu": 23, "memory": 67, "disk": 45, "network": "2.3 MB/s"},
        "database": {"connections": "12/20", "response_time": "45ms", "active_queries": 8, "size": "2.4 GB"},
        "api": {"response_time": "120ms", "requests_per_min": 156, "error_rate": "0.2%", "uptime": "99.8%"},
    }


