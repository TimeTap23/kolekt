"""
Authentication API routes for ThreadStorm
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from src.services.supabase import supabase_service

auth_router = APIRouter()


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None
    full_name: Optional[str] = None


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class AuthResponse(BaseModel):
    user: UserResponse
    session: Dict[str, Any]


@auth_router.post("/signup", response_model=AuthResponse)
async def sign_up(request: SignUpRequest):
    """Sign up a new user"""
    user_data = {}
    if request.username:
        user_data["username"] = request.username
    if request.full_name:
        user_data["full_name"] = request.full_name
    
    result = await supabase_service.sign_up(
        email=request.email,
        password=request.password,
        user_data=user_data
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    user = result["user"]
    return AuthResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            username=user.user_metadata.get("username"),
            full_name=user.user_metadata.get("full_name"),
            avatar_url=user.user_metadata.get("avatar_url")
        ),
        session=result["session"].dict() if result["session"] else {}
    )


@auth_router.post("/signin", response_model=AuthResponse)
async def sign_in(request: SignInRequest):
    """Sign in a user"""
    result = await supabase_service.sign_in(
        email=request.email,
        password=request.password
    )
    
    if not result["success"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = result["user"]
    return AuthResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            username=user.user_metadata.get("username"),
            full_name=user.user_metadata.get("full_name"),
            avatar_url=user.user_metadata.get("avatar_url")
        ),
        session=result["session"].dict() if result["session"] else {}
    )


@auth_router.post("/signout")
async def sign_out():
    """Sign out the current user"""
    result = await supabase_service.sign_out()
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"message": "Successfully signed out"}


@auth_router.get("/me", response_model=UserResponse)
async def get_current_user():
    """Get the current authenticated user"""
    user = await supabase_service.get_current_user()
    
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.user_metadata.get("username"),
        full_name=user.user_metadata.get("full_name"),
        avatar_url=user.user_metadata.get("avatar_url")
    )
