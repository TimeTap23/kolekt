#!/usr/bin/env python3
"""
Kolekt Simple Startup Script for DigitalOcean App Platform
Simplified version to avoid import issues
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Setup basic logging (console only for App Platform)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Only console logging for App Platform
    ]
)

# Import FastAPI components
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="Kolekt",
    description="Transform your content into engaging Threads with AI-powered formatting",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Simple test endpoint
@app.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify app is running"""
    return {
        "message": "Kolekt is running!",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "unknown")
    }

# Authentication endpoints
@app.get("/api/v1/auth/profile")
async def get_user_profile(request: Request):
    """Get current user profile"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        
        # For now, return mock user data
        # In production, this would verify the JWT token
        user_data = {
            "id": "user_123",
            "name": "John Doe",
            "email": "john@example.com",
            "bio": "Content creator and social media enthusiast",
            "plan": "starter",
            "email_notifications": True,
            "marketing_emails": False,
            "product_updates": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        return user_data
    except Exception as e:
        logging.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to get profile")

@app.put("/api/v1/auth/profile")
async def update_user_profile(request: Request):
    """Update user profile"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        data = await request.json()
        
        # For now, return success
        # In production, this would update the user in the database
        return {"success": True, "message": "Profile updated successfully"}
    except Exception as e:
        logging.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile")

@app.post("/api/v1/auth/change-password")
async def change_password(request: Request):
    """Change user password"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        data = await request.json()
        
        current_password = data.get("current_password")
        new_password = data.get("new_password")
        
        if not current_password or not new_password:
            raise HTTPException(status_code=400, detail="Missing password fields")
        
        # For now, return success
        # In production, this would verify current password and update to new password
        return {"success": True, "message": "Password changed successfully"}
    except Exception as e:
        logging.error(f"Error changing password: {e}")
        raise HTTPException(status_code=500, detail="Failed to change password")

@app.post("/api/v1/auth/forgot-password")
async def forgot_password(request: Request):
    """Send password reset email"""
    try:
        data = await request.json()
        email = data.get("email")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        # For now, return success
        # In production, this would send a password reset email
        return {"success": True, "message": "Password reset email sent"}
    except Exception as e:
        logging.error(f"Error sending password reset: {e}")
        raise HTTPException(status_code=500, detail="Failed to send password reset")

@app.put("/api/v1/auth/notification-preferences")
async def update_notification_preferences(request: Request):
    """Update notification preferences"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        data = await request.json()
        
        # For now, return success
        # In production, this would update user preferences in the database
        return {"success": True, "message": "Preferences updated successfully"}
    except Exception as e:
        logging.error(f"Error updating notification preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")

# Content Management endpoints
@app.post("/api/v1/content/create")
async def create_content(request: Request):
    """Create new content"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        data = await request.json()
        
        # Validate required fields
        if not data.get("content"):
            raise HTTPException(status_code=400, detail="Content is required")
        
        if not data.get("platforms"):
            raise HTTPException(status_code=400, detail="At least one platform is required")
        
        # For now, return success with mock content ID
        # In production, this would save to database and potentially schedule posts
        content_id = f"content_{int(time.time())}"
        
        return {
            "success": True,
            "content_id": content_id,
            "message": "Content created successfully"
        }
    except Exception as e:
        logging.error(f"Error creating content: {e}")
        raise HTTPException(status_code=500, detail="Failed to create content")

@app.get("/api/v1/content/drafts")
async def get_drafts(request: Request):
    """Get user drafts"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        
        # For now, return mock drafts
        # In production, this would fetch from database
        mock_drafts = [
            {
                "id": "draft_1",
                "title": "Product Launch Announcement",
                "content": "We're excited to announce the launch of our new product...",
                "type": "announcement",
                "platforms": ["threads", "instagram"],
                "created_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": "draft_2", 
                "title": "Weekly Tips Thread",
                "content": "Here are 5 productivity tips that changed my life...",
                "type": "thread",
                "platforms": ["threads", "twitter"],
                "created_at": "2024-01-14T15:45:00Z"
            }
        ]
        
        return mock_drafts
    except Exception as e:
        logging.error(f"Error getting drafts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get drafts")

