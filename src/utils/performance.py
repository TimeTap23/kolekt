#!/usr/bin/env python3
"""
Performance Optimization Utilities
Provides caching, connection pooling, and performance monitoring
"""

import asyncio
import time
import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional
import json

# Setup logging
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor and log performance metrics"""
    
    def __init__(self):
        self.metrics = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation"""
        self.metrics[operation] = {"start": time.time()}
    
    def end_timer(self, operation: str) -> float:
        """End timing an operation and return duration"""
        if operation in self.metrics:
            duration = time.time() - self.metrics[operation]["start"]
            self.metrics[operation]["duration"] = duration
            self.metrics[operation]["end"] = time.time()
            logger.info(f"Performance: {operation} took {duration:.3f}s")
            return duration
        return 0.0
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all performance metrics"""
        return self.metrics

# Global performance monitor
performance_monitor = PerformanceMonitor()

def monitor_performance(operation_name: str):
    """Decorator to monitor function performance"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            performance_monitor.start_timer(operation_name)
            try:
                result = await func(*args, **kwargs)
                performance_monitor.end_timer(operation_name)
                return result
            except Exception as e:
                performance_monitor.end_timer(operation_name)
                raise e
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            performance_monitor.start_timer(operation_name)
            try:
                result = func(*args, **kwargs)
                performance_monitor.end_timer(operation_name)
                return result
            except Exception as e:
                performance_monitor.end_timer(operation_name)
                raise e
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class SimpleCache:
    """Simple in-memory cache with TTL"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            item = self.cache[key]
            if time.time() < item["expires"]:
                return item["value"]
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        ttl = ttl or self.default_ttl
        self.cache[key] = {
            "value": value,
            "expires": time.time() + ttl
        }
    
    def delete(self, key: str) -> None:
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
    
    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)

# Global cache instance
cache = SimpleCache()

def cached(ttl: Optional[int] = None):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cache miss for {cache_key}, cached result")
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cache miss for {cache_key}, cached result")
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class DatabaseConnectionPool:
    """Simple connection pool for database operations"""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.active_connections = 0
        self.connection_semaphore = asyncio.Semaphore(max_connections)
    
    async def acquire(self):
        """Acquire a database connection"""
        await self.connection_semaphore.acquire()
        self.active_connections += 1
        logger.debug(f"Database connection acquired. Active: {self.active_connections}")
    
    def release(self):
        """Release a database connection"""
        self.connection_semaphore.release()
        self.active_connections -= 1
        logger.debug(f"Database connection released. Active: {self.active_connections}")
    
    async def __aenter__(self):
        await self.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.release()

# Global connection pool
db_pool = DatabaseConnectionPool()

def with_db_connection():
    """Decorator to manage database connections"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with db_pool:
                return await func(*args, **kwargs)
        return wrapper
    return decorator

class BatchProcessor:
    """Process operations in batches for better performance"""
    
    def __init__(self, batch_size: int = 100, max_wait_time: float = 1.0):
        self.batch_size = batch_size
        self.max_wait_time = max_wait_time
        self.batch = []
        self.last_process_time = time.time()
    
    async def add(self, item: Any) -> None:
        """Add item to batch"""
        self.batch.append(item)
        
        # Process if batch is full or max wait time exceeded
        if (len(self.batch) >= self.batch_size or 
            time.time() - self.last_process_time >= self.max_wait_time):
            await self.process()
    
    async def process(self) -> None:
        """Process current batch"""
        if not self.batch:
            return
        
        # Process batch (placeholder - implement actual processing)
        logger.info(f"Processing batch of {len(self.batch)} items")
        
        # Clear batch
        self.batch.clear()
        self.last_process_time = time.time()

# Global batch processor
batch_processor = BatchProcessor()
