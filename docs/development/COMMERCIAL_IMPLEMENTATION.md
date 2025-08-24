# Kolekt Commercial Implementation Guide

## 🚀 **Phase 1: Foundation (Week 1-2)**

### **1. Add Subscription Management**

```python
# src/services/subscriptions.py
import stripe
from fastapi import HTTPException
from src.core.config import settings

class SubscriptionService:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.supabase = SupabaseService()
    
    async def create_subscription(self, user_id: str, plan_type: str):
        """Create a new subscription"""
        # Get user from Supabase
        user = await self.supabase.get_current_user(user_id)
        
        # Create Stripe customer
        customer = stripe.Customer.create(
            email=user.email,
            metadata={'user_id': user_id}
        )
        
        # Get plan price ID
        price_id = self.get_price_id(plan_type)
        
        # Create subscription
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{"price": price_id}],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
        )
        
        # Update user in Supabase
        await self.supabase.update_user_subscription(
            user_id, 
            subscription.id, 
            plan_type
        )
        
        return subscription
    
    def get_price_id(self, plan_type: str):
        """Get Stripe price ID for plan"""
        prices = {
            'pro': 'price_1ABC123DEF456',
            'business': 'price_1ABC123DEF789',
            'enterprise': 'price_1ABC123DEF012'
        }
        return prices.get(plan_type)
```

### **2. Implement Rate Limiting**

```python
# src/middleware/rate_limiting.py
from fastapi import HTTPException, Request
import redis
import time
from src.services.supabase import SupabaseService

class RateLimitMiddleware:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.supabase = SupabaseService()
    
    async def check_rate_limit(self, request: Request, user_id: str):
        """Check if user has exceeded rate limits"""
        # Get user's plan
        user = await self.supabase.get_current_user(user_id)
        plan_type = user.get('plan_type', 'free')
        
        # Define limits
        limits = {
            'free': {'requests_per_minute': 10, 'kolekts_per_month': 10},
            'pro': {'requests_per_minute': 100, 'kolekts_per_month': 100},
            'business': {'requests_per_minute': 500, 'kolekts_per_month': 1000},
            'enterprise': {'requests_per_minute': 2000, 'kolekts_per_month': 10000}
        }
        
        limit = limits.get(plan_type, limits['free'])
        
        # Check minute rate limit
        minute_key = f"rate_limit:{user_id}:{int(time.time() / 60)}"
        current_minute = self.redis_client.get(minute_key)
        
        if current_minute and int(current_minute) >= limit['requests_per_minute']:
            raise HTTPException(
                status_code=429, 
                detail=f"Rate limit exceeded. Upgrade to {plan_type} for higher limits."
            )
        
        # Increment counter
        self.redis_client.incr(minute_key)
        self.redis_client.expire(minute_key, 60)
        
        return True
```

### **3. Add Usage Tracking**

```python
# src/services/analytics.py
from datetime import datetime, timedelta
from src.services.supabase import SupabaseService

class AnalyticsService:
    def __init__(self):
        self.supabase = SupabaseService()
    
    async def track_kolekt_creation(self, user_id: str, metadata: dict):
        """Track kolekt creation for analytics"""
        await self.supabase.table('usage_metrics').insert({
            'user_id': user_id,
            'metric_type': 'kolekt',
            'metadata': {
                'posts_count': metadata.get('total_posts'),
                'character_count': metadata.get('total_characters'),
                'tone': metadata.get('tone'),
                'has_images': metadata.get('has_images', False),
                'engagement_score': metadata.get('engagement_score')
            }
        }).execute()
    
    async def get_user_usage(self, user_id: str, date_range: str = '30d'):
        """Get user usage statistics"""
        start_date = datetime.now() - timedelta(days=30)
        
        response = await self.supabase.table('usage_metrics')\
            .select('*')\
            .eq('user_id', user_id)\
            .gte('created_at', start_date.isoformat())\
            .execute()
        
        return self.aggregate_usage(response.data)
    
    def aggregate_usage(self, data):
        """Aggregate usage data"""
        total_kolekts = len([d for d in data if d['metric_type'] == 'kolekt'])
        total_characters = sum([
            d['metadata'].get('character_count', 0) 
            for d in data if d['metric_type'] == 'kolekt'
        ])
        
        return {
            'total_kolekts': total_kolekts,
            'total_characters': total_characters,
            'average_engagement': sum([
                d['metadata'].get('engagement_score', 0) 
                for d in data if d['metric_type'] == 'kolekt'
            ]) / max(total_kolekts, 1)
        }
```

