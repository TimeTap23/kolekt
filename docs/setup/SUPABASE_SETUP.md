# Supabase Setup Guide for Kolekt

This guide will help you set up Supabase for Kolekt, enabling user authentication, template storage, draft management, and file storage.

## 🚀 **Step 1: Create a Supabase Project**

1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - **Name**: `kolekt` (or your preferred name)
   - **Database Password**: Create a strong password
   - **Region**: Choose closest to your users
5. Click "Create new project"
6. Wait for the project to be created (usually 1-2 minutes)

## 🗄️ **Step 2: Set Up Database Schema**

1. In your Supabase dashboard, go to **SQL Editor**
2. Copy the entire content from `supabase_schema.sql`
3. Paste it into the SQL editor
4. Click **Run** to execute the schema
5. Verify the tables are created in **Table Editor**

## 🔑 **Step 3: Get Your API Keys**

1. Go to **Settings** → **API** in your Supabase dashboard
2. Copy the following values:
   - **Project URL** (e.g., `https://your-project.supabase.co`)
   - **anon public** key
   - **service_role** key (keep this secret!)
3. Note your database connection string format:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
   ```

## ⚙️ **Step 4: Configure Environment Variables**

Create a `.env` file in your Kolekt project root:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key
DATABASE_URL=postgresql://postgres:your-password@db.your-project-ref.supabase.co:5432/postgres

# Application Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
HOST=127.0.0.1
PORT=8000

# Optional: Redis (for background tasks)
REDIS_URL=redis://localhost:6379/0

# Optional: AI Services
OPENAI_API_KEY=your-openai-key
HUGGINGFACE_API_KEY=your-huggingface-key
```

## 🗂️ **Step 5: Set Up Storage Bucket**

1. Go to **Storage** in your Supabase dashboard
2. Click **Create a new bucket**
3. Name it `kolekt`
4. Set it to **Public** (for easy image access)
5. Click **Create bucket**

## 🔐 **Step 6: Configure Authentication**

1. Go to **Authentication** → **Settings**
2. Configure your site URL (e.g., `http://localhost:8000` for development)
3. Add redirect URLs:
   - `http://localhost:8000/auth/callback`
   - `http://localhost:3000/auth/callback` (if using frontend)
4. Save settings

## 🧪 **Step 7: Test the Setup**

1. Update your `simple_startup.py` with your actual Supabase credentials
2. Run the application:
   ```bash
   python simple_startup.py
   ```
3. Test the API endpoints:
   ```bash
   # Test health check
   curl http://127.0.0.1:8000/health
   
   # Test Supabase templates
   curl http://127.0.0.1:8000/api/v1/templates/
   ```

## 📊 **Step 8: Verify Database Tables**

In your Supabase **Table Editor**, you should see:

- ✅ `profiles` - User profiles
- ✅ `templates` - Threadstorm templates
- ✅ `drafts` - User drafts
- ✅ `kolekts` - Completed kolekts
- ✅ `user_settings` - User preferences

## 🔒 **Step 9: Row Level Security (RLS)**

The schema includes RLS policies that ensure:
- Users can only access their own data
- Public templates are accessible to everyone
- Proper authentication is required for sensitive operations

## 🚀 **Step 10: Production Deployment**

For production:

1. **Update environment variables** with production values
2. **Set up a custom domain** in Supabase
3. **Configure email templates** for authentication
4. **Set up monitoring** and logging
5. **Configure backup policies**

## 🔧 **Troubleshooting**

### Common Issues:

**1. Connection Errors**
- Verify your `DATABASE_URL` format
- Check if your IP is allowed in Supabase

**2. Authentication Issues**
- Ensure redirect URLs are configured correctly
- Check if email confirmation is required

**3. RLS Policy Errors**
- Verify the user is authenticated
- Check if the user has proper permissions

**4. Storage Upload Errors**
- Ensure the bucket exists and is public
- Check file size limits

## 📚 **Next Steps**

Once Supabase is set up, you can:

1. **Implement user authentication** in the frontend
2. **Add template management** features
3. **Create draft saving/loading** functionality
4. **Add file upload** for images
5. **Implement real-time features** using Supabase subscriptions

## 🎯 **Features Enabled**

With Supabase integration, Kolekt now supports:

- ✅ **User Authentication** - Sign up, sign in, profile management
- ✅ **Template Storage** - Save and share kolekt templates
- ✅ **Draft Management** - Save work in progress
- ✅ **File Storage** - Upload and store images
- ✅ **User Settings** - Personalized preferences
- ✅ **Real-time Updates** - Live data synchronization
- ✅ **Row Level Security** - Secure data access
- ✅ **Scalable Infrastructure** - Production-ready database

## 🆘 **Support**

If you encounter issues:

1. Check the [Supabase documentation](https://supabase.com/docs)
2. Review the [Supabase community](https://github.com/supabase/supabase/discussions)
3. Check the Kolekt logs for detailed error messages

---

**🎉 Congratulations!** Your Kolekt application is now powered by Supabase and ready for production use!
