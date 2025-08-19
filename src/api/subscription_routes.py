#!/usr/bin/env python3
"""
Subscription Management API Routes
Handles user subscriptions, plans, and billing
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

# Setup logging
logger = logging.getLogger(__name__)

# Create router
subscription_router = APIRouter()

# Pydantic models
from pydantic import BaseModel

class SubscriptionPlan(BaseModel):
    id: str
    name: str
    price: float
    currency: str = "USD"
    interval: str = "month"
    features: List[str]
    limits: Dict[str, Any]

class UserSubscription(BaseModel):
    id: str
    user_id: str
    plan_id: str
    status: str  # active, canceled, past_due, etc.
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool = False
    created_at: datetime
    updated_at: datetime

class UsageStats(BaseModel):
    user_id: str
    current_period_start: datetime
    current_period_end: datetime
    content_created: int
    posts_published: int
    api_calls: int
    storage_used: int  # in bytes
    limits: Dict[str, Any]

# Available plans
AVAILABLE_PLANS = {
    "free": SubscriptionPlan(
        id="free",
        name="Free",
        price=0.0,
        features=["Basic content creation", "Threads posting", "5 posts per month"],
        limits={
            "content_creation": 10,
            "posts_per_month": 5,
            "api_calls_per_month": 100,
            "storage_mb": 100
        }
    ),
    "pro": SubscriptionPlan(
        id="pro",
        name="Pro",
        price=9.99,
        features=["Unlimited content creation", "All platforms", "Analytics", "Scheduling"],
        limits={
            "content_creation": -1,  # unlimited
            "posts_per_month": 100,
            "api_calls_per_month": 1000,
            "storage_mb": 1000
        }
    ),
    "business": SubscriptionPlan(
        id="business",
        name="Business",
        price=29.99,
        features=["Team collaboration", "Advanced analytics", "Priority support", "White-label"],
        limits={
            "content_creation": -1,  # unlimited
            "posts_per_month": 500,
            "api_calls_per_month": 5000,
            "storage_mb": 5000
        }
    )
}

from src.services.authentication import get_current_user

# Dependency to get current user (via JWT)
async def get_current_user_id(current_user: Dict = Depends(get_current_user)) -> str:
    """Get current user ID from JWT-authenticated request"""
    return current_user["user_id"]

@subscription_router.get("/plans")
async def get_available_plans():
    """Get all available subscription plans"""
    try:
        return {
            "success": True,
            "plans": [plan.dict() for plan in AVAILABLE_PLANS.values()]
        }
    except Exception as e:
        logger.error(f"Error getting plans: {e}")
        raise HTTPException(status_code=500, detail="Failed to get plans")

@subscription_router.get("/current")
async def get_current_subscription(
    user_id: str = Depends(get_current_user_id)
):
    """Get current user subscription"""
    try:
        # For now, return mock subscription data
        # In production, this would fetch from database
        
        now = datetime.utcnow()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        period_end = period_start.replace(month=period_start.month + 1)
        
        subscription = UserSubscription(
            id="mock_subscription_id",
            user_id=user_id,
            plan_id="free",
            status="active",
            current_period_start=period_start,
            current_period_end=period_end,
            cancel_at_period_end=False,
            created_at=now,
            updated_at=now
        )
        
        return {
            "success": True,
            "subscription": subscription.dict()
        }
        
    except Exception as e:
        logger.error(f"Error getting current subscription: {e}")
        return {"success": False, "error": str(e)}

@subscription_router.get("/usage")
async def get_usage_stats(
    user_id: str = Depends(get_current_user_id)
):
    """Get current usage statistics"""
    try:
        # For now, return mock usage data
        # In production, this would calculate from actual usage
        
        now = datetime.utcnow()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        period_end = period_start.replace(month=period_start.month + 1)
        
        usage = UsageStats(
            user_id=user_id,
            current_period_start=period_start,
            current_period_end=period_end,
            content_created=5,
            posts_published=1,
            api_calls=25,
            storage_used=1024 * 1024 * 10,  # 10MB
            limits=AVAILABLE_PLANS["free"].limits
        )
        
        return {
            "success": True,
            "usage": usage.dict()
        }
        
    except Exception as e:
        logger.error(f"Error getting usage stats: {e}")
        return {"success": False, "error": str(e)}

@subscription_router.post("/upgrade")
async def upgrade_subscription(
    plan_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Upgrade user subscription"""
    try:
        if plan_id not in AVAILABLE_PLANS:
            raise HTTPException(status_code=400, detail="Invalid plan ID")
        
        plan = AVAILABLE_PLANS[plan_id]
        
        # For now, just return success
        # In production, this would integrate with Stripe
        
        logger.info(f"User {user_id} upgrading to plan {plan_id}")
        
        return {
            "success": True,
            "message": f"Successfully upgraded to {plan.name} plan",
            "plan": plan,
            "checkout_url": f"https://stripe.com/checkout/mock?plan={plan_id}"  # Mock Stripe URL
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error upgrading subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to upgrade subscription")

@subscription_router.post("/cancel")
async def cancel_subscription(
    user_id: str = Depends(get_current_user_id)
):
    """Cancel user subscription"""
    try:
        # For now, just return success
        # In production, this would update Stripe subscription
        
        logger.info(f"User {user_id} canceling subscription")
        
        return {
            "success": True,
            "message": "Subscription will be canceled at the end of the current period",
            "cancel_at_period_end": True
        }
        
    except Exception as e:
        logger.error(f"Error canceling subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")

@subscription_router.get("/limits")
async def get_user_limits(
    user_id: str = Depends(get_current_user_id)
):
    """Get user's current plan limits"""
    try:
        # For now, return free plan limits
        # In production, this would be based on actual subscription
        
        return {
            "plan": "free",
            "limits": AVAILABLE_PLANS["free"].limits,
            "features": AVAILABLE_PLANS["free"].features
        }
        
    except Exception as e:
        logger.error(f"Error getting user limits: {e}")
        raise HTTPException(status_code=500, detail="Failed to get limits")

@subscription_router.post("/check-usage")
async def check_usage_limits(
    action: str,
    user_id: str = Depends(get_current_user_id)
):
    """Check if user can perform an action based on their plan limits"""
    try:
        # For now, always allow (free plan limits are generous)
        # In production, this would check actual usage against limits
        
        return {
            "allowed": True,
            "remaining": 999,  # Mock remaining count
            "limit": 1000,     # Mock limit
            "action": action
        }
        
    except Exception as e:
        logger.error(f"Error checking usage limits: {e}")
        raise HTTPException(status_code=500, detail="Failed to check usage limits")
