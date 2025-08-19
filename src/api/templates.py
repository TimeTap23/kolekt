"""
Template management API routes for ThreadStorm
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from src.services.supabase import supabase_service

templates_router = APIRouter()


class TemplateCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    content: str
    tone: str = "professional"
    tags: List[str] = []
    is_public: bool = False


class TemplateUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    content: Optional[str] = None
    tone: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None


class TemplateResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    category: str
    content: str
    tone: str
    tags: List[str]
    usage_count: int
    is_featured: bool
    is_public: bool
    created_at: str
    updated_at: str


@templates_router.get("/", response_model=List[TemplateResponse])
async def get_templates(
    category: Optional[str] = None,
    user_id: Optional[str] = None,
    public_only: bool = False
):
    """Get templates, optionally filtered by category and user"""
    templates = await supabase_service.get_templates(
        user_id=user_id,
        category=category
    )
    
    # Filter public templates if requested
    if public_only:
        templates = [t for t in templates if t.get("is_public", False)]
    
    return [
        TemplateResponse(
            id=template["id"],
            user_id=template.get("user_id"),
            name=template["name"],
            description=template.get("description"),
            category=template["category"],
            content=template["content"],
            tone=template.get("tone", "professional"),
            tags=template.get("tags", []),
            usage_count=template.get("usage_count", 0),
            is_featured=template.get("is_featured", False),
            is_public=template.get("is_public", False),
            created_at=template["created_at"],
            updated_at=template["updated_at"]
        )
        for template in templates
    ]


@templates_router.get("/featured", response_model=List[TemplateResponse])
async def get_featured_templates():
    """Get featured templates"""
    templates = await supabase_service.get_templates()
    featured_templates = [t for t in templates if t.get("is_featured", False)]
    
    return [
        TemplateResponse(
            id=template["id"],
            user_id=template.get("user_id"),
            name=template["name"],
            description=template.get("description"),
            category=template["category"],
            content=template["content"],
            tone=template.get("tone", "professional"),
            tags=template.get("tags", []),
            usage_count=template.get("usage_count", 0),
            is_featured=template.get("is_featured", False),
            is_public=template.get("is_public", False),
            created_at=template["created_at"],
            updated_at=template["updated_at"]
        )
        for template in featured_templates
    ]


@templates_router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str):
    """Get a specific template by ID"""
    template = await supabase_service.get_template(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return TemplateResponse(
        id=template["id"],
        user_id=template.get("user_id"),
        name=template["name"],
        description=template.get("description"),
        category=template["category"],
        content=template["content"],
        tone=template.get("tone", "professional"),
        tags=template.get("tags", []),
        usage_count=template.get("usage_count", 0),
        is_featured=template.get("is_featured", False),
        is_public=template.get("is_public", False),
        created_at=template["created_at"],
        updated_at=template["updated_at"]
    )


@templates_router.post("/", response_model=TemplateResponse)
async def create_template(request: TemplateCreateRequest):
    """Create a new template"""
    # Get current user
    user = await supabase_service.get_current_user()
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    template_data = {
        "name": request.name,
        "description": request.description,
        "category": request.category,
        "content": request.content,
        "tone": request.tone,
        "tags": request.tags,
        "is_public": request.is_public
    }
    
    result = await supabase_service.create_template(template_data, user.id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    template = result["template"]
    return TemplateResponse(
        id=template["id"],
        user_id=template.get("user_id"),
        name=template["name"],
        description=template.get("description"),
        category=template["category"],
        content=template["content"],
        tone=template.get("tone", "professional"),
        tags=template.get("tags", []),
        usage_count=template.get("usage_count", 0),
        is_featured=template.get("is_featured", False),
        is_public=template.get("is_public", False),
        created_at=template["created_at"],
        updated_at=template["updated_at"]
    )


@templates_router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(template_id: str, request: TemplateUpdateRequest):
    """Update a template"""
    # Get current user
    user = await supabase_service.get_current_user()
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get the template to check ownership
    template = await supabase_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if template.get("user_id") != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this template")
    
    template_data = {}
    if request.name is not None:
        template_data["name"] = request.name
    if request.description is not None:
        template_data["description"] = request.description
    if request.category is not None:
        template_data["category"] = request.category
    if request.content is not None:
        template_data["content"] = request.content
    if request.tone is not None:
        template_data["tone"] = request.tone
    if request.tags is not None:
        template_data["tags"] = request.tags
    if request.is_public is not None:
        template_data["is_public"] = request.is_public
    
    result = await supabase_service.update_template(template_id, template_data)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    updated_template = result["template"]
    return TemplateResponse(
        id=updated_template["id"],
        user_id=updated_template.get("user_id"),
        name=updated_template["name"],
        description=updated_template.get("description"),
        category=updated_template["category"],
        content=updated_template["content"],
        tone=updated_template.get("tone", "professional"),
        tags=updated_template.get("tags", []),
        usage_count=updated_template.get("usage_count", 0),
        is_featured=updated_template.get("is_featured", False),
        is_public=updated_template.get("is_public", False),
        created_at=updated_template["created_at"],
        updated_at=updated_template["updated_at"]
    )


@templates_router.delete("/{template_id}")
async def delete_template(template_id: str):
    """Delete a template"""
    # Get current user
    user = await supabase_service.get_current_user()
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get the template to check ownership
    template = await supabase_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if template.get("user_id") != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this template")
    
    result = await supabase_service.delete_template(template_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Template deleted successfully"}
