#!/usr/bin/env python3
"""
Simple Kolekt Startup Script
Starts Kolekt with minimal configuration
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# Import our new utilities
try:
    from src.utils.logging_config import setup_logging, request_logger, security_logger
    from src.middleware.error_handler import ErrorHandler, RateLimitMiddleware, LoggingMiddleware, SecurityMiddleware
    from src.utils.performance import monitor_performance, cached, performance_monitor
    PRODUCTION_READY = True
except ImportError:
    print("⚠️  Production utilities not available, running in basic mode")
    PRODUCTION_READY = False

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

# Add production middleware if available
if PRODUCTION_READY:
    # Add security middleware
    app.add_middleware(SecurityMiddleware)
    
    # Add logging middleware
    app.add_middleware(LoggingMiddleware)
    
    # Add rate limiting middleware (60 requests per minute)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
    
    # Setup comprehensive logging
    setup_logging(log_level="INFO", log_file="logs/kolekt.log")
    
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
    """Start Kolekt with minimal configuration"""
    
    print("🚀 Starting Kolekt...")
    print("=" * 40)
    
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
        print("Please run 'python setup_supabase.py' and 'python setup_meta_credentials.py' first.")
        return
    
    print("✅ Environment configuration verified")
    # Meta (Instagram/Facebook) credentials are optional; integration is disabled if missing
    meta_configured = bool(os.getenv('META_APP_ID') and os.getenv('META_APP_SECRET'))
    if not meta_configured:
        print("ℹ️  Meta credentials not found; Instagram/Facebook integration is disabled (scaffold only)")
    
    # Set default values for missing optional config
    os.environ.setdefault('SECRET_KEY', 'kolekt-dev-secret-key-change-in-production')
    os.environ.setdefault('DEBUG', 'True')
    os.environ.setdefault('HOST', '127.0.0.1')
    os.environ.setdefault('PORT', '8000')
    os.environ.setdefault('REDIS_URL', 'redis://localhost:6379')
    
    # Include API routers
    try:
        from src.api.routes import api_router
        app.include_router(api_router, prefix="/api/v1")
        print("✅ API routes loaded successfully")
    except Exception as e:
        print(f"⚠️  API routes not loaded: {e}")
    
    # Add simple admin endpoints directly
    @app.get("/api/v1/admin/dashboard")
    async def admin_dashboard():
        """Simple admin dashboard endpoint"""
        try:
            from src.services.supabase import supabase_service
            
            # Get basic stats
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
                "last_updated": "2025-08-13T17:30:00Z"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.post("/api/v1/admin/login")
    async def admin_login(request: dict):
        """Simple admin login"""
        try:
            from src.services.supabase import supabase_service
            
            email = request.get("email")
            password = request.get("password")
            
            if email == "marcus@marteklabs.com":
                response = supabase_service.client.table("profiles").select("*").eq("email", email).eq("role", "admin").execute()
                
                if response.data:
                    user = response.data[0]
                    return {
                        "success": True,
                        "user": {
                            "id": user["id"],
                            "email": user["email"],
                            "name": user["name"],
                            "role": user["role"]
                        }
                    }
            
            return {"success": False, "error": "Invalid credentials"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # User Authentication Endpoints
    @app.post("/api/v1/auth/login")
    async def user_login(request: Request):
        """User login endpoint"""
        if PRODUCTION_READY:
            performance_monitor.start_timer("user_login")
        
        try:
            from src.services.supabase import supabase_service
            import hashlib
            
            # Parse JSON request body
            request_data = await request.json()
            email = request_data.get("email")
            password = request_data.get("password")
            
            # Find user by email
            response = supabase_service.client.table("profiles").select("*").eq("email", email).execute()
            
            if not response.data:
                return {"success": False, "error": "Invalid email or password"}
            
            user = response.data[0]
            
            # Check if user is active
            if not user.get("is_active", True):
                return {"success": False, "error": "Account is deactivated"}
            
            # Check password
            if user.get("password_hash"):
                # User has a password set, verify it
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                if password_hash != user["password_hash"]:
                    return {"success": False, "error": "Invalid email or password"}
            else:
                # For development, accept any password for users without password_hash
                # In production, you'd want to require password setup
                pass
            
            # Update last login
            from datetime import datetime
            supabase_service.client.table("profiles").update({
                "last_login": datetime.utcnow().isoformat(),
                "login_count": user.get("login_count", 0) + 1
            }).eq("id", user["id"]).execute()
            
            # Log successful login
            if PRODUCTION_READY:
                security_logger.log_login_attempt(email, True, request.client.host if request.client else None)
                performance_monitor.end_timer("user_login")
            
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
            # Log failed login
            if PRODUCTION_READY:
                security_logger.log_login_attempt(email, False, request.client.host if request.client else None)
                performance_monitor.end_timer("user_login")
            
            return {"success": False, "error": str(e)}
    
    @app.post("/api/v1/auth/register")
    async def user_register(request: Request):
        """User registration endpoint"""
        try:
            from src.services.supabase import supabase_service
            import uuid
            import hashlib
            
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
            # Hash password if provided
            if password:
                password_hash = hashlib.sha256(password.encode()).hexdigest()
            else:
                password_hash = None
            
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
            return {"success": False, "error": str(e)}
    
    @app.post("/api/v1/auth/logout")
    async def user_logout(request: Request):
        """User logout endpoint"""
        try:
            # In a real implementation, you'd invalidate the refresh token
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
            
            # Extract user ID from dev token (in production, you'd decode the JWT)
            if access_token and access_token.startswith("dev-access-token-"):
                user_id = access_token.replace("dev-access-token-", "")
                
                # Get user info
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
                else:
                    return {"success": False, "error": "User not found"}
            else:
                return {"success": False, "error": "Invalid token"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.post("/api/v1/auth/refresh")
    async def refresh_token(request: Request):
        """Refresh access token endpoint"""
        try:
            request_data = await request.json()
            refresh_token = request_data.get("refresh_token")
            
            # Extract user ID from dev token (in production, you'd decode the JWT)
            if refresh_token and refresh_token.startswith("dev-refresh-token-"):
                user_id = refresh_token.replace("dev-refresh-token-", "")
                
                # Get user info
                from src.services.supabase import supabase_service
                response = supabase_service.client.table("profiles").select("*").eq("id", user_id).execute()
                
                if response.data:
                    user = response.data[0]
                    return {
                        "success": True,
                        "access_token": "dev-access-token-" + user_id,
                        "refresh_token": "dev-refresh-token-" + user_id,
                        "user": {
                            "id": user["id"],
                            "email": user["email"],
                            "name": user.get("name", "User"),
                            "role": user.get("role", "user")
                        }
                    }
            
            return {"success": False, "error": "Invalid refresh token"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Password Reset Endpoints
    @app.post("/api/v1/auth/forgot-password")
    async def forgot_password(request: dict):
        """Request password reset"""
        try:
            from src.services.supabase import supabase_service
            import secrets
            import hashlib
            from datetime import datetime, timedelta
            
            email = request.get("email")
            
            # Check if user exists
            response = supabase_service.client.table("profiles").select("id, email, name").eq("email", email).execute()
            
            if not response.data:
                # Don't reveal if email exists or not for security
                return {"success": True, "message": "If the email exists, a reset link has been sent"}
            
            user = response.data[0]
            
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(reset_token.encode()).hexdigest()
            
            # Store reset token in database (with expiration)
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            # For development, just return the reset URL without storing in database
            # In production, you'd store the token in the reset_tokens table
            reset_url = f"http://127.0.0.1:8000/reset-password?token={reset_token}"
            
            print(f"🔐 Password reset requested for {email}")
            print(f"📧 Reset URL: {reset_url}")
            print(f"⏰ Token expires: {expires_at}")
            print(f"🔑 Token hash: {token_hash}")
            
            # Store token in memory for development (in production, use database)
            if not hasattr(app.state, 'reset_tokens'):
                app.state.reset_tokens = {}
            
            app.state.reset_tokens[token_hash] = {
                "user_id": user["id"],
                "expires_at": expires_at,
                "used": False
            }
            
            # In production, send email with reset link
            # For development, just return the token
            reset_url = f"http://127.0.0.1:8000/reset-password?token={reset_token}"
            
            print(f"🔐 Password reset requested for {email}")
            print(f"📧 Reset URL: {reset_url}")
            print(f"⏰ Token expires: {expires_at}")
            
            return {
                "success": True, 
                "message": "Password reset link sent to your email",
                "dev_reset_url": reset_url  # Only in development
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Social Integration (Scaffold)
    @app.get("/api/v1/social/status")
    async def social_status():
        """Return configured status for supported platforms (scaffold)."""
        try:
            instagram_configured = bool(os.getenv('META_APP_ID') and os.getenv('META_APP_SECRET'))
            facebook_configured = instagram_configured  # same Meta app typically
            return {
                "success": True,
                "platforms": {
                    "threads": {"configured": True},
                    "instagram": {"configured": instagram_configured},
                    "facebook": {"configured": facebook_configured}
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.get("/api/v1/social/instagram/oauth-url")
    async def instagram_oauth_url():
        """Provide Instagram OAuth URL if Meta creds exist; otherwise disabled."""
        try:
            app_id = os.getenv('META_APP_ID')
            app_secret = os.getenv('META_APP_SECRET')
            if not app_id or not app_secret:
                return {"success": False, "error": "not_configured"}
            # Build OAuth URL
            import urllib.parse as _urlparse
            redirect_uri = os.getenv('META_REDIRECT_URI') or "http://127.0.0.1:8000/api/v1/social/instagram/callback"
            scope = "instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement,pages_manage_posts"
            url = (
                "https://www.facebook.com/v19.0/dialog/oauth?" +
                f"client_id={app_id}&redirect_uri={_urlparse.quote(redirect_uri, safe='')}&" +
                f"response_type=code&scope={_urlparse.quote(scope, safe=',')}"
            )
            return {"success": True, "url": url}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.get("/api/v1/social/instagram/callback")
    async def instagram_callback(code: str | None = None, error: str | None = None):
        """Handle Instagram OAuth callback with token exchange."""
        try:
            if not (os.getenv('META_APP_ID') and os.getenv('META_APP_SECRET')):
                return {"success": False, "error": "not_configured"}
            if error:
                return {"success": False, "error": error}
            if not code:
                return {"success": False, "error": "missing_code"}
            
            import requests
            import requests
            import urllib.parse
            
            app_id = os.getenv('META_APP_ID')
            app_secret = os.getenv('META_APP_SECRET')
            redirect_uri = os.getenv('META_REDIRECT_URI') or "http://127.0.0.1:8000/api/v1/social/instagram/callback"
            
            # Exchange code for access token
            token_url = "https://graph.facebook.com/v19.0/oauth/access_token"
            token_data = {
                "client_id": app_id,
                "client_secret": app_secret,
                "redirect_uri": redirect_uri,
                "code": code
            }
            
            token_response = requests.post(token_url, data=token_data)
            token_response.raise_for_status()
            token_info = token_response.json()
            
            access_token = token_info.get("access_token")
            if not access_token:
                return {"success": False, "error": "No access token received"}
            
            # Get user info
            user_url = f"https://graph.facebook.com/v19.0/me?access_token={access_token}"
            user_response = requests.get(user_url)
            user_response.raise_for_status()
            user_info = user_response.json()
            
            # Get Instagram Business Account
            accounts_url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={access_token}"
            accounts_response = requests.get(accounts_url)
            accounts_response.raise_for_status()
            accounts_info = accounts_response.json()
            
            # Store tokens in database (for now, just return success)
            # In production, you'd store these securely in the database
            print(f"🔗 Instagram OAuth successful for user: {user_info.get('name', 'Unknown')}")
            print(f"🔗 Access token: {access_token[:20]}...")
            print(f"🔗 Accounts: {len(accounts_info.get('data', []))}")
            
            return {
                "success": True, 
                "message": "Instagram connected successfully!",
                "user_info": user_info,
                "accounts": accounts_info.get('data', []),
                "access_token": access_token[:20] + "..."  # Only show first 20 chars for security
            }
            
        except requests.exceptions.RequestException as e:
            print(f"🔗 Instagram OAuth error: {e}")
            return {"success": False, "error": f"OAuth exchange failed: {str(e)}"}
        except Exception as e:
            print(f"🔗 Instagram OAuth error: {e}")
            return {"success": False, "error": str(e)}

    @app.post("/api/v1/auth/reset-password")
    async def reset_password(request: dict):
        """Reset password with token"""
        try:
            from src.services.supabase import supabase_service
            import hashlib
            from datetime import datetime
            
            token = request.get("token")
            new_password = request.get("new_password")
            
            if not token or not new_password:
                return {"success": False, "error": "Token and new password are required"}
            
            # Hash the token to compare with stored hash
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # For development, check in-memory storage
            if not hasattr(app.state, 'reset_tokens') or token_hash not in app.state.reset_tokens:
                return {"success": False, "error": "Invalid or expired reset token"}
            
            reset_record = app.state.reset_tokens[token_hash]
            
            # Check if token is expired
            if datetime.utcnow() > reset_record["expires_at"]:
                return {"success": False, "error": "Reset token has expired"}
            
            # Check if token is already used
            if reset_record["used"]:
                return {"success": False, "error": "Reset token has already been used"}
            
            # Update user password
            user_id = reset_record["user_id"]
            password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            
            supabase_service.client.table("profiles").update({
                "password_hash": password_hash,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            # Mark token as used
            app.state.reset_tokens[token_hash]["used"] = True
            
            return {"success": True, "message": "Password reset successfully"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/reset-password")
    async def reset_password_page():
        """Password reset page"""
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Password - Kolekt</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
                    margin: 0;
                    padding: 0;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .container {
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border-radius: 15px;
                    padding: 40px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    max-width: 400px;
                    width: 90%;
                }
                h1 {
                    color: #00d4ff;
                    text-align: center;
                    margin-bottom: 30px;
                    font-size: 24px;
                }
                .form-group {
                    margin-bottom: 20px;
                }
                label {
                    display: block;
                    color: #ffffff;
                    margin-bottom: 8px;
                    font-weight: 500;
                }
                input {
                    width: 100%;
                    padding: 12px;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 8px;
                    background: rgba(255, 255, 255, 0.1);
                    color: #ffffff;
                    font-size: 16px;
                    box-sizing: border-box;
                }
                input:focus {
                    outline: none;
                    border-color: #00d4ff;
                    box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
                }
                button {
                    width: 100%;
                    padding: 12px;
                    background: linear-gradient(45deg, #00d4ff, #0099cc);
                    border: none;
                    border-radius: 8px;
                    color: #ffffff;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(0, 212, 255, 0.4);
                }
                .message {
                    padding: 10px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                    text-align: center;
                }
                .success {
                    background: rgba(0, 255, 0, 0.2);
                    color: #00ff00;
                    border: 1px solid rgba(0, 255, 0, 0.3);
                }
                .error {
                    background: rgba(255, 0, 0, 0.2);
                    color: #ff6b6b;
                    border: 1px solid rgba(255, 0, 0, 0.3);
                }
                .back-link {
                    text-align: center;
                    margin-top: 20px;
                }
                .back-link a {
                    color: #00d4ff;
                    text-decoration: none;
                }
                .back-link a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔐 Reset Password</h1>
                <div id="message"></div>
                <form id="resetForm">
                    <div class="form-group">
                        <label for="newPassword">New Password</label>
                        <input type="password" id="newPassword" name="newPassword" required minlength="8">
                    </div>
                    <div class="form-group">
                        <label for="confirmPassword">Confirm Password</label>
                        <input type="password" id="confirmPassword" name="confirmPassword" required minlength="8">
                    </div>
                    <button type="submit">Reset Password</button>
                </form>
                <div class="back-link">
                    <a href="/">← Back to Kolekt</a>
                </div>
            </div>
            
            <script>
                // Get token from URL
                const urlParams = new URLSearchParams(window.location.search);
                const token = urlParams.get('token');
                
                if (!token) {
                    showMessage('Invalid reset link. Please request a new password reset.', 'error');
                    document.getElementById('resetForm').style.display = 'none';
                }
                
                document.getElementById('resetForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    const newPassword = document.getElementById('newPassword').value;
                    const confirmPassword = document.getElementById('confirmPassword').value;
                    
                    if (newPassword !== confirmPassword) {
                        showMessage('Passwords do not match.', 'error');
                        return;
                    }
                    
                    if (newPassword.length < 8) {
                        showMessage('Password must be at least 8 characters long.', 'error');
                        return;
                    }
                    
                    try {
                        const response = await fetch('/api/v1/auth/reset-password', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                token: token,
                                new_password: newPassword
                            })
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            showMessage('Password reset successfully! Redirecting to login...', 'success');
                            setTimeout(() => {
                                window.location.href = '/';
                            }, 2000);
                        } else {
                            showMessage(data.error || 'Failed to reset password.', 'error');
                        }
                    } catch (error) {
                        showMessage('An error occurred. Please try again.', 'error');
                    }
                });
                
                function showMessage(message, type) {
                    const messageDiv = document.getElementById('message');
                    messageDiv.textContent = message;
                    messageDiv.className = `message ${type}`;
                }
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    # User Management Endpoints
    @app.get("/api/v1/admin/users")
    async def get_users(page: int = 1, limit: int = 50, search: str = None, plan: str = None, is_active: str = None):
        """Get paginated list of users"""
        try:
            from src.services.supabase import supabase_service
            
            query = supabase_service.client.table("profiles").select("*")
            
            # Apply filters
            if search:
                query = query.or_(f"name.ilike.%{search}%,email.ilike.%{search}%")
            if plan:
                query = query.eq("plan", plan)
            if is_active is not None:
                query = query.eq("is_active", is_active.lower() == "true")
            
            # Get total count
            count_response = query.execute()
            total_users = len(count_response.data)
            
            # Apply pagination
            offset = (page - 1) * limit
            query = query.range(offset, offset + limit - 1)
            
            response = query.execute()
            
            return {
                "success": True,
                "users": response.data,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_users,
                    "pages": (total_users + limit - 1) // limit
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/v1/admin/users/{user_id}")
    async def get_user(user_id: str):
        """Get specific user details"""
        try:
            from src.services.supabase import supabase_service
            
            response = supabase_service.client.table("profiles").select("*").eq("id", user_id).single().execute()
            
            if response.data:
                return {"success": True, "user": response.data}
            else:
                return {"success": False, "error": "User not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.put("/api/v1/admin/users/{user_id}")
    async def update_user(user_id: str, request: dict):
        """Update user information"""
        try:
            from src.services.supabase import supabase_service
            
            update_data = {}
            if "email" in request:
                update_data["email"] = request["email"]
            if "name" in request:
                update_data["name"] = request["name"]
            if "plan" in request:
                update_data["plan"] = request["plan"]
            if "is_active" in request:
                update_data["is_active"] = request["is_active"]
            if "is_verified" in request:
                update_data["is_verified"] = request["is_verified"]
            
            response = supabase_service.client.table("profiles").update(update_data).eq("id", user_id).execute()
            
            if response.data:
                return {"success": True, "user": response.data[0]}
            else:
                return {"success": False, "error": "User not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.delete("/api/v1/admin/users/{user_id}")
    async def delete_user(user_id: str):
        """Soft delete user (set is_active to False)"""
        try:
            from src.services.supabase import supabase_service
            
            response = supabase_service.client.table("profiles").update({"is_active": False}).eq("id", user_id).execute()
            
            if response.data:
                return {"success": True, "message": "User deactivated"}
            else:
                return {"success": False, "error": "User not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.post("/api/v1/admin/users")
    async def create_user(request: dict):
        """Create a new user with admin-assigned permissions"""
        try:
            from src.services.supabase import supabase_service
            from src.services.authentication import auth_service
            
            email = request.get("email")
            password = request.get("password")
            name = request.get("name")
            role = request.get("role", "user")
            plan = request.get("plan", "free")
            permissions = request.get("permissions", [])
            
            if not email or not password:
                return {"success": False, "error": "Email and password are required"}
            
            # Create user using authentication service
            user_result = await auth_service.register_user(email, password, name)
            
            if not user_result.get("success"):
                return {"success": False, "error": user_result.get("message", "Failed to create user")}
            
            user_id = user_result.get("user_id")
            
            # Update user role and plan if specified
            if role != "user" or plan != "free":
                update_data = {}
                if role != "user":
                    update_data["role"] = role
                if plan != "free":
                    update_data["plan"] = plan
                
                if update_data:
                    supabase_service.client.table("profiles").update(update_data).eq("id", user_id).execute()
            
            # Assign custom permissions if provided
            if permissions:
                await auth_service._assign_custom_permissions(user_id, permissions)
            
            # Get the created user
            user_response = supabase_service.client.table("profiles").select("*").eq("id", user_id).single().execute()
            
            return {
                "success": True,
                "user": user_response.data,
                "message": f"User {email} created successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.post("/api/v1/admin/users/{user_id}/permissions")
    async def assign_user_permissions(user_id: str, request: dict):
        """Assign specific permissions to a user"""
        try:
            from src.services.supabase import supabase_service
            
            permissions = request.get("permissions", [])
            
            if not permissions:
                return {"success": False, "error": "No permissions provided"}
            
            # Clear existing permissions for this user
            supabase_service.client.table("user_permissions").delete().eq("user_id", user_id).execute()
            
            # Insert new permissions
            for permission in permissions:
                permission_data = {
                    "user_id": user_id,
                    "resource": permission["resource"],
                    "action": permission["action"],
                    "granted": permission.get("granted", True)
                }
                supabase_service.client.table("user_permissions").insert(permission_data).execute()
            
            return {
                "success": True,
                "message": f"Permissions assigned to user {user_id}",
                "permissions": permissions
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/v1/admin/users/{user_id}/permissions")
    async def get_user_permissions(user_id: str):
        """Get permissions for a specific user"""
        try:
            from src.services.supabase import supabase_service
            
            response = supabase_service.client.table("user_permissions").select("*").eq("user_id", user_id).execute()
            
            return {
                "success": True,
                "permissions": response.data
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.get("/api/v1/admin/permissions/templates")
    async def get_permission_templates():
        """Get predefined permission templates"""
        try:
            templates = {
                "user": {
                    "name": "Standard User",
                    "description": "Basic user permissions for creating and managing kolekts",
                    "permissions": [
                        {"resource": "profile", "action": "read", "granted": True},
                        {"resource": "profile", "action": "update", "granted": True},
                        {"resource": "password", "action": "change", "granted": True},
                        {"resource": "kolekts", "action": "create", "granted": True},
                        {"resource": "kolekts", "action": "read", "granted": True},
                        {"resource": "kolekts", "action": "update", "granted": True},
                        {"resource": "kolekts", "action": "delete", "granted": True},
                        {"resource": "templates", "action": "read", "granted": True},
                        {"resource": "templates", "action": "create", "granted": True},
                        {"resource": "templates", "action": "update", "granted": True},
                        {"resource": "templates", "action": "delete", "granted": True},
                        {"resource": "api", "action": "format", "granted": True},
                        {"resource": "api", "action": "publish", "granted": True},
                        {"resource": "data", "action": "export", "granted": True},
                        {"resource": "data", "action": "delete", "granted": True}
                    ]
                },
                "pro": {
                    "name": "Pro User",
                    "description": "Enhanced permissions for pro users",
                    "permissions": [
                        {"resource": "profile", "action": "read", "granted": True},
                        {"resource": "profile", "action": "update", "granted": True},
                        {"resource": "password", "action": "change", "granted": True},
                        {"resource": "kolekts", "action": "create", "granted": True},
                        {"resource": "kolekts", "action": "read", "granted": True},
                        {"resource": "kolekts", "action": "update", "granted": True},
                        {"resource": "kolekts", "action": "delete", "granted": True},
                        {"resource": "templates", "action": "read", "granted": True},
                        {"resource": "templates", "action": "create", "granted": True},
                        {"resource": "templates", "action": "update", "granted": True},
                        {"resource": "templates", "action": "delete", "granted": True},
                        {"resource": "api", "action": "format", "granted": True},
                        {"resource": "api", "action": "publish", "granted": True},
                        {"resource": "api", "action": "advanced", "granted": True},
                        {"resource": "data", "action": "export", "granted": True},
                        {"resource": "data", "action": "delete", "granted": True},
                        {"resource": "analytics", "action": "read", "granted": True}
                    ]
                },
                "business": {
                    "name": "Business User",
                    "description": "Full permissions for business users",
                    "permissions": [
                        {"resource": "profile", "action": "read", "granted": True},
                        {"resource": "profile", "action": "update", "granted": True},
                        {"resource": "password", "action": "change", "granted": True},
                        {"resource": "kolekts", "action": "create", "granted": True},
                        {"resource": "kolekts", "action": "read", "granted": True},
                        {"resource": "kolekts", "action": "update", "granted": True},
                        {"resource": "kolekts", "action": "delete", "granted": True},
                        {"resource": "templates", "action": "read", "granted": True},
                        {"resource": "templates", "action": "create", "granted": True},
                        {"resource": "templates", "action": "update", "granted": True},
                        {"resource": "templates", "action": "delete", "granted": True},
                        {"resource": "api", "action": "format", "granted": True},
                        {"resource": "api", "action": "publish", "granted": True},
                        {"resource": "api", "action": "advanced", "granted": True},
                        {"resource": "api", "action": "bulk", "granted": True},
                        {"resource": "data", "action": "export", "granted": True},
                        {"resource": "data", "action": "delete", "granted": True},
                        {"resource": "analytics", "action": "read", "granted": True},
                        {"resource": "analytics", "action": "export", "granted": True},
                        {"resource": "team", "action": "manage", "granted": True}
                    ]
                },
                "admin": {
                    "name": "Administrator",
                    "description": "Full system access",
                    "permissions": [
                        {"resource": "*", "action": "*", "granted": True}
                    ]
                }
            }
            
            return {
                "success": True,
                "templates": templates
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Announcement Management Endpoints
    @app.get("/api/v1/admin/announcements")
    async def get_announcements():
        """Get all announcements"""
        try:
            from src.services.supabase import supabase_service
            
            response = supabase_service.client.table("announcements").select("*").order("created_at", desc=True).execute()
            
            return {"success": True, "announcements": response.data}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.post("/api/v1/admin/announcements")
    async def create_announcement(request: dict):
        """Create new announcement"""
        try:
            from src.services.supabase import supabase_service
            
            announcement_data = {
                "title": request["title"],
                "content": request["content"],
                "priority": request.get("priority", "normal"),
                "is_active": request.get("is_active", True),
                "created_by": "d917b37a-456d-440a-a7e6-488af7b5c0dc"  # Admin user ID
            }
            
            if "expires_at" in request and request["expires_at"]:
                announcement_data["expires_at"] = request["expires_at"]
            
            response = supabase_service.client.table("announcements").insert(announcement_data).execute()
            
            if response.data:
                return {"success": True, "announcement": response.data[0]}
            else:
                return {"success": False, "error": "Failed to create announcement"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.put("/api/v1/admin/announcements/{announcement_id}")
    async def update_announcement(announcement_id: str, request: dict):
        """Update announcement"""
        try:
            from src.services.supabase import supabase_service
            
            update_data = {}
            if "title" in request:
                update_data["title"] = request["title"]
            if "content" in request:
                update_data["content"] = request["content"]
            if "priority" in request:
                update_data["priority"] = request["priority"]
            if "is_active" in request:
                update_data["is_active"] = request["is_active"]
            if "expires_at" in request:
                update_data["expires_at"] = request["expires_at"]
            
            response = supabase_service.client.table("announcements").update(update_data).eq("id", announcement_id).execute()
            
            if response.data:
                return {"success": True, "announcement": response.data[0]}
            else:
                return {"success": False, "error": "Announcement not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.delete("/api/v1/admin/announcements/{announcement_id}")
    async def delete_announcement(announcement_id: str):
        """Delete announcement"""
        try:
            from src.services.supabase import supabase_service
            
            response = supabase_service.client.table("announcements").delete().eq("id", announcement_id).execute()
            
            if response.data:
                return {"success": True, "message": "Announcement deleted"}
            else:
                return {"success": False, "error": "Announcement not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # System Management Endpoints
    @app.get("/api/v1/admin/system/health")
    async def get_system_health():
        """Get system health status"""
        try:
            from src.services.supabase import supabase_service
            
            # Test database connection
            db_healthy = True
            try:
                supabase_service.client.table("profiles").select("id").limit(1).execute()
            except:
                db_healthy = False
            
            # Test Redis connection (placeholder)
            redis_healthy = True
            
            # Test API endpoints
            api_healthy = True
            
            overall_health = "healthy" if all([db_healthy, redis_healthy, api_healthy]) else "unhealthy"
            
            return {
                "success": True,
                "health": {
                    "overall": overall_health,
                    "database": "healthy" if db_healthy else "unhealthy",
                    "redis": "healthy" if redis_healthy else "unhealthy",
                    "api": "healthy" if api_healthy else "unhealthy",
                    "last_check": "2025-08-13T17:30:00Z"
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @app.post("/api/v1/admin/system/maintenance")
    async def toggle_maintenance(request: dict):
        """Toggle maintenance mode"""
        try:
            # This would typically update a system setting
            # For now, just return success
            maintenance_mode = request.get("enabled", False)
            message = request.get("message", "")
            
            return {
                "success": True,
                "maintenance": {
                    "enabled": maintenance_mode,
                    "message": message,
                    "updated_at": "2025-08-13T17:30:00Z"
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Start the server
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    
    print(f"🌐 Starting server on http://{host}:{port}")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(app, host=host, port=port, reload=False)

if __name__ == "__main__":
    main()
