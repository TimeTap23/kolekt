"""
Stripe Service for Kolekt
Encapsulates Stripe SDK usage for checkout sessions, billing portal, and webhook verification
"""

from typing import Optional, Dict, Any
import logging
import stripe

from src.core.config import settings

logger = logging.getLogger(__name__)

class StripeService:
    def __init__(self) -> None:
        self.enabled = bool(settings.STRIPE_SECRET_KEY)
        if not self.enabled:
            logger.warning("Stripe not configured; billing endpoints will be in mock mode.")
            return
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_checkout_session(self, user_id: str, price_id: str, success_url: str, cancel_url: str) -> Dict[str, Any]:
        if not self.enabled:
            return {"url": f"https://billing.mock/checkout?price={price_id}"}
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=user_id,
            allow_promotion_codes=True,
            payment_method_types=["card"],
            metadata={"user_id": user_id}
        )
        return {"id": session.id, "url": session.url}

    def create_billing_portal(self, customer_id: str, return_url: str) -> Dict[str, Any]:
        if not self.enabled:
            return {"url": "https://billing.mock/portal"}
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url or settings.STRIPE_BILLING_PORTAL_RETURN_URL or "https://www.kolekt.io/dashboard"
        )
        return {"id": session.id, "url": session.url}

    def verify_webhook(self, payload: bytes, sig_header: str) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return None
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
            return event
        except Exception as e:
            logger.error(f"Stripe webhook verification failed: {e}")
            raise

stripe_service = StripeService()
