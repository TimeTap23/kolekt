# Local Development Setup for Kolekt

This guide will help you set up Kolekt for local development.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/TimeTap23/kolekt.git
cd kolekt
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Copy the example environment file and configure it:
```bash
cp env.example .env
```

Edit `.env` and add your configuration:
```env
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Authentication
SECRET_KEY=your_secret_key_here
TOKEN_ENCRYPTION_KEY=your_32_character_encryption_key

# Meta/Threads OAuth
META_APP_ID=your_meta_app_id
META_APP_SECRET=your_meta_app_secret
THREADS_APP_ID=your_threads_app_id
THREADS_APP_SECRET=your_threads_app_secret

# AI Services
HUGGINGFACE_TOKEN=your_huggingface_token

# Stripe (optional for local dev)
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
```

### 4. Run the Development Server
```bash
python run_local.py
```

The app will be available at:
- **Main App**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Login Page**: http://localhost:8000/login
- **Register Page**: http://localhost:8000/register
- **Dashboard**: http://localhost:8000/dashboard
- **Pricing**: http://localhost:8000/pricing
- **Formatter**: http://localhost:8000/formatter
- **Templates**: http://localhost:8000/templates
- **Analytics**: http://localhost:8000/analytics

## Features Available Locally

### ✅ Working Features
- **Authentication**: Login/Register pages with proper validation
- **Dashboard**: Main dashboard with navigation
- **Content Formatter**: AI-powered content formatting
- **Templates**: Ready-to-use content templates
- **Analytics**: Performance metrics and insights
- **Pricing**: Subscription plans and credit packs
- **Navigation**: Full navigation between all pages

### 🔧 Development Features
- **Auto-reload**: Server automatically restarts when files change
- **Error logging**: Detailed error messages in console
- **API documentation**: Interactive API docs at `/docs`

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Make sure you're in the correct directory
   - Check that all dependencies are installed: `pip install -r requirements.txt`

2. **Environment Variables**
   - Ensure `.env` file exists and is properly configured
   - Check that all required variables are set

3. **Port Already in Use**
   - Change the port in `run_local.py` if 8000 is occupied
   - Or kill the process using port 8000

4. **Database Connection**
   - Verify your Supabase credentials in `.env`
   - Check that your Supabase project is active

### Getting Help

If you encounter issues:
1. Check the console output for error messages
2. Verify your environment variables
3. Try restarting the development server
4. Check the API documentation at `/docs`

## Next Steps

Once the local server is running:

1. **Test Authentication**: Visit `/register` to create an account
2. **Explore Features**: Navigate through all the pages
3. **Test AI Features**: Try the content formatter with your Hugging Face token
4. **Check API**: Visit `/docs` to see all available endpoints

## Development Workflow

1. Make changes to your code
2. Save the file
3. The server will automatically reload
4. Test your changes in the browser
5. Repeat!

Happy coding! 🚀
