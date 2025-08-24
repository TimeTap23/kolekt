#!/usr/bin/env python3
"""
Database Connection Pool Service for ThreadStorm
Manages database connections efficiently with connection pooling
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import asyncpg
from src.core.config import settings

logger = logging.getLogger(__name__)


class DatabasePool:
    """Database connection pool manager"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.min_size = 5
        self.max_size = 20
        self.max_queries = 50000
        self.max_inactive_connection_lifetime = 300.0
        self.enabled = True
    
    async def init_pool(self):
        """Initialize the database connection pool"""
        try:
            # Parse database URL to get connection parameters
            db_url = settings.DATABASE_URL
            if not db_url:
                logger.warning("⚠️ Database URL not configured, connection pooling disabled")
                self.enabled = False
                return
            
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                db_url,
                min_size=self.min_size,
                max_size=self.max_size,
                max_queries=self.max_queries,
                max_inactive_connection_lifetime=self.max_inactive_connection_lifetime,
                command_timeout=60,
                server_settings={
                    'application_name': 'threadstorm',
                    'jit': 'off'  # Disable JIT for better performance
                }
            )
            
            logger.info(f"✅ Database connection pool initialized (min: {self.min_size}, max: {self.max_size})")
            
            # Test the pool
            async with self.pool.acquire() as conn:
                await conn.execute('SELECT 1')
            
            logger.info("✅ Database pool connection test successful")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database pool: {e}")
            self.enabled = False
            self.pool = None
    
    @asynccontextmanager
    async def acquire(self):
        """Acquire a database connection from the pool"""
        if not self.enabled or not self.pool:
            raise Exception("Database pool not initialized")
        
        try:
            async with self.pool.acquire() as connection:
                yield connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    async def execute(self, query: str, *args, **kwargs):
        """Execute a query using the connection pool"""
        if not self.enabled or not self.pool:
            raise Exception("Database pool not initialized")
        
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args, **kwargs)
    
    async def fetch(self, query: str, *args, **kwargs):
        """Fetch rows using the connection pool"""
        if not self.enabled or not self.pool:
            raise Exception("Database pool not initialized")
        
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args, **kwargs)
    
    async def fetchrow(self, query: str, *args, **kwargs):
        """Fetch a single row using the connection pool"""
        if not self.enabled or not self.pool:
            raise Exception("Database pool not initialized")
        
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args, **kwargs)
    
    async def fetchval(self, query: str, *args, **kwargs):
        """Fetch a single value using the connection pool"""
        if not self.enabled or not self.pool:
            raise Exception("Database pool not initialized")
        
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args, **kwargs)
    
    async def get_pool_stats(self) -> Dict[str, Any]:
        """Get database pool statistics"""
        if not self.enabled or not self.pool:
            return {"enabled": False}
        
        try:
            stats = self.pool.get_stats()
            return {
                "enabled": True,
                "min_size": self.min_size,
                "max_size": self.max_size,
                "size": stats.get("size", 0),
                "free_size": stats.get("free_size", 0),
                "checkedout_connections": stats.get("checkedout_connections", 0),
                "checkedin_connections": stats.get("checkedin_connections", 0),
                "overflow": stats.get("overflow", 0),
                "overflow_used": stats.get("overflow_used", 0),
                "overflow_used_high_water": stats.get("overflow_used_high_water", 0),
                "returned_connections": stats.get("returned_connections", 0),
                "total_queries": stats.get("total_queries", 0),
                "total_queries_high_water": stats.get("total_queries_high_water", 0)
            }
        except Exception as e:
            logger.error(f"Error getting pool stats: {e}")
            return {"enabled": False, "error": str(e)}
    
    async def health_check(self) -> bool:
        """Health check for database pool"""
        if not self.enabled or not self.pool:
            return False
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('SELECT 1')
            return True
        except Exception as e:
            logger.error(f"Database pool health check failed: {e}")
            return False
    
    async def close(self):
        """Close the database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("✅ Database connection pool closed")


# Global database pool instance
db_pool = DatabasePool()
