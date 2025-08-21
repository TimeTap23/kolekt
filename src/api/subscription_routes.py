#!/usr/bin/env python3
"""
Subscription Management API Routes
Handles user subscriptions, plans, and billing
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Request
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
    "starter": SubscriptionPlan(
        id="starter",
        name="Starter",
        price=12.00,
        features=["100 AI credits/month", "Up to 3 connected accounts", "Basic scheduling", "Basic analytics"],
        limits={
            "ai_credits_per_month": 100,
            "connected_accounts": 3,
            "posts_per_month": 50,
            "api_calls_per_month": 500,
            "storage_mb": 500
        }
    ),
    "pro": SubscriptionPlan(
        id="pro",
        name="Pro",
        price=29.00,
        features=["400 AI credits/month", "Up to 6 connected accounts", "Advanced analytics", "Content templates"],
        limits={
            "ai_credits_per_month": 400,
            "connected_accounts": 6,
            "posts_per_month": 200,
            "api_calls_per_month": 2000,
            "storage_mb": 2000
        }
    ),
    "business": SubscriptionPlan(
        id="business",
        name="Business",
        price=79.00,
        features=["1500 AI credits/month", "Up to 10 connected accounts", "Team collaboration", "Priority support"],
        limits={
            "ai_credits_per_month": 1500,
            "connected_accounts": 10,
            "posts_per_month": 1000,
            "api_calls_per_month": 10000,
            "storage_mb": 10000
        }
    )
}

# Credit packs
CREDIT_PACKS = {
    "100": {
        "id": "100",
        "name": "100 Credits",
        "credits": 100,
        "price": 10.00,
        "description": "Perfect for trying out AI features"
    },
    "300": {
        "id": "300", 
        "name": "300 Credits",
        "credits": 300,
        "price": 25.00,
        "description": "Most popular choice"
    },
    "750": {
        "id": "750",
        "name": "750 Credits", 
        "credits": 750,
        "price": 50.00,
        "description": "Best value for power users"
    }
}

from src.services.authentication import get_current_user
from src.services.stripe_service import stripe_service
from src.core.config import settings, CREDIT_PACKS

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

@subscription_router.get("/credit-packs")
async def get_credit_packs():
    """Get all available credit packs"""
    try:
        return {
            "success": True,
            "credit_packs": list(CREDIT_PACKS.values())
        }
    except Exception as e:
        logger.error(f"Error getting credit packs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get credit packs")

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
            plan_id="starter",
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
            limits=AVAILABLE_PLANS["starter"].limits
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
        
        logger.info(f"User {user_id} upgrading to plan {plan_id}")
        # Map plan to Stripe price
        price_map = {
            'starter': settings.STRIPE_PRICE_STARTER_MONTHLY,
            'pro': settings.STRIPE_PRICE_PRO_MONTHLY,
            'business': settings.STRIPE_PRICE_BUSINESS_MONTHLY
        }
        price_id = price_map.get(plan_id)
        success_url = "https://www.kolekt.io/dashboard?billing=success"
        cancel_url = "https://www.kolekt.io/dashboard?billing=cancel"
        session = stripe_service.create_checkout_session(user_id, price_id or 'price_mock', success_url, cancel_url)
        return {
            "success": True,
            "message": f"Proceed to checkout for {plan.name}",
            "plan": plan,
            "checkout_url": session.get('url')
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

@subscription_router.post("/portal")
async def create_billing_portal(
    user_id: str = Depends(get_current_user_id)
):
    """Create a Stripe billing portal session for the current user.
    Note: In production, look up the user's Stripe customer ID in your DB."""
    try:
        # TODO: Replace with actual lookup of user's Stripe customer ID
        mock_customer_id = "cus_mock"
        session = stripe_service.create_billing_portal(
            customer_id=mock_customer_id,
            return_url=settings.STRIPE_BILLING_PORTAL_RETURN_URL or "https://www.kolekt.io/dashboard"
        )
        return {"success": True, "portal_url": session.get('url')}
    except Exception as e:
        logger.error(f"Error creating billing portal: {e}")
        raise HTTPException(status_code=500, detail="Failed to create billing portal")

@subscription_router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    try:
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        event = None
        try:
            event = stripe_service.verify_webhook(payload, sig_header) if sig_header else None
        except Exception:
            raise HTTPException(status_code=400, detail="Webhook verification failed")

        # If Stripe not enabled, accept mock
        if event is None:
            return {"received": True, "mock": True}

        event_type = event['type']
        data_object = event['data']['object']

        # Handle subscription lifecycle events (skeleton)
        if event_type == 'checkout.session.completed':
            logger.info('Stripe checkout completed')
        elif event_type == 'invoice.payment_succeeded':
            logger.info('Invoice payment succeeded')
        elif event_type == 'customer.subscription.updated':
            logger.info('Subscription updated')
        elif event_type == 'customer.subscription.deleted':
            logger.info('Subscription canceled')

        return {"received": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        raise HTTPException(status_code=400, detail="Webhook error")

@subscription_router.post("/buy-credits")
async def buy_credit_pack(
    pack_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Purchase a credit pack"""
    try:
        if pack_id not in CREDIT_PACKS:
            raise HTTPException(status_code=400, detail="Invalid credit pack ID")
        
        pack = CREDIT_PACKS[pack_id]
        
        logger.info(f"User {user_id} purchasing credit pack {pack_id}")
        
        # Map pack to Stripe price
        price_map = {
            '100': settings.STRIPE_PRICE_CREDITS_100,
            '300': settings.STRIPE_PRICE_CREDITS_300,
            '750': settings.STRIPE_PRICE_CREDITS_750
        }
        price_id = price_map.get(pack_id)
        
        success_url = "https://www.kolekt.io/dashboard?credits=success"
        cancel_url = "https://www.kolekt.io/dashboard?credits=cancel"
        
        # Use payment mode for one-time purchases
        session = stripe_service.create_checkout_session(
            user_id, 
            price_id or 'price_mock', 
            success_url, 
            cancel_url, 
            mode="payment"
        )
        
        return {
            "success": True,
            "message": f"Proceed to checkout for {pack['name']}",
            "pack": pack,
            "checkout_url": session.get('url')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error purchasing credit pack: {e}")
        raise HTTPException(status_code=500, detail="Failed to purchase credit pack")

@subscription_router.get("/limits")
async def get_user_limits(
    user_id: str = Depends(get_current_user_id)
):
    """Get user's current plan limits"""
    try:
        # For now, return free plan limits
        # In production, this would be based on actual subscription
        
        return {
            "plan": "starter",
            "limits": AVAILABLE_PLANS["starter"].limits,
            "features": AVAILABLE_PLANS["starter"].features
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
