# 🌐 Railway Custom Domain Setup for Kolekt

## 🎯 **Quick Setup Guide**

### **Step 1: Add Custom Domain in Railway**

1. **Go to Railway Dashboard**
   - Navigate to your Kolekt project
   - Click **Settings** tab
   - Select **Domains** section

2. **Add Your Domain**
   - Click **"Add Domain"**
   - Enter your domain: `kolekt.io` or `www.kolekt.io`
   - Railway will provide DNS records to configure

### **Step 2: Configure DNS Records**

#### **Option A: Railway-Managed DNS (Recommended)**
```bash
# Railway will automatically manage these records:
# A Record: kolekt.io → Railway IP
# CNAME Record: www.kolekt.io → kolekt.io
# TXT Record: Verification record
```

#### **Option B: External DNS Provider**
If using external DNS (Cloudflare, Route53, etc.):

```bash
# Add these records to your DNS provider:

# A Record
kolekt.io → [Railway IP Address]

# CNAME Record  
www.kolekt.io → kolekt.io

# TXT Record (for verification)
@ → railway-verification=your-verification-code

# Optional: Subdomains
api.kolekt.io → kolekt.io
admin.kolekt.io → kolekt.io
```

### **Step 3: Update Environment Variables**

After domain is active, update these variables in Railway:

```bash
# Update CORS origins
CORS_ORIGINS=["https://kolekt.io", "https://www.kolekt.io"]

# Update redirect URIs for OAuth
GOOGLE_REDIRECT_URI=https://kolekt.io/api/v1/auth/google/callback
META_REDIRECT_URI=https://kolekt.io/api/v1/auth/meta/callback

# Update Supabase site URL
SUPABASE_SITE_URL=https://kolekt.io
```

## 🔧 **Advanced Domain Configuration**

### **Subdomain Setup**

#### **API Subdomain**
```bash
# Add subdomain in Railway
api.kolekt.io

# DNS Record
api.kolekt.io → CNAME → kolekt.io
```

#### **Admin Subdomain**
```bash
# Add subdomain in Railway  
admin.kolekt.io

# DNS Record
admin.kolekt.io → CNAME → kolekt.io
```

### **Multiple Domains**

Railway supports multiple domains per project:

```bash
# Primary domain
kolekt.io

# Alternative domains
kolekt.com
kolekt.app
kolekt.net
```

## 🔒 **SSL/TLS Configuration**

### **Automatic Certificate Management**

Railway automatically handles:
- ✅ **Let's Encrypt certificates**
- ✅ **90-day renewal cycle**
- ✅ **Wildcard certificates** for subdomains
- ✅ **HTTP/2 and HTTP/3** protocols

### **Certificate Status Monitoring**

Check certificate status in Railway dashboard:
- **Valid**: Green checkmark
- **Pending**: Yellow clock icon
- **Expired**: Red X icon

## 📊 **Domain Performance**

### **Railway CDN Benefits**

With custom domains, you get:
- 🌍 **Global CDN** distribution
- ⚡ **Edge caching** for static assets
- 📈 **Automatic optimization**
- 🛡️ **DDoS protection**

### **Performance Metrics**

Monitor in Railway dashboard:
- **Response times** by region
- **Uptime** statistics
- **Error rates** by domain
- **Traffic volume** analytics

## 🔍 **Troubleshooting**

### **Common Issues**

#### **DNS Propagation**
```bash
# Check DNS propagation
dig kolekt.io
nslookup kolekt.io

# Wait up to 48 hours for full propagation
```

#### **SSL Certificate Issues**
```bash
# Check certificate status
openssl s_client -connect kolekt.io:443 -servername kolekt.io

# Verify certificate chain
curl -I https://kolekt.io
```

#### **CORS Errors**
```bash
# Ensure CORS origins include your domain
CORS_ORIGINS=["https://kolekt.io", "https://www.kolekt.io"]
```

### **Debug Commands**

#### **Check Domain Status**
```bash
# Railway CLI
railway domains

# Check specific domain
railway domains:show kolekt.io
```

#### **Test Domain Configuration**
```bash
# Test HTTP response
curl -I https://kolekt.io

# Test health endpoint
curl https://kolekt.io/health

# Test admin panel
curl -I https://kolekt.io/admin
```

## 🎯 **Best Practices**

### **Domain Strategy**

#### **Recommended Setup**
```bash
# Primary domain
kolekt.io (main application)

# Subdomains
www.kolekt.io → kolekt.io (redirect)
api.kolekt.io → API endpoints
admin.kolekt.io → Admin panel
```

#### **SEO Optimization**
- ✅ **Canonical URLs** pointing to primary domain
- ✅ **301 redirects** from www to non-www
- ✅ **SSL certificates** for all domains
- ✅ **Mobile-friendly** responsive design

### **Security Considerations**

#### **Domain Security**
- 🔒 **HSTS headers** for HTTPS enforcement
- 🛡️ **CSP headers** for content security
- 🔐 **Secure cookies** with domain scope
- 🚫 **XSS protection** headers

#### **Monitoring Setup**
- 📊 **Uptime monitoring** for all domains
- 🚨 **SSL certificate** expiration alerts
- 📈 **Performance monitoring** by domain
- 🔍 **Error tracking** and alerting

## 📋 **Domain Setup Checklist**

### **Pre-Setup**
- [ ] **Domain purchased** and active
- [ ] **DNS provider** configured
- [ ] **Railway project** deployed
- [ ] **Environment variables** ready

### **Setup Process**
- [ ] **Add domain** in Railway dashboard
- [ ] **Configure DNS records** correctly
- [ ] **Verify domain ownership**
- [ ] **Wait for SSL certificate** generation
- [ ] **Test domain functionality**

### **Post-Setup**
- [ ] **Update environment variables**
- [ ] **Test all endpoints** on new domain
- [ ] **Configure monitoring** and alerts
- [ ] **Update documentation** and links
- [ ] **Test OAuth flows** with new domain

## 🚀 **Go Live Checklist**

### **Final Verification**
- [ ] **Domain resolves** correctly
- [ ] **SSL certificate** is valid
- [ ] **All endpoints** working
- [ ] **OAuth redirects** configured
- [ ] **Admin panel** accessible
- [ ] **Performance** acceptable
- [ ] **Monitoring** active

### **Launch Steps**
1. **Update DNS** to point to Railway
2. **Wait for propagation** (up to 48 hours)
3. **Verify SSL certificate** is active
4. **Test all functionality** on new domain
5. **Update marketing materials** with new URL
6. **Launch announcement** to users

---

**Railway Custom Domain Status**: ✅ Ready for Setup  
**Last Updated**: August 24, 2025  
**Next Step**: Add domain in Railway dashboard and configure DNS
