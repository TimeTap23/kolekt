# 🚀 Production OAuth Setup Guide for Kolekt.io

This guide will help you set up real OAuth integration for Instagram and Facebook when deploying Kolekt to production at `https://www.kolekt.io`.

## 📋 Prerequisites

1. **Meta Developer Account**: https://developers.facebook.com/
2. **Facebook App**: Create a new app in Meta Developer Console
3. **Instagram Basic Display**: Add Instagram Basic Display product to your app
4. **Facebook Login**: Add Facebook Login product to your app

## 🔧 Step 1: Meta Developer Console Configuration

### 1.1 Create/Configure Your Facebook App

1. Go to https://developers.facebook.com/
2. Click "Create App" or select your existing app
3. Choose "Consumer" as the app type
4. Fill in basic app information:
   - **App Name**: Kolekt
   - **App Contact Email**: your-email@kolekt.io
   - **App Purpose**: Social media content management

### 1.2 Configure App Settings

In your app dashboard, go to **Settings → Basic**:

```
App Domains: www.kolekt.io
Privacy Policy URL: https://www.kolekt.io/privacy
Terms of Service URL: https://www.kolekt.io/terms
```

### 1.3 Add Threads Integration

1. Go to **Products → Threads** (or create a custom app integration)
2. Click "Set Up"
3. Configure **Threads Integration**:
   - **Client OAuth Settings**:
     - **Valid OAuth Redirect URIs**: `https://www.kolekt.io/oauth/threads/callback`
     - **Uninstall Callback URL**: `https://www.kolekt.io/oauth/threads/uninstall`
     - **Delete Callback URL**: `https://www.kolekt.io/oauth/threads/delete`
   - **Permissions and Features**:
     - ✅ `threads_basic`
     - ✅ `threads_content_publish`

### 1.4 Add Instagram Basic Display

1. Go to **Products → Instagram Basic Display**
2. Click "Set Up"
3. Configure **Basic Display**:
   - **Client OAuth Settings**:
     - **Valid OAuth Redirect URIs**: `https://www.kolekt.io/oauth/instagram/callback`
     - **Uninstall Callback URL**: `https://www.kolekt.io/oauth/instagram/uninstall`
     - **Data Deletion Request URL**: `https://www.kolekt.io/oauth/instagram/delete`
   - **Permissions and Features**:
     - ✅ `user_profile`
     - ✅ `user_media`

### 1.5 Add Facebook Login

1. Go to **Products → Facebook Login**
2. Click "Set Up"
3. Configure **Facebook Login**:
   - **Client OAuth Settings**:
     - **Valid OAuth Redirect URIs**: `https://www.kolekt.io/oauth/facebook/callback`
     - **Uninstall Callback URL**: `https://www.kolekt.io/oauth/facebook/uninstall`
     - **Data Deletion Request URL**: `https://www.kolekt.io/oauth/facebook/delete`
   - **Permissions and Features**:
     - ✅ `pages_show_list`
     - ✅ `pages_read_engagement`
     - ✅ `pages_manage_posts`

## 🔑 Step 2: Environment Variables

Add these environment variables to your production `.env` file:

```bash
# Meta OAuth Configuration (for Instagram, Facebook, and Threads)
META_APP_ID=your_facebook_app_id_here
META_APP_SECRET=your_facebook_app_secret_here
META_REDIRECT_URI=https://www.kolekt.io/oauth/{platform}/callback
META_WEBHOOK_VERIFY_TOKEN=your_webhook_verify_token_here

# Production URLs
OAUTH_REDIRECT_BASE=https://www.kolekt.io

# Security (Production)
SECRET_KEY=your_secure_secret_key_here
ENABLE_TOKEN_ENCRYPTION=true
TOKEN_ENCRYPTION_KEY=your_encryption_key_here
```

## 🛡️ Step 3: Security Considerations

### 3.1 Token Encryption

In production, access tokens should be encrypted before storage:

```python
# In src/services/meta_oauth.py, add encryption:
from cryptography.fernet import Fernet

def encrypt_token(self, token: str) -> str:
    """Encrypt access token for storage"""
    f = Fernet(self.encryption_key.encode())
    return f.encrypt(token.encode()).decode()

def decrypt_token(self, encrypted_token: str) -> str:
    """Decrypt access token from storage"""
    f = Fernet(self.encryption_key.encode())
    return f.decrypt(encrypted_token.encode()).decode()
```

### 3.2 HTTPS Requirements

Meta requires HTTPS for production OAuth:
- ✅ `https://www.kolekt.io` - Valid
- ❌ `http://www.kolekt.io` - Invalid

## 🔄 Step 4: OAuth Flow Testing

### 4.1 Test Threads OAuth

1. Visit: `https://www.kolekt.io/oauth/threads/url`
2. You'll be redirected to: `https://threads.net/oauth/authorize?...`
3. After authorization, you'll be redirected to: `https://www.kolekt.io/oauth/threads/callback?code=...`