@app.post("/api/v1/content/drafts")
async def save_draft(request: Request):
    """Save content draft"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        data = await request.json()
        
        # Validate required fields
        if not data.get("content"):
            raise HTTPException(status_code=400, detail="Content is required")
        
        # For now, return success
        # In production, this would save to database
        return {"success": True, "message": "Draft saved successfully"}
    except Exception as e:
        logging.error(f"Error saving draft: {e}")
        raise HTTPException(status_code=500, detail="Failed to save draft")

@app.get("/api/v1/content/{content_id}")
async def get_content(content_id: str, request: Request):
    """Get specific content"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        
        # For now, return mock content
        # In production, this would fetch from database
        mock_content = {
            "id": content_id,
            "title": "Sample Content",
            "content": "This is sample content for demonstration purposes.",
            "type": "post",
            "platforms": ["threads"],
            "status": "draft",
            "created_at": "2024-01-15T10:30:00Z"
        }
        
        return mock_content
    except Exception as e:
        logging.error(f"Error getting content: {e}")
        raise HTTPException(status_code=500, detail="Failed to get content")

@app.put("/api/v1/content/{content_id}")
async def update_content(content_id: str, request: Request):
    """Update content"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        data = await request.json()
        
        # For now, return success
        # In production, this would update in database
        return {"success": True, "message": "Content updated successfully"}
    except Exception as e:
        logging.error(f"Error updating content: {e}")
        raise HTTPException(status_code=500, detail="Failed to update content")

@app.delete("/api/v1/content/{content_id}")
async def delete_content(content_id: str, request: Request):
    """Delete content"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        
        # For now, return success
        # In production, this would delete from database
        return {"success": True, "message": "Content deleted successfully"}
    except Exception as e:
        logging.error(f"Error deleting content: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete content")

# Social Media Integration endpoints
@app.post("/api/v1/social/post")
async def post_to_social_media(request: Request):
    """Post content to social media platforms"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        data = await request.json()
        
        # Validate required fields
        if not data.get("content"):
            raise HTTPException(status_code=400, detail="Content is required")
        
        if not data.get("platforms"):
            raise HTTPException(status_code=400, detail="At least one platform is required")
        
        # Extract data
        content_text = data.get("content")
        platforms = data.get("platforms", [])
        schedule_time = data.get("schedule_time")
        hashtags = data.get("hashtags", [])
        mentions = data.get("mentions", [])
        
        # For now, simulate posting
        # In production, this would use the SocialPostingService
        results = []
        
        for platform in platforms:
            # Simulate posting delay
            await asyncio.sleep(0.5)
            
            # Mock successful post
            post_id = f"{platform}_{int(time.time())}"
            results.append({
                "platform": platform,
                "success": True,
                "post_id": post_id,
                "url": f"https://{platform}.com/post/{post_id}",
                "published_at": datetime.utcnow().isoformat()
            })
        
        return {
            "success": True,
            "results": results,
            "message": f"Posted to {len(platforms)} platform(s) successfully"
        }
        
    except Exception as e:
        logging.error(f"Error posting to social media: {e}")
        raise HTTPException(status_code=500, detail="Failed to post to social media")

@app.get("/api/v1/social/posts")
async def get_social_posts(request: Request):
    """Get user's social media posts"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        
        # For now, return mock posts
        # In production, this would fetch from database
        mock_posts = [
            {
                "id": "post_1",
                "content": "Just posted some amazing content! 🚀",
                "platforms": ["threads", "instagram"],
                "status": "published",
                "published_at": "2024-01-15T10:30:00Z",
                "engagement": {
                    "likes": 42,
                    "comments": 7,
                    "shares": 3
                }
            },
            {
                "id": "post_2",
                "content": "Weekly productivity tips thread...",
                "platforms": ["threads", "twitter"],
                "status": "published",
                "published_at": "2024-01-14T15:45:00Z",
                "engagement": {
                    "likes": 28,
                    "comments": 12,
                    "shares": 5
                }
            }
        ]
        
        return {"posts": mock_posts}
        
    except Exception as e:
        logging.error(f"Error getting social posts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get social posts")