## 💳 **Phase 2: Payment Integration (Week 3-4)**

### **1. Stripe Webhook Handler**

```python
# src/api/payments.py
from fastapi import APIRouter, Request, HTTPException
import stripe
from src.services.subscriptions import SubscriptionService

payment_router = APIRouter()
subscription_service = SubscriptionService()

@payment_router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    if event['type'] == 'invoice.payment_succeeded':
        await subscription_service.handle_payment_success(event['data']['object'])
    elif event['type'] == 'invoice.payment_failed':
        await subscription_service.handle_payment_failure(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        await subscription_service.handle_subscription_cancelled(event['data']['object'])
    
    return {"status": "success"}

@payment_router.post("/create-checkout-session")
async def create_checkout_session(user_id: str, plan_type: str):
    """Create Stripe checkout session"""
    try:
        session = stripe.checkout.Session.create(
            customer_email=user_email,
            line_items=[{
                'price': subscription_service.get_price_id(plan_type),
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://kolekt.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://kolekt.com/cancel',
            metadata={'user_id': user_id, 'plan_type': plan_type}
        )
        return {"session_id": session.id, "url": session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### **2. Subscription Management UI**

```javascript
// web/static/js/subscriptions.js
class SubscriptionManager {
    constructor() {
        this.stripe = Stripe('pk_test_your_publishable_key');
    }
    
    async createCheckoutSession(planType) {
        try {
            const response = await fetch('/api/v1/payments/create-checkout-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    plan_type: planType
                })
            });
            
            const session = await response.json();
            
            // Redirect to Stripe checkout
            const result = await this.stripe.redirectToCheckout({
                sessionId: session.session_id
            });
            
            if (result.error) {
                this.showError(result.error.message);
            }
        } catch (error) {
            this.showError('Failed to create checkout session');
        }
    }
    
    async getCurrentSubscription() {
        try {
            const response = await fetch('/api/v1/subscriptions/current', {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });
            
            return await response.json();
        } catch (error) {
            console.error('Failed to get subscription:', error);
            return null;
        }
    }
    
    showUpgradeModal() {
        const modal = document.getElementById('upgrade-modal');
        modal.style.display = 'block';
        
        // Populate plan options
        this.populatePlanOptions();
    }
    
    populatePlanOptions() {
        const plans = [
            {
                name: 'Pro',
                price: '$9.99/month',
                features: ['100 kolekts/month', 'All templates', 'Analytics', 'Priority support'],
                plan_type: 'pro'
            },
            {
                name: 'Business',
                price: '$29.99/month',
                features: ['Unlimited kolekts', 'Team collaboration', 'API access', 'White-label options'],
                plan_type: 'business'
            },
            {
                name: 'Enterprise',
                price: '$99.99/month',
                features: ['Everything in Business', 'Custom integrations', 'Dedicated support', 'SLA guarantee'],
                plan_type: 'enterprise'
            }
        ];
        
        const container = document.getElementById('plan-options');
        container.innerHTML = plans.map(plan => `
            <div class="plan-card">
                <h3>${plan.name}</h3>
                <div class="price">${plan.price}</div>
                <ul>
                    ${plan.features.map(feature => `<li>${feature}</li>`).join('')}
                </ul>
                <button onclick="subscriptionManager.createCheckoutSession('${plan.plan_type}')">
                    Upgrade to ${plan.name}
                </button>
            </div>
        `).join('');
    }
}
```

## 📊 **Phase 3: Analytics Dashboard (Week 5-6)**

### **1. User Dashboard**

```python
# src/api/dashboard.py
from fastapi import APIRouter, Depends
from src.services.analytics import AnalyticsService
from src.services.subscriptions import SubscriptionService

dashboard_router = APIRouter()
analytics_service = AnalyticsService()
subscription_service = SubscriptionService()

@dashboard_router.get("/usage")
async def get_user_usage(user_id: str = Depends(get_current_user)):
    """Get user usage statistics"""
    usage = await analytics_service.get_user_usage(user_id)
    subscription = await subscription_service.get_current_subscription(user_id)
    
    return {
        "usage": usage,
        "subscription": subscription,
        "limits": subscription_service.get_plan_limits(subscription['plan_type'])
    }

