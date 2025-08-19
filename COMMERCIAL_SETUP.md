# ThreadStorm Commercial Setup Guide

## 🚀 **Quick Start for Commercial Deployment**

This guide will help you set up ThreadStorm for commercial deployment with all the necessary infrastructure and configurations.

## 📋 **Prerequisites**

- Python 3.11+
- Supabase account
- Stripe account (for payments)
- Redis server (for caching and rate limiting)
- Domain name (for production)

## 🏗️ **Step 1: Database Setup**

### **1.1 Update Supabase Schema**

1. Go to your Supabase project dashboard
2. Navigate to the SQL Editor
3. Copy and paste the contents of `supabase_schema_commercial.sql`
4. Execute the script to create all commercial tables and functions

### **1.2 Verify Database Setup**

```sql
-- Check that all tables were created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'organizations', 'profiles', 'templates', 'drafts', 
    'threadstorms', 'usage_metrics', 'api_keys', 
    'subscriptions', 'payments', 'referrals', 
    'referral_rewards', 'user_settings'
);

-- Check that all functions were created
SELECT routine_name 
FROM information_schema.routines 
WHERE routine_schema = 'public' 
AND routine_name IN (
    'update_updated_at_column', 'handle_new_user', 'track_usage_metric'
);
```

## 🔧 **Step 2: Environment Configuration**

### **2.1 Create Production Environment File**

```bash
# Copy the example environment file
cp env.example .env.production

# Edit the production environment file
nano .env.production
```

### **2.2 Configure Required Variables**

```bash
# App Configuration
APP_NAME=ThreadStorm
APP_VERSION=1.0.0
DEBUG=false
HOST=0.0.0.0
PORT=8000
SECRET_KEY=your-super-secret-production-key-here

# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_STORAGE_BUCKET=threadstorm

# Stripe Configuration (for payments)
STRIPE_SECRET_KEY=sk_live_your-live-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=pk_live_your-live-stripe-publishable-key
STRIPE_WEBHOOK_SECRET=whsec_your-stripe-webhook-secret

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com

# Redis Configuration
REDIS_URL=redis://your-redis-host:6379
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_DB=0

# Commercial Features
COMMERCIAL_MODE=true
TRIAL_DAYS=14
REFERRAL_REWARD_DAYS=30

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_FREE=10
RATE_LIMIT_PRO=100
RATE_LIMIT_BUSINESS=500
RATE_LIMIT_ENTERPRISE=2000

# Usage Limits
USAGE_LIMIT_FREE=10
USAGE_LIMIT_PRO=100
USAGE_LIMIT_BUSINESS=1000
USAGE_LIMIT_ENTERPRISE=10000
```

## 💳 **Step 3: Stripe Setup**

### **3.1 Create Stripe Products and Prices**

1. Go to your Stripe Dashboard
2. Navigate to Products
3. Create the following products:

**Pro Plan**
- Name: ThreadStorm Pro
- Price: $9.99/month
- Price ID: `price_1ABC123DEF456`

**Business Plan**
- Name: ThreadStorm Business
- Price: $29.99/month
- Price ID: `price_1ABC123DEF789`

**Enterprise Plan**
- Name: ThreadStorm Enterprise
- Price: $99.99/month
- Price ID: `price_1ABC123DEF012`

### **3.2 Configure Stripe Webhooks**

1. Go to Stripe Dashboard > Webhooks
2. Add endpoint: `https://yourdomain.com/api/v1/payments/webhook`
3. Select events:
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
4. Copy the webhook secret to your `.env.production`

### **3.3 Update Pricing Configuration**

Edit `src/core/config.py` and update the `PRICING` dictionary with your actual Stripe price IDs:

```python
PRICING = {
    'pro': {
        'monthly': 999,  # $9.99 in cents
        'yearly': 9990,  # $99.90 in cents (save 17%)
        'stripe_price_id': 'price_1ABC123DEF456'  # Your actual price ID
    },
    'business': {
        'monthly': 2999,  # $29.99 in cents
        'yearly': 29990,  # $299.90 in cents (save 17%)
        'stripe_price_id': 'price_1ABC123DEF789'  # Your actual price ID
    },
    'enterprise': {
        'monthly': 9999,  # $99.99 in cents
        'yearly': 99990,  # $999.90 in cents (save 17%)
        'stripe_price_id': 'price_1ABC123DEF012'  # Your actual price ID
    }
}
```

## 📧 **Step 4: Email Configuration**

### **4.1 Gmail Setup (Recommended)**

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security > 2-Step Verification > App passwords
   - Generate password for "Mail"
3. Use the generated password in your `.env.production`

### **4.2 Alternative Email Providers**

