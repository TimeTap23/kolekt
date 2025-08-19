#!/usr/bin/env python3
"""
Production-Ready Kolekt Startup Script
Simplified version with essential production features
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

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/kolekt.log'),
        logging.StreamHandler()
    ]
)

# Create logs directory
Path("logs").mkdir(exist_ok=True)

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
    
    # Log request
    logging.info(f"Request: {request.method} {request.url.path} from {client_ip}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Response-Time"] = f"{duration:.3f}s"
    
    # Log response
    logging.info(f"Response: {response.status_code} - {duration:.3f}s")
    
    return response

# Error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logging.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Invalid request data",
            "details": exc.errors()
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logging.warning(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logging.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "An unexpected error occurred"
        }
    )

# Mount static files
static_path = Path(__file__).parent / "web" / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Define routes
@app.get("/")
async def root():
    html_path = Path(__file__).parent / "web" / "templates" / "index.html"
    if html_path.exists():
        with open(html_path, 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return {"message": "Kolekt API is running", "status": "healthy"}

@app.get("/admin")
async def admin_panel():
    html_path = Path(__file__).parent / "web" / "templates" / "admin.html"
    if html_path.exists():
        with open(html_path, 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return {"message": "Admin panel not found", "status": "error"}

@app.get("/dashboard")
async def dashboard():
    html_path = Path(__file__).parent / "web" / "templates" / "dashboard.html"
    if html_path.exists():
        with open(html_path, 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        return {"message": "Dashboard not found", "status": "error"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Kolekt is running"}

def main():
    """Start Kolekt with production configuration"""
    
    print("🚀 Starting Kolekt (Production Mode)...")
    print("=" * 50)
    
    # Check if .env exists
    if not Path(".env").exists():
        print("❌ .env file not found. Please run setup first.")
        return
    
    # Check required environment variables
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY', 
        'SUPABASE_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please run 'python setup_supabase.py' first.")
        return
    
    print("✅ Environment configuration verified")
    
    # Meta credentials are optional
    meta_configured = bool(os.getenv('META_APP_ID') and os.getenv('META_APP_SECRET'))
    if not meta_configured:
        print("ℹ️  Meta credentials not found; Instagram/Facebook integration is disabled")
    
    # Set default values
    os.environ.setdefault('SECRET_KEY', 'kolekt-dev-secret-key-change-in-production')
    os.environ.setdefault('DEBUG', 'False')
    os.environ.setdefault('HOST', '127.0.0.1')
    os.environ.setdefault('PORT', '8000')
    
    # Include API routers
    try:
        from src.api.routes import api_router
        app.include_router(api_router, prefix="/api/v1")
        print("✅ API routes loaded successfully")
    except Exception as e:
        print(f"⚠️  API routes not loaded: {e}")
    
    # Add simple admin endpoints
    @app.get("/api/v1/admin/dashboard")
    async def admin_dashboard():
        """Simple admin dashboard endpoint"""
        try:
            from src.services.supabase import supabase_service
            
            users_response = supabase_service.client.table("profiles").select("id").execute()
            total_users = len(users_response.data)
            
            return {
                "success": True,
                "stats": {
                    "total_users": total_users,
                    "active_users": total_users,
                    "total_kolekts": 0,
                    "total_api_calls": 0,
                    "storage_used": 0.0,
                    "revenue_monthly": 0.0
                },
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logging.error(f"Admin dashboard error: {e}")
            return {"success": False, "error": str(e)}
    
    # User Authentication Endpoints
    @app.post("/api/v1/auth/login")
    async def user_login(request: Request):
        """User login endpoint"""
        start_time = time.time()
        
        try:
            from src.services.supabase import supabase_service
            
            # Parse JSON request body
            request_data = await request.json()
            email = request_data.get("email")
            password = request_data.get("password")
            
            # Find user by email
            response = supabase_service.client.table("profiles").select("*").eq("email", email).execute()
            
            if not response.data:
                logging.warning(f"Failed login attempt for {email}")
                return {"success": False, "error": "Invalid email or password"}
            
            user = response.data[0]
            
            # Check if user is active
            if not user.get("is_active", True):
                return {"success": False, "error": "Account is deactivated"}
            
            # Check password
            if user.get("password_hash"):
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                if password_hash != user["password_hash"]:
                    logging.warning(f"Failed login attempt for {email}")
                    return {"success": False, "error": "Invalid email or password"}
            
            # Update last login
            supabase_service.client.table("profiles").update({
                "last_login": datetime.utcnow().isoformat(),
                "login_count": user.get("login_count", 0) + 1
            }).eq("id", user["id"]).execute()
            
            duration = time.time() - start_time
            logging.info(f"Successful login for {email} in {duration:.3f}s")
            
            return {
                "success": True,
                "access_token": "dev-access-token-" + user["id"],
                "refresh_token": "dev-refresh-token-" + user["id"],
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "name": user.get("name", "User"),
                    "role": user.get("role", "user")
                }
            }
                
        except Exception as e:
            duration = time.time() - start_time
            logging.error(f"Login error: {e} in {duration:.3f}s")
            return {"success": False, "error": str(e)}
    
    @app.post("/api/v1/auth/register")
    async def user_register(request: Request):
        """User registration endpoint"""
        try:
            from src.services.supabase import supabase_service
            import uuid
            
            # Parse JSON request body
            request_data = await request.json()
            email = request_data.get("email")
            password = request_data.get("password")
            name = request_data.get("name", "")
            
            # Check if user already exists
            existing_response = supabase_service.client.table("profiles").select("id").eq("email", email).execute()
            if existing_response.data:
                return {"success": False, "error": "User already exists"}
            
            # Create new user
            user_id = str(uuid.uuid4())
            password_hash = hashlib.sha256(password.encode()).hexdigest() if password else None
            
            new_user = {
                "id": user_id,
                "email": email,
                "name": name,
                "role": "user",
                "plan": "free",
                "is_active": True,
                "is_verified": False,
                "email_verified": False,
                "last_login": None,
                "login_count": 0,
                "password_hash": password_hash
            }
            
            response = supabase_service.client.table("profiles").insert(new_user).execute()
            
            if response.data:
                logging.info(f"New user registered: {email}")
                return {
                    "success": True,
                    "access_token": "dev-access-token-" + user_id,
                    "refresh_token": "dev-refresh-token-" + user_id,
                    "user": {
                        "id": user_id,
                        "email": email,
                        "name": name,
                        "role": "user"
                    }
                }
            else:
                return {"success": False, "error": "Failed to create user"}
                
        except Exception as e:
            logging.error(f"Registration error: {e}")
            return {"success": False, "error": str(e)}
    
    @app.post("/api/v1/auth/logout")
    async def user_logout(request: Request):
        """User logout endpoint"""
        try:
            return {"success": True, "message": "Logged out successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/v1/auth/me")
    async def get_current_user(request: Request):
        """Get current user info endpoint"""
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return {"success": False, "error": "No valid authorization header"}
            
            access_token = auth_header.replace("Bearer ", "")
            
            # Extract user ID from dev token
            if access_token and access_token.startswith("dev-access-token-"):
                user_id = access_token.replace("dev-access-token-", "")
                
                from src.services.supabase import supabase_service
                response = supabase_service.client.table("profiles").select("*").eq("id", user_id).execute()
                
                if response.data:
                    user = response.data[0]
                    return {
                        "success": True,
                        "user": {
                            "id": user["id"],
                            "email": user["email"],
                            "name": user.get("name", "User"),
                            "role": user.get("role", "user"),
                            "plan": user.get("plan", "free")
                        }
                    }
            
            return {"success": False, "error": "Invalid token"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Social Media Integration Endpoints
    @app.get("/api/v1/social/status")
    async def social_status():
        """Get social media integration status"""
        return {
            "threads": {"connected": True, "status": "active"},
            "instagram": {"connected": bool(os.getenv('META_APP_ID')), "status": "configured" if os.getenv('META_APP_ID') else "not_configured"},
            "facebook": {"connected": bool(os.getenv('META_APP_ID')), "status": "configured" if os.getenv('META_APP_ID') else "not_configured"}
        }
    
    @app.get("/api/v1/social/instagram/oauth-url")
    async def instagram_oauth_url():
        """Get Instagram OAuth URL"""
        meta_app_id = os.getenv('META_APP_ID')
        if not meta_app_id:
            return {"success": False, "error": "Instagram integration not configured"}
        
        redirect_uri = "http://127.0.0.1:8000/api/v1/social/instagram/callback"
        oauth_url = f"https://www.facebook.com/v18.0/dialog/oauth?client_id={meta_app_id}&redirect_uri={redirect_uri}&scope=instagram_basic,instagram_content_publish,pages_show_list"
        
        return {"success": True, "oauth_url": oauth_url}
    
    @app.get("/api/v1/social/instagram/callback")
    async def instagram_callback(code: str | None = None, error: str | None = None):
        """Handle Instagram OAuth callback"""
        if error:
            return {"success": False, "error": f"OAuth error: {error}"}
        
        if not code:
            return {"success": False, "error": "No authorization code received"}
        
        try:
            meta_app_id = os.getenv('META_APP_ID')
            meta_app_secret = os.getenv('META_APP_SECRET')
            
            if not meta_app_id or not meta_app_secret:
                return {"success": False, "error": "Meta credentials not configured"}
            
            # Exchange code for access token
            token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
            token_data = {
                "client_id": meta_app_id,
                "client_secret": meta_app_secret,
                "code": code,
                "redirect_uri": "http://127.0.0.1:8000/api/v1/social/instagram/callback"
            }
            
            token_response = requests.post(token_url, data=token_data)
            token_response.raise_for_status()
            token_info = token_response.json()
            access_token = token_info.get("access_token")
            
            if not access_token:
                return {"success": False, "error": "Failed to get access token"}
            
            # Get user info
            user_url = f"https://graph.facebook.com/v18.0/me?access_token={access_token}"
            user_response = requests.get(user_url)
            user_response.raise_for_status()
            user_info = user_response.json()
            
            # Get Instagram business accounts
            accounts_url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={access_token}"
            accounts_response = requests.get(accounts_url)
            accounts_response.raise_for_status()
            accounts_info = accounts_response.json()
            
            logging.info(f"Instagram connected successfully for user {user_info.get('id')}")
            
            return {
                "success": True,
                "message": "Instagram connected successfully!",
                "user_info": user_info,
                "accounts": accounts_info.get('data', []),
                "access_token": access_token[:20] + "..."
            }
            
        except Exception as e:
            logging.error(f"Instagram callback error: {e}")
            return {"success": False, "error": str(e)}
    
    print("✅ Production features enabled:")
    print("   - Rate limiting (60 requests/minute)")
    print("   - Security headers")
    print("   - Comprehensive logging")
    print("   - Error handling")
    print("   - Performance monitoring")
    
    print(f"\n🌐 Starting server on http://{os.getenv('HOST', '127.0.0.1')}:{os.getenv('PORT', '8000')}")
    print("Press Ctrl+C to stop")
    
    # Start server
    uvicorn.run(
        app,
        host=os.getenv('HOST', '127.0.0.1'),
        port=int(os.getenv('PORT', '8000')),
        log_level="info"
    )

if __name__ == "__main__":
    main()
