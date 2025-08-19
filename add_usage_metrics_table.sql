-- Add usage_metrics table for analytics
CREATE TABLE IF NOT EXISTS public.usage_metrics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    metric_type VARCHAR(50) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for usage_metrics
CREATE INDEX IF NOT EXISTS idx_usage_metrics_user_id ON public.usage_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_metrics_metric_type ON public.usage_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_usage_metrics_created_at ON public.usage_metrics(created_at);

-- RLS Policies for usage_metrics (users can view their own)
DROP POLICY IF EXISTS "Users can view their own usage metrics" ON public.usage_metrics;
CREATE POLICY "Users can view their own usage metrics" ON public.usage_metrics
    FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert their own usage metrics" ON public.usage_metrics;
CREATE POLICY "Users can insert their own usage metrics" ON public.usage_metrics
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Enable RLS
ALTER TABLE public.usage_metrics ENABLE ROW LEVEL SECURITY;

-- Grant permissions
GRANT ALL ON public.usage_metrics TO anon, authenticated;
