#!/usr/bin/env python3
"""
ThreadStorm Configuration Settings
"""

import os
from typing import List, Optional, Dict
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # App Configuration
    APP_NAME: str = "ThreadStorm"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = Field(default="127.0.0.1", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    JWT_SECRET: str = Field(..., env="JWT_SECRET")  # New JWT signing key from Supabase
    
    # Database - Supabase
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_KEY: str = Field(..., env="SUPABASE_KEY")
    SUPABASE_ANON_KEY: str = Field(..., env="SUPABASE_ANON_KEY")
    SUPABASE_STORAGE_BUCKET: str = Field(default="threadstorm", env="SUPABASE_STORAGE_BUCKET")
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    # Threads API Configuration
    THREADS_API_KEY: Optional[str] = Field(default=None, env="THREADS_API_KEY")
    THREADS_API_SECRET: Optional[str] = Field(default=None, env="THREADS_API_SECRET")
    THREADS_ACCESS_TOKEN: Optional[str] = Field(default=None, env="THREADS_ACCESS_TOKEN")
    THREADS_ACCESS_TOKEN_SECRET: Optional[str] = Field(default=None, env="THREADS_ACCESS_TOKEN_SECRET")
    
    # Commercial Features
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None, env="STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY: Optional[str] = Field(default=None, env="STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(default=None, env="STRIPE_WEBHOOK_SECRET")
    
    # Email Configuration
    SMTP_SERVER: Optional[str] = Field(default=None, env="SMTP_SERVER")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    FROM_EMAIL: str = Field(default="noreply@threadstorm.com", env="FROM_EMAIL")
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_FREE: int = Field(default=10, env="RATE_LIMIT_FREE")  # requests per minute
    RATE_LIMIT_PRO: int = Field(default=100, env="RATE_LIMIT_PRO")
    RATE_LIMIT_BUSINESS: int = Field(default=500, env="RATE_LIMIT_BUSINESS")
    RATE_LIMIT_ENTERPRISE: int = Field(default=2000, env="RATE_LIMIT_ENTERPRISE")
    
    # Usage Limits
    USAGE_LIMIT_FREE: int = Field(default=10, env="USAGE_LIMIT_FREE")  # threadstorms per month
    USAGE_LIMIT_PRO: int = Field(default=100, env="USAGE_LIMIT_PRO")
    USAGE_LIMIT_BUSINESS: int = Field(default=1000, env="USAGE_LIMIT_BUSINESS")
    USAGE_LIMIT_ENTERPRISE: int = Field(default=10000, env="USAGE_LIMIT_ENTERPRISE")
    
    # API Configuration
    API_QUOTA_FREE: int = Field(default=10, env="API_QUOTA_FREE")  # API calls per month
    API_QUOTA_PRO: int = Field(default=1000, env="API_QUOTA_PRO")
    API_QUOTA_BUSINESS: int = Field(default=10000, env="API_QUOTA_BUSINESS")
    API_QUOTA_ENTERPRISE: int = Field(default=100000, env="API_QUOTA_ENTERPRISE")
    
    # File Upload Configuration
    ALLOWED_EXTENSIONS: List[str] = Field(default=["jpg", "jpeg", "png", "gif", "webp"], env="ALLOWED_EXTENSIONS")
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    
    # Authentication
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "http://127.0.0.1:8000"],
        env="ALLOWED_ORIGINS"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
    
    # Commercial Features
    COMMERCIAL_MODE: bool = Field(default=False, env="COMMERCIAL_MODE")
    TRIAL_DAYS: int = Field(default=14, env="TRIAL_DAYS")
    REFERRAL_REWARD_DAYS: int = Field(default=30, env="REFERRAL_REWARD_DAYS")
    
    # Analytics
    ANALYTICS_ENABLED: bool = Field(default=True, env="ANALYTICS_ENABLED")
    ANALYTICS_RETENTION_DAYS: int = Field(default=365, env="ANALYTICS_RETENTION_DAYS")
    
    # Security
    PASSWORD_MIN_LENGTH: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    SESSION_TIMEOUT_MINUTES: int = Field(default=60, env="SESSION_TIMEOUT_MINUTES")
    
    # Performance
    CACHE_TTL_SECONDS: int = Field(default=3600, env="CACHE_TTL_SECONDS")  # 1 hour
    TEMPLATE_CACHE_TTL: int = Field(default=1800, env="TEMPLATE_CACHE_TTL")  # 30 minutes
    
    # Monitoring
    HEALTH_CHECK_ENABLED: bool = Field(default=True, env="HEALTH_CHECK_ENABLED")
    METRICS_ENABLED: bool = Field(default=True, env="METRICS_ENABLED")
    
    # Meta Platform Configuration
    META_APP_ID: Optional[str] = Field(default=None, env="META_APP_ID")
    META_APP_SECRET: Optional[str] = Field(default=None, env="META_APP_SECRET")
    META_REDIRECT_URI: str = Field(default="https://threadstorm.com/oauth/callback", env="META_REDIRECT_URI")
    META_WEBHOOK_VERIFY_TOKEN: Optional[str] = Field(default=None, env="META_WEBHOOK_VERIFY_TOKEN")

    # Meta API Configuration
    META_API_VERSION: str = Field(default="v18.0", env="META_API_VERSION")
    META_GRAPH_API_URL: str = Field(default="https://graph.facebook.com", env="META_GRAPH_API_URL")
    META_OAUTH_URL: str = Field(default="https://www.facebook.com", env="META_OAUTH_URL")

    # Meta Rate Limits (per profile per day)
    META_POSTS_PER_DAY: int = Field(default=250, env="META_POSTS_PER_DAY")
    META_REPLIES_PER_DAY: int = Field(default=1000, env="META_REPLIES_PER_DAY")
    META_REQUESTS_PER_HOUR: int = Field(default=200, env="META_REQUESTS_PER_HOUR")
    META_BULK_OPERATIONS_PER_DAY: int = Field(default=50, env="META_BULK_OPERATIONS_PER_DAY")

    # Meta Compliance Settings
    META_APP_REVIEW_MODE: bool = Field(default=True, env="META_APP_REVIEW_MODE")
    META_BUSINESS_VERIFICATION_REQUIRED: bool = Field(default=True, env="META_BUSINESS_VERIFICATION_REQUIRED")
    META_DATA_USE_CHECKUP_REQUIRED: bool = Field(default=True, env="META_DATA_USE_CHECKUP_REQUIRED")

    # Privacy & Compliance
    PRIVACY_POLICY_URL: str = Field(default="https://threadstorm.com/privacy", env="PRIVACY_POLICY_URL")
    DATA_DELETION_URL: str = Field(default="https://threadstorm.com/data-deletion", env="DATA_DELETION_URL")
    GDPR_COMPLIANT: bool = Field(default=True, env="GDPR_COMPLIANT")
    CCPA_COMPLIANT: bool = Field(default=True, env="CCPA_COMPLIANT")

    # Business Information
    BUSINESS_NAME: str = Field(default="Martek Labs LLC", env="BUSINESS_NAME")
    BUSINESS_EIN: Optional[str] = Field(default=None, env="BUSINESS_EIN")
    BUSINESS_ADDRESS: Optional[str] = Field(default=None, env="BUSINESS_ADDRESS")
    BUSINESS_VERIFICATION_STATUS: str = Field(default="pending", env="BUSINESS_VERIFICATION_STATUS")

    # Annual Compliance
    DATA_USE_CHECKUP_LAST_COMPLETED: Optional[str] = Field(default=None, env="DATA_USE_CHECKUP_LAST_COMPLETED")
    DATA_USE_CHECKUP_NEXT_DUE: Optional[str] = Field(default=None, env="DATA_USE_CHECKUP_NEXT_DUE")
    PLATFORM_TERMS_ACCEPTED: bool = Field(default=True, env="PLATFORM_TERMS_ACCEPTED")

    # Production Safety
    PRODUCTION_MODE: bool = Field(default=False, env="PRODUCTION_MODE")
    ENABLE_BULK_OPERATIONS: bool = Field(default=False, env="ENABLE_BULK_OPERATIONS")
    MAX_BULK_POSTS: int = Field(default=10, env="MAX_BULK_POSTS")
    ENABLE_SCHEDULING: bool = Field(default=True, env="ENABLE_SCHEDULING")
    MAX_SCHEDULE_DAYS: int = Field(default=30, env="MAX_SCHEDULE_DAYS")

    # Security & Monitoring
    ENABLE_AUDIT_LOGS: bool = Field(default=True, env="ENABLE_AUDIT_LOGS")
    ENABLE_RATE_LIMIT_LOGS: bool = Field(default=True, env="ENABLE_RATE_LIMIT_LOGS")
    ENABLE_ACCESS_LOGS: bool = Field(default=True, env="ENABLE_ACCESS_LOGS")
    ENABLE_DELETION_LOGS: bool = Field(default=True, env="ENABLE_DELETION_LOGS")

    # Token Management
    TOKEN_ENCRYPTION_KEY: Optional[str] = Field(default=None, env="TOKEN_ENCRYPTION_KEY")
    TOKEN_REFRESH_THRESHOLD_DAYS: int = Field(default=7, env="TOKEN_REFRESH_THRESHOLD_DAYS")
    MAX_TOKEN_REFRESH_ATTEMPTS: int = Field(default=3, env="MAX_TOKEN_REFRESH_ATTEMPTS")

    # Job Queue Configuration
    JOB_QUEUE_ENABLED: bool = Field(default=True, env="JOB_QUEUE_ENABLED")
    JOB_QUEUE_MAX_RETRIES: int = Field(default=3, env="JOB_QUEUE_MAX_RETRIES")
    JOB_QUEUE_BASE_DELAY: float = Field(default=1.0, env="JOB_QUEUE_BASE_DELAY")
    JOB_QUEUE_MAX_DELAY: int = Field(default=300, env="JOB_QUEUE_MAX_DELAY")

    # Backoff Strategies
    BACKOFF_EXPONENTIAL_MAX: int = Field(default=300, env="BACKOFF_EXPONENTIAL_MAX")
    BACKOFF_LINEAR_MAX: int = Field(default=60, env="BACKOFF_LINEAR_MAX")
    BACKOFF_JITTER_MAX: int = Field(default=120, env="BACKOFF_JITTER_MAX")

    # Data Retention
    DATA_RETENTION_DAYS: int = Field(default=730, env="DATA_RETENTION_DAYS")  # 2 years
    DELETION_LOG_RETENTION_DAYS: int = Field(default=30, env="DELETION_LOG_RETENTION_DAYS")
    AUDIT_LOG_RETENTION_DAYS: int = Field(default=365, env="AUDIT_LOG_RETENTION_DAYS")

    # Email Configuration for Compliance
    COMPLIANCE_EMAIL_ENABLED: bool = Field(default=True, env="COMPLIANCE_EMAIL_ENABLED")
    COMPLIANCE_EMAIL_FROM: str = Field(default="privacy@threadstorm.com", env="COMPLIANCE_EMAIL_FROM")
    COMPLIANCE_EMAIL_TEMPLATES: Dict[str, str] = Field(default={
        "data_deletion_confirmation": "data_deletion_confirmation.html",
        "account_deletion": "account_deletion.html",
        "privacy_update": "privacy_update.html"
    }, env="COMPLIANCE_EMAIL_TEMPLATES")

    # Meta Platform Terms Compliance
    PLATFORM_TERMS_VERSION: str = Field(default="2024-01-01", env="PLATFORM_TERMS_VERSION")
    ANTI_SPAM_ENABLED: bool = Field(default=True, env="ANTI_SPAM_ENABLED")
    CONTENT_MODERATION_ENABLED: bool = Field(default=True, env="CONTENT_MODERATION_ENABLED")
    USER_GUIDANCE_ENABLED: bool = Field(default=True, env="USER_GUIDANCE_ENABLED")

    # App Review Requirements
    APP_REVIEW_SCREENCAST_URL: Optional[str] = Field(default=None, env="APP_REVIEW_SCREENCAST_URL")
    APP_REVIEW_TEST_CREDENTIALS: Optional[str] = Field(default=None, env="APP_REVIEW_TEST_CREDENTIALS")
    APP_REVIEW_DATA_USAGE_DESCRIPTION: str = Field(
        default="ThreadStorm formats and publishes content to Threads. We collect content you choose to publish, basic profile information, and usage analytics to provide our service.",
        env="APP_REVIEW_DATA_USAGE_DESCRIPTION"
    )

    # Webhook Configuration
    WEBHOOK_ENABLED: bool = Field(default=True, env="WEBHOOK_ENABLED")
    WEBHOOK_VERIFY_TOKEN: Optional[str] = Field(default=None, env="WEBHOOK_VERIFY_TOKEN")
    WEBHOOK_SECRET: Optional[str] = Field(default=None, env="WEBHOOK_SECRET")

    # Monitoring & Alerting
    MONITORING_ENABLED: bool = Field(default=True, env="MONITORING_ENABLED")
    ALERT_EMAIL: Optional[str] = Field(default=None, env="ALERT_EMAIL")
    RATE_LIMIT_ALERT_THRESHOLD: float = Field(default=0.8, env="RATE_LIMIT_ALERT_THRESHOLD")
    ERROR_ALERT_THRESHOLD: int = Field(default=10, env="ERROR_ALERT_THRESHOLD")

    # Compliance Reporting
    COMPLIANCE_REPORTING_ENABLED: bool = Field(default=True, env="COMPLIANCE_REPORTING_ENABLED")
    MONTHLY_COMPLIANCE_REPORT: bool = Field(default=True, env="MONTHLY_COMPLIANCE_REPORT")
    QUARTERLY_DATA_USE_REVIEW: bool = Field(default=True, env="QUARTERLY_DATA_USE_REVIEW")

    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "http://127.0.0.1:8000"], env="CORS_ORIGINS")
    
    # Threads API Configuration (if separate from Meta)
    THREADS_APP_ID: Optional[str] = Field(default=None, env="THREADS_APP_ID")
    THREADS_APP_SECRET: Optional[str] = Field(default=None, env="THREADS_APP_SECRET")

    class Config:
        env_file = ".env"
        case_sensitive = True


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
    },
    'enterprise': {
        'rate_limit': settings.RATE_LIMIT_ENTERPRISE,
        'usage_limit': settings.USAGE_LIMIT_ENTERPRISE,
        'api_quota': settings.API_QUOTA_ENTERPRISE,
        'features': ['basic_formatting', 'all_templates', 'advanced_analytics', 'priority_support', 'api_access', 'team_collaboration', 'white_label', 'custom_integrations', 'sla_guarantee']
    }
}


