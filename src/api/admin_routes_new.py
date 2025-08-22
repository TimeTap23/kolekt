from fastapi import APIRouter
from datetime import datetime, timezone

# Create a simple admin router
admin_router_new = APIRouter(tags=["admin"])

@admin_router_new.get("/test")
async def admin_test():
    """Simple test endpoint"""
    return {"message": "Admin router is working", "status": "ok"}

@admin_router_new.get("/dashboard")
async def get_admin_dashboard():
    """Get admin dashboard statistics"""
    return {
        "success": True,
        "stats": {
            "total_users": 5,
            "active_users": 3,
            "total_content_items": 12,
            "social_connections": 8,
            "monthly_posts": 25,
            "total_api_calls": 150,
            "storage_used": 2.5,
            "revenue_monthly": 0.0
        },
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "note": "Demo data - database integration in progress"
    }
