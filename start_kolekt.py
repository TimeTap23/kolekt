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

# Railway-specific fix: Handle direct uvicorn calls
if len(sys.argv) > 1 and 'uvicorn' in sys.argv[0]:
    # If called directly by uvicorn, handle PORT properly
    port_str = os.getenv("PORT", "8000")
    try:
        port = int(port_str)
    except ValueError:
        port = 8000
    
    # Set the port in environment for uvicorn
    os.environ["PORT"] = str(port)
    print(f"🚂 Railway: Fixed PORT to {port}")

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
    from src.api.routes import api_router
    ROUTES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  API routes not available: {e}")
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

# Mount static files
static_path = Path(__file__).parent / "web" / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

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

# Define page routes FIRST (before API routes to prevent conflicts)
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

@app.get("/test-preview")
async def test_preview():
    """Test preview page"""
    return {"message": "Test preview route works!"}

@app.get("/formatter-preview")
async def formatter_preview():
    """Formatter preview page"""
    html_path = Path(__file__).parent / "web" / "templates" / "formatter-preview.html"
    if html_path.exists():
        with open(html_path, 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return {"message": "Formatter preview not available"}

@app.get("/templates-preview")
async def templates_preview():
    """Templates preview page"""
    html_path = Path(__file__).parent / "web" / "templates" / "templates-preview.html"
    if html_path.exists():
        with open(html_path, 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return {"message": "Templates preview not available"}

@app.get("/analytics-preview")
async def analytics_preview():
    """Analytics preview page"""
    html_path = Path(__file__).parent / "web" / "templates" / "analytics-preview.html"
    if html_path.exists():
        with open(html_path, 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return {"message": "Analytics preview not available"}

@app.get("/review-queue-preview")
async def review_queue_preview():
    """Review queue preview page"""
    html_path = Path(__file__).parent / "web" / "templates" / "review-queue-preview.html"
    if html_path.exists():
        with open(html_path, 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return {"message": "Review queue preview not available"}

@app.get("/formatter")
async def formatter():
    """Formatter application page"""
    html_path = Path(__file__).parent / "web" / "templates" / "formatter.html"
    if html_path.exists():
        with open(html_path, 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return {"message": "Formatter not available"}

@app.get("/templates")
async def templates():
    """Templates application page"""
    html_path = Path(__file__).parent / "web" / "templates" / "templates.html"
    if html_path.exists():
        with open(html_path, 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return {"message": "Templates not available"}

@app.get("/analytics")
async def analytics():
    """Analytics application page"""
    html_path = Path(__file__).parent / "web" / "templates" / "analytics.html"
    if html_path.exists():
        with open(html_path, 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return {"message": "Analytics not available"}

@app.get("/social-manager")
async def social_manager():
    """Social manager application page"""
    html_path = Path(__file__).parent / "web" / "templates" / "social-manager.html"
    if html_path.exists():
        with open(html_path, 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return {"message": "Social manager not available"}

@app.get("/team-management")
async def team_management():
    """Team management application page"""
    html_path = Path(__file__).parent / "web" / "templates" / "team-management.html"
    if html_path.exists():
        with open(html_path, 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return {"message": "Team management not available"}

@app.get("/login")
async def login_page():
    """Login page"""
    html_path = Path(__file__).parent / "web" / "templates" / "login.html"
    if html_path.exists():
        with open(html_path, 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return {"message": "Login page not available"}

@app.get("/register")
async def register_page():
    """Registration page"""
    html_path = Path(__file__).parent / "web" / "templates" / "register.html"
    if html_path.exists():
        with open(html_path, 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return {"message": "Registration page not available"}

@app.get("/forgot-password")
async def forgot_password_page():
    """Forgot password page"""
    html_path = Path(__file__).parent / "web" / "templates" / "forgot-password.html"
    if html_path.exists():
        with open(html_path, 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return {"message": "Forgot password page not available"}

# Include API routes AFTER page routes to prevent conflicts
if ROUTES_AVAILABLE:
    app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    # This block is for local development only
    # Railway uses start.py for production deployment
    import uvicorn
    
    # Get port from environment or default to 8000
    port_str = os.getenv("PORT", "8000")
    try:
        port = int(port_str)
    except ValueError:
        print(f"⚠️  Invalid PORT value: {port_str}, using default 8000")
        port = 8000
    
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting Kolekt (local development) on {host}:{port}")
    print(f"📊 Production mode: {PRODUCTION_READY}")
    print(f"🔗 Routes available: {ROUTES_AVAILABLE}")
    print(f"🛡️  Middleware available: {MIDDLEWARE_AVAILABLE}")
    
    uvicorn.run(
        "start_kolekt:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
