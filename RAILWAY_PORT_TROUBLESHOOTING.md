# 🔧 Railway Port Listening Issues - Troubleshooting Guide

## 🚨 **Common "Target Port Listening" Errors**

### **Error Messages You Might See:**
- `"Target port listening" failed`
- `"Health check failed"`
- `"Application not responding on port"`
- `"Connection refused"`

## ✅ **Solutions Applied**

### **1. Improved Startup Script (`start.py`)**
- **Robust port handling** with error checking
- **Proper environment variable** parsing
- **Logs directory creation** if missing
- **Better error reporting** and debugging info

### **2. Updated Configuration Files**
- **`railway.json`** - Uses `python start.py`
- **`Procfile`** - Uses `python start.py`
- **`Dockerfile`** - Backup deployment option

### **3. Health Check Integration**
- **`health_check_railway.py`** - Verifies application health
- **Railway health check** configured to `/health` endpoint
- **Multiple retry attempts** for startup

## 🔍 **Debugging Steps**

### **Step 1: Check Railway Logs**
1. **Go to Railway dashboard**
2. **Click on your service**
3. **Check "Deployments" tab**
4. **Look for error messages** in the logs

### **Step 2: Verify Environment Variables**
Make sure these are set in Railway:
```bash
PORT=8000 (Railway sets this automatically)
HOST=0.0.0.0
ENVIRONMENT=production
```

### **Step 3: Check Application Startup**
Look for these log messages:
```
🚂 Railway: Starting Kolekt on 0.0.0.0:8000
🌍 Environment: production
🔗 Host: 0.0.0.0
🚪 Port: 8000
📁 Working directory: /app
🚀 Starting Kolekt application...
```

### **Step 4: Test Health Endpoint**
```bash
# Test locally first
curl http://localhost:8000/health

# Test on Railway (replace with your URL)
curl https://your-app.railway.app/health
```

## 🛠️ **Manual Fixes**

### **Option 1: Force Rebuild**
1. **Go to Railway dashboard**
2. **Click "Deploy" → "Deploy Latest Commit"**
3. **Check "Clear build cache"**
4. **Deploy**

### **Option 2: Update Start Command**
In Railway dashboard:
1. **Go to your service**
2. **Click "Settings"**
3. **Under "Start Command"** enter: `python start.py`
4. **Save and redeploy**

### **Option 3: Use Dockerfile**
1. **Railway will automatically detect** the Dockerfile
2. **Use containerized deployment** instead of Nixpacks
3. **More predictable** environment

## 🔧 **Advanced Troubleshooting**

### **Check Port Binding**
```bash
# In Railway logs, look for:
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### **Verify Application Loading**
Look for these success messages:
```
✅ start_kolekt imports successfully
✅ Admin routes work
✅ AI features enabled
✅ Configuration loaded
```

### **Check for Import Errors**
Common issues:
- **Missing dependencies** in `requirements.txt`
- **Import path issues** with `src/` directory
- **Environment variable** configuration problems

## 📋 **Railway Configuration Checklist**

### **Required Files:**
- [x] `start.py` - Main startup script
- [x] `railway.json` - Railway configuration
- [x] `Procfile` - Process definition
- [x] `Dockerfile` - Backup deployment option
- [x] `requirements.txt` - Python dependencies

### **Environment Variables:**
- [x] `HUGGINGFACE_TOKEN` - AI integration
- [x] `SUPABASE_URL` - Database connection
- [x] `SECRET_KEY` - Application security
- [x] `AI_ENABLED` - AI features toggle

### **Health Check:**
- [x] `/health` endpoint responding
- [x] Returns 200 status code
- [x] JSON response format
- [x] Application status information

## 🚀 **Quick Fix Commands**

### **If Railway is Still Having Issues:**

#### **1. Reset Railway Configuration**
```bash
# Delete and recreate railway.json
rm railway.json
# Create new one with minimal config
```

#### **2. Use Simple Start Command**
In Railway dashboard, set start command to:
```bash
python -c "import os; import uvicorn; port=int(os.getenv('PORT', 8000)); uvicorn.run('start_kolekt:app', host='0.0.0.0', port=port)"
```

#### **3. Force Port Binding**
Add to environment variables:
```bash
PORT=8000
HOST=0.0.0.0
BIND=0.0.0.0:8000
```

## 📞 **Getting Help**

### **If Issues Persist:**
1. **Check Railway status** at https://status.railway.app
2. **Review Railway documentation** for latest changes
3. **Contact Railway support** with deployment logs
4. **Try alternative deployment** (Heroku, Render, etc.)

### **Useful Debugging Commands:**
```bash
# Test local startup
python start.py

# Test health check
python health_check_railway.py

# Check environment
python -c "import os; print('PORT:', os.getenv('PORT')); print('HOST:', os.getenv('HOST'))"
```

## 🎯 **Success Indicators**

### **✅ Application is Working When:**
1. **Railway shows "Deployed"** status
2. **Health check passes** (green status)
3. **Logs show successful startup**
4. **Application responds** to HTTP requests
5. **No port binding errors** in logs

### **🚀 Ready for Production When:**
1. **All endpoints** respond correctly
2. **AI features** are working
3. **Admin panel** is accessible
4. **User authentication** functions
5. **No critical errors** in logs

---

**🔧 If you're still experiencing issues, the improved startup configuration should resolve most Railway port listening problems!**