**SendGrid**
```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

**Mailgun**
```bash
SMTP_SERVER=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=your-mailgun-username
SMTP_PASSWORD=your-mailgun-password
```

## 🚀 **Step 5: Production Deployment**

### **5.1 Docker Production Setup**

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - COMMERCIAL_MODE=true
    depends_on:
      - redis
    restart: unless-stopped
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  redis_data:
```

### **5.2 Nginx Configuration**

Create `nginx.conf`:

```nginx
upstream threadstorm {
    server app:8000;
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
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
        proxy_pass http://threadstorm;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://threadstorm;
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

### **5.3 Deploy to Production**

```bash
# Build and start the production stack
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f app

# Scale if needed
docker-compose -f docker-compose.prod.yml up -d --scale app=3
```

## 🔍 **Step 6: Verification**

### **6.1 Test Core Functionality**

```bash
# Test health endpoint
curl https://yourdomain.com/health

# Test threadstorm formatting
curl -X POST https://yourdomain.com/api/v1/format \
  -H "Content-Type: application/json" \
  -d '{"content": "Test content for ThreadStorm formatting.", "tone": "professional"}'

# Test usage tracking
curl https://yourdomain.com/api/v1/usage

# Test analytics
curl https://yourdomain.com/api/v1/analytics
```

### **6.2 Test Stripe Integration**

1. Go to Stripe Dashboard > Test mode
2. Create a test customer
3. Create a test subscription
4. Verify webhook events are received

### **6.3 Monitor Logs**

```bash
# Application logs
docker-compose -f docker-compose.prod.yml logs -f app

# Nginx logs
docker-compose -f docker-compose.prod.yml logs -f nginx

# Redis logs
docker-compose -f docker-compose.prod.yml logs -f redis
```

## 📊 **Step 7: Analytics and Monitoring**

### **7.1 Set Up Monitoring**

1. **Application Monitoring**: Use tools like Sentry or DataDog
2. **Database Monitoring**: Supabase provides built-in monitoring
3. **Payment Monitoring**: Stripe Dashboard provides comprehensive analytics

### **7.2 Business Metrics Dashboard**

Access your business metrics at:
- `https://yourdomain.com/api/v1/admin/metrics` (when implemented)

### **7.3 Usage Analytics**

Monitor usage patterns:
- User engagement
- Feature adoption
- Conversion rates
- Churn analysis

## 🔐 **Step 8: Security Hardening**

### **8.1 SSL Certificate**

```bash
# Using Let's Encrypt
sudo certbot --nginx -d yourdomain.com

# Or use your own SSL certificate
sudo cp your-cert.pem /path/to/ssl/cert.pem
sudo cp your-key.pem /path/to/ssl/key.pem
```

### **8.2 Security Headers**

The Nginx configuration already includes security headers. Additional considerations:

1. **Rate Limiting**: Already configured in Nginx
2. **CORS**: Configured in FastAPI
3. **Input Validation**: Pydantic models handle this
4. **SQL Injection**: Supabase handles this

### **8.3 Backup Strategy**

```bash
# Database backup (Supabase handles this automatically)
# File backup
rsync -av /path/to/uploads/ /backup/uploads/

# Configuration backup
cp .env.production /backup/config/
cp nginx.conf /backup/config/
```

## 🚀 **Step 9: Launch Checklist**

- [ ] Database schema deployed
- [ ] Environment variables configured
- [ ] Stripe products and webhooks set up
- [ ] Email service configured
- [ ] SSL certificate installed
- [ ] Production deployment running
- [ ] Core functionality tested
- [ ] Payment flow tested
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] Domain DNS configured
- [ ] Analytics tracking enabled

## 📈 **Step 10: Post-Launch**

### **10.1 Marketing Setup**

1. **Google Analytics**: Add tracking code to your frontend
2. **Social Media**: Set up business accounts
3. **Content Marketing**: Start blog/educational content
4. **SEO**: Optimize for relevant keywords

### **10.2 Customer Support**

1. **Help Documentation**: Create user guides
2. **Support Email**: Set up support@yourdomain.com
3. **FAQ Page**: Common questions and answers
4. **Live Chat**: Consider adding live chat support

### **10.3 Growth Strategy**

1. **Referral Program**: Implement the referral system
2. **Email Marketing**: Set up automated email campaigns
3. **Partnerships**: Reach out to potential partners
4. **Content Marketing**: Create valuable content for your audience

## 🎯 **Next Steps**

1. **Add your Meta API keys** when the Threads API becomes available
2. **Implement advanced features** like team collaboration
3. **Add more payment options** like PayPal or Apple Pay
4. **Expand to other platforms** beyond Threads
5. **Build a mobile app** for iOS and Android

Your ThreadStorm commercial deployment is now ready! 🚀
