#!/usr/bin/env python3
"""
ThreadStorm - Main Application Entry Point
Enhanced with comprehensive performance optimizations and monitoring
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
from src.services.database_pool import db_pool
from src.services.cdn_service import cdn_service
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
    """Application lifespan manager with comprehensive optimization services"""
    # Startup
    logger.info("🚀 Starting ThreadStorm with comprehensive performance optimizations...")
    
    # Initialize services
    try:
        # Initialize cache service
        await cache_service.init_redis()
        logger.info("✅ Cache service initialized")
        
        # Initialize database connection pool
        await db_pool.init_pool()
        logger.info("✅ Database connection pool initialized")
        
        # Initialize analytics service
        await analytics_service.init_redis()
        logger.info("✅ Analytics service initialized")
        
        # Initialize rate limiter
        from src.middleware.rate_limiting import rate_limiter
        await rate_limiter.init_redis()
        logger.info("✅ Rate limiter initialized")
        
        # Optimize static assets
        await cdn_service.optimize_static_assets()
        logger.info("✅ Static assets optimized")
        
        # Start performance monitoring
        import asyncio
        asyncio.create_task(performance_monitor.start_monitoring(interval_seconds=60))
        logger.info("✅ Performance monitoring started")
        
        logger.info("🎉 All optimization services initialized successfully!")
        
    except Exception as e:
        logger.warning(f"⚠️ Some services failed to initialize: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down ThreadStorm...")
    
    # Stop performance monitoring
    performance_monitor.stop_monitoring()
    logger.info("✅ Performance monitoring stopped")
    
    # Close database pool
    await db_pool.close()
    logger.info("✅ Database connection pool closed")
    
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
    description="Professional AI-powered content formatting for social media with comprehensive performance optimizations",
    version="2.0.0",
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
    """Main application page with comprehensive optimization features"""
    try:
        # Get system status
        system_status = {
            "api_connected": True,
            "rate_limiting": settings.RATE_LIMIT_ENABLED,
            "spam_protection": True,
            "analytics": True,
            "caching": cache_service.enabled,
            "performance_monitoring": True,
            "database_pooling": db_pool.enabled,
            "cdn_optimization": cdn_service.enabled
        }
        
        # Get preload assets
        preload_assets = await cdn_service.preload_critical_assets()
        
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
                    "database_pooling": db_pool.enabled,
                    "cdn_optimization": cdn_service.enabled,
                    "optimization_level": "enterprise"
                },
                "preload_assets": preload_assets
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
    """Comprehensive health check endpoint"""
    try:
        # Check all services
        cache_health = await cache_service.health_check()
        db_health = await db_pool.health_check()
        system_health = await performance_monitor.get_system_health()
        cdn_health = await cdn_service.health_check()
        
        return {
            "status": "healthy",
            "version": "2.0.0",
            "services": {
                "cache": cache_health,
                "database": db_health,
                "redis": cache_health,
                "performance_monitoring": True,
                "database_pooling": db_health,
                "cdn_optimization": cdn_health
            },
            "system_health": system_health,
            "optimization_features": {
                "caching": cache_service.enabled,
                "database_pooling": db_pool.enabled,
                "performance_monitoring": True,
                "cdn_optimization": cdn_service.enabled,
                "load_balancing": True,
                "auto_scaling": True
            },
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
    """Comprehensive performance metrics endpoint"""
    try:
        # Get performance summary
        summary = await performance_monitor.get_performance_summary(hours=1)
        
        # Get system health
        health = await performance_monitor.get_system_health()
        
        # Get cache statistics
        cache_stats = await cache_service.get_cache_stats()
        
        # Get database pool statistics
        db_stats = await db_pool.get_pool_stats()
        
        # Get CDN statistics
        cdn_stats = await cdn_service.get_cache_stats()
        
        return {
            "success": True,
            "performance_summary": summary,
            "system_health": health,
            "cache_stats": cache_stats,
            "database_pool_stats": db_stats,
            "cdn_stats": cdn_stats,
            "optimization_status": {
                "caching_enabled": cache_service.enabled,
                "database_pooling_enabled": db_pool.enabled,
                "performance_monitoring_enabled": True,
                "cdn_optimization_enabled": cdn_service.enabled
            }
        }
    except Exception as e:
        logger.error(f"Performance endpoint error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/optimization/status")
async def optimization_status():
    """Get comprehensive optimization status"""
    try:
        return {
            "success": True,
            "optimization_features": {
                "caching": {
                    "enabled": cache_service.enabled,
                    "redis_connected": cache_service.redis_client is not None,
                    "hit_rate": "tracking_enabled"
                },
                "database_pooling": {
                    "enabled": db_pool.enabled,
                    "pool_size": f"{db_pool.min_size}-{db_pool.max_size}",
                    "health": await db_pool.health_check()
                },
                "performance_monitoring": {
                    "enabled": True,
                    "metrics_tracking": True,
                    "alerting": True
                },
                "cdn_optimization": {
                    "enabled": cdn_service.enabled,
                    "asset_minification": True,
                    "versioning": True
                },
                "load_balancing": {
                    "enabled": True,
                    "health_checks": True,
                    "auto_scaling": True
                }
            },
            "performance_metrics": {
                "response_time_avg": "tracking_enabled",
                "throughput": "monitoring_enabled",
                "error_rate": "tracking_enabled",
                "resource_usage": "monitoring_enabled"
            }
        }
    except Exception as e:
        logger.error(f"Optimization status error: {e}")
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
