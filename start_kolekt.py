#!/usr/bin/env python3
"""
Kolekt - Consolidated Startup Script
Optimized for Railway deployment
"""
import os
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Railway-specific optimizations
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('DEBUG', 'false')
os.environ.setdefault('HOST', '0.0.0.0')

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Import FastAPI components
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Import core services
try:
    from src.core.config import settings
    from src.utils.logging_config import setup_logging
    from src.services.cache_service import cache_service
    from src.services.performance_monitor import performance_monitor
    from src.services.database_pool import db_pool
    from src.services.cdn_service import cdn_service
    PRODUCTION_READY = True
except ImportError:
    print("⚠️  Production utilities not available, running in basic mode")
    PRODUCTION_READY = False

# Import API routes
try:
    from src.api.auth_routes import auth_router
    from src.api.content_routes import content_router
    from src.api.admin_routes_new import admin_router_new
    from src.api.connections_routes import connections_router
    from src.api.curation_routes import curation_router
    ROUTES_AVAILABLE = True
except ImportError:
    print("⚠️  API routes not available")
    ROUTES_AVAILABLE = False

# Import middleware
try:
    from src.middleware.error_handler import ErrorHandler, RateLimitMiddleware, LoggingMiddleware, SecurityMiddleware
    MIDDLEWARE_AVAILABLE = True
except ImportError:
    print("⚠️  Middleware not available")
    MIDDLEWARE_AVAILABLE = False

# Setup logging
if PRODUCTION_READY:
    setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with comprehensive optimization services"""
    if PRODUCTION_READY:
        logger.info("🚀 Starting Kolekt with comprehensive performance optimizations...")
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
            
            logger.info("🎉 All optimization services initialized successfully!")
        except Exception as e:
            logger.warning(f"⚠️ Some services failed to initialize: {e}")
    else:
        logger.info("🚀 Starting Kolekt in basic mode...")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Kolekt...")
    if PRODUCTION_READY:
        performance_monitor.stop_monitoring()
        logger.info("✅ Performance monitoring stopped")
        await db_pool.close()
        logger.info("✅ Database connection pool closed")
        cache_service.close()
        logger.info("✅ Cache service closed")
    logger.info("✅ Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Kolekt",
    description="Transform your content into engaging Threads with AI-powered formatting",
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

# Add production middleware if available
if PRODUCTION_READY and MIDDLEWARE_AVAILABLE:
    # Add security middleware
    app.add_middleware(SecurityMiddleware)
    # Add logging middleware
    app.add_middleware(LoggingMiddleware)
    # Add rate limiting middleware (60 requests per minute)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
    
    # Add error handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return await ErrorHandler.handle_validation_error(request, exc)
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return await ErrorHandler.handle_http_exception(request, exc)
    
    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
        return await ErrorHandler.handle_http_exception(request, exc)
    
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return await ErrorHandler.handle_generic_exception(request, exc)

# Mount static files
static_path = Path(__file__).parent / "web" / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Include API routes if available
if ROUTES_AVAILABLE:
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(content_router, prefix="/api/v1/content", tags=["Content"])
    app.include_router(admin_router_new, prefix="/api/v1/admin", tags=["Admin"])
    app.include_router(connections_router, prefix="/api/v1/connections", tags=["Connections"])
    app.include_router(curation_router, prefix="/api/v1/curation", tags=["Curation"])

# Define routes
@app.get("/")
async def root():
    html_path = Path(__file__).parent / "web" / "templates" / "index.html"
    if html_path.exists():
        with open(html_path, 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return {
            "message": "Kolekt API is running",
            "status": "healthy",
            "version": "2.0.0",
            "mode": "production" if PRODUCTION_READY else "basic",
            "deployment": "railway"
        }

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {
        "status": "healthy",
        "timestamp": "2025-08-24T14:00:00Z",
        "version": "2.0.0",
        "deployment": "railway",
        "services": {
            "production_mode": PRODUCTION_READY,
            "routes_available": ROUTES_AVAILABLE,
            "middleware_available": MIDDLEWARE_AVAILABLE
        }
    }

@app.get("/admin")
async def admin_panel():
    """Admin panel endpoint"""
    html_path = Path(__file__).parent / "web" / "templates" / "admin_dashboard.html"
    if html_path.exists():
        with open(html_path, 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return {"message": "Admin panel not available"}

if __name__ == "__main__":
    # Get port from environment or default to 8000
    # Handle Railway's PORT environment variable properly
    port_str = os.getenv("PORT", "8000")
    try:
        port = int(port_str)
    except ValueError:
        print(f"⚠️  Invalid PORT value: {port_str}, using default 8000")
        port = 8000
    
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting Kolekt on {host}:{port}")
    print(f"📊 Production mode: {PRODUCTION_READY}")
    print(f"🔗 Routes available: {ROUTES_AVAILABLE}")
    print(f"🛡️  Middleware available: {MIDDLEWARE_AVAILABLE}")
    print(f"🚂 Railway deployment: Ready")
    
    uvicorn.run(
        "start_kolekt:app",
        host=host,
        port=port,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False,
        log_level="info"
    )
