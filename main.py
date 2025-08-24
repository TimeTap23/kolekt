#!/usr/bin/env python3
"""
ThreadStorm - Main Application Entry Point
Enhanced with performance optimizations and monitoring
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from src.services.authentication import require_admin

# Import our modules
from src.api.routes import api_router
from src.services.analytics import AnalyticsService
from src.services.cache_service import cache_service
from src.services.performance_monitor import performance_monitor
from src.middleware.rate_limiting import rate_limit_middleware, spam_detection_middleware
from src.middleware.performance import performance_middleware
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
    logger.info("🚀 Starting ThreadStorm with performance optimizations...")
    
    # Initialize services
    try:
        # Initialize cache service
        await cache_service.init_redis()
        logger.info("✅ Cache service initialized")
        
        # Initialize analytics service
        await analytics_service.init_redis()
        logger.info("✅ Analytics service initialized")
        
        # Initialize rate limiter
        from src.middleware.rate_limiting import rate_limiter
        await rate_limiter.init_redis()
        logger.info("✅ Rate limiter initialized")
        
        # Start performance monitoring
        import asyncio
        asyncio.create_task(performance_monitor.start_monitoring(interval_seconds=60))
        logger.info("✅ Performance monitoring started")
        
    except Exception as e:
        logger.warning(f"⚠️ Some services failed to initialize: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down ThreadStorm...")
    
    # Stop performance monitoring
    performance_monitor.stop_monitoring()
    logger.info("✅ Performance monitoring stopped")
    
    # Cleanup services
    try:
        if cache_service.redis_client:
            cache_service.redis_client.close()
            logger.info("✅ Cache service cleaned up")
    except Exception as e:
        logger.warning(f"⚠️ Cache cleanup failed: {e}")


# Create FastAPI app with lifespan
app = FastAPI(
    title="ThreadStorm",
    description="Professional AI-powered content formatting for social media",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add performance monitoring middleware
@app.middleware("http")
async def performance_monitoring_middleware(request: Request, call_next):
    """Performance monitoring middleware"""
    return await performance_middleware(request, call_next)

# Add anti-spam middleware
@app.middleware("http")
async def anti_spam_middleware(request: Request, call_next):
    """Anti-spam middleware for request processing"""
    try:
        # Apply rate limiting
        response = await rate_limit_middleware(request, call_next)
        
        # Apply spam detection for content endpoints
        if request.url.path.startswith("/api/v1/content"):
            response = await spam_detection_middleware(request, lambda req: response)
        
        return response
        
    except Exception as e:
        logger.error(f"Middleware error: {e}")
        return await call_next(request)


# Mount static files
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Templates
templates = Jinja2Templates(directory="web/templates")

# Include API routes FIRST (before individual routes)
app.include_router(api_router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main application page with performance features"""
    try:
        # Get system status
        system_status = {
            "api_connected": True,
            "rate_limiting": settings.RATE_LIMIT_ENABLED,
            "spam_protection": True,
            "analytics": True,
            "caching": cache_service.enabled,
            "performance_monitoring": True
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
                },
                "performance_features": {
                    "caching": cache_service.enabled,
                    "redis_connected": cache_service.redis_client is not None,
                    "performance_monitoring": True,
                    "optimization_level": "high"
                }
            }
        )
    except Exception as e:
        logger.error(f"Error rendering main page: {e}")
        return HTMLResponse(content="<h1>ThreadStorm</h1><p>System starting up...</p>")


@app.get("/formatter", response_class=HTMLResponse)
async def formatter_page(request: Request):
    """Threads formatter page"""
    return templates.TemplateResponse("formatter-preview.html", {"request": request})


@app.get("/templates", response_class=HTMLResponse)
async def templates_page(request: Request):
    """Templates page"""
    return templates.TemplateResponse("templates-preview.html", {"request": request})


@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Analytics page"""
    return templates.TemplateResponse("analytics-preview.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/admin-dashboard", response_class=HTMLResponse)
async def admin_dashboard_page(request: Request, current_user = Depends(require_admin)):
    """Admin dashboard page - requires admin authentication"""
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})


@app.get("/content-creator", response_class=HTMLResponse)
async def content_creator_page(request: Request):
    """Content creator page"""
    return templates.TemplateResponse("content-creator.html", {"request": request})


@app.get("/system-health", response_class=HTMLResponse)
async def system_health_page(request: Request):
    """System health page"""
    return templates.TemplateResponse("system-health.html", {"request": request})


@app.get("/announcements", response_class=HTMLResponse)
async def announcements_page(request: Request):
    """Announcements page"""
    return templates.TemplateResponse("announcements.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check cache service health
        cache_health = await cache_service.health_check()
        
        # Get system health
        system_health = await performance_monitor.get_system_health()
        
        return {
            "status": "healthy",
            "services": {
                "cache": cache_health,
                "database": True,  # TODO: Add actual database health check
                "redis": cache_health,
                "performance_monitoring": True
            },
            "system_health": system_health,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }


@app.get("/performance")
async def performance_endpoint():
    """Performance metrics endpoint"""
    try:
        # Get performance summary
        summary = await performance_monitor.get_performance_summary(hours=1)
        
        # Get system health
        health = await performance_monitor.get_system_health()
        
        return {
            "success": True,
            "performance_summary": summary,
            "system_health": health,
            "cache_stats": await cache_service.get_cache_stats()
        }
    except Exception as e:
        logger.error(f"Performance endpoint error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
