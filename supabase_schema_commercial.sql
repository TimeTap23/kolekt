-- ThreadStorm Commercial Database Schema
-- Enhanced version with multi-tenancy and commercial features

-- Create custom types
CREATE TYPE template_category AS ENUM (
    'business', 'tech', 'lifestyle', 'education', 'marketing', 'personal', 'premium'
);

CREATE TYPE draft_status AS ENUM (
    'draft', 'published', 'archived'
);

CREATE TYPE threadstorm_status AS ENUM (
    'draft', 'completed', 'published', 'archived'
);

CREATE TYPE subscription_plan AS ENUM (
    'free', 'pro', 'business', 'enterprise'
);

CREATE TYPE subscription_status AS ENUM (
    'active', 'past_due', 'canceled', 'unpaid', 'trialing'
);

CREATE TYPE payment_status AS ENUM (
    'pending', 'succeeded', 'failed', 'refunded'
);

-- Organizations table (for multi-tenancy)
CREATE TABLE public.organizations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    plan_type subscription_plan DEFAULT 'free',
    subscription_status subscription_status DEFAULT 'active',
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    billing_email VARCHAR(255),
    api_keys JSONB DEFAULT '{}',
    settings JSONB DEFAULT '{}',
    white_label_config JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enhanced profiles table with organization support
CREATE TABLE public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    organization_id UUID REFERENCES public.organizations(id) ON DELETE SET NULL,
    username VARCHAR(50) UNIQUE,
    full_name VARCHAR(100),
    avatar_url TEXT,
    bio TEXT,
    website VARCHAR(255),
    plan_type subscription_plan DEFAULT 'free',
    subscription_status subscription_status DEFAULT 'active',
    stripe_customer_id VARCHAR(255),
    api_quota_used INTEGER DEFAULT 0,
    api_quota_limit INTEGER DEFAULT 10,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enhanced templates table with premium support