@app.get("/api/v1/social/scheduled")
async def get_scheduled_posts(request: Request):
    """Get scheduled posts"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        
        # For now, return mock scheduled posts
        # In production, this would fetch from database
        mock_scheduled = [
            {
                "id": "scheduled_1",
                "content": "Product launch announcement coming soon!",
                "platforms": ["threads", "instagram", "linkedin"],
                "schedule_time": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
                "status": "scheduled"
            }
        ]
        
        return {"scheduled_posts": mock_scheduled}
        
    except Exception as e:
        logging.error(f"Error getting scheduled posts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get scheduled posts")

@app.delete("/api/v1/social/posts/{post_id}")
async def delete_social_post(post_id: str, request: Request):
    """Delete a social media post"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        
        # For now, return success
        # In production, this would delete from all platforms
        return {"success": True, "message": "Post deleted successfully"}
        
    except Exception as e:
        logging.error(f"Error deleting social post: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete post")

@app.post("/api/v1/social/connect/{platform}")
async def connect_social_account(platform: str, request: Request):
    """Connect a social media account"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        data = await request.json()
        
        # For now, return success
        # In production, this would initiate OAuth flow
        return {
            "success": True,
            "platform": platform,
            "message": f"Successfully connected {platform} account"
        }
        
    except Exception as e:
        logging.error(f"Error connecting social account: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect account")

@app.get("/api/v1/social/accounts")
async def get_connected_accounts(request: Request):
    """Get user's connected social media accounts"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        
        # For now, return mock connected accounts
        # In production, this would fetch from database
        mock_accounts = [
            {
                "platform": "threads",
                "username": "@user123",
                "connected": True,
                "connected_at": "2024-01-01T00:00:00Z"
            },
            {
                "platform": "instagram",
                "username": "@user123",
                "connected": True,
                "connected_at": "2024-01-01T00:00:00Z"
            },
            {
                "platform": "twitter",
                "username": "@user123",
                "connected": False,
                "connected_at": None
            }
        ]
        
        return {"accounts": mock_accounts}
        
    except Exception as e:
        logging.error(f"Error getting connected accounts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get connected accounts")

# Analytics endpoints
@app.get("/api/v1/analytics/overview")
async def get_analytics_overview(request: Request):
    """Get analytics overview for user"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        
        # For now, return mock analytics data
        # In production, this would use the AnalyticsBackendService
        mock_analytics = {
            "total_posts": 42,
            "total_content_created": 67,
            "ai_credits_used": 234,
            "total_engagement": 1250,
            "platform_usage": {
                "threads": 15,
                "instagram": 12,
                "twitter": 8,
                "linkedin": 7
            },
            "daily_activity": [
                {"date": "2024-01-15", "posts": 2, "engagement": 45, "ai_credits": 5},
                {"date": "2024-01-14", "posts": 1, "engagement": 32, "ai_credits": 3},
                {"date": "2024-01-13", "posts": 3, "engagement": 78, "ai_credits": 8},
                {"date": "2024-01-12", "posts": 0, "engagement": 0, "ai_credits": 0},
                {"date": "2024-01-11", "posts": 2, "engagement": 56, "ai_credits": 4}
            ],
            "top_content": [
                {
                    "content_id": "content_1",
                    "engagement": 234,
                    "platform": "threads",
                    "timestamp": "2024-01-13T10:30:00Z"
                },
                {
                    "content_id": "content_2",
                    "engagement": 189,
                    "platform": "instagram",
                    "timestamp": "2024-01-12T15:45:00Z"
                }
            ],
            "engagement_rate": 15.6,
            "growth_metrics": {
                "posts_growth": 12.5,
                "engagement_growth": 8.3
            }
        }
        
        return mock_analytics
        
    except Exception as e:
        logging.error(f"Error getting analytics overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

@app.get("/api/v1/analytics/platform/{platform}")
async def get_platform_analytics(platform: str, request: Request):
    """Get analytics for a specific platform"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        
        # For now, return mock platform analytics
        mock_platform_data = {
            "platform": platform,
            "total_posts": 15 if platform == "threads" else 12,
            "total_engagement": 450 if platform == "threads" else 380,
            "avg_engagement_per_post": 30.0 if platform == "threads" else 31.7,
            "best_performing_content": [
                {
                    "content_id": f"content_{platform}_1",
                    "engagement": 234,
                    "platform": platform,
                    "timestamp": "2024-01-13T10:30:00Z"
                }
            ],
            "posting_frequency": 0.5,
            "engagement_trends": [
                {"date": "2024-01-15", "engagement": 45, "posts": 1},
                {"date": "2024-01-14", "engagement": 32, "posts": 1},
                {"date": "2024-01-13", "engagement": 78, "posts": 2}
            ]
        }
        
        return mock_platform_data
        
    except Exception as e:
        logging.error(f"Error getting platform analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get platform analytics")

