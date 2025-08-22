"""
AI Routes for Kolekt
Handles AI-powered content generation and optimization
"""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.services.ai_service import (
    ai_service, 
    ContentGenerationRequest, 
    ContentGenerationResponse
)
from src.services.authentication import get_current_user, require_admin

logger = logging.getLogger(__name__)
router = APIRouter()
# Export alias for inclusion consistency
ai_router = router

class ContentOptimizationRequest(BaseModel):
    """Request model for content optimization"""
    content: str
    target_platform: str
    optimization_type: str = "engagement"  # "engagement", "reach", "conversion"
    target_audience: str = "general"

class ContentOptimizationResponse(BaseModel):
    """Response model for content optimization"""
    optimized_content: str
    suggestions: List[str]
    confidence_score: float
    model_used: str

class HashtagGenerationRequest(BaseModel):
    """Request model for hashtag generation"""
    content: str
    platform: str
    count: int = 10

class HashtagGenerationResponse(BaseModel):
    """Response model for hashtag generation"""
    hashtags: List[str]
    relevance_scores: List[float]
    model_used: str

@router.post("/generate-content", response_model=ContentGenerationResponse)
async def generate_content(
    request: ContentGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate AI-powered content for social media"""
    try:
        logger.info(f"Generating content for user {current_user.get('id')} about {request.topic}")
        
        response = ai_service.generate_content(request)
        
        logger.info(f"Content generated successfully using {response.model_used}")
        return response
        
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate content")

@router.post("/optimize-content", response_model=ContentOptimizationResponse)
async def optimize_content(
    request: ContentOptimizationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Optimize existing content for better performance"""
    try:
        logger.info(f"Optimizing content for user {current_user.get('id')}")
        
        # For now, return a simple optimization
        # In the future, this will use Mistral or another optimization model
        optimized_content = request.content
        
        suggestions = [
            "Consider adding more engaging questions",
            "Include relevant hashtags",
            "Add a call-to-action",
            "Use more visual language"
        ]
        
        return ContentOptimizationResponse(
            optimized_content=optimized_content,
            suggestions=suggestions,
            confidence_score=0.75,
            model_used="content-optimizer"
        )
        
    except Exception as e:
        logger.error(f"Error optimizing content: {e}")
        raise HTTPException(status_code=500, detail="Failed to optimize content")

@router.post("/generate-hashtags", response_model=HashtagGenerationResponse)
async def generate_hashtags(
    request: HashtagGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate relevant hashtags for content"""
    try:
        logger.info(f"Generating hashtags for user {current_user.get('id')}")
        
        # Extract hashtags from the AI service
        hashtags = ai_service._generate_hashtags(request.content)
        
        # Limit to requested count
        hashtags = hashtags[:request.count]
        
        # Generate relevance scores (mock for now)
        relevance_scores = [0.8] * len(hashtags)
        
        return HashtagGenerationResponse(
            hashtags=hashtags,
            relevance_scores=relevance_scores,
            model_used="hashtag-generator"
        )
        
    except Exception as e:
        logger.error(f"Error generating hashtags: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate hashtags")

# ----- Frontend compatibility alias endpoints -----

class SimpleContentRequest(BaseModel):
    content: str


@router.post("/suggest-title")
async def suggest_title(
    payload: SimpleContentRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        text = (payload.content or "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="content is required")
        first_sentence = text.split(".")[0]
        words = first_sentence.split()[:6]
        title = (" ".join(words) + ("..." if len(words) == 6 else "")).strip()
        return {"success": True, "title": title or "Untitled"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"suggest_title failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to suggest title")


@router.post("/suggest-hashtags")
async def suggest_hashtags_alias(
    payload: HashtagGenerationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    # Delegate to existing implementation
    return await generate_hashtags(payload, current_user)


@router.post("/optimize")
async def optimize_alias(
    payload: ContentOptimizationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    # Delegate to existing implementation
    return await optimize_content(payload, current_user)


@router.post("/generate-thread")
async def generate_thread(
    payload: SimpleContentRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        text = (payload.content or "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="content is required")
        # Naive thread splitter: ~260 chars per chunk
        chunks: List[str] = []
        step = 260
        for i in range(0, len(text), step):
            chunks.append(text[i:i+step])
        thread = "\n\n".join(f"{i+1}/{len(chunks)} {c}" for i, c in enumerate(chunks))
        return {"success": True, "thread_content": thread}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"generate_thread failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate thread")

@router.post("/format-content")
async def format_content(
    request: dict,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Format content for different platforms"""
    try:
        logger.info(f"Formatting content for user {current_user.get('id')}")
        
        content = request.get("content", "")
        format_type = request.get("format", "threads")
        
        if not content:
            raise HTTPException(status_code=400, detail="Content is required")
        
        # Generate platform-specific formatting
        formatted_content = ai_service._format_content_for_platform(content, format_type)
        
        return {"formatted_content": formatted_content}
        
    except Exception as e:
        logger.error(f"Error formatting content: {e}")
        raise HTTPException(status_code=500, detail="Failed to format content")

@router.get("/models/available")
async def get_available_models(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get list of available AI models"""
    try:
        models = [
            {
                "id": "llama-3.1-8b",
                "name": "Llama 3.1 8B",
                "type": "content_generation",
                "description": "Meta's Llama 3.1 model for creative content generation",
                "capabilities": ["content_generation", "creative_writing", "conversational"]
            },
            {
                "id": "content-optimizer",
                "name": "Content Optimizer",
                "type": "optimization",
                "description": "Optimizes content for better engagement",
                "capabilities": ["content_optimization", "platform_adaptation"]
            },
            {
                "id": "hashtag-generator",
                "name": "Hashtag Generator",
                "type": "hashtag_generation",
                "description": "Generates relevant hashtags for content",
                "capabilities": ["hashtag_generation", "trend_analysis"]
            }
        ]
        
        return {"models": models}
        
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        raise HTTPException(status_code=500, detail="Failed to get available models")

@router.get("/health")
async def ai_health_check(current_user: Dict[str, Any] = Depends(require_admin)):
    """Health check for AI services (admin only)"""
    try:
        hf_available = ai_service.client is not None
        return {
            "status": "healthy" if hf_available else "degraded",
            "huggingface_available": hf_available,
            "models_ready": hf_available
        }
    except Exception as e:
        logger.error(f"AI health check failed: {e}")
        return {
            "status": "unhealthy",
            "huggingface_available": False,
            "models_ready": False,
            "error": str(e)
        }
