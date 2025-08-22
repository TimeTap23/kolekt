# 🔧 Fixing Supabase Site URL for Email Validation

## 🚨 **Root Cause Identified**
Your Supabase project's **Site URL** is set to `localhost` instead of your production domain `kolekt.io`. This is causing email validation to fail because Supabase expects emails to match the configured domain.

## 📋 **Step-by-Step Fix**

### **1. Access Your Supabase Dashboard**
1. Go to [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Select your project: `cnloucmzugnkwszqdxjl`
3. Navigate to **Authentication** in the left sidebar

### **2. Fix Site URL Settings**
Go to **Authentication > Settings** and update:

#### **Site URL (Critical Fix)**
- **Current**: `http://localhost:8000`
- **Change to**: `https://kolekt.io`

#### **Redirect URLs (Add Both)**
Add these URLs to the Redirect URLs list:
```
http://localhost:8000/auth/callback
http://localhost:8000/api/v1/auth/callback
https://kolekt.io/auth/callback
https://kolekt.io/api/v1/auth/callback
```

### **3. Email Settings**
In the same Authentication Settings page:

#### **Email Confirmations**
- **Enable email confirmations**: `OFF` (for testing)
- **Enable email change confirmations**: `OFF`

#### **Email Templates**
- Check that email templates are configured for your domain
- Ensure sender email is set correctly

### **4. Additional Settings to Check**

#### **URL Configuration**
- **Site URL**: `https://kolekt.io`
- **Redirect URLs**: Include both localhost and production URLs
- **Additional Redirect URLs**: Add any other domains you use

#### **Security Settings**
- **Enable email confirmations**: `OFF` (temporarily for testing)
- **Enable phone confirmations**: `OFF`
- **Enable sign up**: `ON`

## 🔍 **Why This Fixes the Issue**

The error "Email address is invalid" occurs because:

1. **Supabase Site URL** is set to `localhost`
2. **Email validation** expects emails to match the configured domain
3. **Gmail, Yahoo, etc.** don't match `localhost` domain
4. **Supabase rejects** these emails as "invalid"

By changing the Site URL to `https://kolekt.io`, Supabase will:
- Accept emails from any domain (gmail.com, yahoo.com, etc.)
- Allow proper user registration
- Enable Google OAuth to work correctly

## 🧪 **Testing After Fix**

### **Test Registration**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@gmail.com","password":"testpass123"}'
```

### **Expected Response**
```json
{
  "success": true,
  "user": {
    "id": "...",
    "email": "test@gmail.com",
    "email_confirmed_at": "..."
  }
}
```

## 🚀 **Production Deployment**

After fixing the Site URL:

1. **Commit your changes** to Git
2. **Push to GitHub** for Digital Ocean deployment
3. **Test registration** on your live site
4. **Verify Google OAuth** works correctly

## 🔧 **Troubleshooting**

### **If Email Validation Still Fails**
1. Check if you have **custom email validation functions**
2. Verify **RLS policies** don't restrict email domains
3. Ensure **no Edge Functions** are blocking emails

### **If OAuth Still Doesn't Work**
1. Update **Google OAuth settings** with correct redirect URLs
2. Verify **Digital Ocean environment variables** are set correctly
3. Check **Supabase Auth logs** for specific errors

## 📝 **Summary**

The key fix is changing your Supabase **Site URL** from `localhost` to `https://kolekt.io`. This will:

- ✅ Allow Gmail, Yahoo, Outlook, and other email providers
- ✅ Enable proper user registration
- ✅ Fix Google OAuth integration
- ✅ Resolve "Email address is invalid" errors

---

**Next Steps:**
1. Update Site URL in Supabase Dashboard
2. Test registration with Gmail address
3. Deploy to production
4. Verify Google OAuth works
