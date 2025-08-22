-- Create centralized_logs table for observability
CREATE TABLE IF NOT EXISTS public.centralized_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    event_type VARCHAR(100) NOT NULL,
    event_category VARCHAR(50),
    message TEXT,
    details JSONB,
    severity VARCHAR(20) DEFAULT 'info',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on centralized_logs
ALTER TABLE public.centralized_logs ENABLE ROW LEVEL SECURITY;

-- Only service role can access centralized_logs
CREATE POLICY IF NOT EXISTS "Service role can access centralized_logs" 
ON public.centralized_logs FOR ALL USING (auth.role() = 'service_role');

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_centralized_logs_event_type ON public.centralized_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_centralized_logs_user_id ON public.centralized_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_centralized_logs_created_at ON public.centralized_logs(created_at);