### 4.2 Test Instagram OAuth

1. Visit: `https://www.kolekt.io/oauth/instagram/url`
2. You'll be redirected to: `https://api.instagram.com/oauth/authorize?...`
3. After authorization, you'll be redirected to: `https://www.kolekt.io/oauth/instagram/callback?code=...`

### 4.3 Test Facebook OAuth

1. Visit: `https://www.kolekt.io/oauth/facebook/url`
2. You'll be redirected to: `https://www.facebook.com/v18.0/dialog/oauth?...`
3. After authorization, you'll be redirected to: `https://www.kolekt.io/oauth/facebook/callback?code=...`

## 📱 Step 5: Platform-Specific Notes

### 5.1 Threads Integration

- **Scope**: `threads_basic, threads_content_publish`
- **Token Expiration**: Varies (typically 60 days)
- **API Endpoints**: https://graph.facebook.com/ (Threads uses Facebook Graph API)
- **Features**: Post content to Threads, read basic profile info
- **Required URLs**: 
  - OAuth Callback: `https://www.kolekt.io/oauth/threads/callback`
  - Uninstall: `https://www.kolekt.io/oauth/threads/uninstall`
  - Delete: `https://www.kolekt.io/oauth/threads/delete`

### 5.2 Instagram Basic Display

- **Scope**: `user_profile, user_media`
- **Token Expiration**: 60 days
- **API Endpoints**: https://graph.instagram.com/
- **Limitations**: Read-only for basic display
- **Required URLs**:
  - OAuth Callback: `https://www.kolekt.io/oauth/instagram/callback`
  - Uninstall: `https://www.kolekt.io/oauth/instagram/uninstall`
  - Data Deletion: `https://www.kolekt.io/oauth/instagram/delete`

### 5.3 Facebook Login

- **Scope**: `pages_show_list, pages_read_engagement, pages_manage_posts`
- **Token Expiration**: Varies (can be extended to 60 days)
- **API Endpoints**: https://graph.facebook.com/
- **Features**: Can post to pages, read insights
- **Required URLs**:
  - OAuth Callback: `https://www.kolekt.io/oauth/facebook/callback`
  - Uninstall: `https://www.kolekt.io/oauth/facebook/uninstall`
  - Data Deletion: `https://www.kolekt.io/oauth/facebook/delete`

## 🚨 Step 6: Error Handling

Common OAuth errors and solutions:

### 6.1 Invalid Redirect URI

```
Error: "redirect_uri" parameter does not match any registered redirect URIs
```

**Solution**: Ensure the redirect URI in Meta Developer Console exactly matches:
- `https://www.kolekt.io/oauth/instagram/callback`
- `https://www.kolekt.io/oauth/facebook/callback`

### 6.2 App Not Approved

```
Error: App is not approved for this scope
```

**Solution**: 
1. Submit your app for review in Meta Developer Console
2. Or use test users during development

### 6.3 Token Expired

```
Error: Token expired
```

**Solution**: Implement token refresh logic or re-authenticate user

## 🔍 Step 7: Monitoring & Debugging

### 7.1 Enable Debug Mode

Add to your `.env`:
```bash
DEBUG=true
META_DEBUG=true
```

### 7.2 Log OAuth Events

The system logs all OAuth events:
- OAuth URL generation
- Token exchange
- Profile fetching
- Connection storage

### 7.3 Test with Meta's Test Users

1. Create test users in Meta Developer Console
2. Use test users for development/testing
3. Avoid using real accounts during development

## 📊 Step 8: Production Checklist

Before going live:

- [ ] Threads App configured with correct redirect URIs and required URLs
- [ ] Meta App configured with correct redirect URIs and required URLs
- [ ] Environment variables set in production (Threads + Meta credentials)
- [ ] HTTPS enabled on kolekt.io
- [ ] Token encryption implemented
- [ ] Error handling tested
- [ ] OAuth flow tested with real accounts
- [ ] Uninstall and data deletion endpoints tested
- [ ] Privacy policy and terms of service pages created
- [ ] App submitted for platform review (if needed)

## 🆘 Troubleshooting

### Common Issues:

1. **"Invalid client_id"**: Check META_APP_ID in environment
2. **"Invalid redirect_uri"**: Verify redirect URIs in Meta Console
3. **"App not approved"**: Submit app for review or use test users
4. **"Token expired"**: Implement refresh logic

### Getting Help:

- Meta Developer Documentation: https://developers.facebook.com/docs/
- Instagram Basic Display: https://developers.facebook.com/docs/instagram-basic-display-api/
- Facebook Login: https://developers.facebook.com/docs/facebook-login/

## 🎯 Next Steps

After OAuth is working:

1. **Step 3**: Implement Admin Authentication
2. **Step 4**: Add real JWT tokens and password hashing
3. **Step 5**: Implement content posting to real APIs
4. **Step 6**: Add analytics and monitoring

---

**Need help?** Check the logs in your production environment or contact the development team.