CREATE TABLE public.templates (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
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
    is_premium BOOLEAN DEFAULT FALSE,
    price DECIMAL(10,2) DEFAULT 0.00,
    creator_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enhanced drafts table
CREATE TABLE public.drafts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
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

-- Enhanced threadstorms table
CREATE TABLE public.threadstorms (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
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

-- Usage metrics table for analytics and billing
CREATE TABLE public.usage_metrics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    metric_type VARCHAR(50) NOT NULL, -- 'threadstorm', 'api_call', 'template_use', 'storage_used'
    count INTEGER DEFAULT 1,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- API keys table for business users
CREATE TABLE public.api_keys (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    key_hash VARCHAR(255) NOT NULL UNIQUE,
    permissions TEXT[] DEFAULT '{}',
    active BOOLEAN DEFAULT TRUE,
    last_used TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Subscriptions table for detailed subscription tracking
CREATE TABLE public.subscriptions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    stripe_customer_id VARCHAR(255),
    plan_type subscription_plan NOT NULL,
    status subscription_status DEFAULT 'active',
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Payments table for payment history
CREATE TABLE public.payments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    organization_id UUID REFERENCES public.organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    stripe_invoice_id VARCHAR(255),
    amount INTEGER NOT NULL, -- Amount in cents
    currency VARCHAR(3) DEFAULT 'usd',
    status payment_status DEFAULT 'pending',
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Referrals table for viral growth
CREATE TABLE public.referrals (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    code VARCHAR(20) UNIQUE NOT NULL,
    uses INTEGER DEFAULT 0,
    max_uses INTEGER DEFAULT 10,
    rewards JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Referral rewards table
CREATE TABLE public.referral_rewards (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'free_month', 'discount', 'credits'
    description TEXT,
    discount_percent INTEGER DEFAULT 0,
    amount INTEGER DEFAULT 0, -- Amount in cents
    used BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User settings table
CREATE TABLE public.user_settings (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    organization_id UUID REFERENCES public.organizations(id) ON DELETE SET NULL,
    default_tone VARCHAR(50) DEFAULT 'professional',
    default_include_numbering BOOLEAN DEFAULT TRUE,
    auto_save_drafts BOOLEAN DEFAULT TRUE,
    theme VARCHAR(20) DEFAULT 'cyberpunk',
    notifications_enabled BOOLEAN DEFAULT TRUE,
    email_preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_profiles_organization_id ON public.profiles(organization_id);
CREATE INDEX idx_templates_organization_id ON public.templates(organization_id);
CREATE INDEX idx_templates_is_premium ON public.templates(is_premium);
CREATE INDEX idx_drafts_organization_id ON public.drafts(organization_id);
CREATE INDEX idx_threadstorms_organization_id ON public.threadstorms(organization_id);
CREATE INDEX idx_usage_metrics_organization_id ON public.usage_metrics(organization_id);
CREATE INDEX idx_usage_metrics_user_id ON public.usage_metrics(user_id);
CREATE INDEX idx_usage_metrics_created_at ON public.usage_metrics(created_at);
CREATE INDEX idx_api_keys_organization_id ON public.api_keys(organization_id);
CREATE INDEX idx_api_keys_key_hash ON public.api_keys(key_hash);
CREATE INDEX idx_subscriptions_organization_id ON public.subscriptions(organization_id);
CREATE INDEX idx_subscriptions_stripe_subscription_id ON public.subscriptions(stripe_subscription_id);
CREATE INDEX idx_payments_organization_id ON public.payments(organization_id);
CREATE INDEX idx_referrals_code ON public.referrals(code);
CREATE INDEX idx_referral_rewards_user_id ON public.referral_rewards(user_id);

-- Enable Row Level Security
ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.threadstorms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.usage_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.referrals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.referral_rewards ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_settings ENABLE ROW LEVEL SECURITY;

-- RLS Policies for organizations
CREATE POLICY "Users can view their own organization" ON public.organizations
    FOR SELECT USING (auth.uid() IN (
        SELECT user_id FROM public.profiles WHERE organization_id = id
    ));

CREATE POLICY "Users can update their own organization" ON public.organizations
    FOR UPDATE USING (auth.uid() IN (
        SELECT user_id FROM public.profiles WHERE organization_id = id
    ));

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

CREATE POLICY "Users can view their organization templates" ON public.templates
    FOR SELECT USING (organization_id IN (
        SELECT organization_id FROM public.profiles WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can view premium templates if subscribed" ON public.templates
    FOR SELECT USING (
        is_premium = TRUE AND 
        EXISTS (
            SELECT 1 FROM public.profiles 
            WHERE user_id = auth.uid() 
            AND plan_type IN ('pro', 'business', 'enterprise')
        )
    );

CREATE POLICY "Users can create templates in their organization" ON public.templates
    FOR INSERT WITH CHECK (organization_id IN (
        SELECT organization_id FROM public.profiles WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can update their organization templates" ON public.templates
    FOR UPDATE USING (organization_id IN (
        SELECT organization_id FROM public.profiles WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can delete their organization templates" ON public.templates
    FOR DELETE USING (organization_id IN (
        SELECT organization_id FROM public.profiles WHERE user_id = auth.uid()
    ));

-- RLS Policies for usage metrics
CREATE POLICY "Users can view their own usage metrics" ON public.usage_metrics
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can view their organization usage metrics" ON public.usage_metrics
    FOR SELECT USING (organization_id IN (
        SELECT organization_id FROM public.profiles WHERE user_id = auth.uid()
    ));

CREATE POLICY "System can insert usage metrics" ON public.usage_metrics
    FOR INSERT WITH CHECK (true);

-- RLS Policies for API keys
CREATE POLICY "Users can view their own API keys" ON public.api_keys
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can create their own API keys" ON public.api_keys
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own API keys" ON public.api_keys
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can delete their own API keys" ON public.api_keys
    FOR DELETE USING (user_id = auth.uid());

-- Function to update updated_at column
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER update_organizations_updated_at
    BEFORE UPDATE ON public.organizations
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

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

CREATE TRIGGER update_api_keys_updated_at
    BEFORE UPDATE ON public.api_keys
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON public.subscriptions
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_payments_updated_at
    BEFORE UPDATE ON public.payments
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_referrals_updated_at
    BEFORE UPDATE ON public.referrals
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_referral_rewards_updated_at
    BEFORE UPDATE ON public.referral_rewards
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_user_settings_updated_at
    BEFORE UPDATE ON public.user_settings
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Function to handle new user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- Create default organization for the user
    INSERT INTO public.organizations (name, slug, billing_email)
    VALUES (
        COALESCE(NEW.raw_user_meta_data->>'organization_name', 'Personal'),
        COALESCE(NEW.raw_user_meta_data->>'organization_slug', 'personal-' || NEW.id::text),
        NEW.email
    );
    
    -- Create user profile
    INSERT INTO public.profiles (id, organization_id, username, full_name)
    VALUES (
        NEW.id,
        (SELECT id FROM public.organizations WHERE slug = COALESCE(NEW.raw_user_meta_data->>'organization_slug', 'personal-' || NEW.id::text)),
        NEW.raw_user_meta_data->>'username',
        NEW.raw_user_meta_data->>'full_name'
    );
    
    -- Create user settings
    INSERT INTO public.user_settings (id, organization_id)
    VALUES (
        NEW.id,
        (SELECT id FROM public.organizations WHERE slug = COALESCE(NEW.raw_user_meta_data->>'organization_slug', 'personal-' || NEW.id::text))
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile and settings on user signup
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to track usage metrics
CREATE OR REPLACE FUNCTION public.track_usage_metric(
    p_user_id UUID,
    p_metric_type TEXT,
    p_count INTEGER DEFAULT 1,
    p_metadata JSONB DEFAULT '{}'
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO public.usage_metrics (user_id, organization_id, metric_type, count, metadata)
    VALUES (
        p_user_id,
        (SELECT organization_id FROM public.profiles WHERE user_id = p_user_id),
        p_metric_type,
        p_count,
        p_metadata
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Insert default public templates
INSERT INTO public.templates (user_id, name, description, category, content, tone, is_public, is_featured) VALUES
    (NULL, 'Business Threadstorm', 'Professional business content formatted for Threads', 'business', 'Transform your business insights into engaging Threads content. Break down complex ideas into digestible posts that drive engagement and build your professional brand.', 'professional', TRUE, TRUE),
    (NULL, 'Tech Tutorial', 'Step-by-step tech tutorials for Threads', 'tech', 'Share your technical knowledge through engaging Threads. Break down complex concepts into easy-to-follow posts that help others learn and grow.', 'educational', TRUE, TRUE),
    (NULL, 'Lifestyle Tips', 'Engaging lifestyle content for Threads', 'lifestyle', 'Share your lifestyle tips and experiences in an engaging way. Create relatable content that connects with your audience on a personal level.', 'casual', TRUE, TRUE),
    (NULL, 'Marketing Strategy', 'Marketing insights formatted for Threads', 'marketing', 'Share your marketing expertise through compelling Threads. Break down strategies into actionable insights that help others succeed.', 'professional', TRUE, TRUE),
    (NULL, 'Personal Story', 'Personal storytelling for Threads', 'personal', 'Share your personal journey and experiences. Connect with your audience through authentic storytelling that inspires and resonates.', 'casual', TRUE, TRUE);

-- Insert premium templates (only accessible to paid users)
INSERT INTO public.templates (user_id, name, description, category, content, tone, is_public, is_featured, is_premium, price) VALUES
    (NULL, 'Premium Business Case Study', 'Detailed business case study format for Threads', 'business', 'Transform your business case studies into compelling Threads content. Break down complex business scenarios into engaging, educational posts that showcase your expertise and drive engagement.', 'professional', TRUE, TRUE, TRUE, 4.99),
    (NULL, 'Advanced Tech Deep Dive', 'In-depth technical content for Threads', 'tech', 'Share complex technical concepts through engaging Threads. Break down advanced topics into digestible, educational posts that help your audience master new skills.', 'educational', TRUE, TRUE, TRUE, 4.99),
    (NULL, 'Premium Marketing Funnel', 'Complete marketing funnel strategy for Threads', 'marketing', 'Create comprehensive marketing funnel content for Threads. Break down complex marketing strategies into actionable, engaging posts that drive conversions.', 'professional', TRUE, TRUE, TRUE, 4.99);

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated;