@dashboard_router.get("/analytics")
async def get_user_analytics(user_id: str = Depends(get_current_user)):
    """Get detailed user analytics"""
    analytics = await analytics_service.get_detailed_analytics(user_id)
    return analytics
```

### **2. Admin Dashboard**

```python
# src/api/admin.py
from fastapi import APIRouter, Depends
from src.services.analytics import AnalyticsService

admin_router = APIRouter()
analytics_service = AnalyticsService()

@dashboard_router.get("/admin/revenue")
async def get_revenue_analytics():
    """Get revenue analytics for admin"""
    return await analytics_service.get_revenue_metrics()

@dashboard_router.get("/admin/users")
async def get_user_analytics():
    """Get user analytics for admin"""
    return await analytics_service.get_user_metrics()

@dashboard_router.get("/admin/usage")
async def get_platform_usage():
    """Get platform usage analytics"""
    return await analytics_service.get_platform_metrics()
```

## 🔐 **Phase 4: Security & Compliance (Week 7-8)**

### **1. API Key Management**

```python
# src/services/api_keys.py
import secrets
import hashlib
from src.services.supabase import SupabaseService

class APIKeyService:
    def __init__(self):
        self.supabase = SupabaseService()
    
    async def generate_api_key(self, user_id: str, name: str):
        """Generate a new API key for user"""
        api_key = secrets.token_urlsafe(32)
        hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
        
        await self.supabase.table('api_keys').insert({
            'user_id': user_id,
            'key_hash': hashed_key,
            'name': name,
            'permissions': ['read', 'write'],
            'active': True
        }).execute()
        
        return api_key
    
    async def validate_api_key(self, api_key: str):
        """Validate API key and return user info"""
        hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
        
        response = await self.supabase.table('api_keys')\
            .select('*')\
            .eq('key_hash', hashed_key)\
            .eq('active', True)\
            .execute()
        
        if response.data:
            return response.data[0]
        return None
```

### **2. GDPR Compliance**

```python
# src/services/gdpr.py
from src.services.supabase import SupabaseService

class GDPRService:
    def __init__(self):
        self.supabase = SupabaseService()
    
    async def export_user_data(self, user_id: str):
        """Export all user data for GDPR compliance"""
        # Get user profile
        profile = await self.supabase.table('profiles')\
            .select('*')\
            .eq('id', user_id)\
            .execute()
        
        # Get kolekts
        kolekts = await self.supabase.table('kolekts')\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
        
        # Get usage metrics
        usage = await self.supabase.table('usage_metrics')\
            .select('*')\
            .eq('user_id', user_id)\
            .execute()
        
        return {
            'profile': profile.data[0] if profile.data else None,
            'kolekts': kolekts.data,
            'usage_metrics': usage.data,
            'export_date': datetime.utcnow().isoformat()
        }
    
    async def delete_user_data(self, user_id: str):
        """Delete all user data for GDPR compliance"""
        # Delete kolekts
        await self.supabase.table('kolekts')\
            .delete()\
            .eq('user_id', user_id)\
            .execute()
        
        # Delete usage metrics
        await self.supabase.table('usage_metrics')\
            .delete()\
            .eq('user_id', user_id)\
            .execute()
        
        # Delete profile
        await self.supabase.table('profiles')\
            .delete()\
            .eq('id', user_id)\
            .execute()
        
        # Delete from Supabase Auth
        await self.supabase.auth.admin.delete_user(user_id)
```

## 🚀 **Phase 5: Deployment & Scaling (Week 9-10)**

### **1. Production Environment Variables**

```bash
# .env.production
DATABASE_URL=postgresql://user:pass@host:5432/kolekt
REDIS_URL=redis://host:6379
STRIPE_SECRET_KEY=sk_live_your_live_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key
SUPABASE_ANON_KEY=your_anon_key
SECRET_KEY=your_secret_key
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

### **2. Docker Production Setup**

```dockerfile
# Dockerfile.prod
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **3. Nginx Configuration**

```nginx
# nginx.conf
upstream kolekt {
    server app:8000;
}

