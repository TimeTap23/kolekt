#!/usr/bin/env python3
"""
Cache Service for ThreadStorm
Handles Redis-based caching for improved performance
"""

import json
import logging
import pickle
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import redis
from src.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based caching service for ThreadStorm"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = True
        self.default_ttl = 3600  # 1 hour default TTL
        
        # Cache key prefixes
        self.prefixes = {
            'user': 'user:',
            'profile': 'profile:',
            'dashboard': 'dashboard:',
            'analytics': 'analytics:',
            'content': 'content:',
            'template': 'template:',
            'api': 'api:',
            'session': 'session:'
        }
    
    async def init_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=False,  # Keep as bytes for pickle
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis cache connection established")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis cache not available: {e}")
            self.enabled = False
            self.redis_client = None
    
    def _get_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key with prefix"""
        return f"{self.prefixes.get(prefix, '')}{identifier}"
    
    def _serialize(self, data: Any) -> bytes:
        """Serialize data for caching"""
        try:
            return pickle.dumps(data)
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            return json.dumps(data, default=str).encode()
    
    def _deserialize(self, data: bytes) -> Any:
        """Deserialize cached data"""
        try:
            return pickle.loads(data)
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            try:
                return json.loads(data.decode())
            except:
                return None
    
    async def get(self, prefix: str, identifier: str) -> Optional[Any]:
        """Get cached data"""
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            key = self._get_key(prefix, identifier)
            data = self.redis_client.get(key)
            
            if data:
                logger.debug(f"Cache HIT: {key}")
                return self._deserialize(data)
            else:
                logger.debug(f"Cache MISS: {key}")
                return None
                
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, prefix: str, identifier: str, data: Any, ttl: int = None) -> bool:
        """Set cached data"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            key = self._get_key(prefix, identifier)
            serialized_data = self._serialize(data)
            ttl = ttl or self.default_ttl
            
            result = self.redis_client.setex(key, ttl, serialized_data)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return bool(result)
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, prefix: str, identifier: str) -> bool:
        """Delete cached data"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            key = self._get_key(prefix, identifier)
            result = self.redis_client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return bool(result)
            
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.enabled or not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                result = self.redis_client.delete(*keys)
                logger.debug(f"Cache DELETE PATTERN: {pattern} ({len(keys)} keys)")
                return result
            return 0
            
        except Exception as e:
            logger.error(f"Cache delete pattern error: {e}")
            return 0
    
    async def exists(self, prefix: str, identifier: str) -> bool:
        """Check if cache key exists"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            key = self._get_key(prefix, identifier)
            return bool(self.redis_client.exists(key))
            
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    async def expire(self, prefix: str, identifier: str, ttl: int) -> bool:
        """Set expiration for cache key"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            key = self._get_key(prefix, identifier)
            result = self.redis_client.expire(key, ttl)
            logger.debug(f"Cache EXPIRE: {key} (TTL: {ttl}s)")
            return bool(result)
            
        except Exception as e:
            logger.error(f"Cache expire error: {e}")
            return False
    
    async def get_many(self, prefix: str, identifiers: List[str]) -> Dict[str, Any]:
        """Get multiple cached items"""
        if not self.enabled or not self.redis_client:
            return {}
        
        try:
            keys = [self._get_key(prefix, identifier) for identifier in identifiers]
            values = self.redis_client.mget(keys)
            
            result = {}
            for identifier, value in zip(identifiers, values):
                if value is not None:
                    result[identifier] = self._deserialize(value)
            
            logger.debug(f"Cache GET MANY: {len(result)}/{len(identifiers)} hits")
            return result
            
        except Exception as e:
            logger.error(f"Cache get many error: {e}")
            return {}
    
    async def set_many(self, prefix: str, data: Dict[str, Any], ttl: int = None) -> bool:
        """Set multiple cached items"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            pipeline = self.redis_client.pipeline()
            
            for identifier, value in data.items():
                key = self._get_key(prefix, identifier)
                serialized_data = self._serialize(value)
                pipeline.setex(key, ttl, serialized_data)
            
            pipeline.execute()
            logger.debug(f"Cache SET MANY: {len(data)} items")
            return True
            
        except Exception as e:
            logger.error(f"Cache set many error: {e}")
            return False
    
    async def invalidate_user_cache(self, user_id: str):
        """Invalidate all cache entries for a user"""
        patterns = [
            f"{self.prefixes['user']}{user_id}*",
            f"{self.prefixes['profile']}{user_id}*",
            f"{self.prefixes['dashboard']}*{user_id}*",
            f"{self.prefixes['analytics']}*{user_id}*"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            deleted = await self.delete_pattern(pattern)
            total_deleted += deleted
        
        logger.info(f"Invalidated {total_deleted} cache entries for user {user_id}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.enabled or not self.redis_client:
            return {"enabled": False}
        
        try:
            info = self.redis_client.info()
            return {
                "enabled": True,
                "connected_clients": info.get('connected_clients', 0),
                "used_memory_human": info.get('used_memory_human', '0B'),
                "keyspace_hits": info.get('keyspace_hits', 0),
                "keyspace_misses": info.get('keyspace_misses', 0),
                "total_commands_processed": info.get('total_commands_processed', 0),
                "hit_rate": self._calculate_hit_rate(info)
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"enabled": False, "error": str(e)}
    
    def _calculate_hit_rate(self, info: Dict[str, Any]) -> float:
        """Calculate cache hit rate"""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        
        if total == 0:
            return 0.0
        
        return (hits / total) * 100
    
    async def health_check(self) -> bool:
        """Health check for cache service"""
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return False


# Global cache service instance
cache_service = CacheService()


# Cache decorators for easy use
def cached(prefix: str, ttl: int = None):
    """Decorator for caching function results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = await cache_service.get(prefix, cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_service.set(prefix, cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def invalidate_cache(prefix: str, pattern: str = None):
    """Decorator for invalidating cache after function execution"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            if pattern:
                await cache_service.delete_pattern(pattern)
            else:
                # Try to extract user_id from arguments for user-specific invalidation
                user_id = None
                for arg in args:
                    if hasattr(arg, 'get') and isinstance(arg, dict):
                        user_id = arg.get('user_id') or arg.get('id')
                        break
                
                if user_id:
                    await cache_service.invalidate_user_cache(user_id)
            
            return result
        return wrapper
    return decorator