@app.get("/api/v1/analytics/content/{content_id}")
async def get_content_analytics(content_id: str, request: Request):
    """Get analytics for specific content"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        
        # For now, return mock content analytics
        mock_content_data = {
            "content_id": content_id,
            "total_engagement": 234,
            "platforms_published": ["threads", "instagram"],
            "publish_date": "2024-01-13T10:30:00Z",
            "last_engagement": "2024-01-15T14:20:00Z",
            "engagement_breakdown": {
                "threads": 156,
                "instagram": 78
            }
        }
        
        return mock_content_data
        
    except Exception as e:
        logging.error(f"Error getting content analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get content analytics")

@app.get("/api/v1/analytics/insights")
async def get_analytics_insights(request: Request):
    """Get actionable insights for user"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        
        # For now, return mock insights
        # In production, this would use the AnalyticsBackendService.generate_insights()
        mock_insights = [
            {
                "type": "engagement",
                "title": "Low Engagement Rate",
                "message": "Your posts are getting low engagement. Try using more hashtags and engaging with your audience.",
                "priority": "high"
            },
            {
                "type": "frequency",
                "title": "Low Posting Frequency",
                "message": "You're posting less than once every 3 days. Consistent posting can improve engagement.",
                "priority": "medium"
            },
            {
                "type": "platform",
                "title": "Platform Performance",
                "message": "Threads is your best performing platform. Consider focusing more content there.",
                "priority": "low"
            }
        ]
        
        return {"insights": mock_insights}
        
    except Exception as e:
        logging.error(f"Error getting analytics insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get insights")

@app.post("/api/v1/analytics/track")
async def track_analytics_event(request: Request):
    """Track an analytics event"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        data = await request.json()
        
        # Validate required fields
        if not data.get("event_type"):
            raise HTTPException(status_code=400, detail="Event type is required")
        
        # For now, just log the event
        # In production, this would use the AnalyticsBackendService.track_event()
        logging.info(f"Analytics event tracked: {data}")
        
        return {"success": True, "message": "Event tracked successfully"}
        
    except Exception as e:
        logging.error(f"Error tracking analytics event: {e}")
        raise HTTPException(status_code=500, detail="Failed to track event")

@app.get("/api/v1/analytics/export")
async def export_analytics_data(request: Request):
    """Export analytics data"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        
        token = auth_header.split(" ")[1]
        format_type = request.query_params.get("format", "json")
        
        # For now, return mock export data
        # In production, this would use the AnalyticsBackendService.export_analytics_data()
        if format_type == "json":
            mock_export = {
                "user_id": "user_123",
                "export_date": datetime.utcnow().isoformat(),
                "data": {
                    "total_posts": 42,
                    "total_engagement": 1250,
                    "platform_usage": {
                        "threads": 15,
                        "instagram": 12,
                        "twitter": 8,
                        "linkedin": 7
                    }
                }
            }
            return mock_export
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
        
    except Exception as e:
        logging.error(f"Error exporting analytics data: {e}")
        raise HTTPException(status_code=500, detail="Failed to export data")

