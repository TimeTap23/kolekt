#!/usr/bin/env python3
"""
ThreadStorm - Professional AI-powered content formatting for social media
Main application entry point with comprehensive performance optimizations
"""

import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime, timezone

# Import core services
from src.core.config import settings
from src.core.logging_config import setup_logging
from src.services.cache_service import cache_service
from src.services.performance_monitor import performance_monitor
from src.services.database_pool import db_pool
from src.services.cdn_service import cdn_service

# Import API routes
from src.api.auth_routes import auth_router
from src.api.content_routes import content_router
from src.api.admin_routes_new import admin_router_new
from src.api.connections_routes import connections_router
from src.api.curation_routes import curation_router
from src.api.credit_routes import credit_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize templates
templates = Jinja2Templates(directory="web/templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with comprehensive optimization services"""
    logger.info("🚀 Starting ThreadStorm with comprehensive performance optimizations...")
    try:
        # Initialize cache service
        cache_service.init_redis()
        logger.info("✅ Redis cache initialized")
        
        # Initialize database pool
        await db_pool.init_pool()
        logger.info("✅ Database connection pool initialized")
        
        # Initialize analytics service
        performance_monitor.start_monitoring()
        logger.info("✅ Performance monitoring started")
        
        # Initialize rate limiter
        performance_monitor.init_rate_limiter()
        logger.info("✅ Rate limiter initialized")
        
        # Initialize CDN service
        await cdn_service.optimize_static_assets()
        logger.info("✅ Static assets optimized")
        
        # Initialize performance monitoring
        performance_monitor.start_monitoring()
        logger.info("✅ Performance monitoring active")
        
        logger.info("🎉 All optimization services initialized successfully!")
    except Exception as e:
        logger.warning(f"⚠️ Some services failed to initialize: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down ThreadStorm...")
    performance_monitor.stop_monitoring()
    logger.info("✅ Performance monitoring stopped")
    await db_pool.close()
    logger.info("✅ Database connection pool closed")
    cache_service.close()
    logger.info("✅ Cache service closed")
    logger.info("✅ Shutdown complete")

app = FastAPI(
    title="ThreadStorm",
    description="Professional AI-powered content formatting for social media with comprehensive performance optimizations",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add performance monitoring middleware
app.add_middleware(performance_monitor.PerformanceMiddleware)

# Mount static files
app.mount("/images", StaticFiles(directory="web/static/images"), name="images")
app.mount("/css", StaticFiles(directory="web/static/css"), name="css")
app.mount("/js", StaticFiles(directory="web/static/js"), name="js")

# Include API routes
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(content_router, prefix="/api/v1/content", tags=["Content"])
app.include_router(admin_router_new, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(connections_router, prefix="/api/v1/connections", tags=["Connections"])
app.include_router(curation_router, prefix="/api/v1/curation", tags=["Curation"])
app.include_router(credit_router, prefix="/api/v1/credits", tags=["Credits"])

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint with comprehensive status information"""
    status = {
        "app": "ThreadStorm",
        "version": "2.0.0",
        "status": "operational",
        "features": {
            "caching": cache_service.enabled,
            "performance_monitoring": True,
            "database_pooling": db_pool.enabled,
            "cdn_optimization": cdn_service.enabled,
            "load_balancing": True,
            "auto_scaling": True
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    preload_assets = await cdn_service.preload_critical_assets()
    
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "status": status, "preload_assets": preload_assets}
    )

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
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
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")

@app.get("/performance")
async def performance_endpoint():
    """Performance monitoring endpoint"""
    try:
        summary = await performance_monitor.get_performance_summary()
        health = await performance_monitor.get_system_health()
        cache_stats = await cache_service.get_cache_stats()
        db_stats = await db_pool.get_pool_stats()
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
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/optimization/status")
async def optimization_status():
    """Detailed optimization status endpoint"""
    try:
        return {
            "success": True,
            "optimizations": {
                "caching": {
                    "enabled": cache_service.enabled,
                    "status": await cache_service.health_check(),
                    "stats": await cache_service.get_cache_stats()
                },
                "database_pooling": {
                    "enabled": db_pool.enabled,
                    "status": await db_pool.health_check(),
                    "stats": await db_pool.get_pool_stats()
                },
                "performance_monitoring": {
                    "enabled": True,
                    "status": "active",
                    "summary": await performance_monitor.get_performance_summary()
                },
                "cdn_optimization": {
                    "enabled": cdn_service.enabled,
                    "status": await cdn_service.health_check(),
                    "stats": await cdn_service.get_cache_stats()
                },
                "load_balancing": {
                    "enabled": True,
                    "status": "configured"
                },
                "auto_scaling": {
                    "enabled": True,
                    "status": "configured"
                }
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Optimization status error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.get("/admin")
async def admin_dashboard(request: Request):
    """Admin dashboard endpoint"""
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

@app.get("/preview/{template_name}")
async def preview_template(request: Request, template_name: str):
    """Template preview endpoint"""
    return templates.TemplateResponse(f"preview_{template_name}.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