server {
    listen 80;
    server_name kolekt.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name kolekt.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    location / {
        proxy_pass http://kolekt;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://kolekt;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /app/web/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 📈 **Phase 6: Marketing & Growth (Week 11-12)**

### **1. Referral System**

```python
# src/services/referrals.py
import random
import string
from src.services.supabase import SupabaseService

class ReferralService:
    def __init__(self):
        self.supabase = SupabaseService()
    
    async def create_referral_code(self, user_id: str):
        """Create referral code for user"""
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        await self.supabase.table('referrals').insert({
            'user_id': user_id,
            'code': code,
            'uses': 0,
            'max_uses': 10,
            'rewards': []
        }).execute()
        
        return code
    
    async def apply_referral_code(self, code: str, new_user_id: str):
        """Apply referral code for new user"""
        referral = await self.supabase.table('referrals')\
            .select('*')\
            .eq('code', code)\
            .lt('uses', 'max_uses')\
            .execute()
        
        if referral.data:
            # Update referral usage
            await self.supabase.table('referrals')\
                .update({'uses': referral.data[0]['uses'] + 1})\
                .eq('code', code)\
                .execute()
            
            # Give benefits to both users
            await self.give_referral_benefits(
                referral.data[0]['user_id'], 
                new_user_id
            )
            
            return True
        
        return False
    
    async def give_referral_benefits(self, referrer_id: str, new_user_id: str):
        """Give benefits to both referrer and new user"""
        # Give referrer 1 month free upgrade
        await self.supabase.table('referral_rewards').insert({
            'user_id': referrer_id,
            'type': 'free_month',
            'description': 'Referral reward: 1 month free upgrade'
        }).execute()
        
        # Give new user 50% off first month
        await self.supabase.table('referral_rewards').insert({
            'user_id': new_user_id,
            'type': 'discount',
            'description': 'Referral reward: 50% off first month',
            'discount_percent': 50
        }).execute()
```

### **2. Email Marketing Integration**

```python
# src/services/email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.core.config import settings

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
    
    async def send_welcome_email(self, user_email: str, user_name: str):
        """Send welcome email to new user"""
        subject = "Welcome to Kolekt! 🚀"
        
        html_content = f"""
        <html>
        <body>
            <h1>Welcome to Kolekt, {user_name}!</h1>
            <p>You're now ready to create engaging Threads content that drives engagement.</p>
            <p>Here's what you can do:</p>
            <ul>
                <li>Format long content into digestible Threads posts</li>
                <li>Use our professional templates</li>
                <li>Track your engagement analytics</li>
                <li>Collaborate with your team</li>
            </ul>
            <p><a href="https://kolekt.com/dashboard">Get Started</a></p>
        </body>
        </html>
        """
        
        await self.send_email(user_email, subject, html_content)
    
    async def send_upgrade_reminder(self, user_email: str, user_name: str):
        """Send upgrade reminder to free users"""
        subject = "Upgrade to Kolekt Pro! 🚀"
        
        html_content = f"""
        <html>
        <body>
            <h1>Ready to scale your Threads game, {user_name}?</h1>
            <p>You've used 8/10 free kolekts this month. Upgrade to Pro for:</p>
            <ul>
                <li>100 kolekts per month</li>
                <li>Advanced analytics</li>
                <li>Priority support</li>
                <li>All premium templates</li>
            </ul>
            <p><a href="https://kolekt.com/upgrade">Upgrade Now</a></p>
        </body>
        </html>
        """
        
        await self.send_email(user_email, subject, html_content)
    
    async def send_email(self, to_email: str, subject: str, html_content: str):
        """Send email via SMTP"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.FROM_EMAIL
        msg['To'] = to_email
        
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
```

## 💰 **Revenue Projections**

### **Conservative Estimates (Year 1)**
- **Month 1-3**: 100 free users, 10 paid users
- **Month 4-6**: 500 free users, 50 paid users ($500/month)
- **Month 7-9**: 1,000 free users, 150 paid users ($1,500/month)
- **Month 10-12**: 2,000 free users, 300 paid users ($3,000/month)

### **Aggressive Estimates (Year 1)**
- **Month 1-3**: 500 free users, 50 paid users
- **Month 4-6**: 2,000 free users, 200 paid users ($2,000/month)
- **Month 7-9**: 5,000 free users, 500 paid users ($5,000/month)
- **Month 10-12**: 10,000 free users, 1,000 paid users ($10,000/month)

### **Break-even Analysis**
- **Monthly Costs**: ~$500 (hosting, Stripe fees, Supabase)
- **Break-even**: 50 Pro users or 25 Business users
- **Profitability**: Achievable within 6 months

This implementation guide provides a roadmap for transforming Kolekt into a profitable commercial SaaS application while maintaining the core functionality and user experience.
