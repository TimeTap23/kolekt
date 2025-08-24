#!/usr/bin/env python3
"""
Performance Monitoring Middleware for ThreadStorm
Tracks request performance metrics and response times
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from src.services.performance_monitor import performance_monitor

logger = logging.getLogger(__name__)


async def performance_middleware(request: Request, call_next: Callable) -> Response:
    """Performance monitoring middleware"""
    start_time = time.time()
    
    try:
        # Process the request
        response = await call_next(request)
        
        # Calculate response time
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Record performance metric
        await performance_monitor.record_request_metric(
            endpoint=request.url.path,
            method=request.method,
            response_time=response_time,
            status_code=response.status_code
        )
        
        # Add performance headers
        response.headers["X-Response-Time"] = f"{response_time:.2f}ms"
        response.headers["X-Performance-Monitored"] = "true"
        
        # Log slow requests
        if response_time > 1000:  # Log requests taking more than 1 second
            logger.warning(f"Slow request: {request.method} {request.url.path} took {response_time:.2f}ms")
        
        # Log error responses
        if response.status_code >= 400:
            logger.error(f"Error response: {request.method} {request.url.path} returned {response.status_code}")
        
        return response
        
    except Exception as e:
        # Calculate response time even for exceptions
        response_time = (time.time() - start_time) * 1000
        
        # Record error metric
        await performance_monitor.record_request_metric(
            endpoint=request.url.path,
            method=request.method,
            response_time=response_time,
            status_code=500
        )
        
        logger.error(f"Request failed: {request.method} {request.url.path} - {str(e)}")
        raise
