#!/usr/bin/env python3
"""
AI Assistant API Routes
Handles AI-powered content generation, optimization, and suggestions
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import asyncio
import json

# Setup logging
logger = logging.getLogger(__name__)

# Create router
ai_router = APIRouter()

# Pydantic models
from pydantic import BaseModel

class AIGenerationRequest(BaseModel):
    prompt: str
    tone: str = "professional"  # professional, casual, friendly, authoritative, humorous, inspirational
    length: str = "medium"  # short, medium, long, thread
    platform: str = "general"  # threads, instagram, facebook, linkedin, twitter, general
    context: Optional[str] = None
    keywords: Optional[List[str]] = None
    target_audience: Optional[str] = None

class AIOptimizationRequest(BaseModel):
    content: str
    platform: str
    goal: str = "engagement"  # engagement, reach, conversions, brand_awareness
    tone_adjustment: Optional[str] = None
    length_adjustment: Optional[str] = None

class AISuggestionRequest(BaseModel):
    content_type: str  # thread, post, caption, story
    topic: Optional[str] = None
    industry: Optional[str] = None
    platform: str = "general"

class AIResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    suggestions: Optional[List[str]] = None
    optimization_tips: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AIGenerationResponse(BaseModel):
    success: bool
    generated_content: str
    alternatives: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    optimization_score: Optional[float] = None
    error_message: Optional[str] = None

from src.services.authentication import get_current_user

# Dependency to get current user (via JWT)
async def get_current_user_id(current_user: Dict = Depends(get_current_user)) -> str:
    """Get current user ID from JWT-authenticated request"""
    return current_user["user_id"]

@ai_router.post("/generate", response_model=AIGenerationResponse)
async def generate_content(
    request: AIGenerationRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Generate AI-powered content based on prompt and parameters"""
    try:
        logger.info(f"Generating AI content for user {user_id}: {request.prompt[:50]}...")
        
        # Simulate AI processing delay
        await asyncio.sleep(2)
        
        # Generate content based on parameters
        generated_content = await _generate_ai_content(request)
        
        # Generate hashtags
        hashtags = await _generate_hashtags(request.prompt, request.platform)
        
        # Calculate optimization score
        optimization_score = await _calculate_optimization_score(generated_content, request.platform)
        
        return AIGenerationResponse(
            success=True,
            generated_content=generated_content,
            hashtags=hashtags,
            optimization_score=optimization_score,
            alternatives=await _generate_alternatives(request)
        )
        
    except Exception as e:
        logger.error(f"Error generating AI content: {e}")
        return AIGenerationResponse(
            success=False,
            generated_content="",
            error_message=str(e)
        )

