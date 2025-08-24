#!/usr/bin/env python3
"""
Common Error Handling Utilities for Kolekt
Provides standardized error handling across the application
"""

import logging
from typing import Dict, Any, Optional, Callable
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Centralized error handling for Kolekt"""
    
    # Error type mappings
    ERROR_TYPES = {
        "validation_error": 422,
        "authentication_error": 401,
        "authorization_error": 403,
        "not_found_error": 404,
        "rate_limit_error": 429,
        "internal_error": 500,
        "service_unavailable": 503,
    }
    
    # Error messages
    ERROR_MESSAGES = {
        "validation_error": "Invalid request data",
        "authentication_error": "Authentication required",
        "authorization_error": "Insufficient permissions",
        "not_found_error": "Resource not found",
        "rate_limit_error": "Too many requests",
        "internal_error": "An unexpected error occurred",
        "service_unavailable": "Service temporarily unavailable",
    }
    
    @classmethod
    async def handle_validation_error(cls, request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle validation errors"""
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "message": cls.ERROR_MESSAGES["validation_error"],
                "details": exc.errors(),
                "path": request.url.path
            }
        )
    
    @classmethod
    async def handle_http_exception(cls, request: Request, exc: HTTPException) -> JSONResponse:
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
    
    @classmethod
    async def handle_generic_exception(cls, request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions"""
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": cls.ERROR_MESSAGES["internal_error"],
                "path": request.url.path
            }
        )
    
    @classmethod
    def create_error_response(
        cls,
        error_type: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create a standardized error response"""
        status = status_code or cls.ERROR_TYPES.get(error_type, 500)
        error_message = message or cls.ERROR_MESSAGES.get(error_type, "Unknown error")
        
        response = {
            "error": error_type,
            "message": error_message,
            "status_code": status
        }
        
        if details:
            response["details"] = details
        
        return response
    
    @classmethod
    def raise_http_exception(
        cls,
        error_type: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Raise a standardized HTTP exception"""
        status_code = cls.ERROR_TYPES.get(error_type, 500)
        error_message = message or cls.ERROR_MESSAGES.get(error_type, "Unknown error")
        
        raise HTTPException(
            status_code=status_code,
            detail=error_message
        )


def handle_errors(func: Callable) -> Callable:
    """Decorator to handle errors in route functions"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            # Re-raise HTTP exceptions as they're already handled
            raise
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred"
            )
    return wrapper


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
    """Validate that required fields are present"""
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    
    if missing_fields:
        ErrorHandler.raise_http_exception(
            "validation_error",
            f"Missing required fields: {', '.join(missing_fields)}"
        )


def validate_field_types(data: Dict[str, Any], field_types: Dict[str, type]) -> None:
    """Validate field types"""
    for field, expected_type in field_types.items():
        if field in data and not isinstance(data[field], expected_type):
            ErrorHandler.raise_http_exception(
                "validation_error",
                f"Field '{field}' must be of type {expected_type.__name__}"
            )


def sanitize_error_message(message: str) -> str:
    """Sanitize error messages for security"""
    # Remove sensitive information from error messages
    sensitive_patterns = [
        r'password.*',
        r'token.*',
        r'secret.*',
        r'key.*',
        r'api_key.*',
        r'access_token.*',
    ]
    
    import re
    for pattern in sensitive_patterns:
        message = re.sub(pattern, '[REDACTED]', message, flags=re.IGNORECASE)
    
    return message
