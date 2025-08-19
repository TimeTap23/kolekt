#!/usr/bin/env python3
"""
Posting Pipeline Service for ThreadStorm
Handles queue → dedupe → rate-limit gate → poster worker → result sink
"""

import asyncio
import logging
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import redis.asyncio as redis

from src.core.config import settings
from src.services.supabase import SupabaseService
from src.services.security import security_service
from src.services.job_queue import JobQueue, JobType, JobStatus

logger = logging.getLogger(__name__)


class PipelineStage(Enum):
    QUEUED = "queued"
    DEDUPLICATED = "deduplicated"
    RATE_LIMITED = "rate_limited"
    POSTING = "posting"
    COMPLETED = "completed"
    FAILED = "failed"


class PostingPipeline:
    """Robust posting pipeline with deduplication and rate limiting"""
    
    def __init__(self):
        self.supabase = SupabaseService()
        self.job_queue = JobQueue()
        self.redis_client = None
        self.processing = False
        
        # Pipeline configuration
        self.deduplication_window = timedelta(hours=24)
        self.rate_limit_window = timedelta(hours=1)
        self.max_retries = 3
        
        # Per-profile governors
        self.profile_governors = {
            'posts_per_day': 250,
            'replies_per_day': 1000,
            'requests_per_hour': 200,
            'bulk_operations_per_day': 50
        }
    
    async def init_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL)
            await self.redis_client.ping()
            logger.info("Posting pipeline Redis connection established")
        except Exception as e:
            logger.warning(f"Redis not available for posting pipeline: {e}")
            self.redis_client = None
    
    async def add_to_queue(self, user_id: str, profile_id: str, content: Dict, 
                          priority: int = 1) -> str:
        """Add posting job to queue with deduplication"""
        try:
            # Generate idempotency key
            idempotency_key = security_service.generate_idempotency_key(
                user_id, f"post_{profile_id}"
            )
            
            # Check for existing operation
            existing = await security_service.check_idempotency(idempotency_key)
            if existing:
                logger.info(f"Duplicate operation detected: {idempotency_key}")
                return existing['result']
            
            # Create content hash for deduplication
            content_hash = self._generate_content_hash(content)
            
            # Check for duplicate content
            if await self._is_duplicate_content(user_id, profile_id, content_hash):
                raise Exception("Duplicate content detected within 24 hours")
            
            # Add to job queue
            job_id = await self.job_queue.add_job(
                JobType.POST_THREAD,
                user_id,
                {
                    'profile_id': profile_id,
                    'content': content,
                    'content_hash': content_hash,
                    'idempotency_key': idempotency_key,
                    'priority': priority
                },
                priority
            )
            
            # Store idempotency key
            await security_service.store_idempotency_key(
                idempotency_key,
                {'job_id': job_id, 'status': 'queued'}
            )
            
            # Log pipeline event
            await self._log_pipeline_event(
                user_id, profile_id, PipelineStage.QUEUED,
                {'job_id': job_id, 'content_hash': content_hash}
            )
            
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to add to queue: {e}")
            raise
    
    async def process_pipeline(self):
        """Process the complete posting pipeline"""
        if self.processing:
            return
        
        self.processing = True
        
        try:
            while True:
                # Get next job from queue
                job = await self._get_next_job()
                if not job:
                    await asyncio.sleep(5)
                    continue
                
                # Process through pipeline stages
                await self._process_job_through_pipeline(job)
                
        except Exception as e:
            logger.error(f"Pipeline processing error: {e}")
        finally:
            self.processing = False
    
    async def _process_job_through_pipeline(self, job: Dict):
        """Process job through all pipeline stages"""
        try:
            job_data = json.loads(job['data'])
            user_id = job['user_id']
            profile_id = job_data['profile_id']
            
            # Stage 1: Deduplication
            if not await self._deduplicate_job(job_data):
                await self._update_job_status(job['id'], JobStatus.FAILED, 
                                            {'error': 'Duplicate content'})
                return
            
            await self._log_pipeline_event(
                user_id, profile_id, PipelineStage.DEDUPLICATED,
                {'job_id': job['id']}
            )
            
            # Stage 2: Rate Limit Check
            if not await self._check_rate_limits(user_id, profile_id):
                await self._update_job_status(job['id'], JobStatus.RATE_LIMITED)
                return
            
            await self._log_pipeline_event(
                user_id, profile_id, PipelineStage.RATE_LIMITED,
                {'job_id': job['id']}
            )
            
            # Stage 3: Posting
            await self._update_job_status(job['id'], JobStatus.PROCESSING)
            await self._log_pipeline_event(
                user_id, profile_id, PipelineStage.POSTING,
                {'job_id': job['id']}
            )
            
            result = await self._execute_posting(job_data)
            
            # Stage 4: Result Processing
            if result['success']:
                await self._update_job_status(job['id'], JobStatus.COMPLETED, result)
                await self._log_pipeline_event(
                    user_id, profile_id, PipelineStage.COMPLETED,
                    {'job_id': job['id'], 'result': result}
                )
                
                # Store successful result
                await security_service.store_idempotency_key(
                    job_data['idempotency_key'],
                    result,
                    datetime.now() + timedelta(hours=24)
                )
            else:
                await self._update_job_status(job['id'], JobStatus.FAILED, result)
                await self._log_pipeline_event(
                    user_id, profile_id, PipelineStage.FAILED,
                    {'job_id': job['id'], 'error': result.get('error')}
                )
            
        except Exception as e:
            logger.error(f"Pipeline processing failed: {e}")
            await self._update_job_status(job['id'], JobStatus.FAILED, 
                                        {'error': str(e)})
    
    async def _deduplicate_job(self, job_data: Dict) -> bool:
        """Check for duplicate content"""
        try:
            content_hash = job_data['content_hash']
            user_id = job_data.get('user_id')
            profile_id = job_data['profile_id']
            
            # Check Redis for recent duplicates
            if self.redis_client:
                duplicate_key = f"duplicate:{user_id}:{profile_id}:{content_hash}"
                if await self.redis_client.exists(duplicate_key):
                    return False
                
                # Store content hash for deduplication window
                await self.redis_client.setex(
                    duplicate_key,
                    int(self.deduplication_window.total_seconds()),
                    "1"
                )
            
            # Check database for duplicates
            return not await self._is_duplicate_content(
                user_id, profile_id, content_hash
            )
            
        except Exception as e:
            logger.error(f"Deduplication failed: {e}")
            return True  # Allow if deduplication fails
    
    async def _is_duplicate_content(self, user_id: str, profile_id: str, 
                                  content_hash: str) -> bool:
        """Check if content is duplicate in database"""
        try:
            # Check recent posts with same content hash
            cutoff_time = datetime.now() - self.deduplication_window
            
            response = await self.supabase.table('threadstorms')\
                .select('id')\
                .eq('user_id', user_id)\
                .eq('profile_id', profile_id)\
                .eq('content_hash', content_hash)\
                .gte('created_at', cutoff_time.isoformat())\
                .execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Duplicate check failed: {e}")
            return False
    
    async def _check_rate_limits(self, user_id: str, profile_id: str) -> bool:
        """Check rate limits for user and profile"""
        try:
            # Check per-profile governors
            today = datetime.now().date().isoformat()
            
            # Get current usage
            usage = await self._get_profile_usage(profile_id, today)
            
            # Check limits
            if usage['posts_today'] >= self.profile_governors['posts_per_day']:
                logger.warning(f"Daily post limit exceeded for profile {profile_id}")
                return False
            
            if usage['requests_hour'] >= self.profile_governors['requests_per_hour']:
                logger.warning(f"Hourly request limit exceeded for profile {profile_id}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Allow if rate limit check fails
    
    async def _get_profile_usage(self, profile_id: str, date: str) -> Dict:
        """Get profile usage for rate limiting"""
        try:
            response = await self.supabase.table('profile_usage')\
                .select('*')\
                .eq('profile_id', profile_id)\
                .eq('date', date)\
                .single()\
                .execute()
            
            if response.data:
                return response.data
            
            # Create new usage record
            return {
                'posts_today': 0,
                'replies_today': 0,
                'requests_hour': 0,
                'bulk_operations': 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get profile usage: {e}")
            return {
                'posts_today': 0,
                'replies_today': 0,
                'requests_hour': 0,
                'bulk_operations': 0
            }
    
    async def _execute_posting(self, job_data: Dict) -> Dict:
        """Execute the actual posting to Meta API"""
        try:
            # Get valid access token
            access_token = await self._get_profile_token(job_data['profile_id'])
            if not access_token:
                return {'success': False, 'error': 'No valid access token'}
            
            # Make API call to Meta
            result = await self._make_meta_api_call(
                access_token,
                job_data['content']
            )
            
            # Update usage if successful
            if result['success']:
                await self._increment_profile_usage(job_data['profile_id'])
            
            return result
            
        except Exception as e:
            logger.error(f"Posting execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _get_profile_token(self, profile_id: str) -> Optional[str]:
        """Get valid access token for profile"""
        try:
            response = await self.supabase.table('user_tokens')\
                .select('access_token')\
                .eq('profile_id', profile_id)\
                .is_('deleted_at', 'null')\
                .single()\
                .execute()
            
            if response.data:
                # Decrypt token
                return await security_service.decrypt_token(
                    response.data['access_token'],
                    response.data['user_id']
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get profile token: {e}")
            return None
    
    async def _make_meta_api_call(self, access_token: str, content: Dict) -> Dict:
        """Make API call to Meta with retry logic"""
        import httpx
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    headers = {
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'
                    }
                    
                    response = await client.post(
                        f"{settings.META_GRAPH_API_URL}/{settings.META_API_VERSION}/me/media",
                        headers=headers,
                        json=content
                    )
                    
                    if response.status_code == 200:
                        return {
                            'success': True,
                            'data': response.json(),
                            'attempt': attempt + 1
                        }
                    elif response.status_code == 429:  # Rate limited
                        retry_after = int(response.headers.get('Retry-After', 60))
                        await asyncio.sleep(retry_after)
                        continue
                    else:
                        response.raise_for_status()
                        
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    # Rate limited, wait and retry
                    await asyncio.sleep(60 * (attempt + 1))
                    continue
                else:
                    return {
                        'success': False,
                        'error': f'HTTP {e.response.status_code}: {e.response.text}',
                        'attempt': attempt + 1
                    }
            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(5 * (attempt + 1))
                    continue
                else:
                    return {
                        'success': False,
                        'error': str(e),
                        'attempt': attempt + 1
                    }
        
        return {'success': False, 'error': 'Max retries exceeded'}
    
    async def _increment_profile_usage(self, profile_id: str):
        """Increment profile usage counters"""
        try:
            today = datetime.now().date().isoformat()
            
            # Get current usage
            response = await self.supabase.table('profile_usage')\
                .select('*')\
                .eq('profile_id', profile_id)\
                .eq('date', today)\
                .single()\
                .execute()
            
            if response.data:
                # Update existing record
                await self.supabase.table('profile_usage')\
                    .update({
                        'posts_today': response.data['posts_today'] + 1,
                        'requests_hour': response.data['requests_hour'] + 1,
                        'updated_at': datetime.now().isoformat()
                    })\
                    .eq('id', response.data['id'])\
                    .execute()
            else:
                # Create new record
                await self.supabase.table('profile_usage').insert({
                    'profile_id': profile_id,
                    'date': today,
                    'posts_today': 1,
                    'replies_today': 0,
                    'requests_hour': 1,
                    'bulk_operations': 0,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }).execute()
                
        except Exception as e:
            logger.error(f"Failed to increment profile usage: {e}")
    
    def _generate_content_hash(self, content: Dict) -> str:
        """Generate hash for content deduplication"""
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    async def _get_next_job(self) -> Optional[Dict]:
        """Get next job from queue"""
        try:
            now = datetime.now().isoformat()
            
            response = await self.supabase.table('job_queue')\
                .select('*')\
                .eq('status', JobStatus.PENDING.value)\
                .lte('scheduled_time', now)\
                .order('priority', desc=True)\
                .order('created_at', desc=False)\
                .limit(1)\
                .execute()
            
            if response.data:
                return response.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get next job: {e}")
            return None
    
    async def _update_job_status(self, job_id: str, status: JobStatus, 
                               result: Dict = None):
        """Update job status and result"""
        try:
            update_data = {
                'status': status.value,
                'updated_at': datetime.now().isoformat()
            }
            
            if result:
                update_data['result'] = json.dumps(result)
            
            await self.supabase.table('job_queue')\
                .update(update_data)\
                .eq('id', job_id)\
                .execute()
                
        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
    
    async def _log_pipeline_event(self, user_id: str, profile_id: str, 
                                stage: PipelineStage, metadata: Dict = None):
        """Log pipeline event for observability"""
        try:
            await self.supabase.table('pipeline_events').insert({
                'user_id': user_id,
                'profile_id': profile_id,
                'stage': stage.value,
                'metadata': json.dumps(metadata) if metadata else None,
                'timestamp': datetime.now().isoformat()
            }).execute()
            
        except Exception as e:
            logger.error(f"Failed to log pipeline event: {e}")


# Global posting pipeline instance
posting_pipeline = PostingPipeline()


# Background task to process pipeline
async def process_posting_pipeline_background():
    """Background task to continuously process posting pipeline"""
    await posting_pipeline.init_redis()
    
    while True:
        try:
            await posting_pipeline.process_pipeline()
        except Exception as e:
            logger.error(f"Posting pipeline background error: {e}")
            await asyncio.sleep(10)
