"""
Background tasks service for ThreadStorm
"""

import logging
import os
from typing import Optional

from celery import Celery
import redis

logger = logging.getLogger(__name__)

# Celery configuration
celery_app = Celery(
    "threadstorm",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=["src.services.background"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Redis client for caching
redis_client: Optional[redis.Redis] = None

def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client with error handling"""
    global redis_client
    if redis_client is None:
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            redis_client = redis.from_url(redis_url)
            redis_client.ping()  # Test connection
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Background tasks will be disabled.")
            redis_client = None
    return redis_client

async def start_background_tasks():
    """Start background task processing"""
    try:
        # Try to connect to Redis, but don't fail if unavailable
        redis_client = get_redis_client()
        if redis_client:
            logger.info("Background tasks started successfully")
        else:
            logger.info("Background tasks disabled (Redis unavailable)")
    except Exception as e:
        logger.error(f"Failed to start background tasks: {e}")
        # Don't raise the exception - allow the app to start without background tasks

async def stop_background_tasks():
    """Stop background task processing"""
    try:
        if redis_client:
            redis_client.close()
            logger.info("Background tasks stopped")
    except Exception as e:
        logger.error(f"Error stopping background tasks: {e}")

# Example Celery tasks
@celery_app.task
def process_content_async(content_id: str):
    """Process content asynchronously"""
    logger.info(f"Processing content {content_id}")
    # Add your async processing logic here
    return {"status": "completed", "content_id": content_id}

@celery_app.task
def generate_threadstorm_async(text: str, images: Optional[list] = None):
    """Generate threadstorm asynchronously"""
    logger.info("Generating threadstorm asynchronously")
    # Add your threadstorm generation logic here
    return {"status": "completed", "thread_count": 5}
