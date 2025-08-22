"""
Main API router for ThreadStorm
"""

import logging
from fastapi import APIRouter, Body, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

from src.services.threads_formatter import ThreadsFormatter
from src.services.templates import TemplateLibrary, TemplateCategory
from src.services.threads_api import threads_service, ThreadsResponse
from src.services.analytics import AnalyticsService
from src.api.auth_routes import auth_router
from src.api.admin_routes import admin_router
from src.api.templates import templates_router
from src.api.curation_routes import curation_router
from src.api.content_routes import content_router
from src.api.threads_routes import threads_router
from src.api.social_routes import social_router
from src.api.subscription_routes import subscription_router
from src.api.ai_routes import ai_router
from src.api.import_routes import import_router
from src.api.connections_routes import connections_router
from src.api.analytics_routes import analytics_router
from src.api.health_routes import health_router
from src.api.announcements_routes import announcements_router

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
api_router.include_router(templates_router, prefix="/templates", tags=["Templates"])
api_router.include_router(curation_router, prefix="/curation", tags=["Curation"])
api_router.include_router(content_router, prefix="/content", tags=["Content"])
api_router.include_router(threads_router, prefix="/threads", tags=["Threads"])
api_router.include_router(social_router, prefix="/social", tags=["Social"])
api_router.include_router(subscription_router, prefix="/subscription", tags=["Subscription"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI Assistant"])
api_router.include_router(import_router, prefix="/import", tags=["Content Import"])
api_router.include_router(connections_router, prefix="/connections", tags=["Social Connections"]) 
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"]) 
api_router.include_router(health_router, prefix="/system", tags=["System Health"]) 
api_router.include_router(announcements_router, prefix="/announcements", tags=["Announcements"]) 

# Initialize services
formatter = ThreadsFormatter()
template_library = TemplateLibrary()
analytics_service = AnalyticsService()

logger = logging.getLogger(__name__)


class FormatRequest(BaseModel):
    content: Optional[str] = None
    images: Optional[List[str]] = None
    tone: Optional[str] = "professional"
    include_numbering: Optional[bool] = True


class PostResponse(BaseModel):
    post_number: int
    total_posts: int
    content: str
    character_count: int
    image_suggestion: Optional[str] = None


class FormatResponse(BaseModel):
    total_posts: int
    total_characters: int
    engagement_score: float
    suggestions: List[str]
    posts: List[PostResponse]
    rendered_output: str


class ThreadsAuthRequest(BaseModel):
    user_id: str
    access_token: str


class ThreadsPublishRequest(BaseModel):
    user_id: str
    posts: List[str]
    images: Optional[List[List[str]]] = None
    scheduled_time: Optional[datetime] = None


class ThreadsPublishResponse(BaseModel):
    success: bool
    responses: List[dict]
    error_message: Optional[str] = None


class UsageResponse(BaseModel):
    current_usage: int
    usage_limit: int
    remaining: int
    exceeded: bool
    usage_percentage: float


class AnalyticsResponse(BaseModel):
    total_threadstorms: int
    total_characters: int
    total_api_calls: int
    average_engagement: float
    most_used_tone: str
    has_images: bool
    period_start: str
    period_end: str


# Dependency to get current user (placeholder for now)
async def get_current_user(request: Request):
    """Get current user from request (placeholder)"""
    # This would be implemented with proper JWT authentication
    # For now, return a placeholder user ID
    return "placeholder-user-id"


@api_router.post("/format", response_model=FormatResponse)
async def format_threads_payload(
    payload: FormatRequest = Body(...),
    current_user: str = Depends(get_current_user)
) -> FormatResponse:
    """Format content into Threads-optimized posts with anti-spam protection"""
    try:
        # Enhanced content validation
        if not payload.content or len(payload.content.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Content must be at least 10 characters long. Please provide meaningful content."
            )
        
        if len(payload.content) > 10000:
            raise HTTPException(
                status_code=400,
                detail="Content is too long (max 10,000 characters). Please break it into smaller sections."
            )
        
        # Check for spam indicators
        spam_indicators = await check_content_quality(payload.content)
        if spam_indicators['is_spam']:
            raise HTTPException(
                status_code=400,
                detail=f"Content appears to be spam. Please review: {spam_indicators['message']}"
            )
        
        # Check usage limits with enhanced messaging
        usage_check = await analytics_service.check_usage_limits(current_user, 'free')
        if usage_check['exceeded']:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Usage limit exceeded",
                    "message": f"You've used {usage_check['current_usage']}/{usage_check['usage_limit']} threadstorms this month.",
                    "upgrade_message": "Upgrade to Pro for unlimited threadstorms and advanced features.",
                    "current_usage": usage_check['current_usage'],
                    "usage_limit": usage_check['usage_limit'],
                    "remaining": usage_check['remaining']
                }
            )
        
        # Format the threadstorm
        result = formatter.format_threadstorm(
            content=payload.content,
            images=payload.images,
            tone=payload.tone or "professional",
            include_numbering=payload.include_numbering if payload.include_numbering is not None else True,
        )
        
        # Track usage with quality metrics
        await analytics_service.track_threadstorm_creation(current_user, {
            'total_posts': result.total_posts,
            'total_characters': result.total_characters,
            'tone': payload.tone or "professional",
            'has_images': bool(payload.images),
            'engagement_score': result.engagement_score,
            'include_numbering': payload.include_numbering if payload.include_numbering is not None else True,
            'quality_score': spam_indicators['quality_score'],
            'spam_indicators': spam_indicators['indicators']
        })
        
        return FormatResponse(
            total_posts=result.total_posts,
            total_characters=result.total_characters,
            engagement_score=result.engagement_score,
            suggestions=result.suggestions,
            posts=[
                PostResponse(
                    post_number=p.post_number,
                    total_posts=p.total_posts,
                    content=p.content,
                    character_count=p.character_count,
                    image_suggestion=p.image_suggestion,
                )
                for p in result.posts
            ],
            rendered_output=result.rendered_output,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error formatting threadstorm: {e}")
        raise HTTPException(status_code=500, detail="Failed to format threadstorm")


@api_router.get("/usage", response_model=UsageResponse)
async def get_usage_limits(current_user: str = Depends(get_current_user)):
    """Get current usage and limits for the user"""
    try:
        usage = await analytics_service.check_usage_limits(current_user, 'free')
        return UsageResponse(**usage)
    except Exception as e:
        logger.error(f"Error getting usage limits: {e}")
        raise HTTPException(status_code=500, detail="Failed to get usage limits")


@api_router.get("/analytics", response_model=AnalyticsResponse)
async def get_user_analytics(
    current_user: str = Depends(get_current_user),
    date_range: str = "30d"
):
    """Get user analytics and performance insights"""
    try:
        # Get user usage metrics
        usage_metrics = await analytics_service.get_user_usage(current_user, date_range)
        
        return AnalyticsResponse(
            total_threadstorms=usage_metrics.total_threadstorms,
            total_characters=usage_metrics.total_characters,
            total_api_calls=usage_metrics.total_api_calls,
            average_engagement=usage_metrics.average_engagement,
            most_used_tone=usage_metrics.most_used_tone,
            has_images=usage_metrics.has_images,
            period_start=usage_metrics.period_start.isoformat(),
            period_end=usage_metrics.period_end.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting user analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")


@api_router.get("/analytics/activity")
async def get_user_activity_timeline(
    current_user: str = Depends(get_current_user),
    days: int = 30
):
    """Get user activity timeline"""
    try:
        activity = await analytics_service.get_user_activity_timeline(current_user, days)
        return activity
    except Exception as e:
        logger.error(f"Error getting activity timeline: {e}")
        raise HTTPException(status_code=500, detail="Failed to get activity timeline")


@api_router.get("/analytics/templates/popular")
async def get_popular_templates(limit: int = 10):
    """Get most popular templates"""
    try:
        templates = await analytics_service.get_popular_templates(limit)
        return templates
    except Exception as e:
        logger.error(f"Error getting popular templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get popular templates")


@api_router.get("/templates/legacy", response_model=List[dict])
async def get_legacy_templates(
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Get legacy templates (for backward compatibility)"""
    try:
        if search:
            templates = template_library.search_templates(search)
        elif category:
            try:
                cat = TemplateCategory(category)
                templates = template_library.get_templates(cat)
            except ValueError:
                templates = []
        else:
            templates = template_library.get_templates()
        
        return [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "category": t.category.value,
                "content": t.content,
                "tone": t.tone,
                "tags": t.tags,
                "usage_count": t.usage_count,
                "is_featured": t.is_featured,
            }
            for t in templates
        ]
    except Exception as e:
        logger.error(f"Error getting legacy templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get templates")


@api_router.get("/templates/legacy/featured", response_model=List[dict])
async def get_legacy_featured_templates(current_user: str = Depends(get_current_user)):
    """Get legacy featured templates"""
    try:
        templates = template_library.get_featured_templates()
        return [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "category": t.category.value,
                "content": t.content,
                "tone": t.tone,
                "tags": t.tags,
                "usage_count": t.usage_count,
                "is_featured": t.is_featured,
            }
            for t in templates
        ]
    except Exception as e:
        logger.error(f"Error getting featured templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get featured templates")


@api_router.get("/templates/legacy/{template_id}", response_model=dict)
async def get_legacy_template(
    template_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get a specific legacy template by ID"""
    try:
        template = template_library.get_template_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Track template usage
        await analytics_service.track_template_usage(current_user, template_id, template.name)
        
        # Increment usage count
        template_library.increment_usage(template_id)
        
        return {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "category": template.category.value,
            "content": template.content,
            "tone": template.tone,
            "tags": template.tags,
            "usage_count": template.usage_count,
            "is_featured": template.is_featured,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get template")


@api_router.get("/templates/legacy/categories", response_model=List[dict])
async def get_legacy_template_categories(current_user: str = Depends(get_current_user)):
    """Get legacy template categories"""
    try:
        categories = template_library.get_categories()
        return categories
    except Exception as e:
        logger.error(f"Error getting template categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get template categories")


@api_router.post("/threads/auth")
async def authenticate_threads(
    payload: ThreadsAuthRequest,
    current_user: str = Depends(get_current_user)
):
    """Authenticate with Threads API"""
    try:
        # Track API call
        await analytics_service.track_api_call(current_user, "/threads/auth", {
            'method': 'POST',
            'user_id': payload.user_id
        })
        
        # Test connection to real Threads API
        success = await threads_service.test_connection(payload.user_id)
        
        if success:
            # Get user info to verify authentication
            user_info = await threads_service.get_user_info(payload.user_id)
            return {
                "success": True,
                "message": "Threads API authentication successful",
                "user_info": user_info
            }
        else:
            return {
                "success": False,
                "message": "Threads API authentication failed. Please check your API credentials."
            }
            
    except Exception as e:
        logger.error(f"Error authenticating with Threads API: {e}")
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")


@api_router.post("/threads/publish", response_model=ThreadsPublishResponse)
async def publish_to_threads(
    payload: ThreadsPublishRequest,
    current_user: str = Depends(get_current_user)
):
    """Publish threadstorm to Threads with enhanced spam prevention"""
    try:
        # Validate posts before publishing
        if not payload.posts or len(payload.posts) == 0:
            raise HTTPException(
                status_code=400,
                detail="No posts to publish. Please format content first."
            )
        
        if len(payload.posts) > 20:
            raise HTTPException(
                status_code=400,
                detail="Too many posts (max 20). Please break content into smaller threadstorms."
            )
        
        # Check each post for spam
        for i, post in enumerate(payload.posts):
            if len(post) < 10:
                raise HTTPException(
                    status_code=400,
                    detail=f"Post {i+1} is too short (min 10 characters). Please provide meaningful content."
                )
            
            if len(post) > 500:
                raise HTTPException(
                    status_code=400,
                    detail=f"Post {i+1} exceeds Threads limit (max 500 characters). Please shorten content."
                )
            
            spam_check = await check_content_quality(post)
            if spam_check['is_spam']:
                raise HTTPException(
                    status_code=400,
                    detail=f"Post {i+1} appears to be spam: {spam_check['message']}"
                )
        
        # Check publishing limits
        publishing_limits = await check_publishing_limits(current_user)
        if not publishing_limits['can_publish']:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Publishing limit exceeded",
                    "message": publishing_limits['message'],
                    "retry_after": publishing_limits['retry_after'],
                    "daily_posts": publishing_limits['daily_posts'],
                    "daily_limit": publishing_limits['daily_limit']
                }
            )
        
        # Track API call
        await analytics_service.track_api_call(current_user, "/threads/publish", {
            'method': 'POST',
            'posts_count': len(payload.posts),
            'has_images': bool(payload.images),
            'content_quality': 'validated'
        })
        
        # Publish to real Threads API
        responses = await threads_service.publish_threadstorm(
            user_id=payload.user_id,
            posts=payload.posts,
            images=payload.images,
            scheduled_time=payload.scheduled_time
        )
        
        # Check if all posts were successful
        all_successful = all(r.success for r in responses)
        
        # Track publishing activity
        await track_publishing_activity(current_user, len(payload.posts), all_successful)
        
        return ThreadsPublishResponse(
            success=all_successful,
            responses=[{
                "post_id": r.post_id,
                "success": r.success,
                "error_message": r.error_message,
                "response_time": r.response_time
            } for r in responses]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing to Threads: {e}")
        return ThreadsPublishResponse(
            success=False,
            responses=[],
            error_message=str(e)
        )


@api_router.get("/threads/user/{user_id}")
async def get_threads_user_info(
    user_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get Threads user information from real API"""
    try:
        # Track API call
        await analytics_service.track_api_call(current_user, "/threads/user/{user_id}", {
            'method': 'GET',
            'target_user_id': user_id
        })
        
        # Get real user info from Threads API
        user_info = await threads_service.get_user_info(user_id)
        
        if "error" in user_info:
            raise HTTPException(status_code=500, detail=user_info["error"])
        
        return user_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Threads user info: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching user info: {str(e)}")


@api_router.get("/threads/posts/{user_id}")
async def get_threads_recent_posts(
    user_id: str,
    limit: int = 10,
    current_user: str = Depends(get_current_user)
):
    """Get recent Threads posts from real API"""
    try:
        # Track API call
        await analytics_service.track_api_call(current_user, "/threads/posts/{user_id}", {
            'method': 'GET',
            'target_user_id': user_id,
            'limit': limit
        })
        
        # Get real posts from Threads API
        posts = await threads_service.get_recent_posts(user_id, limit)
        
        return {
            "user_id": user_id,
            "posts": posts,
            "total": len(posts)
        }
        
    except Exception as e:
        logger.error(f"Error getting Threads posts: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching posts: {str(e)}")


@api_router.post("/threads/test-connection")
async def test_threads_connection(
    payload: ThreadsAuthRequest,
    current_user: str = Depends(get_current_user)
):
    """Test Threads API connection with real API"""
    try:
        # Track API call
        await analytics_service.track_api_call(current_user, "/threads/test-connection", {
            'method': 'POST',
            'user_id': payload.user_id
        })
        
        # Test real connection to Threads API
        success = await threads_service.test_connection(payload.user_id)
        
        if success:
            # Get additional connection details
            user_info = await threads_service.get_user_info(payload.user_id)
            return {
                "success": True,
                "message": "Threads API connection successful",
                "user_info": user_info,
                "api_version": "v18.0",
                "endpoint": "https://graph.instagram.com/v18.0"
            }
        else:
            return {
                "success": False,
                "message": "Threads API connection failed. Please check your API credentials and permissions.",
                "api_version": "v18.0",
                "endpoint": "https://graph.instagram.com/v18.0"
            }
            
    except Exception as e:
        logger.error(f"Error testing Threads connection: {e}")
        raise HTTPException(status_code=500, detail=f"Connection test error: {str(e)}")


@api_router.get("/popular-templates")
async def get_popular_templates(
    limit: int = 10,
    current_user: str = Depends(get_current_user)
):
    """Get most popular templates"""
    try:
        templates = await analytics_service.get_popular_templates(limit)
        return templates
    except Exception as e:
        logger.error(f"Error getting popular templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to get popular templates")


@api_router.get("/activity-timeline")
async def get_user_activity_timeline(
    days: int = 30,
    current_user: str = Depends(get_current_user)
):
    """Get user activity timeline"""
    try:
        activity = await analytics_service.get_user_activity_timeline(current_user, days)
        return activity
    except Exception as e:
        logger.error(f"Error getting activity timeline: {e}")
        raise HTTPException(status_code=500, detail="Failed to get activity timeline")


# Helper functions for anti-spam measures
async def check_content_quality(content: str) -> Dict:
    """Check content quality and detect spam indicators"""
    indicators = {}
    quality_score = 100.0
    
    # Check for excessive caps
    if content.isupper():
        indicators['excessive_caps'] = True
        quality_score -= 20
    
    # Check for excessive punctuation
    if content.count('!') > 3 or content.count('?') > 3:
        indicators['excessive_punctuation'] = True
        quality_score -= 15
    
    # Check for repetitive words
    words = content.lower().split()
    if len(words) > 5:
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Only check meaningful words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        max_freq = max(word_freq.values()) if word_freq else 0
        if max_freq > len(words) * 0.2:  # 20% repetition
            indicators['repetitive_words'] = True
            quality_score -= 25
    
    # Check for suspicious patterns
    suspicious_patterns = [
        r'\b(buy\s+now|click\s+here|free\s+offer|limited\s+time)\b',
        r'\b(earn\s+money|make\s+money|work\s+from\s+home)\b',
        r'\b(weight\s+loss|diet\s+pills|miracle\s+cure)\b',
        r'\b(viagra|cialis|casino|poker|bet)\b',
        r'\b(loan|debt|credit|refinance)\b',
        r'\b(degree|diploma|certificate)\b',
    ]
    
    import re
    for pattern in suspicious_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            indicators['suspicious_patterns'] = True
            quality_score -= 30
            break
    
    # Check for URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    if re.search(url_pattern, content):
        indicators['contains_urls'] = True
        quality_score -= 15
    
    # Determine if content is spam
    is_spam = quality_score < 50 or len(indicators) >= 3
    
    # Generate helpful message
    message = "Content looks good!"
    if indicators:
        issues = []
        if indicators.get('excessive_caps'):
            issues.append("Avoid using ALL CAPS")
        if indicators.get('excessive_punctuation'):
            issues.append("Reduce excessive punctuation")
        if indicators.get('repetitive_words'):
            issues.append("Avoid repetitive words")
        if indicators.get('suspicious_patterns'):
            issues.append("Avoid suspicious marketing language")
        if indicators.get('contains_urls'):
            issues.append("Remove URLs from content")
        
        message = f"Please review: {', '.join(issues)}"
    
    return {
        'is_spam': is_spam,
        'quality_score': quality_score,
        'indicators': indicators,
        'message': message
    }


async def check_publishing_limits(user_id: str) -> Dict:
    """Check if user can publish based on daily limits"""
    try:
        # Get user's daily publishing count
        today = datetime.now().strftime('%Y-%m-%d')
        daily_key = f"daily_posts:{user_id}:{today}"
        
        # This would integrate with Redis/analytics service
        daily_posts = 0  # Placeholder - would get from analytics
        
        # Get user's plan limits
        plan = 'free'  # Placeholder - would get from user profile
        daily_limit = 10 if plan == 'free' else 100  # Example limits
        
        if daily_posts >= daily_limit:
            return {
                'can_publish': False,
                'message': f'Daily publishing limit reached ({daily_limit} posts). Try again tomorrow or upgrade your plan.',
                'retry_after': 'tomorrow',
                'daily_posts': daily_posts,
                'daily_limit': daily_limit
            }
        
        return {
            'can_publish': True,
            'daily_posts': daily_posts,
            'daily_limit': daily_limit
        }
        
    except Exception as e:
        logger.error(f"Error checking publishing limits: {e}")
        return {'can_publish': True}  # Allow if check fails


async def track_publishing_activity(user_id: str, posts_count: int, success: bool):
    """Track publishing activity for spam prevention"""
    try:
        # Track daily publishing count
        today = datetime.now().strftime('%Y-%m-%d')
        daily_key = f"daily_posts:{user_id}:{today}"
        
        # This would integrate with analytics service
        # await analytics_service.increment_daily_posts(user_id, posts_count)
        
        # Track publishing success rate
        if success:
            # await analytics_service.track_successful_publish(user_id, posts_count)
            pass
        else:
            # await analytics_service.track_failed_publish(user_id, posts_count)
            pass
            
    except Exception as e:
        logger.error(f"Error tracking publishing activity: {e}")


@api_router.get("/content-guidelines")
async def get_content_guidelines():
    """Get content guidelines to help users avoid spam detection"""
    return {
        "guidelines": {
            "do": [
                "Write original, engaging content",
                "Use natural language and tone",
                "Keep posts under 500 characters",
                "Include relevant hashtags (max 3-5)",
                "Use proper grammar and spelling",
                "Add value to your audience",
                "Engage with your community"
            ],
            "dont": [
                "Use excessive caps or punctuation",
                "Include suspicious marketing language",
                "Post repetitive or duplicate content",
                "Include URLs in posts",
                "Use spam keywords (buy now, earn money, etc.)",
                "Post too frequently (max 10/day for free users)",
                "Use automated posting tools"
            ],
            "limits": {
                "free": {
                    "daily_posts": 10,
                    "monthly_threadstorms": 10,
                    "rate_limit": "10 requests/minute"
                },
                "pro": {
                    "daily_posts": 100,
                    "monthly_threadstorms": 100,
                    "rate_limit": "100 requests/minute"
                },
                "business": {
                    "daily_posts": 500,
                    "monthly_threadstorms": 1000,
                    "rate_limit": "500 requests/minute"
                }
            }
        }
    }