# Status endpoint
@app.get("/api/v1/status")
async def status():
    """Status endpoint"""
    return {"status": "running", "message": "Kolekt is running"}

# Load routers individually to avoid import errors
try:
    from src.api.auth_routes import router as auth_router
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    logging.info("Auth router loaded successfully")
except Exception as e:
    logging.error(f"Error loading auth router: {e}")

try:
    from src.api.connections_routes import router as connections_router
    app.include_router(connections_router, prefix="/api/v1/connections", tags=["Social Connections"])
    logging.info("Connections router loaded successfully")
except Exception as e:
    logging.error(f"Error loading connections router: {e}")

try:
    from src.api.content_routes import router as content_router
    app.include_router(content_router, prefix="/api/v1/content", tags=["Content Management"])
    logging.info("Content router loaded successfully")
except Exception as e:
    logging.error(f"Error loading content router: {e}")

try:
    from src.api.social_routes import router as social_router
    app.include_router(social_router, prefix="/api/v1/social", tags=["Social Media"])
    logging.info("Social router loaded successfully")
except Exception as e:
    logging.error(f"Error loading social router: {e}")

try:
    from src.api.admin_routes import router as admin_router
    app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])
    logging.info("Admin router loaded successfully")
except Exception as e:
    logging.error(f"Error loading admin router: {e}")

try:
    from src.api.ai_routes import router as ai_router
    app.include_router(ai_router, prefix="/api/v1/ai", tags=["AI Services"])
    logging.info("AI router loaded successfully")
except Exception as e:
    logging.error(f"Error loading AI router: {e}")

try:
    from src.api.threads_routes import router as threads_router
    app.include_router(threads_router, prefix="/api/v1/threads", tags=["Threads"])
    logging.info("Threads router loaded successfully")
except Exception as e:
    logging.error(f"Error loading threads router: {e}")

try:
    from src.api.subscription_routes import router as subscription_router
    app.include_router(subscription_router, prefix="/api/v1/subscriptions", tags=["Subscriptions"])
    logging.info("Subscription router loaded successfully")
except Exception as e:
    logging.error(f"Error loading subscription router: {e}")

try:
    from src.api.import_routes import router as import_router
    app.include_router(import_router, prefix="/api/v1/import", tags=["Import"])
    logging.info("Import router loaded successfully")
except Exception as e:
    logging.error(f"Error loading import router: {e}")

# Serve static files
try:
    app.mount("/static", StaticFiles(directory="web/static"), name="static")
    logging.info("Static files mounted successfully")
except Exception as e:
    logging.error(f"Error mounting static files: {e}")

