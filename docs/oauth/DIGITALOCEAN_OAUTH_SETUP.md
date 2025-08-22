# 🔐 Digital Ocean OAuth Setup Guide

## 🎯 **Overview**

This guide shows you how to add OAuth credentials (Google, Meta, etc.) to your Digital Ocean deployment for ThreadStorm.

## 🚀 **Option 1: Digital Ocean App Platform**

### **Step 1: Access Your App**
1. Go to [Digital Ocean App Platform](https://cloud.digitalocean.com/apps)
2. Select your ThreadStorm app
3. Click on **"Settings"** tab

### **Step 2: Add Environment Variables**
1. Scroll down to **"Environment Variables"** section
2. Click **"Edit"** or **"Add Variable"**
3. Add these OAuth variables:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://your-app-domain.com/api/v1/auth/google/callback

# Meta OAuth (Facebook/Instagram)
META_APP_ID=your-meta-app-id
META_APP_SECRET=your-meta-app-secret
META_REDIRECT_URI=https://your-app-domain.com/api/v1/auth/meta/callback

# Other OAuth providers
TWITTER_CLIENT_ID=your-twitter-client-id
TWITTER_CLIENT_SECRET=your-twitter-client-secret
TWITTER_REDIRECT_URI=https://your-app-domain.com/api/v1/auth/twitter/callback

LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret
LINKEDIN_REDIRECT_URI=https://your-app-domain.com/api/v1/auth/linkedin/callback
```

### **Step 3: Save and Deploy**
1. Click **"Save"**
2. Your app will automatically redeploy with the new environment variables

## 🐳 **Option 2: Docker/Kubernetes Deployment**

### **Step 1: Update docker-compose.prod.yml**
```yaml
version: '3.8'
services:
  app:
    build: .
    environment:
      # Google OAuth
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - GOOGLE_REDIRECT_URI=${GOOGLE_REDIRECT_URI}
      
      # Meta OAuth
      - META_APP_ID=${META_APP_ID}
      - META_APP_SECRET=${META_APP_SECRET}
      - META_REDIRECT_URI=${META_REDIRECT_URI}
      
      # Other environment variables...
    ports:
      - "8000:8000"
```

### **Step 2: Create .env.production**
```bash
# Copy your local .env file
cp .env .env.production

# Edit with production values
nano .env.production
```

### **Step 3: Deploy with Environment File**
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
```

## ☸️ **Option 3: Kubernetes (K8s)**

### **Step 1: Create Secret**
```bash
kubectl create secret generic oauth-secrets \
  --from-literal=GOOGLE_CLIENT_ID=your-google-client-id \
  --from-literal=GOOGLE_CLIENT_SECRET=your-google-client-secret \
  --from-literal=META_APP_ID=your-meta-app-id \
  --from-literal=META_APP_SECRET=your-meta-app-secret
```

### **Step 2: Update Deployment YAML**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: threadstorm-app
spec:
  template:
    spec:
      containers:
      - name: app
        image: your-registry/threadstorm:latest
        env:
        - name: GOOGLE_CLIENT_ID
          valueFrom:
            secretKeyRef:
              name: oauth-secrets
              key: GOOGLE_CLIENT_ID
        - name: GOOGLE_CLIENT_SECRET
          valueFrom:
            secretKeyRef:
              name: oauth-secrets
              key: GOOGLE_CLIENT_SECRET
        - name: META_APP_ID
          valueFrom:
            secretKeyRef:
              name: oauth-secrets
              key: META_APP_ID
        - name: META_APP_SECRET
          valueFrom:
            secretKeyRef:
              name: oauth-secrets
              key: META_APP_SECRET
```

## 🔧 **Option 4: Digital Ocean Droplet (Manual)**

### **Step 1: SSH into Your Droplet**
```bash
ssh root@your-droplet-ip
```

### **Step 2: Edit Environment File**
```bash
cd /opt/threadstorm
nano .env.production
```

### **Step 3: Add OAuth Variables**
```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://your-domain.com/api/v1/auth/google/callback

# Meta OAuth
META_APP_ID=your-meta-app-id
META_APP_SECRET=your-meta-app-secret
META_REDIRECT_URI=https://your-domain.com/api/v1/auth/meta/callback
```

### **Step 4: Restart Application**
```bash
sudo systemctl restart threadstorm
```

## 🔐 **Getting OAuth Credentials**

### **Google OAuth Setup**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client IDs**
5. Set authorized redirect URIs:
   - `https://your-domain.com/api/v1/auth/google/callback`
6. Copy Client ID and Client Secret

### **Meta OAuth Setup**
1. Go to [Meta Developers](https://developers.facebook.com/)
2. Create a new app or select existing
3. Add **Facebook Login** product
4. Go to **Settings** → **Basic**
5. Copy App ID and App Secret
6. Add OAuth redirect URIs:
   - `https://your-domain.com/api/v1/auth/meta/callback`

## 🧪 **Testing OAuth Setup**

### **Step 1: Test OAuth Endpoints**
```bash
# Test Google OAuth
curl https://your-domain.com/api/v1/auth/google/authorize

# Test Meta OAuth
curl https://your-domain.com/api/v1/auth/meta/authorize
```

### **Step 2: Check Environment Variables**
```bash
# If using Docker
docker exec -it your-container-name env | grep -E "(GOOGLE|META)"

# If using Kubernetes
kubectl exec -it deployment/threadstorm-app -- env | grep -E "(GOOGLE|META)"
```

## 🔒 **Security Best Practices**

### **1. Use Secrets Management**
- Never commit OAuth secrets to Git
- Use Digital Ocean's secret management or Kubernetes secrets
- Rotate secrets regularly

### **2. Environment-Specific Configuration**
```bash
# Development
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# Production
GOOGLE_REDIRECT_URI=https://your-domain.com/api/v1/auth/google/callback
```

### **3. HTTPS Required**
- Always use HTTPS in production
- Configure SSL certificates properly
- OAuth providers require HTTPS for production

## 🚨 **Troubleshooting**

### **Common Issues**

**1. "Invalid redirect URI"**
- Check that your redirect URI exactly matches what's configured in OAuth provider
- Ensure HTTPS is used in production

**2. "Client ID not found"**
- Verify environment variables are set correctly
- Check for typos in variable names

**3. "OAuth flow failed"**
- Check server logs for detailed error messages
- Verify OAuth provider configuration

### **Debug Commands**
```bash
# Check if environment variables are loaded
echo $GOOGLE_CLIENT_ID

# Test OAuth configuration
curl -X GET "https://your-domain.com/api/v1/auth/health"

# Check application logs
docker logs your-container-name
```

## 📋 **Checklist**

- [ ] OAuth credentials obtained from providers
- [ ] Environment variables configured in Digital Ocean
- [ ] Redirect URIs set correctly
- [ ] HTTPS configured for production
- [ ] Application deployed with new environment variables
- [ ] OAuth endpoints tested
- [ ] User registration/login working
- [ ] OAuth flows tested end-to-end

## 🎯 **Next Steps**

1. **Deploy your changes** to Digital Ocean
2. **Test OAuth flows** with real credentials
3. **Monitor logs** for any OAuth-related errors
4. **Set up monitoring** for OAuth success/failure rates
5. **Configure backup OAuth providers** if needed
