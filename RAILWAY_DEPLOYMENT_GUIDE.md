# 🚂 Railway Deployment Guide for Kolekt

## 🎯 **Quick Start**

### **1. Connect Your Repository**
1. Go to [Railway.app](https://railway.app)
2. Sign in with your GitHub account
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `kolekt` repository
5. Railway will automatically detect the Python project

### **2. Configure Environment Variables**
In your Railway project dashboard, go to **Variables** tab and add:

#### **Required Variables:**
```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_KEY=your-supabase-service-role-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# Security Configuration
SECRET_KEY=your-super-secret-jwt-key-here
JWT_SECRET=your-jwt-signing-key-here
TOKEN_ENCRYPTION_KEY=your-token-encryption-key-here

# Admin Configuration
ADMIN_EMAIL=info@marteklabs.com
ADMIN_PASSWORD=your-secure-admin-password-here

# Application Configuration
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
```

#### **Optional Variables:**
```bash
# Meta/Threads Configuration
META_APP_ID=your-meta-app-id
META_APP_SECRET=your-meta-app-secret
THREADS_APP_SECRET=your-threads-app-secret

# Redis Configuration (if using external Redis)
REDIS_URL=your-redis-url

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### **3. Deploy**
1. Railway will automatically build and deploy your application
2. Monitor the build logs for any issues
3. Once deployed, Railway will provide a public URL

## 🔧 **Configuration Details**

### **Build Configuration**
- **Builder**: Nixpacks (automatically detected)
- **Python Version**: 3.9+
- **Start Command**: `uvicorn start_kolekt:app --host 0.0.0.0 --port $PORT`
- **Health Check**: `/health` endpoint

### **Environment Optimization**
- **Production Mode**: `ENVIRONMENT=production`
- **Debug Disabled**: `DEBUG=false`
- **Host Binding**: `0.0.0.0` for Railway's proxy

## 📊 **Monitoring & Health Checks**

### **Health Check Endpoint**
Railway will automatically monitor: `https://your-app.railway.app/health`

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-24T14:00:00Z",
  "version": "2.0.0",
  "services": {
    "production_mode": true,
    "routes_available": true,
    "middleware_available": true
  }
}
```

### **Performance Monitoring**
- Railway provides built-in metrics
- Monitor CPU, memory, and network usage
- Set up alerts for resource limits

## 🔒 **Security Configuration**

### **SSL/TLS**
- Railway automatically provides SSL certificates
- All traffic is encrypted by default
- Custom domains supported

### **Environment Variables**
- All secrets stored securely in Railway
- No hardcoded credentials in code
- Automatic encryption at rest

## 🚀 **Scaling Configuration**

### **Auto-Scaling**
Railway automatically scales based on:
- CPU usage
- Memory consumption
- Request volume

### **Resource Limits**
- **Free Tier**: 500 hours/month
- **Pro Tier**: Unlimited usage
- **Custom**: Enterprise plans available

## 📝 **Deployment Checklist**

### **Pre-Deployment**
- [ ] **Environment variables configured**
- [ ] **Supabase project set up**
- [ ] **Domain configured (optional)**
- [ ] **SSL certificate ready**

### **Post-Deployment**
- [ ] **Health check passing**
- [ ] **Admin panel accessible**
- [ ] **User registration working**
- [ ] **Database connections verified**
- [ ] **Performance monitoring active**

## 🔍 **Troubleshooting**

### **Common Issues**

#### **Build Failures**
```bash
# Check build logs in Railway dashboard
# Common fixes:
pip install --upgrade pip
pip install -r requirements.txt
```

#### **Environment Variable Issues**
```bash
# Verify all required variables are set
# Check variable names match exactly
# Ensure no extra spaces or quotes
```

#### **Database Connection Issues**
```bash
# Verify Supabase URL and keys
# Check network connectivity
# Ensure database is accessible
```

### **Debug Commands**
```bash
# Check application logs
railway logs

# Access application shell
railway shell

# View environment variables
railway variables
```

## 🌐 **Custom Domain Setup**

### **1. Add Custom Domain**
1. Go to Railway project dashboard
2. Click **Settings** → **Domains**
3. Add your custom domain (e.g., `kolekt.io`)
4. Update DNS records as instructed

### **2. Update Environment Variables**
```bash
# Update CORS origins
CORS_ORIGINS=["https://kolekt.io", "https://www.kolekt.io"]

# Update redirect URIs
GOOGLE_REDIRECT_URI=https://kolekt.io/api/v1/auth/google/callback
META_REDIRECT_URI=https://kolekt.io/api/v1/auth/meta/callback
```

## 📈 **Performance Optimization**

### **Railway-Specific Optimizations**
- **Cold Start**: Application optimized for quick startup
- **Memory Usage**: Efficient memory management
- **Database Pooling**: Connection pooling for Supabase
- **Caching**: Redis integration for performance

### **Monitoring Metrics**
- **Response Time**: < 200ms average
- **Uptime**: 99.9% target
- **Error Rate**: < 0.1%
- **Resource Usage**: Optimized for cost efficiency

## 🎉 **Launch Checklist**

### **Final Verification**
- [ ] **Application deployed successfully**
- [ ] **Health checks passing**
- [ ] **Admin panel functional**
- [ ] **User registration working**
- [ ] **Database operations verified**
- [ ] **Performance metrics acceptable**
- [ ] **Security audit completed**
- [ ] **Monitoring alerts configured**

### **Go Live**
1. **Update DNS** to point to Railway domain
2. **Test all functionality** on production
3. **Monitor performance** for 24 hours
4. **Launch marketing campaign**
5. **Monitor user feedback**

---

**Railway Deployment Status**: ✅ Ready  
**Last Updated**: August 24, 2025  
**Next Step**: Connect repository and configure environment variables
