
# 🔧 Fixing Supabase Authentication Settings

## 🚨 **Current Issue**
Your Supabase project has email domain restrictions that are preventing user registration. The test shows:
- ✅ `test@outlook.com` and `test@kolekt.io` work
- ❌ `test@example.com` and `test@gmail.com` are rejected

## 📋 **Step-by-Step Fix**

### **1. Access Your Supabase Dashboard**
1. Go to [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Select your project: `cnloucmzugnkwszqdxjl`
3. Navigate to **Authentication** in the left sidebar

### **2. Fix Email Settings**
Go to **Authentication > Settings** and configure:

#### **Email Confirmations**
- ✅ **Enable email confirmations**: `OFF` (for testing)
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
- Add allowed domains: `gmail.com`, `outlook.com`, `hotmail.com`, `yahoo.com`
- Or disable domain restrictions entirely for testing

#### **Email Templates**
Go to **Authentication > Email Templates** and verify:
- **Confirm signup** template is configured
- **Invite user** template is configured
- **Magic Link** template is configured

### **4. Test the Fix**

#### **Option A: Test with Working Email**
```bash
curl -s http://localhost:8000/api/v1/auth/register \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@outlook.com","password":"testpass123"}' \
  | jq .
```

#### **Option B: Test with Gmail (after fixing)**
```bash
curl -s http://localhost:8000/api/v1/auth/register \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"test@gmail.com","password":"testpass123"}' \
  | jq .
```

### **5. Production Settings**

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

## 🔍 **Troubleshooting**

### **If Registration Still Fails**
1. Check the server logs for specific error messages
2. Verify your Supabase keys are correct
3. Ensure the `profiles` table exists and has the correct schema
4. Check that RLS (Row Level Security) policies allow inserts

### **Common Error Messages**
- `"Email address is invalid"` → Check domain restrictions
- `"Foreign key constraint violation"` → Check table relationships
- `"RLS policy violation"` → Check security policies

## 📝 **Next Steps**

1. **Apply the settings above** in your Supabase dashboard
2. **Test registration** with a working email domain
3. **Deploy to production** with proper email confirmations enabled
4. **Monitor registration success** in your application logs

## 🔗 **Useful Links**

- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [Supabase Auth Settings](https://supabase.com/docs/guides/auth/auth-settings)
- [Supabase Email Templates](https://supabase.com/docs/guides/auth/auth-email-templates)
