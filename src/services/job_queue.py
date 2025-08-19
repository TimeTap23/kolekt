#!/usr/bin/env python3
"""
Job Queue Service for ThreadStorm
Handles rate limiting, backoff strategies, and Meta API compliance
"""

import asyncio
import logging
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import json

from src.core.config import settings
from src.services.supabase import SupabaseService
from src.services.meta_oauth import meta_oauth

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"
    RETRY = "retry"


class JobType(Enum):
    POST_THREAD = "post_thread"
    POST_REPLY = "post_reply"
    SCHEDULE_POST = "schedule_post"
    BULK_PUBLISH = "bulk_publish"


class JobQueue:
    """Intelligent job queue with Meta API compliance"""
    
    def __init__(self):
        self.supabase = SupabaseService()
        self.processing = False
        self.max_retries = 3
        self.base_delay = 1.0  # Base delay in seconds
        
        # Meta API rate limits
        self.rate_limits = {
            'posts_per_day': 250,
            'replies_per_day': 1000,
            'requests_per_hour': 200,
            'bulk_operations': 50  # Max bulk operations per day
        }
        
        # Backoff strategies
        self.backoff_strategies = {
            'exponential': lambda attempt: min(300, self.base_delay * (2 ** attempt)),
            'linear': lambda attempt: min(60, self.base_delay * attempt),
            'jitter': lambda attempt: min(120, self.base_delay * (2 ** attempt) + random.uniform(0, 1))
        }
    
    async def add_job(self, job_type: JobType, user_id: str, data: Dict, 
                     priority: int = 1, scheduled_time: Optional[datetime] = None) -> str:
        """Add job to queue with rate limiting checks"""
        try:
            # Check rate limits before adding job
            rate_check = await self._check_rate_limits(user_id, job_type)
            if not rate_check['can_add']:
                raise Exception(f"Rate limit exceeded: {rate_check['message']}")
            
            # Create job record
            job_data = {
                'job_type': job_type.value,
                'user_id': user_id,
                'data': json.dumps(data),
                'priority': priority,
                'status': JobStatus.PENDING.value,
                'attempts': 0,
                'scheduled_time': scheduled_time.isoformat() if scheduled_time else None,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            response = await self.supabase.table('job_queue').insert(job_data).execute()
            job_id = response.data[0]['id']
            
            logger.info(f"Added job {job_id} of type {job_type.value} for user {user_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to add job: {e}")
            raise
    
    async def process_jobs(self):
        """Process jobs with intelligent rate limiting and backoff"""
        if self.processing:
            return
        
        self.processing = True
        
        try:
            while True:
                # Get next job to process
                job = await self._get_next_job()
                if not job:
                    await asyncio.sleep(5)  # Wait before checking again
                    continue
                
                # Process the job
                await self._process_job(job)
                
                # Add delay between jobs to respect rate limits
                await asyncio.sleep(self._calculate_job_delay(job))
                
        except Exception as e:
            logger.error(f"Job processing error: {e}")
        finally:
            self.processing = False
    
    async def _get_next_job(self) -> Optional[Dict]:
        """Get next job to process based on priority and scheduling"""
        try:
            now = datetime.now().isoformat()
            
            # Get highest priority job that's ready to process
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
    
    async def _process_job(self, job: Dict):
        """Process a single job with retry logic"""
        try:
            # Update job status to processing
            await self._update_job_status(job['id'], JobStatus.PROCESSING)
            
            # Check rate limits before processing
            rate_check = await self._check_rate_limits(job['user_id'], JobType(job['job_type']))
            if not rate_check['can_process']:
                await self._handle_rate_limit(job, rate_check)
                return
            
            # Execute the job
            result = await self._execute_job(job)
            
            if result['success']:
                await self._update_job_status(job['id'], JobStatus.COMPLETED, result)
                await self._increment_usage(job['user_id'], job['job_type'])
            else:
                await self._handle_job_failure(job, result)
                
        except Exception as e:
            logger.error(f"Job processing error: {e}")
            await self._handle_job_failure(job, {'error': str(e)})
    
    async def _execute_job(self, job: Dict) -> Dict:
        """Execute the actual job based on type"""
        try:
            job_data = json.loads(job['data'])
            
            if job['job_type'] == JobType.POST_THREAD.value:
                return await self._post_thread(job['user_id'], job_data)
            elif job['job_type'] == JobType.POST_REPLY.value:
                return await self._post_reply(job['user_id'], job_data)
            elif job['job_type'] == JobType.SCHEDULE_POST.value:
                return await self._schedule_post(job['user_id'], job_data)
            elif job['job_type'] == JobType.BULK_PUBLISH.value:
                return await self._bulk_publish(job['user_id'], job_data)
            else:
                return {'success': False, 'error': f'Unknown job type: {job["job_type"]}'}
                
        except Exception as e:
            logger.error(f"Job execution error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _post_thread(self, user_id: str, data: Dict) -> Dict:
        """Post a thread to Meta API"""
        try:
            # Get valid access token
            access_token = await meta_oauth.get_valid_token(user_id)
            if not access_token:
                return {'success': False, 'error': 'No valid access token'}
            
            # Post to Meta API with retry logic
            result = await self._make_meta_api_call(
                'POST',
                f"https://graph.facebook.com/v18.0/me/media",
                access_token,
                data,
                max_retries=3
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Post thread error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _post_reply(self, user_id: str, data: Dict) -> Dict:
        """Post a reply to Meta API"""
        try:
            access_token = await meta_oauth.get_valid_token(user_id)
            if not access_token:
                return {'success': False, 'error': 'No valid access token'}
            
            result = await self._make_meta_api_call(
                'POST',
                f"https://graph.facebook.com/v18.0/{data['parent_id']}/comments",
                access_token,
                data,
                max_retries=3
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Post reply error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _schedule_post(self, user_id: str, data: Dict) -> Dict:
        """Schedule a post for later"""
        try:
            scheduled_time = datetime.fromisoformat(data['scheduled_time'])
            
            # If scheduled time is in the future, reschedule the job
            if scheduled_time > datetime.now():
                await self._reschedule_job(data['job_id'], scheduled_time)
                return {'success': True, 'message': 'Post scheduled'}
            
            # Otherwise, post immediately
            return await self._post_thread(user_id, data)
            
        except Exception as e:
            logger.error(f"Schedule post error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _bulk_publish(self, user_id: str, data: Dict) -> Dict:
        """Handle bulk publishing with rate limiting"""
        try:
            posts = data.get('posts', [])
            if not posts:
                return {'success': False, 'error': 'No posts provided'}
            
            # Check bulk operation limits
            bulk_check = await self._check_bulk_limits(user_id)
            if not bulk_check['can_bulk']:
                return {'success': False, 'error': bulk_check['message']}
            
            results = []
            for i, post in enumerate(posts):
                # Add delay between posts
                if i > 0:
                    await asyncio.sleep(random.uniform(2, 5))  # Random delay 2-5 seconds
                
                result = await self._post_thread(user_id, post)
                results.append(result)
                
                if not result['success']:
                    break  # Stop on first failure
            
            success_count = sum(1 for r in results if r['success'])
            return {
                'success': success_count == len(posts),
                'results': results,
                'success_count': success_count,
                'total_count': len(posts)
            }
            
        except Exception as e:
            logger.error(f"Bulk publish error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _make_meta_api_call(self, method: str, url: str, access_token: str, 
                                data: Dict, max_retries: int = 3) -> Dict:
        """Make API call to Meta with intelligent retry logic"""
        import httpx
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    headers = {
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'
                    }
                    
                    if method.upper() == 'POST':
                        response = await client.post(url, headers=headers, json=data)
                    else:
                        response = await client.get(url, headers=headers, params=data)
                    
                    if response.status_code == 200:
                        return {'success': True, 'data': response.json()}
                    elif response.status_code == 429:  # Rate limited
                        retry_after = int(response.headers.get('Retry-After', 60))
                        await asyncio.sleep(retry_after)
                        continue
                    else:
                        response.raise_for_status()
                        
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    # Rate limited, use exponential backoff
                    delay = self.backoff_strategies['exponential'](attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    return {'success': False, 'error': f'HTTP {e.response.status_code}: {e.response.text}'}
            except Exception as e:
                if attempt < max_retries - 1:
                    delay = self.backoff_strategies['jitter'](attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    return {'success': False, 'error': str(e)}
        
        return {'success': False, 'error': 'Max retries exceeded'}
    
    async def _check_rate_limits(self, user_id: str, job_type: JobType) -> Dict:
        """Check if user can add/process job based on rate limits"""
        try:
            today = datetime.now().date().isoformat()
            
            # Get today's usage
            response = await self.supabase.table('api_usage')\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('date', today)\
                .single()\
                .execute()
            
            usage = response.data if response.data else {
                'posts_today': 0,
                'replies_today': 0,
                'requests_hour': 0,
                'bulk_operations': 0
            }
            
            # Check limits based on job type
            if job_type == JobType.POST_THREAD:
                can_add = usage.get('posts_today', 0) < self.rate_limits['posts_per_day']
                message = f"Daily post limit exceeded ({self.rate_limits['posts_per_day']})"
            elif job_type == JobType.POST_REPLY:
                can_add = usage.get('replies_today', 0) < self.rate_limits['replies_per_day']
                message = f"Daily reply limit exceeded ({self.rate_limits['replies_per_day']})"
            elif job_type == JobType.BULK_PUBLISH:
                can_add = usage.get('bulk_operations', 0) < self.rate_limits['bulk_operations']
                message = f"Daily bulk operation limit exceeded ({self.rate_limits['bulk_operations']})"
            else:
                can_add = True
                message = ""
            
            return {
                'can_add': can_add,
                'can_process': can_add,
                'message': message,
                'usage': usage
            }
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return {'can_add': True, 'can_process': True, 'message': '', 'usage': {}}
    
    async def _check_bulk_limits(self, user_id: str) -> Dict:
        """Check bulk operation limits"""
        try:
            today = datetime.now().date().isoformat()
            
            response = await self.supabase.table('api_usage')\
                .select('bulk_operations')\
                .eq('user_id', user_id)\
                .eq('date', today)\
                .single()\
                .execute()
            
            bulk_ops = response.data.get('bulk_operations', 0) if response.data else 0
            
            return {
                'can_bulk': bulk_ops < self.rate_limits['bulk_operations'],
                'message': f"Daily bulk operation limit exceeded ({self.rate_limits['bulk_operations']})"
            }
            
        except Exception as e:
            logger.error(f"Bulk limit check error: {e}")
            return {'can_bulk': True, 'message': ''}
    
    async def _handle_rate_limit(self, job: Dict, rate_check: Dict):
        """Handle rate limit exceeded"""
        await self._update_job_status(job['id'], JobStatus.RATE_LIMITED, {
            'error': rate_check['message'],
            'retry_after': 'tomorrow'
        })
        
        # Log rate limit event
        await self.supabase.table('rate_limit_logs').insert({
            'user_id': job['user_id'],
            'job_id': job['id'],
            'job_type': job['job_type'],
            'timestamp': datetime.now().isoformat(),
            'message': rate_check['message']
        }).execute()
    
    async def _handle_job_failure(self, job: Dict, result: Dict):
        """Handle job failure with retry logic"""
        attempts = job.get('attempts', 0) + 1
        
        if attempts < self.max_retries:
            # Retry with backoff
            delay = self.backoff_strategies['jitter'](attempts)
            retry_time = datetime.now() + timedelta(seconds=delay)
            
            await self._update_job_status(job['id'], JobStatus.RETRY, {
                'error': result.get('error', 'Unknown error'),
                'attempts': attempts,
                'retry_time': retry_time.isoformat()
            })
            
            # Reschedule job
            await self._reschedule_job(job['id'], retry_time)
        else:
            # Max retries exceeded
            await self._update_job_status(job['id'], JobStatus.FAILED, {
                'error': result.get('error', 'Max retries exceeded'),
                'attempts': attempts
            })
    
    async def _update_job_status(self, job_id: str, status: JobStatus, result: Dict = None):
        """Update job status and result"""
        try:
            update_data = {
                'status': status.value,
                'updated_at': datetime.now().isoformat()
            }
            
            if result:
                update_data['result'] = json.dumps(result)
            
            if status == JobStatus.RETRY:
                update_data['attempts'] = result.get('attempts', 0)
            
            await self.supabase.table('job_queue')\
                .update(update_data)\
                .eq('id', job_id)\
                .execute()
                
        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
    
    async def _reschedule_job(self, job_id: str, scheduled_time: datetime):
        """Reschedule job for later execution"""
        try:
            await self.supabase.table('job_queue')\
                .update({
                    'scheduled_time': scheduled_time.isoformat(),
                    'updated_at': datetime.now().isoformat()
                })\
                .eq('id', job_id)\
                .execute()
                
        except Exception as e:
            logger.error(f"Failed to reschedule job: {e}")
    
    async def _increment_usage(self, user_id: str, job_type: str):
        """Increment usage counters"""
        try:
            today = datetime.now().date().isoformat()
            
            # Get current usage
            response = await self.supabase.table('api_usage')\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('date', today)\
                .single()\
                .execute()
            
            if response.data:
                # Update existing record
                current_usage = response.data
                updates = {}
                
                if job_type == JobType.POST_THREAD.value:
                    updates['posts_today'] = current_usage.get('posts_today', 0) + 1
                elif job_type == JobType.POST_REPLY.value:
                    updates['replies_today'] = current_usage.get('replies_today', 0) + 1
                elif job_type == JobType.BULK_PUBLISH.value:
                    updates['bulk_operations'] = current_usage.get('bulk_operations', 0) + 1
                
                updates['requests_hour'] = current_usage.get('requests_hour', 0) + 1
                updates['updated_at'] = datetime.now().isoformat()
                
                await self.supabase.table('api_usage')\
                    .update(updates)\
                    .eq('id', response.data['id'])\
                    .execute()
            else:
                # Create new record
                new_usage = {
                    'user_id': user_id,
                    'date': today,
                    'posts_today': 1 if job_type == JobType.POST_THREAD.value else 0,
                    'replies_today': 1 if job_type == JobType.POST_REPLY.value else 0,
                    'requests_hour': 1,
                    'bulk_operations': 1 if job_type == JobType.BULK_PUBLISH.value else 0,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                
                await self.supabase.table('api_usage').insert(new_usage).execute()
                
        except Exception as e:
            logger.error(f"Failed to increment usage: {e}")
    
    def _calculate_job_delay(self, job: Dict) -> float:
        """Calculate delay between jobs based on type and rate limits"""
        base_delay = 1.0
        
        if job['job_type'] == JobType.BULK_PUBLISH.value:
            base_delay = 5.0  # Longer delay for bulk operations
        
        # Add jitter to prevent thundering herd
        jitter = random.uniform(0, 0.5)
        return base_delay + jitter


# Global job queue instance
job_queue = JobQueue()


# Background task to process jobs
async def process_jobs_background():
    """Background task to continuously process jobs"""
    while True:
        try:
            await job_queue.process_jobs()
        except Exception as e:
            logger.error(f"Job processing background error: {e}")
            await asyncio.sleep(10)  # Wait before retrying
