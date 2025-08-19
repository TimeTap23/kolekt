-- Reset Tokens Table for Password Reset Functionality
-- Run this in your Supabase SQL Editor

-- Create reset_tokens table
CREATE TABLE IF NOT EXISTS public.reset_tokens (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_reset_tokens_user_id ON public.reset_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_reset_tokens_token_hash ON public.reset_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_reset_tokens_expires_at ON public.reset_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_reset_tokens_used ON public.reset_tokens(used);

-- Add RLS policies
ALTER TABLE public.reset_tokens ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own reset tokens
CREATE POLICY "Users can view own reset tokens" ON public.reset_tokens
    FOR SELECT USING (auth.uid() = user_id);

-- Policy: Users can insert their own reset tokens
CREATE POLICY "Users can insert own reset tokens" ON public.reset_tokens
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own reset tokens
CREATE POLICY "Users can update own reset tokens" ON public.reset_tokens
    FOR UPDATE USING (auth.uid() = user_id);

-- Add password_hash column to profiles table if it doesn't exist
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS password_hash TEXT;
ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Create function to clean up expired tokens (optional)
CREATE OR REPLACE FUNCTION cleanup_expired_reset_tokens()
RETURNS void AS $$
BEGIN
    DELETE FROM public.reset_tokens 
    WHERE expires_at < NOW() OR used = TRUE;
END;
$$ LANGUAGE plpgsql;

-- Create a trigger to automatically clean up expired tokens
CREATE OR REPLACE FUNCTION trigger_cleanup_expired_tokens()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM cleanup_expired_reset_tokens();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger (runs after insert/update)
CREATE TRIGGER cleanup_expired_tokens_trigger
    AFTER INSERT OR UPDATE ON public.reset_tokens
    EXECUTE FUNCTION trigger_cleanup_expired_tokens();

-- Grant necessary permissions
GRANT ALL ON public.reset_tokens TO authenticated;
GRANT ALL ON public.reset_tokens TO service_role;
