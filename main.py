#!/usr/bin/env python3
"""
ThreadStorm - Main Application Entry Point
Enhanced with anti-spam and rate limiting middleware
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Import our modules
from src.api.routes import api_router
from src.services.analytics import AnalyticsService
from src.middleware.rate_limiting import rate_limit_middleware, spam_detection_middleware
from src.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global services
analytics_service = AnalyticsService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting ThreadStorm with anti-spam protection...")
    
    # Initialize services
    try:
        # Initialize analytics service
        await analytics_service.init_redis()
        logger.info("✅ Analytics service initialized")
        
        # Initialize rate limiter
        from src.middleware.rate_limiting import rate_limiter
        await rate_limiter.init_redis()
        logger.info("✅ Rate limiter initialized")
        
    except Exception as e:
        logger.warning(f"⚠️ Some services failed to initialize: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down ThreadStorm...")


# Create FastAPI app with anti-spam features
app = FastAPI(
    title="ThreadStorm",
    description="AI-powered Threads formatter with comprehensive anti-spam protection",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add anti-spam middleware
@app.middleware("http")
async def anti_spam_middleware(request: Request, call_next):
    """Combined anti-spam and rate limiting middleware"""
    try:
        # Apply rate limiting
        response = await rate_limit_middleware(request, call_next)
        
        # Apply spam detection for content endpoints
        if request.url.path in ['/api/v1/format', '/api/v1/threads/publish']:
            response = await spam_detection_middleware(request, lambda req: response)
        
        return response
        
    except Exception as e:
        logger.error(f"Middleware error: {e}")
        return await call_next(request)


# Mount static files
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Templates
templates = Jinja2Templates(directory="web/templates")

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main application page with anti-spam features"""
    try:
        # Get system status
        system_status = {
            "api_connected": True,
            "rate_limiting": settings.RATE_LIMIT_ENABLED,
            "spam_protection": True,
            "analytics": True
        }
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "system_status": system_status,
                "anti_spam_features": {
                    "content_validation": True,
                    "rate_limiting": True,
                    "spam_detection": True,
                    "user_guidance": True,
                    "publishing_limits": True
                }
            }
        )
    except Exception as e:
        logger.error(f"Error rendering main page: {e}")
        return HTMLResponse(content="<h1>ThreadStorm</h1><p>System starting up...</p>")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "features": {
            "anti_spam": True,
            "rate_limiting": settings.RATE_LIMIT_ENABLED,
            "analytics": True,
            "threads_api": bool(settings.THREADS_ACCESS_TOKEN)
        }
    }


@app.get("/content-guidelines")
async def content_guidelines():
    """Content guidelines for users"""
    return {
        "guidelines": {
            "do": [
                "Write original, engaging content",
                "Use natural language and tone",
                "Keep posts under 500 characters",
                "Include relevant hashtags (max 3-5)",
                "Use proper grammar and spelling",
                "Add value to your audience",
                "Engage with your community"
            ],
            "dont": [
                "Use excessive caps or punctuation",
                "Include suspicious marketing language",
                "Post repetitive or duplicate content",
                "Include URLs in posts",
                "Use spam keywords (buy now, earn money, etc.)",
                "Post too frequently (max 10/day for free users)",
                "Use automated posting tools"
            ],
            "limits": {
                "free": {
                    "daily_posts": 10,
                    "monthly_threadstorms": 10,
                    "rate_limit": "10 requests/minute"
                },
                "pro": {
                    "daily_posts": 100,
                    "monthly_threadstorms": 100,
                    "rate_limit": "100 requests/minute"
                },
                "business": {
                    "daily_posts": 500,
                    "monthly_threadstorms": 1000,
                    "rate_limit": "500 requests/minute"
                }
            },
            "anti_spam_features": {
                "content_validation": "Real-time content quality checking",
                "spam_detection": "AI-powered spam pattern recognition",
                "rate_limiting": "Intelligent request rate limiting",
                "user_guidance": "Helpful suggestions and warnings",
                "publishing_limits": "Daily and monthly posting limits"
            }
        }
    }


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard page"""
    try:
        return templates.TemplateResponse("admin_dashboard.html", {"request": request})
    except Exception as e:
        logger.error(f"Error rendering admin dashboard: {e}")
        return HTMLResponse(content="<h1>Admin Dashboard</h1><p>Loading...</p>")


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting ThreadStorm with enhanced anti-spam protection...")
    logger.info(f"📊 Rate limiting: {'Enabled' if settings.RATE_LIMIT_ENABLED else 'Disabled'}")
    logger.info(f"🛡️ Spam protection: Enabled")
    logger.info(f"📈 Analytics: Enabled")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