# Pricing configuration
PRICING = {
    'pro': {
        'monthly': 999,  # $9.99 in cents
        'yearly': 9990,  # $99.90 in cents (save 17%)
        'stripe_price_id': 'price_1ABC123DEF456'
    },
    'business': {
        'monthly': 2999,  # $29.99 in cents
        'yearly': 29990,  # $299.90 in cents (save 17%)
        'stripe_price_id': 'price_1ABC123DEF789'
    },
    'enterprise': {
        'monthly': 9999,  # $99.99 in cents
        'yearly': 99990,  # $999.90 in cents (save 17%)
        'stripe_price_id': 'price_1ABC123DEF012'
    }
}

    # AWS KMS Configuration
    AWS_KMS_KEY_ID: Optional[str] = Field(default=None, env="AWS_KMS_KEY_ID")
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")

    # Security Hardening
    ENABLE_KMS_ENCRYPTION: bool = Field(default=True, env="ENABLE_KMS_ENCRYPTION")
    ENABLE_TOKEN_ENCRYPTION: bool = Field(default=True, env="ENABLE_TOKEN_ENCRYPTION")
    ENABLE_WEBHOOK_SIGNATURE_VERIFICATION: bool = Field(default=True, env="ENABLE_WEBHOOK_SIGNATURE_VERIFICATION")
    ENABLE_IDEMPOTENCY_KEYS: bool = Field(default=True, env="ENABLE_IDEMPOTENCY_KEYS")

    # RBAC Configuration
    ENABLE_RBAC: bool = Field(default=True, env="ENABLE_RBAC")
    ADMIN_ROLES: List[str] = Field(default=["admin", "super_admin"], env="ADMIN_ROLES")
    USER_ROLES: List[str] = Field(default=["user", "pro", "business"], env="USER_ROLES")

    # Observability Configuration
    OBSERVABILITY_ENABLED: bool = Field(default=True, env="OBSERVABILITY_ENABLED")
    METRICS_ENABLED: bool = Field(default=True, env="METRICS_ENABLED")
    ALERTING_ENABLED: bool = Field(default=True, env="ALERTING_ENABLED")
    CENTRALIZED_LOGGING_ENABLED: bool = Field(default=True, env="CENTRALIZED_LOGGING_ENABLED")

    # Metrics Configuration
    METRICS_RETENTION_DAYS: int = Field(default=7, env="METRICS_RETENTION_DAYS")
    METRICS_FLUSH_INTERVAL: int = Field(default=60, env="METRICS_FLUSH_INTERVAL")  # seconds
    METRICS_BUFFER_SIZE: int = Field(default=100, env="METRICS_BUFFER_SIZE")

    # Alerting Configuration
    ALERT_RETENTION_DAYS: int = Field(default=90, env="ALERT_RETENTION_DAYS")
    ALERT_CHECK_INTERVAL: int = Field(default=60, env="ALERT_CHECK_INTERVAL")  # seconds
    ALERT_NOTIFICATION_CHANNELS: List[str] = Field(default=["email", "slack"], env="ALERT_NOTIFICATION_CHANNELS")

    # Pipeline Configuration
    PIPELINE_ENABLED: bool = Field(default=True, env="PIPELINE_ENABLED")
    DEDUPLICATION_ENABLED: bool = Field(default=True, env="DEDUPLICATION_ENABLED")
    DEDUPLICATION_WINDOW_HOURS: int = Field(default=24, env="DEDUPLICATION_WINDOW_HOURS")
    IDEMPOTENCY_KEY_EXPIRY_HOURS: int = Field(default=24, env="IDEMPOTENCY_KEY_EXPIRY_HOURS")

    # Brand Protection
    BRAND_PROTECTION_ENABLED: bool = Field(default=True, env="BRAND_PROTECTION_ENABLED")
    TRADEMARK_CHECK_ENABLED: bool = Field(default=True, env="TRADEMARK_CHECK_ENABLED")
    BRAND_COMPLIANCE_MIDDLEWARE_ENABLED: bool = Field(default=True, env="BRAND_COMPLIANCE_MIDDLEWARE_ENABLED")

    # App Version
    APP_VERSION: str = Field(default="2.0.0", env="APP_VERSION")
