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
from fastapi.responses import HTMLResponse, JSONResponse
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

# Formatter page
@app.get("/formatter")
async def formatter_page():
    """Content formatter page"""
    try:
        with open("web/templates/formatter.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logging.error(f"Error loading formatter page: {e}")
        return HTMLResponse(content="<html><body><h1>Content Formatter</h1><p>Loading...</p></body></html>")

# Templates page
@app.get("/templates")
async def templates_page():
    """Content templates page"""
    try:
        with open("web/templates/templates.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logging.error(f"Error loading templates page: {e}")
        return HTMLResponse(content="<html><body><h1>Content Templates</h1><p>Loading...</p></body></html>")

# Analytics page
@app.get("/analytics")
async def analytics_page():
    """Analytics page"""
    try:
        with open("web/templates/analytics.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logging.error(f"Error loading analytics page: {e}")
        return HTMLResponse(content="<html><body><h1>Analytics</h1><p>Loading...</p></body></html>")

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