# Dashboard route - requires authentication
@app.get("/dashboard")
async def dashboard(request: Request):
    """Main dashboard page - requires authentication"""
    # Check authentication
    if not check_auth_token(request):
        # Redirect to login page
        return RedirectResponse(url="/login?redirect=/dashboard", status_code=302)
    
    try:
        with open("web/templates/dashboard.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logging.error(f"Error loading dashboard: {e}")
        return HTMLResponse(content="<html><body><h1>Kolekt Dashboard</h1><p>Loading...</p></body></html>")

# OAuth callback routes
@app.get("/oauth/{platform}/callback")
async def oauth_callback(platform: str, code: str = None, state: str = None, error: str = None):
    """Handle OAuth callbacks"""
    try:
        with open("web/templates/oauth_callback.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logging.error(f"Error loading OAuth callback: {e}")
        return HTMLResponse(content="<html><body><h1>OAuth Callback</h1><p>Processing...</p></body></html>")

@app.get("/oauth/{platform}/uninstall")
async def oauth_uninstall(platform: str, signed_request: str = None):
    """Handle OAuth uninstall for platforms"""
    try:
        logging.info(f"Processing uninstall for {platform}")
        return {"success": True, "message": f"Uninstall processed for {platform}"}
    except Exception as e:
        logging.error(f"Uninstall error: {e}")
        return {"success": False, "error": str(e)}

@app.get("/oauth/{platform}/delete")
async def oauth_delete(platform: str, signed_request: str = None):
    """Handle data deletion requests for platforms"""
    try:
        logging.info(f"Processing data deletion request for {platform}")
        return {"success": True, "message": f"Data deletion request processed for {platform}"}
    except Exception as e:
        logging.error(f"Data deletion error: {e}")
        return {"success": False, "error": str(e)}

# Admin routes
@app.get("/admin")
async def admin_dashboard():
    """Admin dashboard page"""
    try:
        with open("web/templates/admin_dashboard.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logging.error(f"Error loading admin dashboard: {e}")
        return HTMLResponse(content="<html><body><h1>Admin Dashboard</h1><p>Loading...</p></body></html>")

# Main page
@app.get("/")
async def main_page():
    """Main landing page"""
    try:
        with open("web/templates/index.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logging.error(f"Error loading main page: {e}")
        return HTMLResponse(content="<html><body><h1>Welcome to Kolekt</h1><p>Loading...</p></body></html>")

# Pricing page
@app.get("/pricing")
async def pricing_page():
    """Pricing page"""
    try:
        with open("web/templates/pricing.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logging.error(f"Error loading pricing page: {e}")
        return HTMLResponse(content="<html><body><h1>Pricing</h1><p>Loading...</p></body></html>")

# Authentication check function
def check_auth_token(request: Request):
    """Check if user has valid authentication token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return False
    
    token = auth_header.split(" ")[1]
    # For now, just check if token exists (in production, validate against database)
    return bool(token and len(token) > 10)

# Formatter page - removed (now integrated in dashboard)
# @app.get("/formatter")
# async def formatter_page(request: Request):
#     """Content formatter page - requires authentication"""
#     # Check authentication
#     if not check_auth_token(request):
#         # Redirect to login page
#         return RedirectResponse(url="/login?redirect=/formatter", status_code=302)
#     
#     try:
#         with open("web/templates/formatter.html", "r") as f:
#             content = f.read()
#         return HTMLResponse(content=content)
#     except Exception as e:
#         logging.error(f"Error loading formatter page: {e}")
#         return HTMLResponse(content="<html><body><h1>Content Formatter</h1><p>Loading...</p></body></html>")

# Templates page - removed (now integrated in dashboard)
# @app.get("/templates")
# async def templates_page(request: Request):
#     """Content templates page - requires authentication"""
#     # Check authentication
#     if not check_auth_token(request):
#         # Redirect to login page
#         return RedirectResponse(url="/login?redirect=/templates", status_code=302)
#     
#     try:
#         with open("web/templates/templates.html", "r") as f:
#             content = f.read()
#         return HTMLResponse(content=content)
#     except Exception as e:
#         logging.error(f"Error loading templates page: {e}")
#         return HTMLResponse(content="<html><body><h1>Content Templates</h1><p>Loading...</p></body></html>")

# Analytics page - removed (now integrated in dashboard)
# @app.get("/analytics")
# async def analytics_page(request: Request):
#     """Analytics page - requires authentication"""
#     # Check authentication
#     if not check_auth_token(request):
#         # Redirect to login page
#         return RedirectResponse(url="/login?redirect=/analytics", status_code=302)
#     
#     try:
#         with open("web/templates/analytics.html", "r") as f:
#             content = f.read()
#         return HTMLResponse(content=content)
#     except Exception as e:
#         logging.error(f"Error loading analytics page: {e}")
#         return HTMLResponse(content="<html><body><h1>Analytics</h1><p>Loading...</p></body></html>")

# Login page
@app.get("/login")
async def login_page():
    """Login page"""
    try:
        with open("web/templates/login.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logging.error(f"Error loading login page: {e}")
        return HTMLResponse(content="<html><body><h1>Sign In</h1><p>Loading...</p></body></html>")

# Register page
@app.get("/register")
async def register_page():
    """Register page"""
    try:
        with open("web/templates/register.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logging.error(f"Error loading register page: {e}")
        return HTMLResponse(content="<html><body><h1>Sign Up</h1><p>Loading...</p></body></html>")

# Profile page - requires authentication
@app.get("/profile")
async def profile_page(request: Request):
    """Profile page - requires authentication"""
    # Check authentication
    if not check_auth_token(request):
        # Redirect to login page
        return RedirectResponse(url="/login?redirect=/profile", status_code=302)
    
    try:
        with open("web/templates/profile.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logging.error(f"Error loading profile page: {e}")
        return HTMLResponse(content="<html><body><h1>Profile</h1><p>Loading...</p></body></html>")

# Forgot password page
@app.get("/forgot-password")
async def forgot_password_page():
    """Forgot password page"""
    try:
        with open("web/templates/forgot-password.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logging.error(f"Error loading forgot password page: {e}")
        return HTMLResponse(content="<html><body><h1>Reset Password</h1><p>Loading...</p></body></html>")

# Content creator page - removed (now integrated in dashboard)
# @app.get("/content-creator")
# async def content_creator_page(request: Request):
#     """Content creator page - requires authentication"""
#     # Check authentication
#     if not check_auth_token(request):
#         # Redirect to login page
#         return RedirectResponse(url="/login?redirect=/content-creator", status_code=302)
#     
#     try:
#         with open("web/templates/content-creator.html", "r") as f:
#             content = f.read()
#         return HTMLResponse(content=content)
#     except Exception as e:
#         logging.error(f"Error loading content creator page: {e}")
#         return HTMLResponse(content="<html><body><h1>Content Creator</h1><p>Loading...</p></body></html>")

# Social manager page - removed (now integrated in dashboard)
# @app.get("/social-manager")
# async def social_manager_page(request: Request):
#     """Social media manager page - requires authentication"""
#     # Check authentication
#     if not check_auth_token(request):
#         # Redirect to login page
#         return RedirectResponse(url="/login?redirect=/social-manager", status_code=302)
#     
#     try:
#         with open("web/templates/social-manager.html", "r") as f:
#             content = f.read()
#         return HTMLResponse(content=content)
#     except Exception as e:
#         logging.error(f"Error loading social manager page: {e}")
#         return HTMLResponse(content="<html><body><h1>Social Media Manager</h1><p>Loading...</p></body></html>")

# Account settings page - removed (now integrated in dashboard)
# @app.get("/account-settings")
# async def account_settings_page(request: Request):
#     """Account settings page - requires authentication"""
#     # Check authentication
#     if not check_auth_token(request):
#         # Redirect to login page
#         return RedirectResponse(url="/login?redirect=/account-settings", status_code=302)
#     
#     try:
#         with open("web/templates/account-settings.html", "r") as f:
#             content = f.read()
#         return HTMLResponse(content=content)
#     except Exception as e:
#         logging.error(f"Error loading account settings page: {e}")
#         return HTMLResponse(content="<html><body><h1>Account Settings</h1><p>Loading...</p></body></html>")

# Team management page - removed (now integrated in dashboard)
# @app.get("/team-management")
# async def team_management_page(request: Request):
#     """Team management page - requires authentication"""
#     # Check authentication
#     if not check_auth_token(request):
#         # Redirect to login page
#         return RedirectResponse(url="/login?redirect=/team-management", status_code=302)
#     
#     try:
#         with open("web/templates/team-management.html", "r") as f:
#             content = f.read()
#         return HTMLResponse(content=content)
#     except Exception as e:
#         logging.error(f"Error loading team management page: {e}")
#         return HTMLResponse(content="<html><body><h1>Team Management</h1><p>Loading...</p></body></html>")

# Preview pages for homepage
@app.get("/formatter-preview")
async def formatter_preview_page():
    """Formatter preview page"""
    try:
        with open("web/templates/formatter-preview.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logging.error(f"Error loading formatter preview page: {e}")
        return HTMLResponse(content="<html><body><h1>Formatter Preview</h1><p>Loading...</p></body></html>")

@app.get("/templates-preview")
async def templates_preview_page():
    """Templates preview page"""
    try:
        with open("web/templates/templates-preview.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logging.error(f"Error loading templates preview page: {e}")
        return HTMLResponse(content="<html><body><h1>Templates Preview</h1><p>Loading...</p></body></html>")

@app.get("/analytics-preview")
async def analytics_preview_page():
    """Analytics preview page"""
    try:
        with open("web/templates/analytics-preview.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logging.error(f"Error loading analytics preview page: {e}")
        return HTMLResponse(content="<html><body><h1>Analytics Preview</h1><p>Loading...</p></body></html>")

# Team management endpoints (mocked)
@app.get("/api/v1/teams/members")
async def get_team_members(request: Request):
    """Get team members"""
    try:
        # Mock team members data
        members = [
            {
                "user_id": "1",
                "name": "John Doe",
                "email": "john@example.com",
                "role": "owner"
            },
            {
                "user_id": "2",
                "name": "Jane Smith",
                "email": "jane@example.com",
                "role": "admin"
            },
            {
                "user_id": "3",
                "name": "Bob Wilson",
                "email": "bob@example.com",
                "role": "editor"
            }
        ]
        return JSONResponse(content=members)
    except Exception as e:
        logging.error(f"Error getting team members: {e}")
        return JSONResponse(content={"error": "Failed to get team members"}, status_code=500)

@app.post("/api/v1/teams/invite")
async def invite_team_member(request: Request):
    """Invite a team member"""
    try:
        data = await request.json()
        # Mock invitation response
        return JSONResponse(content={
            "success": True,
            "message": f"Invitation sent to {data.get('email')}",
            "invitation_id": "inv_123456"
        })
    except Exception as e:
        logging.error(f"Error inviting team member: {e}")
        return JSONResponse(content={"error": "Failed to send invitation"}, status_code=500)

@app.delete("/api/v1/teams/members/{user_id}")
async def remove_team_member(user_id: str, request: Request):
    """Remove a team member"""
    try:
        # Mock removal response
        return JSONResponse(content={
            "success": True,
            "message": f"Team member {user_id} removed successfully"
        })
    except Exception as e:
        logging.error(f"Error removing team member: {e}")
        return JSONResponse(content={"error": "Failed to remove team member"}, status_code=500)

@app.get("/api/v1/teams/approvals")
async def get_pending_approvals(request: Request):
    """Get pending content approvals"""
    try:
        # Mock approvals data
        approvals = [
            {
                "approval_id": "1",
                "requester_name": "Jane Smith",
                "content_preview": "New product launch announcement...",
                "requested_at": "2 hours ago"
            },
            {
                "approval_id": "2",
                "requester_name": "Bob Wilson",
                "content_preview": "Weekly newsletter content...",
                "requested_at": "1 day ago"
            }
        ]
        return JSONResponse(content=approvals)
    except Exception as e:
        logging.error(f"Error getting approvals: {e}")
        return JSONResponse(content={"error": "Failed to get approvals"}, status_code=500)

@app.post("/api/v1/teams/approvals/{approval_id}")
async def update_approval(approval_id: str, request: Request):
    """Update content approval status"""
    try:
        data = await request.json()
        approved = data.get("approved", False)
        # Mock approval response
        return JSONResponse(content={
            "success": True,
            "message": f"Content {'approved' if approved else 'rejected'} successfully"
        })
    except Exception as e:
        logging.error(f"Error updating approval: {e}")
        return JSONResponse(content={"error": "Failed to update approval"}, status_code=500)

@app.get("/api/v1/teams/analytics")
async def get_team_analytics(request: Request):
    """Get team analytics"""
    try:
        # Mock analytics data
        analytics = {
            "total_members": 3,
            "active_members": 2,
            "pending_approvals": 2,
            "content_created": 15,
            "engagement_rate": 0.045,
            "top_performer": "John Doe"
        }
        return JSONResponse(content=analytics)
    except Exception as e:
        logging.error(f"Error getting team analytics: {e}")
        return JSONResponse(content={"error": "Failed to get analytics"}, status_code=500)

if __name__ == "__main__":
    # Get port from environment or default to 8080
    port = int(os.getenv("PORT", 8080))
    
    # Start the server
    uvicorn.run(
        "start_kolekt_simple:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload for production
        log_level="info"
    )
