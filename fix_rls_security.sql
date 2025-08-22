-- 🔒 CRITICAL SECURITY FIX: Enable RLS on all public tables
-- This script fixes the security vulnerabilities identified by Supabase

-- ==================================================
-- 1. ENABLE RLS ON ALL PUBLIC TABLES
-- ==================================================

-- Enable RLS on content_sources table
ALTER TABLE public.content_sources ENABLE ROW LEVEL SECURITY;

-- Enable RLS on content_items table
ALTER TABLE public.content_items ENABLE ROW LEVEL SECURITY;

-- Enable RLS on content_embeddings table
ALTER TABLE public.content_embeddings ENABLE ROW LEVEL SECURITY;

-- Enable RLS on post_schedules table
ALTER TABLE public.post_schedules ENABLE ROW LEVEL SECURITY;

-- Enable RLS on channel_posts table
ALTER TABLE public.channel_posts ENABLE ROW LEVEL SECURITY;

-- Enable RLS on review_queue table
ALTER TABLE public.review_queue ENABLE ROW LEVEL SECURITY;

-- Enable RLS on channel_drafts table
ALTER TABLE public.channel_drafts ENABLE ROW LEVEL SECURITY;

-- Enable RLS on engagement_metrics table
ALTER TABLE public.engagement_metrics ENABLE ROW LEVEL SECURITY;

-- Enable RLS on social_connections table
ALTER TABLE public.social_connections ENABLE ROW LEVEL SECURITY;

-- ==================================================
-- 2. CREATE SECURITY POLICIES FOR EACH TABLE
-- ==================================================

-- Content Sources Policies
CREATE POLICY "Users can view their own content sources" ON public.content_sources
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own content sources" ON public.content_sources
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own content sources" ON public.content_sources
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own content sources" ON public.content_sources
    FOR DELETE USING (auth.uid() = user_id);

-- Content Items Policies
CREATE POLICY "Users can view their own content items" ON public.content_items
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own content items" ON public.content_items
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own content items" ON public.content_items
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own content items" ON public.content_items
    FOR DELETE USING (auth.uid() = user_id);

-- Content Embeddings Policies
CREATE POLICY "Users can view their own content embeddings" ON public.content_embeddings
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own content embeddings" ON public.content_embeddings
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own content embeddings" ON public.content_embeddings
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own content embeddings" ON public.content_embeddings
    FOR DELETE USING (auth.uid() = user_id);

-- Post Schedules Policies
CREATE POLICY "Users can view their own post schedules" ON public.post_schedules
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own post schedules" ON public.post_schedules
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own post schedules" ON public.post_schedules
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own post schedules" ON public.post_schedules
    FOR DELETE USING (auth.uid() = user_id);

-- Channel Posts Policies
CREATE POLICY "Users can view their own channel posts" ON public.channel_posts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own channel posts" ON public.channel_posts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own channel posts" ON public.channel_posts
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own channel posts" ON public.channel_posts
    FOR DELETE USING (auth.uid() = user_id);

-- Review Queue Policies
CREATE POLICY "Users can view their own review queue items" ON public.review_queue
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own review queue items" ON public.review_queue
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own review queue items" ON public.review_queue
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own review queue items" ON public.review_queue
    FOR DELETE USING (auth.uid() = user_id);

-- Channel Drafts Policies
CREATE POLICY "Users can view their own channel drafts" ON public.channel_drafts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own channel drafts" ON public.channel_drafts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own channel drafts" ON public.channel_drafts
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own channel drafts" ON public.channel_drafts
    FOR DELETE USING (auth.uid() = user_id);

-- Engagement Metrics Policies
CREATE POLICY "Users can view their own engagement metrics" ON public.engagement_metrics
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own engagement metrics" ON public.engagement_metrics
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own engagement metrics" ON public.engagement_metrics
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own engagement metrics" ON public.engagement_metrics
    FOR DELETE USING (auth.uid() = user_id);

-- Social Connections Policies
CREATE POLICY "Users can view their own social connections" ON public.social_connections
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own social connections" ON public.social_connections
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own social connections" ON public.social_connections
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own social connections" ON public.social_connections
    FOR DELETE USING (auth.uid() = user_id);

-- ==================================================
-- 3. ADMIN POLICIES FOR SERVICE ROLE ACCESS
-- ==================================================

-- Allow service role to access all tables (for admin operations)
CREATE POLICY "Service role can access all content_sources" ON public.content_sources
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can access all content_items" ON public.content_items
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can access all content_embeddings" ON public.content_embeddings
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can access all post_schedules" ON public.post_schedules
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can access all channel_posts" ON public.channel_posts
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can access all review_queue" ON public.review_queue
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can access all channel_drafts" ON public.channel_drafts
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can access all engagement_metrics" ON public.engagement_metrics
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can access all social_connections" ON public.social_connections
    FOR ALL USING (auth.role() = 'service_role');

-- ==================================================
-- 4. VERIFICATION QUERIES
-- ==================================================

-- Check which tables have RLS enabled
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename IN (
        'content_sources',
        'content_items', 
        'content_embeddings',
        'post_schedules',
        'channel_posts',
        'review_queue',
        'channel_drafts',
        'engagement_metrics',
        'social_connections'
    );

-- Check policies on each table
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
WHERE schemaname = 'public'
    AND tablename IN (
        'content_sources',
        'content_items', 
        'content_embeddings',
        'post_schedules',
        'channel_posts',
        'review_queue',
        'channel_drafts',
        'engagement_metrics',
        'social_connections'
    );
