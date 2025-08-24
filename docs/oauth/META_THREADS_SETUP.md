# 📱 Meta & Threads API Setup Guide

This guide will help you configure your Meta and Threads app credentials for Kolekt.

## 🎯 **Overview**

Kolekt integrates with Meta's platform to:
- **Authenticate users** via OAuth
- **Publish content** directly to Threads
- **Manage permissions** and rate limits
- **Ensure compliance** with Meta's platform terms

## 📋 **Prerequisites**

1. **Meta Developer Account**: https://developers.facebook.com/
2. **Meta App**: Either existing or new app
3. **Threads API Access**: Requested and approved by Meta
4. **Business Verification**: Required for production use

## 🔧 **Step-by-Step Setup**

### **1. Create/Configure Meta App**

#### **A. Access Meta Developer Console**
1. Go to https://developers.facebook.com/
2. Sign in with your Facebook account
3. Create a new app or select existing app

#### **B. Add Threads API Product**
1. In your app dashboard, click **"Add Product"**
2. Search for **"Threads API"**
3. Click **"Set Up"** to add the product

#### **C. Configure App Settings**
1. Go to **App Settings > Basic**
2. Note your **App ID** and **App Secret**
3. Add your **App Domain** (e.g., `kolekt.com`)
4. Add **Privacy Policy URL** (required for production)

### **2. Configure OAuth Settings**

#### **A. Enable OAuth Login**
1. Go to **Products > Facebook Login > Settings**
2. Add **Valid OAuth Redirect URIs**:
   ```
   http://localhost:8000/api/v1/auth/meta/callback
   https://yourdomain.com/api/v1/auth/meta/callback
   ```
3. Save changes

#### **B. Request Permissions**
1. Go to **App Review > Permissions and Features**
2. Request these permissions:
   - `threads_basic` - Read Threads data
   - `threads_content_publish` - Publish to Threads
   - `instagram_basic` - Read Instagram data (if needed)
   - `instagram_content_publish` - Publish to Instagram (if needed)

### **3. Configure Kolekt**

#### **A. Run Setup Script**
```bash
python setup_meta_credentials.py
```

This will prompt you for:
- **Meta App ID**
- **Meta App Secret**
- **Threads App ID** (if separate)
- **Threads App Secret** (if separate)
- **Redirect URI**

#### **B. Manual Configuration**
Alternatively, edit your `.env` file:

```bash
# Meta Platform Configuration
META_APP_ID=your-meta-app-id
META_APP_SECRET=your-meta-app-secret
META_REDIRECT_URI=http://localhost:8000/api/v1/auth/meta/callback
META_WEBHOOK_VERIFY_TOKEN=your-webhook-verify-token

# Threads API Configuration (if separate from Meta)
THREADS_APP_ID=your-threads-app-id
THREADS_APP_SECRET=your-threads-app-secret
THREADS_API_KEY=your-threads-api-key
THREADS_API_SECRET=your-threads-api-secret
```

### **4. Test Configuration**

#### **A. Run Credential Test**
```bash
python test_meta_credentials.py
```

This will test:
- ✅ Meta OAuth configuration
- ✅ Threads API configuration
- ✅ OAuth flow simulation
- ✅ API endpoints

#### **B. Manual OAuth Test**
1. Start Kolekt: `python main.py`
2. Navigate to: `http://localhost:8000`
3. Click **"Connect Threads"** or **"Threads API"**
4. Complete the OAuth flow
5. Verify successful connection

## 🔒 **Production Requirements**

### **1. App Review Process**

#### **A. Submit for Review**
1. Go to **App Review > Permissions and Features**
2. Submit each permission for review:
   - `threads_basic`
   - `threads_content_publish`
3. Provide detailed use case descriptions
4. Include screencasts of your app's functionality

#### **B. Business Verification**
1. Go to **Business Settings**
2. Add your business information:
   - Business name: **Martek Labs LLC**
   - Business address
   - EIN (if applicable)
3. Upload required documentation
4. Wait for verification (can take several days)

### **2. Compliance Requirements**

#### **A. Privacy Policy**
- Must be publicly accessible
- Include data usage details
- Cover Meta platform data handling

#### **B. Data Deletion**
- Implement data deletion endpoint
- Handle Meta's data deletion callbacks
- Provide user deletion instructions

#### **C. Platform Terms**
- Accept Meta Platform Terms
- Follow content policies
- Implement anti-spam measures

## 🧪 **Testing Your Setup**

### **1. Development Testing**

