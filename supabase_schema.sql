-- ThreadStorm Supabase Database Schema
-- Run this in your Supabase SQL editor

-- Create custom types
CREATE TYPE template_category AS ENUM (
    'business', 'tech', 'lifestyle', 'education', 'marketing', 'personal'
);

CREATE TYPE draft_status AS ENUM (
    'draft', 'published', 'archived'
);

CREATE TYPE threadstorm_status AS ENUM (
    'draft', 'completed', 'published', 'archived'
);

-- Users table (extends Supabase auth.users)
CREATE TABLE public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    username VARCHAR(50) UNIQUE,
    full_name VARCHAR(100),
    avatar_url TEXT,
    bio TEXT,
    website VARCHAR(255),
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'pro', 'business', 'admin')),
    plan VARCHAR(20) DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'business')),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    last_login TIMESTAMP WITH TIME ZONE,
    login_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Templates table
CREATE TABLE public.templates (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category template_category NOT NULL,
    content TEXT NOT NULL,
    tone VARCHAR(50) DEFAULT 'professional',
    tags TEXT[] DEFAULT '{}',
    usage_count INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Drafts table
CREATE TABLE public.drafts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title VARCHAR(200),
    content TEXT,
    images TEXT[] DEFAULT '{}',
    tone VARCHAR(50) DEFAULT 'professional',
    include_numbering BOOLEAN DEFAULT TRUE,
    status draft_status DEFAULT 'draft',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Threadstorms table (completed threadstorms)
CREATE TABLE public.threadstorms (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title VARCHAR(200),
    original_content TEXT,
    formatted_posts JSONB NOT NULL,
    total_posts INTEGER NOT NULL,
    total_characters INTEGER NOT NULL,
    engagement_score FLOAT,
    suggestions TEXT[] DEFAULT '{}',
    images TEXT[] DEFAULT '{}',
    tone VARCHAR(50),
    include_numbering BOOLEAN DEFAULT TRUE,
    status threadstorm_status DEFAULT 'completed',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User settings table
CREATE TABLE public.user_settings (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    default_tone VARCHAR(50) DEFAULT 'professional',
    default_include_numbering BOOLEAN DEFAULT TRUE,
    auto_save_drafts BOOLEAN DEFAULT TRUE,
    theme VARCHAR(20) DEFAULT 'cyberpunk',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Refresh tokens table
CREATE TABLE public.refresh_tokens (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API usage tracking table
CREATE TABLE public.api_usage (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    endpoint VARCHAR(255) NOT NULL,
    calls_count INTEGER DEFAULT 0,
    last_called TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_templates_user_id ON public.templates(user_id);
CREATE INDEX idx_templates_category ON public.templates(category);
CREATE INDEX idx_templates_is_public ON public.templates(is_public);
CREATE INDEX idx_drafts_user_id ON public.drafts(user_id);
CREATE INDEX idx_drafts_status ON public.drafts(status);
CREATE INDEX idx_threadstorms_user_id ON public.threadstorms(user_id);
CREATE INDEX idx_threadstorms_status ON public.threadstorms(status);
CREATE INDEX idx_threadstorms_created_at ON public.threadstorms(created_at);
CREATE INDEX idx_refresh_tokens_user_id ON public.refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token_hash ON public.refresh_tokens(token_hash);
CREATE INDEX idx_api_usage_user_id ON public.api_usage(user_id);
CREATE INDEX idx_api_usage_endpoint ON public.api_usage(endpoint);

-- Enable Row Level Security
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.threadstorms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.refresh_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_usage ENABLE ROW LEVEL SECURITY;

-- RLS Policies for profiles
CREATE POLICY "Users can view their own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile" ON public.profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- RLS Policies for templates
CREATE POLICY "Users can view public templates" ON public.templates
    FOR SELECT USING (is_public = TRUE);

CREATE POLICY "Users can view their own templates" ON public.templates
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own templates" ON public.templates
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own templates" ON public.templates
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own templates" ON public.templates
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for drafts
CREATE POLICY "Users can view their own drafts" ON public.drafts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own drafts" ON public.drafts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own drafts" ON public.drafts
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own drafts" ON public.drafts
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for threadstorms
CREATE POLICY "Users can view their own threadstorms" ON public.threadstorms
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own threadstorms" ON public.threadstorms
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own threadstorms" ON public.threadstorms
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own threadstorms" ON public.threadstorms
    FOR DELETE USING (auth.uid() = user_id);

-- RLS Policies for user_settings
CREATE POLICY "Users can view their own settings" ON public.user_settings
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own settings" ON public.user_settings
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert their own settings" ON public.user_settings
    FOR INSERT WITH CHECK (auth.uid() = id);

-- RLS Policies for refresh_tokens
CREATE POLICY "Users can manage their own refresh tokens" ON public.refresh_tokens
    FOR ALL USING (auth.uid() = user_id);

-- RLS Policies for api_usage
CREATE POLICY "Users can view their own API usage" ON public.api_usage
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own API usage" ON public.api_usage
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own API usage" ON public.api_usage
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Function to update updated_at column
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_templates_updated_at
    BEFORE UPDATE ON public.templates
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_drafts_updated_at
    BEFORE UPDATE ON public.drafts
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_threadstorms_updated_at
    BEFORE UPDATE ON public.threadstorms
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_user_settings_updated_at
    BEFORE UPDATE ON public.user_settings
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_api_usage_updated_at
    BEFORE UPDATE ON public.api_usage
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Function to handle new user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, name, username, full_name)
    VALUES (NEW.id, NEW.email, COALESCE(NEW.raw_user_meta_data->>'name', NEW.email), NEW.raw_user_meta_data->>'username', NEW.raw_user_meta_data->>'full_name');
    
    INSERT INTO public.user_settings (id)
    VALUES (NEW.id);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile and settings on user signup
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Insert some default public templates
INSERT INTO public.templates (user_id, name, description, category, content, tone, is_public, is_featured) VALUES
    (NULL, 'Business Threadstorm', 'Professional business content formatted for Threads', 'business', 'Transform your business insights into engaging Threads content. Break down complex ideas into digestible posts that drive engagement and build your professional brand.', 'professional', TRUE, TRUE),
    (NULL, 'Tech Tutorial', 'Step-by-step tech tutorials for Threads', 'tech', 'Share your technical knowledge through engaging Threads. Break down complex concepts into easy-to-follow posts that help others learn and grow.', 'educational', TRUE, TRUE),
    (NULL, 'Lifestyle Tips', 'Engaging lifestyle content for Threads', 'lifestyle', 'Share your lifestyle tips and experiences in an engaging way. Create relatable content that connects with your audience on a personal level.', 'casual', TRUE, TRUE),
    (NULL, 'Marketing Strategy', 'Marketing insights formatted for Threads', 'marketing', 'Share your marketing expertise through compelling Threads. Break down strategies into actionable insights that help others succeed.', 'professional', TRUE, TRUE),
    (NULL, 'Personal Story', 'Personal storytelling for Threads', 'personal', 'Share your personal journey and experiences. Connect with your audience through authentic storytelling that inspires and resonates.', 'casual', TRUE, TRUE);

-- User permissions table
CREATE TABLE public.user_permissions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    granted BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, resource, action)
);

-- Create index for user_permissions
CREATE INDEX idx_user_permissions_user_id ON public.user_permissions(user_id);
CREATE INDEX idx_user_permissions_resource ON public.user_permissions(resource);
CREATE INDEX idx_user_permissions_action ON public.user_permissions(action);

-- RLS Policies for user_permissions (users can manage their own)
CREATE POLICY "Users can manage their own permissions" ON public.user_permissions
    FOR ALL USING (auth.uid() = user_id);

-- Create trigger for user_permissions updated_at
CREATE TRIGGER update_user_permissions_updated_at
    BEFORE UPDATE ON public.user_permissions
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Announcements table
CREATE TABLE public.announcements (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'critical')),
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Create index for announcements
CREATE INDEX idx_announcements_is_active ON public.announcements(is_active);
CREATE INDEX idx_announcements_priority ON public.announcements(priority);
CREATE INDEX idx_announcements_created_at ON public.announcements(created_at);

-- RLS Policies for announcements (admin only)
CREATE POLICY "Admins can manage announcements" ON public.announcements
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.profiles 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Create trigger for announcements updated_at
CREATE TRIGGER update_announcements_updated_at
    BEFORE UPDATE ON public.announcements
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Usage metrics table for analytics
CREATE TABLE public.usage_metrics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    metric_type VARCHAR(50) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for usage_metrics
CREATE INDEX idx_usage_metrics_user_id ON public.usage_metrics(user_id);
CREATE INDEX idx_usage_metrics_metric_type ON public.usage_metrics(metric_type);
CREATE INDEX idx_usage_metrics_created_at ON public.usage_metrics(created_at);

-- RLS Policies for usage_metrics (users can view their own)
CREATE POLICY "Users can view their own usage metrics" ON public.usage_metrics
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own usage metrics" ON public.usage_metrics
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated;
