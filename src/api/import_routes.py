#!/usr/bin/env python3
"""
Content Import API Routes
Handles importing content from URLs, files, and existing social media posts
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import asyncio
import json
import re
from urllib.parse import urlparse

# Setup logging
logger = logging.getLogger(__name__)

# Create router
import_router = APIRouter()

# Pydantic models
from pydantic import BaseModel

class URLImportRequest(BaseModel):
    url: str
    platform: Optional[str] = None  # auto-detect if not provided
    extract_images: bool = True
    extract_links: bool = True

class FileImportRequest(BaseModel):
    file_type: str  # txt, csv, docx, pdf
    extract_metadata: bool = True
    parse_structure: bool = True

class ImportResponse(BaseModel):
    success: bool
    imported_content: Optional[str] = None
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    images: Optional[List[str]] = None
    links: Optional[List[str]] = None
    error_message: Optional[str] = None
    source_info: Optional[Dict[str, Any]] = None

class ImportStatusResponse(BaseModel):
    success: bool
    status: str  # processing, completed, failed
    progress: Optional[float] = None
    message: Optional[str] = None
    result: Optional[ImportResponse] = None

from src.services.authentication import get_current_user

# Dependency to get current user (via JWT)
async def get_current_user_id(current_user: Dict = Depends(get_current_user)) -> str:
    """Get current user ID from JWT-authenticated request"""
    return current_user["user_id"]

@import_router.post("/url", response_model=ImportResponse)
async def import_from_url(
    request: URLImportRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Import content from a URL"""
    try:
        logger.info(f"Importing content from URL for user {user_id}: {request.url}")
        
        # Validate URL
        if not _is_valid_url(request.url):
            raise HTTPException(status_code=400, detail="Invalid URL provided")
        
        # Detect platform if not provided
        platform = request.platform or _detect_platform(request.url)
        
        # Simulate import processing
        await asyncio.sleep(2)
        
        # Extract content based on platform
        imported_content = await _extract_url_content(request.url, platform)
        
        # Extract metadata
        metadata = await _extract_url_metadata(request.url, platform)
        
        # Extract images if requested
        images = []
        if request.extract_images:
            images = await _extract_images_from_url(request.url, platform)
        
        # Extract links if requested
        links = []
        if request.extract_links:
            links = await _extract_links_from_url(request.url, platform)
        
        return ImportResponse(
            success=True,
            imported_content=imported_content,
            title=metadata.get("title", "Imported Content"),
            metadata=metadata,
            images=images,
            links=links,
            source_info={
                "url": request.url,
                "platform": platform,
                "imported_at": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error importing from URL: {e}")
        return ImportResponse(
            success=False,
            error_message=str(e)
        )

@import_router.post("/file", response_model=ImportResponse)
async def import_from_file(
    file: UploadFile = File(...),
    extract_metadata: bool = Form(True),
    parse_structure: bool = Form(True),
    user_id: str = Depends(get_current_user_id)
):
    """Import content from uploaded file"""
    try:
        logger.info(f"Importing content from file for user {user_id}: {file.filename}")
        
        # Validate file type
        if not _is_valid_file_type(file.filename):
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Read file content
        content = await file.read()
        
        # Process based on file type
        file_type = _get_file_type(file.filename)
        processed_content = await _process_file_content(content, file_type, extract_metadata, parse_structure)
        
        return ImportResponse(
            success=True,
            imported_content=processed_content["content"],
            title=processed_content.get("title", file.filename),
            metadata=processed_content.get("metadata", {}),
            source_info={
                "filename": file.filename,
                "file_type": file_type,
                "file_size": len(content),
                "imported_at": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error importing from file: {e}")
        return ImportResponse(
            success=False,
            error_message=str(e)
        )

@import_router.post("/social-posts", response_model=ImportResponse)
async def import_social_posts(
    platform: str = Form(...),  # threads, instagram, facebook
    post_ids: List[str] = Form(...),
    user_id: str = Depends(get_current_user_id)
):
    """Import existing social media posts"""
    try:
        logger.info(f"Importing social posts for user {user_id} from {platform}")
        
        # Simulate social media API calls
        await asyncio.sleep(1.5)
        
        # Import posts from specified platform
        imported_posts = await _import_social_posts(platform, post_ids, user_id)
        
        # Combine posts into content
        combined_content = _combine_social_posts(imported_posts)
        
        return ImportResponse(
            success=True,
            imported_content=combined_content,
            title=f"Imported {len(imported_posts)} posts from {platform.title()}",
            metadata={
                "platform": platform,
                "post_count": len(imported_posts),
                "posts": imported_posts
            },
            source_info={
                "platform": platform,
                "post_ids": post_ids,
                "imported_at": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error importing social posts: {e}")
        return ImportResponse(
            success=False,
            error_message=str(e)
        )

@import_router.get("/supported-platforms")
async def get_supported_platforms():
    """Get list of supported import platforms"""
    return {
        "url_platforms": [
            {
                "name": "Twitter/X",
                "pattern": "twitter.com|x.com",
                "features": ["text", "images", "links", "hashtags"]
            },
            {
                "name": "LinkedIn",
                "pattern": "linkedin.com",
                "features": ["text", "images", "links", "professional_content"]
            },
            {
                "name": "Medium",
                "pattern": "medium.com",
                "features": ["articles", "text", "images", "links"]
            },
            {
                "name": "Blogs",
                "pattern": "wordpress.com|blogspot.com|substack.com",
                "features": ["articles", "text", "images", "links"]
            }
        ],
        "file_types": [
            {
                "extension": ".txt",
                "features": ["text_extraction", "basic_parsing"]
            },
            {
                "extension": ".csv",
                "features": ["structured_data", "table_parsing"]
            },
            {
                "extension": ".docx",
                "features": ["rich_text", "formatting", "images"]
            },
            {
                "extension": ".pdf",
                "features": ["text_extraction", "images", "layout_preservation"]
            }
        ],
        "social_platforms": [
            {
                "name": "Threads",
                "features": ["posts", "threads", "images", "links"]
            },
            {
                "name": "Instagram",
                "features": ["posts", "captions", "images", "stories"]
            },
            {
                "name": "Facebook",
                "features": ["posts", "pages", "groups", "images"]
            }
        ]
    }

# Helper functions
def _is_valid_url(url: str) -> bool:
    """Validate if URL is properly formatted"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def _detect_platform(url: str) -> str:
    """Detect platform from URL"""
    domain = urlparse(url).netloc.lower()
    
    if "twitter.com" in domain or "x.com" in domain:
        return "twitter"
    elif "linkedin.com" in domain:
        return "linkedin"
    elif "medium.com" in domain:
        return "medium"
    elif "instagram.com" in domain:
        return "instagram"
    elif "facebook.com" in domain:
        return "facebook"
    elif "threads.net" in domain:
        return "threads"
    elif "wordpress.com" in domain or "blogspot.com" in domain or "substack.com" in domain:
        return "blog"
    else:
        return "general"

async def _extract_url_content(url: str, platform: str) -> str:
    """Extract content from URL based on platform"""
    
    # Platform-specific content extraction
    platform_extractors = {
        "twitter": _extract_twitter_content,
        "linkedin": _extract_linkedin_content,
        "medium": _extract_medium_content,
        "instagram": _extract_instagram_content,
        "facebook": _extract_facebook_content,
        "threads": _extract_threads_content,
        "blog": _extract_blog_content,
        "general": _extract_general_content
    }
    
    extractor = platform_extractors.get(platform, _extract_general_content)
    return await extractor(url)

async def _extract_twitter_content(url: str) -> str:
    """Extract content from Twitter/X post"""
    # Simulate Twitter API extraction
    return f"Imported Twitter post from: {url}\n\nThis is simulated content from a Twitter/X post. In a real implementation, this would extract the actual tweet content, including text, hashtags, and mentions.\n\n#Twitter #SocialMedia #ContentImport"

async def _extract_linkedin_content(url: str) -> str:
    """Extract content from LinkedIn post"""
    # Simulate LinkedIn API extraction
    return f"Imported LinkedIn post from: {url}\n\nThis is simulated content from a LinkedIn post. In a real implementation, this would extract the actual post content, including professional insights, company updates, and industry commentary.\n\n#LinkedIn #Professional #Networking"

async def _extract_medium_content(url: str) -> str:
    """Extract content from Medium article"""
    # Simulate Medium API extraction
    return f"Imported Medium article from: {url}\n\nThis is simulated content from a Medium article. In a real implementation, this would extract the full article content, including title, body text, and author information.\n\n#Medium #Article #Content"

async def _extract_instagram_content(url: str) -> str:
    """Extract content from Instagram post"""
    # Simulate Instagram API extraction
    return f"Imported Instagram post from: {url}\n\nThis is simulated content from an Instagram post. In a real implementation, this would extract the caption, hashtags, and image descriptions.\n\n#Instagram #SocialMedia #VisualContent"

async def _extract_facebook_content(url: str) -> str:
    """Extract content from Facebook post"""
    # Simulate Facebook API extraction
    return f"Imported Facebook post from: {url}\n\nThis is simulated content from a Facebook post. In a real implementation, this would extract the post text, engagement metrics, and community interactions.\n\n#Facebook #SocialMedia #Community"

async def _extract_threads_content(url: str) -> str:
    """Extract content from Threads post"""
    # Simulate Threads API extraction
    return f"Imported Threads post from: {url}\n\nThis is simulated content from a Threads post. In a real implementation, this would extract the thread content, including text and conversation flow.\n\n#Threads #SocialMedia #Conversation"

async def _extract_blog_content(url: str) -> str:
    """Extract content from blog post"""
    # Simulate blog content extraction
    return f"Imported blog post from: {url}\n\nThis is simulated content from a blog post. In a real implementation, this would extract the full article content, including title, body, and author information.\n\n#Blog #Article #Content"

async def _extract_general_content(url: str) -> str:
    """Extract content from general URL"""
    # Simulate general web scraping
    return f"Imported content from: {url}\n\nThis is simulated content from a general webpage. In a real implementation, this would scrape and extract the main content from the webpage.\n\n#WebContent #Import #Content"

async def _extract_url_metadata(url: str, platform: str) -> Dict[str, Any]:
    """Extract metadata from URL"""
    return {
        "title": f"Imported from {platform.title()}",
        "author": "Unknown Author",
        "published_date": datetime.utcnow().isoformat(),
        "platform": platform,
        "url": url,
        "word_count": 150,
        "reading_time": "1 min"
    }

async def _extract_images_from_url(url: str, platform: str) -> List[str]:
    """Extract images from URL"""
    # Simulate image extraction
    return [
        "https://via.placeholder.com/300x200?text=Imported+Image+1",
        "https://via.placeholder.com/300x200?text=Imported+Image+2"
    ]

async def _extract_links_from_url(url: str, platform: str) -> List[str]:
    """Extract links from URL"""
    # Simulate link extraction
    return [
        "https://example.com/related-article-1",
        "https://example.com/related-article-2"
    ]

def _is_valid_file_type(filename: str) -> bool:
    """Check if file type is supported"""
    supported_extensions = ['.txt', '.csv', '.docx', '.pdf']
    return any(filename.lower().endswith(ext) for ext in supported_extensions)

def _get_file_type(filename: str) -> str:
    """Get file type from filename"""
    for ext in ['.txt', '.csv', '.docx', '.pdf']:
        if filename.lower().endswith(ext):
            return ext[1:]  # Remove the dot
    return 'unknown'

async def _process_file_content(content: bytes, file_type: str, extract_metadata: bool, parse_structure: bool) -> Dict[str, Any]:
    """Process file content based on type"""
    
    # Convert bytes to string
    text_content = content.decode('utf-8', errors='ignore')
    
    # Process based on file type
    if file_type == 'txt':
        return await _process_txt_content(text_content, extract_metadata, parse_structure)
    elif file_type == 'csv':
        return await _process_csv_content(text_content, extract_metadata, parse_structure)
    elif file_type == 'docx':
        return await _process_docx_content(content, extract_metadata, parse_structure)
    elif file_type == 'pdf':
        return await _process_pdf_content(content, extract_metadata, parse_structure)
    else:
        return {
            "content": text_content,
            "title": "Imported File",
            "metadata": {"file_type": file_type}
        }

async def _process_txt_content(content: str, extract_metadata: bool, parse_structure: bool) -> Dict[str, Any]:
    """Process text file content"""
    lines = content.split('\n')
    
    # Extract title from first line if it looks like a title
    title = "Imported Text File"
    if lines and len(lines[0].strip()) > 0 and len(lines[0].strip()) < 100:
        title = lines[0].strip()
        content = '\n'.join(lines[1:])  # Remove title from content
    
    metadata = {}
    if extract_metadata:
        metadata = {
            "line_count": len(lines),
            "word_count": len(content.split()),
            "character_count": len(content)
        }
    
    return {
        "content": content,
        "title": title,
        "metadata": metadata
    }

async def _process_csv_content(content: str, extract_metadata: bool, parse_structure: bool) -> Dict[str, Any]:
    """Process CSV file content"""
    lines = content.split('\n')
    
    # Parse CSV structure
    if parse_structure and lines:
        headers = lines[0].split(',')
        data_rows = lines[1:] if len(lines) > 1 else []
        
        # Convert to readable format
        formatted_content = f"CSV Data with {len(headers)} columns:\n\n"
        formatted_content += f"Headers: {', '.join(headers)}\n\n"
        
        for i, row in enumerate(data_rows[:5]):  # Show first 5 rows
            formatted_content += f"Row {i+1}: {row}\n"
        
        if len(data_rows) > 5:
            formatted_content += f"\n... and {len(data_rows) - 5} more rows"
    else:
        formatted_content = content
    
    metadata = {}
    if extract_metadata:
        metadata = {
            "row_count": len(lines),
            "column_count": len(lines[0].split(',')) if lines else 0,
            "file_type": "csv"
        }
    
    return {
        "content": formatted_content,
        "title": "Imported CSV Data",
        "metadata": metadata
    }

async def _process_docx_content(content: bytes, extract_metadata: bool, parse_structure: bool) -> Dict[str, Any]:
    """Process DOCX file content"""
    # Simulate DOCX processing
    text_content = "This is simulated content from a DOCX file. In a real implementation, this would extract the actual text content, formatting, and structure from the Word document."
    
    metadata = {}
    if extract_metadata:
        metadata = {
            "file_type": "docx",
            "word_count": 25,
            "page_count": 1,
            "has_images": False
        }
    
    return {
        "content": text_content,
        "title": "Imported Word Document",
        "metadata": metadata
    }

async def _process_pdf_content(content: bytes, extract_metadata: bool, parse_structure: bool) -> Dict[str, Any]:
    """Process PDF file content"""
    # Simulate PDF processing
    text_content = "This is simulated content from a PDF file. In a real implementation, this would extract the actual text content, images, and layout information from the PDF document."
    
    metadata = {}
    if extract_metadata:
        metadata = {
            "file_type": "pdf",
            "page_count": 1,
            "has_images": False,
            "text_extractable": True
        }
    
    return {
        "content": text_content,
        "title": "Imported PDF Document",
        "metadata": metadata
    }

async def _import_social_posts(platform: str, post_ids: List[str], user_id: str) -> List[Dict[str, Any]]:
    """Import posts from social media platform"""
    imported_posts = []
    
    for post_id in post_ids:
        # Simulate social media API call
        post_data = {
            "id": post_id,
            "platform": platform,
            "content": f"Imported {platform} post {post_id}",
            "author": f"@{platform}_user",
            "posted_at": datetime.utcnow().isoformat(),
            "engagement": {
                "likes": 42,
                "comments": 7,
                "shares": 3
            }
        }
        imported_posts.append(post_data)
    
    return imported_posts

def _combine_social_posts(posts: List[Dict[str, Any]]) -> str:
    """Combine multiple social posts into content"""
    combined = f"Imported {len(posts)} social media posts:\n\n"
    
    for i, post in enumerate(posts, 1):
        combined += f"Post {i} ({post['platform'].title()}):\n"
        combined += f"{post['content']}\n"
        combined += f"By: {post['author']}\n"
        combined += f"Engagement: {post['engagement']['likes']} likes, {post['engagement']['comments']} comments\n\n"
    
    return combined
