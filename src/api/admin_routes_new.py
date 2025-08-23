from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timezone
from src.services.authentication import require_admin

# Create a simple admin router
admin_router_new = APIRouter(tags=["admin"])

@admin_router_new.get("/test")
async def admin_test(current_user = Depends(require_admin)):
    """Simple test endpoint - requires admin authentication"""
    return {"message": "Admin router is working", "status": "ok", "user": current_user}

@admin_router_new.get("/dashboard")
async def get_admin_dashboard(current_user = Depends(require_admin)):
    """Get admin dashboard statistics - requires admin authentication"""
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

@admin_router_new.post("/login")
async def admin_login(email: str, password: str):
    """Admin login endpoint - no authentication required"""
    try:
        # For development, allow admin login with hardcoded credentials
        if email == "admin@kolekt.io" and password == "admin123":
            return {
                "success": True,
                "user": {
                    "id": "admin-user-id",
                    "email": email,
                    "name": "Admin User",
                    "role": "admin"
                },
                "access_token": "admin_token_mock",  # Mock token for development
                "token_type": "bearer"
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Login failed")
