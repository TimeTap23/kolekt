"""
AI Service for Kolekt
Handles Hugging Face model integration for content generation
"""

import os
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import requests
from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)

class ContentGenerationRequest(BaseModel):
    """Request model for content generation"""
    topic: str
    platform: str  # "threads", "instagram", "facebook"
    tone: str = "engaging"  # "professional", "casual", "humorous", "engaging"
    length: str = "medium"  # "short", "medium", "long"
    style: str = "conversational"  # "conversational", "informative", "storytelling"
    additional_context: Optional[str] = None

class ContentGenerationResponse(BaseModel):
    """Response model for content generation"""
    content: str
    hashtags: List[str]
    platform_suggestions: Dict[str, str]
    confidence_score: float
    model_used: str

class AIService:
    """AI service for content generation using Hugging Face models"""
    
    def __init__(self):
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")
        self.client = None
        
        if self.hf_token:
            self.client = InferenceClient(token=self.hf_token)
            logger.info("Hugging Face client initialized successfully")
        else:
            logger.warning("Hugging Face token not found. AI features will be limited.")
    
    def generate_content(self, request: ContentGenerationRequest) -> ContentGenerationResponse:
        """Generate content using Llama 3.1 model"""
        try:
            if not self.client:
                return self._generate_mock_content(request)
            
            # Create prompt for Llama 3.1
            prompt = self._create_prompt(request)
            
            # Generate content using Llama 3.1
            response = self.client.text_generation(
                prompt,
                model="meta-llama/Llama-3.1-8B-Instruct",
                max_new_tokens=512,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                return_full_text=False
            )
            
            generated_content = response.strip()
            
            # Extract hashtags and create platform suggestions
            hashtags = self._extract_hashtags(generated_content)
            platform_suggestions = self._create_platform_suggestions(generated_content, request.platform)
            
            return ContentGenerationResponse(
                content=generated_content,
                hashtags=hashtags,
                platform_suggestions=platform_suggestions,
                confidence_score=0.85,
                model_used="Llama-3.1-8B-Instruct"
            )
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return self._generate_mock_content(request)
    
    def _create_prompt(self, request: ContentGenerationRequest) -> str:
        """Create a prompt for the AI model"""
        platform_info = {
            "threads": "Threads (conversational, engaging, can be longer)",
            "instagram": "Instagram (visual-focused, hashtag-friendly, concise)",
            "facebook": "Facebook (community-focused, informative, can be detailed)"
        }
        
        tone_info = {
            "professional": "professional and authoritative",
            "casual": "casual and friendly",
            "humorous": "humorous and entertaining",
            "engaging": "engaging and conversational"
        }
        
        length_info = {
            "short": "brief and concise",
            "medium": "moderate length with good detail",
            "long": "comprehensive and detailed"
        }
        
        prompt = f"""You are a social media content creator. Create a {tone_info.get(request.tone, 'engaging')} post about "{request.topic}" for {platform_info.get(request.platform, 'social media')}.

Style: {request.style}
Length: {length_info.get(request.length, 'medium')}

Additional context: {request.additional_context or 'None'}

Create engaging content that would perform well on {request.platform}. Include relevant hashtags at the end.

Content:"""
        
        return prompt
    
    def _extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from generated content"""
        hashtags = []
        words = content.split()
        
        for word in words:
            if word.startswith('#') and len(word) > 1:
                hashtags.append(word)
        
        # If no hashtags found, generate some based on content
        if not hashtags:
            hashtags = self._generate_hashtags(content)
        
        return hashtags[:10]  # Limit to 10 hashtags
    
    def _generate_hashtags(self, content: str) -> List[str]:
        """Generate relevant hashtags based on content"""
        # Simple keyword-based hashtag generation
        # In the future, this could use a more sophisticated model
        common_hashtags = [
            "#socialmedia", "#content", "#digital", "#marketing",
            "#engagement", "#community", "#growth", "#strategy"
        ]
        
        # Extract potential keywords from content
        words = content.lower().split()
        keywords = [word for word in words if len(word) > 4 and word.isalpha()]
        
        hashtags = []
        for keyword in keywords[:5]:  # Take top 5 keywords
            hashtags.append(f"#{keyword}")
        
        # Add some common hashtags
        hashtags.extend(common_hashtags[:3])
        
        return hashtags
    
    def _create_platform_suggestions(self, content: str, target_platform: str) -> Dict[str, str]:
        """Create platform-specific suggestions"""
        suggestions = {}
        
        if target_platform == "threads":
            suggestions["threads"] = content
            suggestions["instagram"] = self._adapt_for_instagram(content)
            suggestions["facebook"] = self._adapt_for_facebook(content)
        elif target_platform == "instagram":
            suggestions["instagram"] = content
            suggestions["threads"] = self._adapt_for_threads(content)
            suggestions["facebook"] = self._adapt_for_facebook(content)
        elif target_platform == "facebook":
            suggestions["facebook"] = content
            suggestions["threads"] = self._adapt_for_threads(content)
            suggestions["instagram"] = self._adapt_for_instagram(content)
        
        return suggestions
    
    def _adapt_for_threads(self, content: str) -> str:
        """Adapt content for Threads platform"""
        # Threads allows longer content and is more conversational
        return content
    
    def _adapt_for_instagram(self, content: str) -> str:
        """Adapt content for Instagram platform"""
        # Instagram prefers shorter, more visual-focused content
        if len(content) > 2200:  # Instagram character limit
            content = content[:2200] + "..."
        return content
    
    def _adapt_for_facebook(self, content: str) -> str:
        """Adapt content for Facebook platform"""
        # Facebook allows longer content and is more community-focused
        return content
    
    def _generate_mock_content(self, request: ContentGenerationRequest) -> ContentGenerationResponse:
        """Generate mock content when AI service is not available"""
        mock_content = f"🎯 Exciting post about {request.topic}! This is a {request.tone} {request.style} piece perfect for {request.platform}. Stay tuned for more engaging content! #content #socialmedia #engagement"
        
        return ContentGenerationResponse(
            content=mock_content,
            hashtags=["#content", "#socialmedia", "#engagement"],
            platform_suggestions={
                "threads": mock_content,
                "instagram": mock_content,
                "facebook": mock_content
            },
            confidence_score=0.5,
            model_used="mock"
        )

# Global AI service instance
ai_service = AIService()