```bash
# Test credentials
python test_meta_credentials.py

# Test OAuth flow
python test_meta_credentials.py validate

# Get setup instructions
python setup_meta_credentials.py instructions
```

### **2. OAuth Flow Testing**

1. **Generate OAuth URL**:
   ```python
   from src.services.meta_oauth import meta_oauth
   
   state = meta_oauth.generate_state_token()
   code_verifier = meta_oauth.generate_code_verifier()
   code_challenge = meta_oauth.generate_code_challenge(code_verifier)
   oauth_url = meta_oauth.get_oauth_url(state, code_challenge)
   print(f"OAuth URL: {oauth_url}")
   ```

2. **Complete OAuth Flow**:
   - Open the OAuth URL in browser
   - Authorize your app
   - Copy the authorization code from redirect URL

3. **Exchange for Token**:
   ```python
   token_data = await meta_oauth.exchange_code_for_token(auth_code, code_verifier)
   print(f"Access Token: {token_data['access_token']}")
   ```

### **3. API Testing**

```python
# Test posting to Threads
from src.services.threads_api import threads_service

response = await threads_service.post_thread(
    user_id="your-user-id",
    content="Test post from Kolekt!",
    access_token="your-access-token"
)
print(f"Post Response: {response}")
```

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. "Invalid App ID" Error**
- Verify your Meta App ID is correct
- Ensure the app is active and not in development mode
- Check that you're using the right app

#### **2. "Invalid Redirect URI" Error**
- Verify redirect URI matches exactly in Meta app settings
- Check for trailing slashes or protocol differences
- Ensure URI is added to valid OAuth redirect URIs

#### **3. "Permission Denied" Error**
- Request permissions in App Review
- Wait for approval (can take days/weeks)
- Use test users during development

#### **4. "Rate Limit Exceeded" Error**
- Check your app's rate limits
- Implement exponential backoff
- Monitor usage in Meta Developer Console

### **Debug Commands**

```bash
# Check environment variables
python -c "from src.core.config import settings; print(f'Meta App ID: {settings.META_APP_ID}')"

# Test OAuth URL generation
python -c "
from src.services.meta_oauth import meta_oauth
state = meta_oauth.generate_state_token()
print(f'State: {state}')
"

# Validate configuration
python setup_meta_credentials.py validate
```

## 📚 **API Reference**

### **Meta OAuth Endpoints**

| Endpoint | Purpose |
|----------|---------|
| `https://www.facebook.com/v18.0/dialog/oauth` | Authorization |
| `https://graph.facebook.com/v18.0/oauth/access_token` | Token exchange |
| `https://graph.facebook.com/v18.0/me` | User info |

### **Threads API Endpoints**

| Endpoint | Purpose |
|----------|---------|
| `https://graph.facebook.com/v18.0/me/media` | Create post |
| `https://graph.facebook.com/v18.0/{post_id}/comments` | Reply to post |
| `https://graph.facebook.com/v18.0/me/accounts` | Get user accounts |

### **Rate Limits**

| Operation | Limit |
|-----------|-------|
| Posts per day | 250 |
| Replies per day | 1,000 |
| API requests per hour | 200 |
| Bulk operations per day | 50 |

## 🚀 **Production Deployment**

### **1. Environment Variables**

```bash
# Production environment
export META_APP_ID="your-production-app-id"
export META_APP_SECRET="your-production-app-secret"
export META_REDIRECT_URI="https://yourdomain.com/api/v1/auth/meta/callback"
export ENVIRONMENT="production"
```

### **2. Security Checklist**

- [ ] Use HTTPS for all OAuth callbacks
- [ ] Implement proper token storage encryption
- [ ] Set up webhook signature verification
- [ ] Configure rate limiting
- [ ] Enable audit logging
- [ ] Set up monitoring and alerts

### **3. Monitoring**

- Monitor OAuth success/failure rates
- Track API usage and rate limits
- Log all Meta API interactions
- Set up alerts for errors

## 📞 **Support**

### **Meta Developer Support**
- [Meta Developer Documentation](https://developers.facebook.com/docs/)
- [Meta Developer Community](https://developers.facebook.com/community/)
- [Meta App Review Guidelines](https://developers.facebook.com/docs/app-review/)

### **Kolekt Support**
- Check logs for detailed error messages
- Verify configuration with test scripts
- Review Meta Developer Console for app status
- Ensure compliance with platform terms

---

**Kolekt Meta Integration** - Secure, compliant, and production-ready Meta/Threads API integration.
