#!/usr/bin/env python3
"""
Kolekt Configuration
Production-ready configuration with Railway support
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings with Railway optimization"""
    
    # Basic App Configuration
    DEBUG: bool = Field(default=False, env="DEBUG")
    SECRET_KEY: str = Field(default="kolekt-dev-secret-key", env="SECRET_KEY")
    JWT_SECRET: Optional[str] = Field(default=None, env="JWT_SECRET")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    ENVIRONMENT: str = Field(default="production", env="ENVIRONMENT")
    
    # Supabase Configuration
    SUPABASE_URL: str = Field(env="SUPABASE_URL")
    SUPABASE_ANON_KEY: str = Field(env="SUPABASE_ANON_KEY")
    SUPABASE_KEY: str = Field(env="SUPABASE_KEY")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(env="SUPABASE_SERVICE_ROLE_KEY")
    
    # Meta/Threads Configuration
    META_APP_ID: Optional[str] = Field(default=None, env="META_APP_ID")
    META_APP_SECRET: str = Field(env="META_APP_SECRET")
    META_REDIRECT_URI: str = Field(default="https://kolekt.io/api/v1/auth/meta/callback", env="META_REDIRECT_URI")
    META_WEBHOOK_VERIFY_TOKEN: str = Field(default="your-webhook-verify-token", env="META_WEBHOOK_VERIFY_TOKEN")
    
    # Threads API Configuration
    THREADS_APP_SECRET: Optional[str] = Field(default=None, env="THREADS_APP_SECRET")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=["https://kolekt.io", "https://www.kolekt.io", "https://api.kolekt.io"],
        env="CORS_ORIGINS"
    )
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Admin Configuration
    ADMIN_EMAIL: str = Field(default="info@marteklabs.com", env="ADMIN_EMAIL")
    ADMIN_PASSWORD: Optional[str] = Field(default=None, env="ADMIN_PASSWORD")
    
    # Security Configuration
    TOKEN_ENCRYPTION_KEY: Optional[str] = Field(default=None, env="TOKEN_ENCRYPTION_KEY")
    ENABLE_TOKEN_ENCRYPTION: bool = Field(default=True, env="ENABLE_TOKEN_ENCRYPTION")
    
    # Custom Domain Configuration
    PRIMARY_DOMAIN: str = Field(default="kolekt.io", env="PRIMARY_DOMAIN")
    API_SUBDOMAIN: str = Field(default="api.kolekt.io", env="API_SUBDOMAIN")
    ADMIN_SUBDOMAIN: str = Field(default="admin.kolekt.io", env="ADMIN_SUBDOMAIN")
    
    # Email Configuration
    SMTP_HOST: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    FROM_EMAIL: str = Field(default="noreply@kolekt.io", env="FROM_EMAIL")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
    
    # AI/Hugging Face Configuration
    HUGGINGFACE_TOKEN: Optional[str] = Field(default=None, env="HUGGINGFACE_TOKEN")
    HUGGINGFACE_API_URL: str = Field(default="https://api-inference.huggingface.co", env="HUGGINGFACE_API_URL")
    AI_MODEL_NAME: str = Field(default="meta-llama/Llama-3.1-8B-Instruct", env="AI_MODEL_NAME")
    AI_ENABLED: bool = Field(default=True, env="AI_ENABLED")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields

# Global settings instance
settings = Settings()

# Helper functions for domain management
def get_primary_domain() -> str:
    """Get the primary domain for the application"""
    return settings.PRIMARY_DOMAIN

def get_api_domain() -> str:
    """Get the API subdomain"""
    return settings.API_SUBDOMAIN

def get_admin_domain() -> str:
    """Get the admin subdomain"""
    return settings.ADMIN_SUBDOMAIN

def get_allowed_origins() -> List[str]:
    """Get all allowed CORS origins including custom domains"""
    origins = settings.CORS_ORIGINS.copy()
    
    # Add custom domain variations
    primary = settings.PRIMARY_DOMAIN
    origins.extend([
        f"https://{primary}",
        f"https://www.{primary}",
        f"https://api.{primary}",
        f"https://admin.{primary}"
    ])
    
    # Add development origins if in debug mode
    if settings.DEBUG:
        origins.extend([
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000"
        ])
    
    return list(set(origins))  # Remove duplicates
