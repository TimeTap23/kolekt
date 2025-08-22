# 🔧 Fixing Supabase Email Domain Restrictions

## 🚨 **Current Issue**
Your Supabase project has **custom email domain validation** that is blocking common email providers like Gmail, Yahoo, and others. This prevents users from registering with their normal email addresses.

**Test Results:**
- ❌ `gmail.com` - BLOCKED
- ❌ `yahoo.com` - BLOCKED  
- ❌ `icloud.com` - BLOCKED
- ❌ `example.com` - BLOCKED
- ✅ `outlook.com` - ALLOWED
- ✅ `hotmail.com` - ALLOWED
- ✅ `aol.com` - ALLOWED

## 📋 **Step-by-Step Fix**

### **1. Access Your Supabase Dashboard**
1. Go to [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Select your project: `cnloucmzugnkwszqdxjl`
3. Navigate to **SQL Editor** in the left sidebar

### **2. Find and Remove Email Domain Restrictions**

#### **Check for Custom Functions**
In the SQL Editor, run this query to find email validation functions:

```sql
SELECT 
    routine_name,
    routine_definition
FROM information_schema.routines 
WHERE routine_type = 'FUNCTION' 
AND routine_definition ILIKE '%email%'
AND routine_definition ILIKE '%domain%';
```

#### **Check for Database Triggers**
Run this query to find triggers that might validate emails:

```sql
SELECT 
    trigger_name,
    event_manipulation,
    action_statement
FROM information_schema.triggers 
WHERE trigger_name ILIKE '%email%'
OR action_statement ILIKE '%email%';
```

#### **Check for RLS Policies**
Run this query to find RLS policies that might restrict emails:

```sql
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE qual ILIKE '%email%'
OR with_check ILIKE '%email%';
```

### **3. Remove Email Domain Validation**

#### **If You Find a Custom Function**
Look for functions with names like:
- `validate_email_domain`
- `check_email_allowed`
- `email_domain_validation`
- `restrict_email_domains`

**Delete the function:**
```sql
DROP FUNCTION IF EXISTS your_email_validation_function_name();
```

#### **If You Find a Trigger**
Look for triggers that validate emails on the `auth.users` table.

**Delete the trigger:**
```sql
DROP TRIGGER IF EXISTS your_email_validation_trigger ON auth.users;
```

#### **If You Find RLS Policies**
Look for policies that restrict email domains.

**Delete the policy:**
```sql
DROP POLICY IF EXISTS your_email_restriction_policy ON auth.users;
```

### **4. Check for Email Validation in Database Functions**

#### **Search for Email Validation Logic**
Run this query to find any SQL that validates email domains:

```sql
SELECT 
    routine_name,
    routine_definition
FROM information_schema.routines 
WHERE routine_definition ILIKE '%gmail.com%'
OR routine_definition ILIKE '%yahoo.com%'
OR routine_definition ILIKE '%icloud.com%'
OR routine_definition ILIKE '%example.com%';
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
