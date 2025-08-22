-- Add authentication table for storing passwords
-- This allows us to bypass Supabase Auth when needed

CREATE TABLE IF NOT EXISTS public.user_auth (
    user_id UUID PRIMARY KEY REFERENCES public.profiles(id) ON DELETE CASCADE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add index for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_auth_user_id ON public.user_auth(user_id);

-- Add RLS policies
ALTER TABLE public.user_auth ENABLE ROW LEVEL SECURITY;

-- Only allow users to see their own auth data
CREATE POLICY "Users can view own auth data" ON public.user_auth
    FOR SELECT USING (auth.uid() = user_id);

-- Only allow users to update their own auth data
CREATE POLICY "Users can update own auth data" ON public.user_auth
    FOR UPDATE USING (auth.uid() = user_id);

-- Allow insert for new registrations
CREATE POLICY "Allow insert for registration" ON public.user_auth
    FOR INSERT WITH CHECK (true);
