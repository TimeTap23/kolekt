# 🔧 Fixing Supabase Email Domain Restrictions

## 🚨 **Current Issue**
Your Supabase project is blocking common email providers like Gmail, Yahoo, and others. This prevents users from registering with their normal email addresses.

## 📋 **Step-by-Step Fix**

### **1. Access Your Supabase Dashboard**
1. Go to [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Select your project: `cnloucmzugnkwszqdxjl`
3. Navigate to **Authentication** in the left sidebar

### **2. Fix Email Settings**
Go to **Authentication > Settings** and configure:

#### **Email Confirmations (For Testing)**
- ✅ **Enable email confirmations**: `OFF` (temporarily for testing)
- ✅ **Enable email change confirmations**: `OFF`
- ✅ **Enable phone confirmations**: `OFF`
- ✅ **Enable phone change confirmations**: `OFF`

#### **Site URL & Redirect URLs**
- **Site URL**: `http://localhost:8000` (for local development)
- **Redirect URLs**: Add these URLs:
  ```
  http://localhost:8000/auth/callback
  http://localhost:8000/api/v1/auth/callback
  https://your-production-domain.com/auth/callback
  https://your-production-domain.com/api/v1/auth/callback
  ```

### **3. Check Email Domain Restrictions**
Go to **Authentication > Policies** and check:

#### **Email Domain Allowlist**
If you have email domain restrictions:
- **Remove all domain restrictions** or add these common domains:
  ```
  gmail.com
  outlook.com
  hotmail.com
  yahoo.com
  ymail.com
  aol.com
  icloud.com
  me.com
  mac.com
  protonmail.com
  ```

#### **Email Templates**
Go to **Authentication > Email Templates** and verify:
- **Confirm signup** template is configured
- **Invite user** template is configured
- **Magic Link** template is configured

### **4. Check RLS (Row Level Security) Policies**
Go to **Authentication > Policies** and ensure:

#### **Profiles Table Policies**
Make sure you have policies that allow:
- **Insert** for new user registration
- **Select** for user profile access
- **Update** for profile updates

#### **User Settings Table Policies**
Ensure policies allow:
- **Insert** for new user settings
- **Select** for user settings access
- **Update** for settings updates

### **5. Test the Fix**

#### **Test with Gmail**
```bash
curl -s http://localhost:8000/api/v1/auth/register \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@gmail.com","password":"testpass123"}' \
  | jq .
```

#### **Test with Outlook**
```bash
curl -s http://localhost:8000/api/v1/auth/register \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@outlook.com","password":"testpass123"}' \
  | jq .
```

#### **Test with Yahoo**
```bash
curl -s http://localhost:8000/api/v1/auth/register \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@yahoo.com","password":"testpass123"}' \
  | jq .
```

### **6. Production Settings**

For production, you should:

#### **Enable Email Confirmations**
- ✅ **Enable email confirmations**: `ON`
- ✅ **Enable email change confirmations**: `ON`

#### **Update Site URL**
- **Site URL**: `https://your-production-domain.com`

#### **Add Production Redirect URLs**
```
https://your-production-domain.com/auth/callback
https://your-production-domain.com/api/v1/auth/callback
```

### **7. Google OAuth Integration**

Since you mentioned Google OAuth, ensure:

#### **Google OAuth Settings**
1. Go to **Authentication > Providers**
2. Enable **Google** provider
3. Add your Google OAuth credentials:
   - **Client ID**: Your Google OAuth client ID
   - **Client Secret**: Your Google OAuth client secret
4. Add redirect URLs:
   ```
   http://localhost:8000/api/v1/auth/google/callback
   https://your-production-domain.com/api/v1/auth/google/callback
   ```

#### **Google Cloud Console Settings**
In your Google Cloud Console project:
- **Authorized JavaScript origins**:
  ```
  http://localhost:8000
  https://your-production-domain.com
  ```
- **Authorized redirect URIs**:
  ```
  http://localhost:8000/api/v1/auth/google/callback
  https://your-production-domain.com/api/v1/auth/google/callback
  ```

## 🔍 **Troubleshooting**

### **If Registration Still Fails**
1. **Check server logs** for specific error messages
2. **Verify Supabase keys** are correct
3. **Ensure tables exist** with correct schema
4. **Check RLS policies** allow the operations

### **Common Error Messages**
- `"Email address is invalid"` → Check domain restrictions
- `"Foreign key constraint violation"` → Check table relationships
- `"RLS policy violation"` → Check security policies
- `"duplicate key value"` → Profile already exists (fixed in code)

### **If Google OAuth Fails**
1. **Verify OAuth credentials** in Google Cloud Console
2. **Check redirect URIs** match exactly
3. **Ensure OAuth consent screen** is configured
4. **Verify scopes** include email and profile

## 📝 **Next Steps**

1. **Apply the settings above** in your Supabase dashboard
2. **Test registration** with common email providers
3. **Test Google OAuth** integration
4. **Deploy to production** with proper email confirmations enabled
5. **Monitor registration success** in your application logs

## 🔗 **Useful Links**

- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [Supabase Auth Settings](https://supabase.com/docs/guides/auth/auth-settings)
- [Supabase Email Templates](https://supabase.com/docs/guides/auth/auth-email-templates)
- [Supabase OAuth Providers](https://supabase.com/docs/guides/auth/auth-oauth)
- [Google OAuth Setup](https://developers.google.com/identity/protocols/oauth2)
