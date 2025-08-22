#!/usr/bin/env python3
"""
Simple Configuration for ThreadStorm
Minimal configuration that works for development
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Simple settings for ThreadStorm"""
    
    # Basic App Configuration
    DEBUG: bool = Field(default=True, env="DEBUG")
    SECRET_KEY: str = Field(default="threadstorm-dev-secret-key", env="SECRET_KEY")
    JWT_SECRET: str = Field(env="JWT_SECRET")  # New JWT signing key from Supabase
    HOST: str = Field(default="127.0.0.1", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Supabase Configuration
    SUPABASE_URL: str = Field(env="SUPABASE_URL")
    SUPABASE_ANON_KEY: str = Field(env="SUPABASE_ANON_KEY")
    SUPABASE_KEY: str = Field(env="SUPABASE_KEY")
    DATABASE_URL: str = Field(env="DATABASE_URL")
    
    # Meta Platform Configuration
    META_APP_ID: str = Field(env="META_APP_ID")
    META_APP_SECRET: str = Field(env="META_APP_SECRET")
    META_REDIRECT_URI: str = Field(default="http://localhost:8000/api/v1/auth/meta/callback", env="META_REDIRECT_URI")
    META_WEBHOOK_VERIFY_TOKEN: str = Field(default="your-webhook-verify-token", env="META_WEBHOOK_VERIFY_TOKEN")
    
    # Threads API Configuration (separate from Meta)
    THREADS_APP_ID: str = Field(env="THREADS_APP_ID")
    THREADS_APP_SECRET: str = Field(env="THREADS_APP_SECRET")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "http://127.0.0.1:8000"], env="CORS_ORIGINS")
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=False, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_FREE: int = Field(default=100, env="RATE_LIMIT_FREE")
    RATE_LIMIT_PRO: int = Field(default=500, env="RATE_LIMIT_PRO")
    RATE_LIMIT_BUSINESS: int = Field(default=2000, env="RATE_LIMIT_BUSINESS")
    
    # Usage Limits
    USAGE_LIMIT_FREE: int = Field(default=10, env="USAGE_LIMIT_FREE")
    USAGE_LIMIT_PRO: int = Field(default=100, env="USAGE_LIMIT_PRO")
    USAGE_LIMIT_BUSINESS: int = Field(default=1000, env="USAGE_LIMIT_BUSINESS")
    
    # API Quotas
    API_QUOTA_FREE: int = Field(default=50, env="API_QUOTA_FREE")
    API_QUOTA_PRO: int = Field(default=500, env="API_QUOTA_PRO")
    API_QUOTA_BUSINESS: int = Field(default=5000, env="API_QUOTA_BUSINESS")
    
    # Security (simplified)
    ENABLE_TOKEN_ENCRYPTION: bool = Field(default=False, env="ENABLE_TOKEN_ENCRYPTION")
    ENABLE_RBAC: bool = Field(default=True, env="ENABLE_RBAC")
    TOKEN_ENCRYPTION_KEY: str = Field(default="dev-encryption-key-change-in-production", env="TOKEN_ENCRYPTION_KEY")
    
    # AWS KMS Configuration (simplified)
    AWS_KMS_KEY_ID: Optional[str] = Field(default=None, env="AWS_KMS_KEY_ID")
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    ENABLE_KMS_ENCRYPTION: bool = Field(default=False, env="ENABLE_KMS_ENCRYPTION")
    
    # Observability (simplified)
    OBSERVABILITY_ENABLED: bool = Field(default=False, env="OBSERVABILITY_ENABLED")
    ENABLE_AUDIT_LOGS: bool = Field(default=False, env="ENABLE_AUDIT_LOGS")
    ENABLE_RATE_LIMIT_LOGS: bool = Field(default=False, env="ENABLE_RATE_LIMIT_LOGS")
    ENABLE_ACCESS_LOGS: bool = Field(default=False, env="ENABLE_ACCESS_LOGS")
    ENABLE_DELETION_LOGS: bool = Field(default=False, env="ENABLE_DELETION_LOGS")
    
    # Anti-spam and content moderation
    ANTI_SPAM_ENABLED: bool = Field(default=False, env="ANTI_SPAM_ENABLED")
    CONTENT_MODERATION_ENABLED: bool = Field(default=False, env="CONTENT_MODERATION_ENABLED")
    
    # App Version
    APP_VERSION: str = Field(default="2.0.0", env="APP_VERSION")
    
    # AI Configuration
    HUGGINGFACE_TOKEN: Optional[str] = Field(default=None, env="HUGGINGFACE_TOKEN")

    # Stripe Configuration
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None, env="STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(default=None, env="STRIPE_WEBHOOK_SECRET")
    STRIPE_PRICE_STARTER_MONTHLY: Optional[str] = Field(default=None, env="STRIPE_PRICE_STARTER_MONTHLY")
    STRIPE_PRICE_PRO_MONTHLY: Optional[str] = Field(default=None, env="STRIPE_PRICE_PRO_MONTHLY")
    STRIPE_PRICE_BUSINESS_MONTHLY: Optional[str] = Field(default=None, env="STRIPE_PRICE_BUSINESS_MONTHLY")
    STRIPE_PRICE_CREDITS_100: Optional[str] = Field(default=None, env="STRIPE_PRICE_CREDITS_100")
    STRIPE_PRICE_CREDITS_300: Optional[str] = Field(default=None, env="STRIPE_PRICE_CREDITS_300")
    STRIPE_PRICE_CREDITS_750: Optional[str] = Field(default=None, env="STRIPE_PRICE_CREDITS_750")
    STRIPE_BILLING_PORTAL_RETURN_URL: Optional[str] = Field(default=None, env="STRIPE_BILLING_PORTAL_RETURN_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env

# Create settings instance
settings = Settings()

# Plan configuration for easy access
PLAN_LIMITS = {
    'free': {
        'rate_limit': settings.RATE_LIMIT_FREE,
        'usage_limit': settings.USAGE_LIMIT_FREE,
        'api_quota': settings.API_QUOTA_FREE,
        'features': ['basic_formatting', 'public_templates', 'basic_analytics']
    },
    'pro': {
        'rate_limit': settings.RATE_LIMIT_PRO,
        'usage_limit': settings.USAGE_LIMIT_PRO,
        'api_quota': settings.API_QUOTA_PRO,
        'features': ['basic_formatting', 'all_templates', 'advanced_analytics', 'priority_support', 'api_access']
    },
    'business': {
        'rate_limit': settings.RATE_LIMIT_BUSINESS,
        'usage_limit': settings.USAGE_LIMIT_BUSINESS,
        'api_quota': settings.API_QUOTA_BUSINESS,
        'features': ['basic_formatting', 'all_templates', 'advanced_analytics', 'priority_support', 'api_access', 'team_collaboration', 'white_label']
    }
}

# Pricing configuration
PRICING = {
    'starter': {
        'monthly': 1200,  # $12.00 in cents
        'stripe_price_id': settings.STRIPE_PRICE_STARTER_MONTHLY
    },
    'pro': {
        'monthly': 2900,  # $29.00 in cents
        'stripe_price_id': settings.STRIPE_PRICE_PRO_MONTHLY
    },
    'business': {
        'monthly': 7900,  # $79.00 in cents
        'stripe_price_id': settings.STRIPE_PRICE_BUSINESS_MONTHLY
    }
}

# Credit pack configuration
CREDIT_PACKS = {
    '100': {
        'credits': 100,
        'price': 1000,  # $10.00 in cents
        'stripe_price_id': settings.STRIPE_PRICE_CREDITS_100
    },
    '300': {
        'credits': 300,
        'price': 2500,  # $25.00 in cents
        'stripe_price_id': settings.STRIPE_PRICE_CREDITS_300
    },
    '750': {
        'credits': 750,
        'price': 5000,  # $50.00 in cents
        'stripe_price_id': settings.STRIPE_PRICE_CREDITS_750
    }
}
