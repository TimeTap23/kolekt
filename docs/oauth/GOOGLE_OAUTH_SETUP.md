# 🔐 Google OAuth Setup for Kolekt

## 🎯 **Quick Setup Guide**

### **Step 1: Google Cloud Console Setup**

1. **Go to**: https://console.cloud.google.com/
2. **Create Project**: `Kolekt OAuth`
3. **Enable APIs**:
   - Google+ API
   - Google Identity

### **Step 2: OAuth Consent Screen**

1. **App Name**: `Kolekt`
2. **Support Email**: Your email
3. **Scopes**: `openid`, `email`, `profile`
4. **Test Users**: Add your email

### **Step 3: Create OAuth 2.0 Client**

1. **Type**: Web application
2. **Name**: `Kolekt Web Client`
3. **Redirect URIs**:
   ```
   http://localhost:8000/api/v1/auth/google/callback
   https://www.kolekt.io/api/v1/auth/google/callback
   https://kolekt.io/api/v1/auth/google/callback
   ```

### **Step 4: Get Credentials**

You'll receive:
- **Client ID**: `123456789-abcdefghijklmnop.apps.googleusercontent.com`
- **Client Secret**: `GOCSPX-abcdefghijklmnopqrstuvwxyz`

## 🔧 **Add to Railway**

### **Option 1: App Platform Environment Variables**

1. Go to your Railway App Platform
2. Select your Kolekt app
3. Go to **Settings** → **Environment Variables**
4. Add these variables:

```bash
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here
GOOGLE_REDIRECT_URI=https://www.kolekt.io/api/v1/auth/google/callback
```

### **Option 2: Update .env.production**

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here
GOOGLE_REDIRECT_URI=https://www.kolekt.io/api/v1/auth/google/callback
```

## 🧪 **Test Your Setup**

### **Local Testing**
```bash
# Test Google OAuth endpoint
curl http://localhost:8000/api/v1/auth/google/authorize
```

### **Production Testing**
```bash
# Test Google OAuth endpoint
curl https://www.kolekt.io/api/v1/auth/google/authorize
```

## 🔒 **Security Notes**

1. **Never commit credentials to Git**
2. **Use environment variables in production**
3. **Rotate secrets regularly**
4. **Monitor OAuth usage**

## 🚨 **Troubleshooting**

### **Common Issues**

**1. "Invalid redirect URI"**
- Ensure redirect URI exactly matches Google Console
- Check for typos in domain name

**2. "Client ID not found"**
- Verify environment variables are set
- Check for extra spaces or characters

**3. "OAuth consent screen not configured"**
- Complete the OAuth consent screen setup
- Add your email as test user

## 📋 **Checklist**

- [ ] Google Cloud project created
- [ ] APIs enabled (Google+, Google Identity)
- [ ] OAuth consent screen configured
- [ ] OAuth 2.0 client created
- [ ] Redirect URIs added
- [ ] Credentials saved securely
- [ ] Environment variables set in Railway
- [ ] OAuth endpoints tested
- [ ] User registration/login working

## 🎯 **Next Steps**

1. **Deploy to Railway** with new credentials
2. **Test OAuth flow** end-to-end
3. **Monitor logs** for any OAuth errors
4. **Set up monitoring** for OAuth success rates
