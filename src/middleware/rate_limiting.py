#!/usr/bin/env python3
"""
Rate Limiting Middleware for Kolekt
Prevents spam and abuse through intelligent rate limiting
"""

import time
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, Response
from fastapi.responses import JSONResponse
import redis.asyncio as redis
from src.core.config import settings, PLAN_LIMITS

logger = logging.getLogger(__name__)


class RateLimiter:
    """Intelligent rate limiter with spam detection"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.spam_patterns = [
            # Common spam patterns
            r'\b(buy\s+now|click\s+here|free\s+offer|limited\s+time|act\s+now)\b',
            r'\b(earn\s+money|make\s+money|work\s+from\s+home|get\s+rich)\b',
            r'\b(weight\s+loss|diet\s+pills|miracle\s+cure|cure\s+all)\b',
            r'\b(viagra|cialis|penis|enlargement|breast)\b',
            r'\b(casino|poker|bet|gambling|lottery)\b',
            r'\b(loan|debt|credit|refinance|mortgage)\b',
            r'\b(degree|diploma|certificate|university)\b',
            r'\b(watch\s+video|click\s+link|visit\s+site|go\s+to)\b',
            # Excessive punctuation and caps
            r'[!]{3,}',
            r'[?]{3,}',
            r'[A-Z]{10,}',
            # URL patterns
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            # Phone numbers
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            # Email addresses
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        ]
        
        # Spam scoring weights
        self.spam_weights = {
            'repetitive_content': 10,
            'excessive_length': 5,
            'suspicious_patterns': 15,
            'rapid_posting': 20,
            'similar_content': 15,
            'new_account': 5,
            'no_engagement': 10,
        }
    
    async def init_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL)
            await self.redis_client.ping()
            logger.info("Rate limiter Redis connection established")
        except Exception as e:
            logger.warning(f"Redis not available for rate limiting: {e}")
            self.redis_client = None
    
    async def get_user_plan(self, user_id: str) -> str:
        """Get user's subscription plan"""
        try:
            if self.redis_client:
                plan = await self.redis_client.get(f"user_plan:{user_id}")
                return plan.decode() if plan else 'free'
        except Exception as e:
            logger.error(f"Error getting user plan: {e}")
        return 'free'
    
    async def check_rate_limit(self, user_id: str, endpoint: str) -> Tuple[bool, Dict]:
        """Check if user has exceeded rate limits"""
        if not self.redis_client:
            return True, {}
        
        try:
            plan = await self.get_user_plan(user_id)
            limits = PLAN_LIMITS.get(plan, PLAN_LIMITS['free'])
            rate_limit = limits['rate_limit']
            
            # Create rate limit key
            current_minute = int(time.time() / 60)
            key = f"rate_limit:{user_id}:{endpoint}:{current_minute}"
            
            # Check current usage
            current_usage = await self.redis_client.get(key)
            current_count = int(current_usage) if current_usage else 0
            
            if current_count >= rate_limit:
                return False, {
                    'limit_exceeded': True,
                    'current_usage': current_count,
                    'rate_limit': rate_limit,
                    'reset_time': (current_minute + 1) * 60
                }
            
            # Increment usage
            await self.redis_client.incr(key)
            await self.redis_client.expire(key, 120)  # 2 minutes TTL
            
            return True, {
                'limit_exceeded': False,
                'current_usage': current_count + 1,
                'rate_limit': rate_limit,
                'remaining': rate_limit - (current_count + 1)
            }
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True, {}
    
    async def detect_spam(self, content: str, user_id: str) -> Tuple[bool, float, Dict]:
        """Detect spam content using multiple heuristics"""
        spam_score = 0.0
        spam_indicators = {}
        
        try:
            # Check content length
            if len(content) > 5000:  # Very long content
                spam_score += self.spam_weights['excessive_length']
                spam_indicators['excessive_length'] = True
            
            # Check for repetitive content
            words = content.lower().split()
            if len(words) > 10:
                word_freq = {}
                for word in words:
                    word_freq[word] = word_freq.get(word, 0) + 1
                
                max_freq = max(word_freq.values())
                if max_freq > len(words) * 0.3:  # 30% repetition
                    spam_score += self.spam_weights['repetitive_content']
                    spam_indicators['repetitive_content'] = True
            
            # Check for suspicious patterns
            import re
            for pattern in self.spam_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    spam_score += self.spam_weights['suspicious_patterns']
                    spam_indicators['suspicious_patterns'] = len(matches)
            
            # Check for rapid posting
            if self.redis_client:
                recent_posts = await self.redis_client.get(f"recent_posts:{user_id}")
                if recent_posts:
                    post_count = int(recent_posts)
                    if post_count > 5:  # More than 5 posts in recent window
                        spam_score += self.spam_weights['rapid_posting']
                        spam_indicators['rapid_posting'] = post_count
            
            # Check for similar content (basic hash-based detection)
            content_hash = hash(content.lower().strip())
            if self.redis_client:
                similar_key = f"content_hash:{content_hash}"
                if await self.redis_client.exists(similar_key):
                    spam_score += self.spam_weights['similar_content']
                    spam_indicators['similar_content'] = True
                else:
                    await self.redis_client.setex(similar_key, 3600, 1)  # 1 hour TTL
            
            # Check account age and engagement
            if self.redis_client:
                account_age = await self.redis_client.get(f"account_age:{user_id}")
                if not account_age:  # New account
                    spam_score += self.spam_weights['new_account']
                    spam_indicators['new_account'] = True
                
                engagement = await self.redis_client.get(f"engagement:{user_id}")
                if engagement and float(engagement) < 0.1:  # Low engagement
                    spam_score += self.spam_weights['no_engagement']
                    spam_indicators['no_engagement'] = True
            
            # Determine if content is spam
            is_spam = spam_score > 50  # Threshold for spam detection
            
            return is_spam, spam_score, spam_indicators
            
        except Exception as e:
            logger.error(f"Spam detection error: {e}")
            return False, 0.0, {}
    
    async def track_user_activity(self, user_id: str, action: str, metadata: Dict = None):
        """Track user activity for spam detection"""
        if not self.redis_client:
            return
        
        try:
            current_time = int(time.time())
            
            # Track recent posts
            recent_key = f"recent_posts:{user_id}"
            await self.redis_client.incr(recent_key)
            await self.redis_client.expire(recent_key, 300)  # 5 minutes
            
            # Track activity pattern
            activity_key = f"activity:{user_id}:{current_time // 60}"
            await self.redis_client.incr(activity_key)
            await self.redis_client.expire(activity_key, 3600)  # 1 hour
            
            # Store activity metadata
            if metadata:
                meta_key = f"activity_meta:{user_id}:{current_time}"
                await self.redis_client.setex(meta_key, 86400, str(metadata))  # 24 hours
            
        except Exception as e:
            logger.error(f"Activity tracking error: {e}")


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware for FastAPI"""
    
    # Initialize Redis if not already done
    if not rate_limiter.redis_client:
        await rate_limiter.init_redis()
    
    # Get user ID (placeholder - would be from JWT token)
    user_id = request.headers.get('X-User-ID', 'anonymous')
    
    # Skip rate limiting for certain endpoints
    skip_endpoints = ['/health', '/docs', '/openapi.json', '/static']
    if any(request.url.path.startswith(endpoint) for endpoint in skip_endpoints):
        response = await call_next(request)
        return response
    
    # Check rate limits
    endpoint = request.url.path
    allowed, limit_info = await rate_limiter.check_rate_limit(user_id, endpoint)
    
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={
                'error': 'Rate limit exceeded',
                'message': f'Too many requests. Limit: {limit_info["rate_limit"]}/minute',
                'retry_after': limit_info['reset_time'] - int(time.time()),
                'current_usage': limit_info['current_usage'],
                'rate_limit': limit_info['rate_limit']
            },
            headers={
                'X-RateLimit-Limit': str(limit_info['rate_limit']),
                'X-RateLimit-Remaining': '0',
                'X-RateLimit-Reset': str(limit_info['reset_time']),
                'Retry-After': str(limit_info['reset_time'] - int(time.time()))
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    response.headers['X-RateLimit-Limit'] = str(limit_info.get('rate_limit', 0))
    response.headers['X-RateLimit-Remaining'] = str(limit_info.get('remaining', 0))
    
    return response


async def spam_detection_middleware(request: Request, call_next):
    """Spam detection middleware for content endpoints"""
    
    # Only check content endpoints
    content_endpoints = ['/api/v1/format', '/api/v1/threads/publish']
    if request.url.path not in content_endpoints:
        response = await call_next(request)
        return response
    
    # Get user ID
    user_id = request.headers.get('X-User-ID', 'anonymous')
    
    try:
        # Get request body for content analysis
        body = await request.body()
        if body:
            import json
            try:
                data = json.loads(body)
                content = data.get('content', '')
                
                if content:
                    # Detect spam
                    is_spam, spam_score, indicators = await rate_limiter.detect_spam(content, user_id)
                    
                    if is_spam:
                        return JSONResponse(
                            status_code=400,
                            content={
                                'error': 'Spam detected',
                                'message': 'Your content appears to be spam. Please review and try again.',
                                'spam_score': spam_score,
                                'indicators': indicators
                            }
                        )
                    
                    # Track activity
                    await rate_limiter.track_user_activity(user_id, 'content_creation', {
                        'spam_score': spam_score,
                        'content_length': len(content),
                        'endpoint': request.url.path
                    })
                    
            except json.JSONDecodeError:
                pass  # Not JSON content
    
    except Exception as e:
        logger.error(f"Spam detection middleware error: {e}")
    
    response = await call_next(request)
    return response
