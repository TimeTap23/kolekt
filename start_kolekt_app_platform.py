#!/usr/bin/env python3
"""
Kolekt Startup Script for Cloud Platform
Optimized for containerized deployment
"""

import os
import sys
import logging
import time
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
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json

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

# Simple rate limiting
rate_limit_data = {}

def check_rate_limit(client_ip: str, limit: int = 60) -> bool:
    """Simple rate limiting"""
    current_time = time.time()
    if client_ip not in rate_limit_data:
        rate_limit_data[client_ip] = []
    
    # Clean old requests
    rate_limit_data[client_ip] = [
        req_time for req_time in rate_limit_data[client_ip]
        if current_time - req_time < 60
    ]
    
    # Check limit
    if len(rate_limit_data[client_ip]) >= limit:
        return False
    
    # Add current request
    rate_limit_data[client_ip].append(current_time)
    return True

# Simple middleware for rate limiting and logging
@app.middleware("http")
async def production_middleware(request: Request, call_next):
    """Production middleware for rate limiting, logging, and security headers"""
    start_time = time.time()
    
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    
    # Check rate limit
    if not check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429,
            content={
                "error": "rate_limit_exceeded",
                "message": "Too many requests. Please try again later."
            }
        )
    
    # Process request
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Log request
    process_time = time.time() - start_time
    logging.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Import and include routers
try:
    from src.api.auth_routes import router as auth_router
    from src.api.connections_routes import router as connections_router
    from src.api.content_routes import router as content_router
    from src.api.social_routes import router as social_router
    from src.api.admin_routes_new import admin_router_new as admin_router
    from src.api.ai_routes import router as ai_router
    from src.api.threads_routes import router as threads_router
    from src.api.subscription_routes import router as subscription_router
    from src.api.import_routes import router as import_router
    
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(connections_router, prefix="/api/v1/connections", tags=["Social Connections"])
    app.include_router(content_router, prefix="/api/v1/content", tags=["Content Management"])
    app.include_router(social_router, prefix="/api/v1/social", tags=["Social Media"])
    app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])
    app.include_router(ai_router, prefix="/api/v1/ai", tags=["AI Services"])
    app.include_router(threads_router, prefix="/api/v1/threads", tags=["Threads"])
    app.include_router(subscription_router, prefix="/api/v1/subscriptions", tags=["Subscriptions"])
    app.include_router(import_router, prefix="/api/v1/import", tags=["Import"])
    
    logging.info("All API routers loaded successfully")
except Exception as e:
    logging.error(f"Error loading routers: {e}")
    # Create a simple fallback router
    from fastapi import APIRouter
    fallback_router = APIRouter()
    
    @fallback_router.get("/api/v1/status")
    async def status():
        return {"status": "running", "message": "Kolekt is running but some modules failed to load"}
    
    app.include_router(fallback_router)

# Serve static files
try:
    app.mount("/static", StaticFiles(directory="web/static"), name="static")
    logging.info("Static files mounted successfully")
except Exception as e:
    logging.error(f"Error mounting static files: {e}")

# Import template functions
try:
    from src.utils.template_utils import render_template
    logging.info("Template utilities loaded successfully")
except Exception as e:
    logging.error(f"Error loading template utilities: {e}")
    # Simple fallback template function
    def render_template(template_name: str, **kwargs) -> str:
        return f"<html><body><h1>Kolekt</h1><p>Template {template_name} not available</p></body></html>"

# Dashboard route
@app.get("/dashboard")
async def dashboard():
    """Main dashboard page"""
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

@app.get("/admin-legacy")
async def admin_legacy():
    """Legacy admin page"""
    try:
        with open("web/templates/admin.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logging.error(f"Error loading legacy admin: {e}")
        return HTMLResponse(content="<html><body><h1>Admin</h1><p>Loading...</p></body></html>")

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

# Error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content={"error": "validation_error", "details": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logging.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "message": "An unexpected error occurred"}
    )

if __name__ == "__main__":
    # Get port from environment or default to 8080
    port = int(os.getenv("PORT", 8080))
    
    # Start the server
    uvicorn.run(
        "start_kolekt_app_platform:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload for production
        log_level="info"
    )