@ai_router.post("/optimize", response_model=AIResponse)
async def optimize_content(
    request: AIOptimizationRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Optimize existing content for better performance"""
    try:
        logger.info(f"Optimizing content for user {user_id}")
        
        # Simulate optimization processing
        await asyncio.sleep(1.5)
        
        # Generate optimization suggestions
        optimization_tips = await _generate_optimization_tips(request)
        
        # Generate optimized version
        optimized_content = await _optimize_content_text(request.content, request.platform, request.goal)
        
        # Generate relevant hashtags
        hashtags = await _generate_hashtags(request.content, request.platform)
        
        return AIResponse(
            success=True,
            content=optimized_content,
            optimization_tips=optimization_tips,
            hashtags=hashtags,
            metadata={
                "original_length": len(request.content),
                "optimized_length": len(optimized_content),
                "improvement_score": 0.85
            }
        )
        
    except Exception as e:
        logger.error(f"Error optimizing content: {e}")
        return AIResponse(
            success=False,
            error_message=str(e)
        )

@ai_router.post("/suggest", response_model=AIResponse)
async def get_content_suggestions(
    request: AISuggestionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Get AI-powered content suggestions"""
    try:
        logger.info(f"Getting content suggestions for user {user_id}")
        
        # Simulate suggestion processing
        await asyncio.sleep(1)
        
        # Generate suggestions based on parameters
        suggestions = await _generate_content_suggestions(request)
        
        return AIResponse(
            success=True,
            suggestions=suggestions,
            metadata={
                "content_type": request.content_type,
                "platform": request.platform,
                "suggestion_count": len(suggestions)
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting content suggestions: {e}")
        return AIResponse(
            success=False,
            error_message=str(e)
        )

@ai_router.post("/refine", response_model=AIGenerationResponse)
async def refine_content(
    request: AIGenerationRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Refine and improve existing content"""
    try:
        logger.info(f"Refining content for user {user_id}")
        
        # Simulate refinement processing
        await asyncio.sleep(2)
        
        # Generate refined content
        refined_content = await _refine_content_text(request.prompt, request.tone, request.platform)
        
        return AIGenerationResponse(
            success=True,
            generated_content=refined_content,
            optimization_score=0.92
        )
        
    except Exception as e:
        logger.error(f"Error refining content: {e}")
        return AIGenerationResponse(
            success=False,
            generated_content="",
            error_message=str(e)
        )

# Helper functions for AI content generation
async def _generate_ai_content(request: AIGenerationRequest) -> str:
    """Generate AI content based on request parameters"""
    
    # Base content based on tone and length
    tone_templates = {
        "professional": "Here's a professional take on {topic}",
        "casual": "Hey! So I was thinking about {topic}",
        "friendly": "I wanted to share something interesting about {topic}",
        "authoritative": "Based on my experience with {topic}",
        "humorous": "Fun fact about {topic} that made me laugh",
        "inspirational": "Let me inspire you with this insight about {topic}"
    }
    
    length_templates = {
        "short": "This is a concise message that gets straight to the point about {topic}.",
        "medium": "This is a well-crafted paragraph that provides valuable insights about {topic} while maintaining engagement. It's perfectly sized for social media platforms.",
        "long": "This is a comprehensive piece that dives deep into {topic}. It provides detailed information, multiple perspectives, and valuable insights that will engage your audience and deliver your message effectively.",
        "thread": "🧵 Thread about {topic}:\n\n(1/3) Opening hook that captures attention\n\n(2/3) Deep dive into the details\n\n(3/3) Conclusion with actionable takeaways"
    }
    
    # Platform-specific adjustments
    platform_adjustments = {
        "threads": "Perfect for Threads' conversational format",
        "instagram": "Optimized for Instagram's visual-first approach",
        "facebook": "Tailored for Facebook's community engagement",
        "linkedin": "Professional tone for LinkedIn's business audience",
        "twitter": "Concise and impactful for Twitter's character limit",
        "general": "Versatile content for any platform"
    }
    
    # Generate content
    base_template = tone_templates.get(request.tone, tone_templates["professional"])
    length_template = length_templates.get(request.length, length_templates["medium"])
    platform_note = platform_adjustments.get(request.platform, "")
    
    content = f"{base_template.format(topic=request.prompt)}\n\n{length_template.format(topic=request.prompt)}\n\n{platform_note}"
    
    # Add context if provided
    if request.context:
        content += f"\n\nContext: {request.context}"
    
    # Add keywords if provided
    if request.keywords:
        content += f"\n\nKey points: {', '.join(request.keywords)}"
    
    return content

async def _generate_hashtags(content: str, platform: str) -> List[str]:
    """Generate relevant hashtags for content"""
    
    # Platform-specific hashtag strategies
    platform_hashtags = {
        "threads": ["#Threads", "#SocialMedia", "#ContentCreation"],
        "instagram": ["#Instagram", "#InstaGood", "#SocialMedia"],
        "facebook": ["#Facebook", "#SocialMedia", "#Community"],
        "linkedin": ["#LinkedIn", "#Professional", "#Networking"],
        "twitter": ["#Twitter", "#SocialMedia", "#Content"],
        "general": ["#ContentCreation", "#SocialMedia", "#DigitalMarketing"]
    }
    
    # Extract potential hashtags from content
    words = content.lower().split()
    potential_tags = [word.strip('.,!?') for word in words if len(word) > 3]
    
    # Combine platform-specific and content-based hashtags
    hashtags = platform_hashtags.get(platform, platform_hashtags["general"])
    hashtags.extend([f"#{tag.title()}" for tag in potential_tags[:5]])
    
    return hashtags[:10]  # Limit to 10 hashtags

async def _calculate_optimization_score(content: str, platform: str) -> float:
    """Calculate content optimization score"""
    
    # Simple scoring algorithm
    score = 0.7  # Base score
    
    # Length scoring
    if 50 <= len(content) <= 500:
        score += 0.1
    elif 500 < len(content) <= 2000:
        score += 0.05
    
    # Platform-specific scoring
    platform_scores = {
        "threads": 0.1,
        "instagram": 0.08,
        "facebook": 0.09,
        "linkedin": 0.07,
        "twitter": 0.06,
        "general": 0.05
    }
    
    score += platform_scores.get(platform, 0.05)
    
    # Engagement indicators
    if any(word in content.lower() for word in ["you", "your", "we", "us"]):
        score += 0.05  # Personal pronouns
    
    if "?" in content:
        score += 0.03  # Questions
    
    if any(word in content.lower() for word in ["how", "what", "why", "when", "where"]):
        score += 0.02  # Question words
    
    return min(score, 1.0)  # Cap at 1.0

async def _generate_alternatives(request: AIGenerationRequest) -> List[str]:
    """Generate alternative versions of content"""
    
    alternatives = []
    
    # Alternative tones
    alternative_tones = ["casual", "professional", "friendly"]
    for tone in alternative_tones:
        if tone != request.tone:
            alt_request = AIGenerationRequest(
                prompt=request.prompt,
                tone=tone,
                length=request.length,
                platform=request.platform
            )
            alternatives.append(await _generate_ai_content(alt_request))
    
    return alternatives[:2]  # Return 2 alternatives

async def _generate_optimization_tips(request: AIOptimizationRequest) -> List[str]:
    """Generate optimization tips for content"""
    
    tips = []
    
    # Platform-specific tips
    platform_tips = {
        "threads": [
            "Use conversational language",
            "Include questions to encourage replies",
            "Keep it under 500 characters for better engagement"
        ],
        "instagram": [
            "Use relevant hashtags (5-10 recommended)",
            "Include a call-to-action",
            "Optimize for visual storytelling"
        ],
        "facebook": [
            "Encourage community engagement",
            "Use Facebook-specific features",
            "Include links when relevant"
        ],
        "linkedin": [
            "Maintain professional tone",
            "Include industry-specific keywords",
            "Focus on thought leadership"
        ],
        "twitter": [
            "Stay within character limits",
            "Use trending hashtags strategically",
            "Engage with your audience"
        ]
    }
    
    tips.extend(platform_tips.get(request.platform, [
        "Use engaging headlines",
        "Include relevant hashtags",
        "Add a clear call-to-action"
    ]))
    
    # Goal-specific tips
    goal_tips = {
        "engagement": [
            "Ask questions to encourage responses",
            "Use interactive elements",
            "Respond to comments quickly"
        ],
        "reach": [
            "Use trending hashtags",
            "Post at optimal times",
            "Encourage sharing"
        ],
        "conversions": [
            "Include clear call-to-action",
            "Use compelling headlines",
            "Provide value first"
        ],
        "brand_awareness": [
            "Maintain consistent brand voice",
            "Share valuable content",
            "Engage with industry conversations"
        ]
    }
    
    tips.extend(goal_tips.get(request.goal, []))
    
    return tips[:5]  # Return top 5 tips

async def _optimize_content_text(content: str, platform: str, goal: str) -> str:
    """Optimize content text for better performance"""
    
    # Simple optimization rules
    optimized = content
    
    # Add platform-specific optimizations
    if platform == "threads" and len(content) > 500:
        optimized = content[:497] + "..."
    
    elif platform == "instagram" and "#" not in content:
        optimized += "\n\n#ContentCreation #SocialMedia"
    
    elif platform == "linkedin" and "professional" not in content.lower():
        optimized = "Professional insight: " + optimized
    
    # Add goal-specific optimizations
    if goal == "engagement" and "?" not in content:
        optimized += "\n\nWhat do you think?"
    
    elif goal == "conversions" and "click" not in content.lower():
        optimized += "\n\nLearn more in the link below!"
    
    return optimized

async def _generate_content_suggestions(request: AISuggestionRequest) -> List[str]:
    """Generate content suggestions based on parameters"""
    
    suggestions = []
    
    # Content type suggestions
    type_suggestions = {
        "thread": [
            "Share a personal story with a lesson learned",
            "Break down a complex topic into digestible parts",
            "Create a how-to guide for your expertise",
            "Share behind-the-scenes of your work process",
            "Discuss a trending topic in your industry"
        ],
        "post": [
            "Share a valuable insight or tip",
            "Celebrate a milestone or achievement",
            "Ask your audience a thought-provoking question",
            "Share a quote that resonates with you",
            "Provide a quick tutorial or explanation"
        ],
        "caption": [
            "Tell the story behind the image",
            "Share what inspired this moment",
            "Ask followers to share their thoughts",
            "Include a relevant quote or saying",
            "Add context to make it more personal"
        ],
        "story": [
            "Share a daily routine or habit",
            "Document a process or journey",
            "Show before and after results",
            "Share a moment of inspiration",
            "Create a mini-tutorial or tip"
        ]
    }
    
    suggestions.extend(type_suggestions.get(request.content_type, [
        "Share your expertise on a relevant topic",
        "Engage with your audience through questions",
        "Provide value through tips or insights",
        "Share personal experiences and lessons",
        "Discuss industry trends and developments"
    ]))
    
    return suggestions[:5]  # Return top 5 suggestions

async def _refine_content_text(content: str, tone: str, platform: str) -> str:
    """Refine and improve existing content"""
    
    refined = content
    
    # Tone refinements
    if tone == "professional" and "I think" in content:
        refined = refined.replace("I think", "Based on my experience")
    
    elif tone == "casual" and "Furthermore" in content:
        refined = refined.replace("Furthermore", "Also")
    
    elif tone == "friendly" and "Dear" in content:
        refined = refined.replace("Dear", "Hi")
    
    # Platform refinements
    if platform == "threads" and len(refined) > 500:
        refined = refined[:497] + "..."
    
    elif platform == "instagram" and "#" not in refined:
        refined += "\n\n#ContentCreation #SocialMedia"
    
    return refined
