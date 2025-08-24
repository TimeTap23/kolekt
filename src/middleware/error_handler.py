#!/usr/bin/env python3
"""
Error Handling Middleware
Provides comprehensive error handling for production
"""

import logging
import traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Union
import time

# Setup logging
logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling for the application"""
    
    @staticmethod
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors"""
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "message": "Invalid request data",
                "details": exc.errors(),
                "path": request.url.path
            }
        )
    
    @staticmethod
    async def handle_http_exception(request: Request, exc: Union[HTTPException, StarletteHTTPException]):
        """Handle HTTP exceptions"""
        logger.warning(f"HTTP error {exc.status_code}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "http_error",
                "message": exc.detail,
                "status_code": exc.status_code,
                "path": request.url.path
            }
        )
    
    @staticmethod
    async def handle_generic_exception(request: Request, exc: Exception):
        """Handle unexpected exceptions"""
        logger.error(f"Unexpected error: {str(exc)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # In production, don't expose internal errors
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": "An unexpected error occurred",
                "path": request.url.path
            }
        )

class RateLimitMiddleware:
    """Simple rate limiting middleware"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        self.app = app
        self.requests_per_minute = requests_per_minute
        self.requests = {}
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Clean old requests
        current_time = time.time()
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if current_time - req_time < 60
            ]
        else:
            self.requests[client_ip] = []
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            response = JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": 60
                }
            )
            await response(scope, receive, send)
            return
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        # Process request
        await self.app(scope, receive, send)

class LoggingMiddleware:
    """Request logging middleware"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {scope['method']} {scope['path']}")
        
        # Process request
        await self.app(scope, receive, send)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(f"Response completed - {duration:.3f}s")

class SecurityMiddleware:
    """Security headers middleware"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Create a custom send function to add headers
        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                # Add security headers
                headers = dict(message.get("headers", []))
                headers[b"x-content-type-options"] = b"nosniff"
                headers[b"x-frame-options"] = b"DENY"
                headers[b"x-xss-protection"] = b"1; mode=block"
                headers[b"referrer-policy"] = b"strict-origin-when-cross-origin"
                message["headers"] = list(headers.items())
            
            await send(message)
        
        await self.app(scope, receive, send_with_headers)
