# 🔐 Kolekt Authentication Setup Guide

This guide covers the complete authentication system implementation for Kolekt, including user registration, login, JWT tokens, role-based access control, and security features.

## 📋 **Table of Contents**

1. [Overview](#overview)
2. [Database Setup](#database-setup)
3. [Backend Configuration](#backend-configuration)
4. [Frontend Integration](#frontend-integration)
5. [Security Features](#security-features)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

## 🎯 **Overview**

Kolekt uses a comprehensive authentication system with the following features:

- **Supabase Auth Integration**: Leverages Supabase for user management
- **JWT Tokens**: Secure access and refresh tokens
- **Role-Based Access Control**: User, Pro, Business, and Admin roles
- **Token Refresh**: Automatic token renewal
- **Security Hardening**: Encrypted tokens, audit logging, rate limiting
- **Frontend Integration**: Seamless login/registration UI

## 🗄️ **Database Setup**

### **1. Run Authentication Schema**

Execute the authentication schema in your Supabase database:

```sql
-- Run the complete schema from supabase_schema_auth.sql
-- This creates all necessary tables and security policies
```

### **2. Enable Required Extensions**

Ensure these extensions are enabled in Supabase:

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

### **3. Verify Tables Created**

Check that these tables exist:

- `profiles` - User profiles and roles
- `user_settings` - User preferences
- `refresh_tokens` - JWT refresh tokens
- `user_tokens` - Meta OAuth tokens
- `oauth_states` - OAuth state management
- `api_usage` - Usage tracking
- `access_logs` - Audit trail
- `deletion_logs` - Compliance logs

## ⚙️ **Backend Configuration**

### **1. Environment Variables**

Add these to your `.env` file:

```bash
# Authentication
SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Supabase Auth
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# Email (for password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### **2. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **3. Initialize Services**

The authentication system automatically initializes these services:

- `AuthenticationService` - Core auth functionality
- `SecurityService` - Token encryption/decryption
- `ObservabilityService` - Audit logging
- `RateLimiter` - Rate limiting and spam detection

## 🎨 **Frontend Integration**

### **1. Include Authentication Script**

The authentication JavaScript is automatically loaded:

```html
<script src="/static/js/auth.js"></script>
```

### **2. Authentication Flow**

1. **Initial Load**: Checks for existing tokens
2. **Token Validation**: Verifies token validity
3. **Login/Register**: Shows auth forms if not authenticated
4. **Token Refresh**: Automatically refreshes tokens
5. **UI Updates**: Shows/hides content based on auth state

### **3. User Interface**

The authentication system provides:

- **Login Form**: Email/password authentication
- **Registration Form**: New user signup
- **Profile Management**: Update user info and password
- **Role-Based UI**: Features shown based on user plan
- **Notifications**: Success/error feedback

## 🔒 **Security Features**

### **1. Token Security**

- **JWT Tokens**: Signed with secret key
- **Token Encryption**: Sensitive tokens encrypted at rest
- **Automatic Refresh**: Tokens refreshed before expiration
- **Token Invalidation**: Secure logout with token cleanup

### **2. Role-Based Access Control**

```python
# User roles and permissions
roles = {
    "user": ["read", "write_own", "delete_own"],
    "pro": ["read", "write_own", "delete_own", "bulk_operations"],
    "business": ["read", "write_own", "delete_own", "bulk_operations", "team_access"],
    "admin": ["read", "write", "delete", "manage_all"]
}
```

### **3. Rate Limiting**

- **API Rate Limits**: Per-user, per-endpoint limits
- **Spam Detection**: Content analysis and behavioral monitoring
- **Usage Tracking**: Daily/monthly limits enforcement

### **4. Audit Logging**

All authentication events are logged:

- User registration/login/logout
- Token refresh/revocation
- Profile updates
- Password changes
- Admin actions

## 🧪 **Testing**

### **1. Test User Registration**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123",
    "name": "Test User"
  }'
```

### **2. Test User Login**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

### **3. Test Protected Endpoints**

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### **4. Test Token Refresh**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. Database Connection Errors**

```bash
# Check Supabase connection
python -c "
from src.services.supabase import SupabaseService
import asyncio

async def test():
    supabase = SupabaseService()
    try:
        response = await supabase.table('profiles').select('count').execute()
        print('Database connection successful')
    except Exception as e:
        print(f'Database connection failed: {e}')

asyncio.run(test())
"
```

#### **2. JWT Token Issues**

```bash
# Verify JWT secret is set
echo $SECRET_KEY

# Check token format
python -c "
import jwt
from src.core.config import settings

try:
    token = jwt.encode({'test': 'data'}, settings.SECRET_KEY, algorithm='HS256')
    print('JWT encoding successful')
except Exception as e:
    print(f'JWT encoding failed: {e}')
"
```

#### **3. Frontend Authentication Issues**

Check browser console for errors:

```javascript
// Test authentication state
console.log('Access Token:', localStorage.getItem('kolekt_access_token'));
console.log('User:', localStorage.getItem('kolekt_user'));
```

#### **4. CORS Issues**

Ensure CORS is properly configured in your FastAPI app:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Debug Mode**

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 **API Reference**

### **Authentication Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Register new user |
| `/auth/login` | POST | User login |
| `/auth/refresh` | POST | Refresh access token |
| `/auth/logout` | POST | User logout |
| `/auth/me` | GET | Get current user profile |
| `/auth/profile` | PUT | Update user profile |
| `/auth/change-password` | POST | Change password |
| `/auth/permissions` | GET | Get user permissions |
| `/auth/forgot-password` | POST | Request password reset |
| `/auth/reset-password` | POST | Reset password |

### **Admin Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/admin/users` | GET | List all users (admin only) |
| `/auth/admin/users/{user_id}/role` | PUT | Update user role (admin only) |

## 🚀 **Production Deployment**

### **1. Security Checklist**

- [ ] Change default JWT secret
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up email service
- [ ] Enable rate limiting
- [ ] Configure audit logging
- [ ] Set up monitoring

### **2. Environment Variables**

```bash
# Production environment
export SECRET_KEY="your-production-secret-key"
export ENVIRONMENT="production"
export LOG_LEVEL="INFO"
```

### **3. Database Security**

- Enable Row Level Security (RLS)
- Configure proper database permissions
- Set up automated backups
- Monitor database access

## 📞 **Support**

For authentication issues:

1. Check the logs for error messages
2. Verify environment variables are set correctly
3. Test database connectivity
4. Review browser console for frontend errors
5. Check Supabase dashboard for auth issues

## 🔄 **Updates and Maintenance**

### **Regular Tasks**

- Monitor authentication logs
- Review rate limiting metrics
- Update dependencies regularly
- Rotate JWT secrets periodically
- Clean up expired tokens

### **Security Updates**

- Keep JWT library updated
- Monitor for security advisories
- Update password policies as needed
- Review and update rate limits

---

**Kolekt Authentication System** - Secure, scalable, and production-ready user authentication for your Threads formatting platform.
