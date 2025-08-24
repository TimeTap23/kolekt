-- Database Optimization Scripts for Kolekt
-- Improves query performance through indexing and optimization

-- 1. Create composite indexes for frequently queried tables
CREATE INDEX IF NOT EXISTS idx_profiles_email_role ON profiles(email, role);
CREATE INDEX IF NOT EXISTS idx_profiles_created_at_role ON profiles(created_at DESC, role);
CREATE INDEX IF NOT EXISTS idx_profiles_last_login ON profiles(last_login DESC) WHERE last_login IS NOT NULL;

-- 2. Content-related indexes
CREATE INDEX IF NOT EXISTS idx_content_items_user_id_status ON content_items(user_id, status);
CREATE INDEX IF NOT EXISTS idx_content_items_created_at ON content_items(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_content_items_category_status ON content_items(category, status);

-- 3. Analytics and metrics indexes
CREATE INDEX IF NOT EXISTS idx_engagement_metrics_content_id_date ON engagement_metrics(content_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_engagement_metrics_user_id ON engagement_metrics(user_id, created_at DESC);

-- 4. Social connections indexes
CREATE INDEX IF NOT EXISTS idx_social_connections_user_id_platform ON social_connections(user_id, platform);
CREATE INDEX IF NOT EXISTS idx_social_connections_status ON social_connections(status, created_at DESC);

-- 5. Audit and security indexes
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id_category ON audit_logs(user_id, category, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_security_audit_logs_severity_date ON security_audit_logs(severity, created_at DESC);

-- 6. Rate limiting and API usage indexes
CREATE INDEX IF NOT EXISTS idx_rate_limits_user_id_endpoint ON rate_limits(user_id, endpoint, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_usage_user_id_date ON api_usage(user_id, created_at DESC);

-- 7. Announcements and notifications indexes
CREATE INDEX IF NOT EXISTS idx_announcements_status_date ON announcements(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_notifications_user_id_read ON user_notifications(user_id, read_at, created_at DESC);

-- 8. Partial indexes for better performance
CREATE INDEX IF NOT EXISTS idx_profiles_active_users ON profiles(id) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_content_items_published ON content_items(id) WHERE status = 'published';
CREATE INDEX IF NOT EXISTS idx_social_connections_active ON social_connections(id) WHERE status = 'active';

-- 9. Text search indexes (if using full-text search)
CREATE INDEX IF NOT EXISTS idx_content_items_content_fts ON content_items USING gin(to_tsvector('english', content));
CREATE INDEX IF NOT EXISTS idx_profiles_name_fts ON profiles USING gin(to_tsvector('english', name));

-- 10. Optimize table statistics
ANALYZE profiles;
ANALYZE content_items;
ANALYZE engagement_metrics;
ANALYZE social_connections;
ANALYZE audit_logs;
ANALYZE announcements;

-- 11. Create materialized views for complex queries
CREATE MATERIALIZED VIEW IF NOT EXISTS user_activity_summary AS
SELECT 
    p.id as user_id,
    p.email,
    p.name,
    p.role,
    COUNT(c.id) as total_content,
    COUNT(CASE WHEN c.status = 'published' THEN 1 END) as published_content,
    MAX(c.created_at) as last_content_created,
    MAX(p.last_login) as last_login,
    AVG(em.engagement_rate) as avg_engagement_rate
FROM profiles p
LEFT JOIN content_items c ON p.id = c.user_id
LEFT JOIN engagement_metrics em ON c.id = em.content_id
GROUP BY p.id, p.email, p.name, p.role;

-- Create index on materialized view
CREATE INDEX IF NOT EXISTS idx_user_activity_summary_role ON user_activity_summary(role);
CREATE INDEX IF NOT EXISTS idx_user_activity_summary_last_login ON user_activity_summary(last_login DESC);

-- 12. Create function for refreshing materialized views
CREATE OR REPLACE FUNCTION refresh_user_activity_summary()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY user_activity_summary;
END;
$$ LANGUAGE plpgsql;

-- 13. Create optimized query functions
CREATE OR REPLACE FUNCTION get_user_dashboard_stats(user_id UUID)
RETURNS TABLE(
    total_content BIGINT,
    published_content BIGINT,
    total_engagement BIGINT,
    avg_engagement_rate NUMERIC,
    last_content_date TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(c.id)::BIGINT as total_content,
        COUNT(CASE WHEN c.status = 'published' THEN 1 END)::BIGINT as published_content,
        COALESCE(SUM(em.total_engagement), 0)::BIGINT as total_engagement,
        COALESCE(AVG(em.engagement_rate), 0) as avg_engagement_rate,
        MAX(c.created_at) as last_content_date
    FROM content_items c
    LEFT JOIN engagement_metrics em ON c.id = em.content_id
    WHERE c.user_id = get_user_dashboard_stats.user_id;
END;
$$ LANGUAGE plpgsql STABLE;

-- 14. Create function for admin dashboard stats
CREATE OR REPLACE FUNCTION get_admin_dashboard_stats()
RETURNS TABLE(
    total_users BIGINT,
    active_users BIGINT,
    total_content BIGINT,
    total_engagement BIGINT,
    avg_engagement_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(p.id)::BIGINT as total_users,
        COUNT(CASE WHEN p.last_login > NOW() - INTERVAL '30 days' THEN 1 END)::BIGINT as active_users,
        COUNT(c.id)::BIGINT as total_content,
        COALESCE(SUM(em.total_engagement), 0)::BIGINT as total_engagement,
        COALESCE(AVG(em.engagement_rate), 0) as avg_engagement_rate
    FROM profiles p
    LEFT JOIN content_items c ON p.id = c.user_id
    LEFT JOIN engagement_metrics em ON c.id = em.content_id;
END;
$$ LANGUAGE plpgsql STABLE;

-- 15. Create function for content analytics
CREATE OR REPLACE FUNCTION get_content_analytics(
    start_date TIMESTAMP DEFAULT NOW() - INTERVAL '30 days',
    end_date TIMESTAMP DEFAULT NOW()
)
RETURNS TABLE(
    date DATE,
    total_content BIGINT,
    published_content BIGINT,
    total_engagement BIGINT,
    avg_engagement_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        DATE(c.created_at) as date,
        COUNT(c.id)::BIGINT as total_content,
        COUNT(CASE WHEN c.status = 'published' THEN 1 END)::BIGINT as published_content,
        COALESCE(SUM(em.total_engagement), 0)::BIGINT as total_engagement,
        COALESCE(AVG(em.engagement_rate), 0) as avg_engagement_rate
    FROM content_items c
    LEFT JOIN engagement_metrics em ON c.id = em.content_id
    WHERE c.created_at BETWEEN start_date AND end_date
    GROUP BY DATE(c.created_at)
    ORDER BY date;
END;
$$ LANGUAGE plpgsql STABLE;

-- 16. Create indexes for the new functions
CREATE INDEX IF NOT EXISTS idx_content_items_user_id_created_at ON content_items(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_engagement_metrics_content_id ON engagement_metrics(content_id);

-- 17. Optimize vacuum and maintenance
-- Run these commands periodically:
-- VACUUM ANALYZE profiles;
-- VACUUM ANALYZE content_items;
-- VACUUM ANALYZE engagement_metrics;

-- 18. Create a maintenance function
CREATE OR REPLACE FUNCTION perform_maintenance()
RETURNS void AS $$
BEGIN
    -- Refresh materialized views
    PERFORM refresh_user_activity_summary();
    
    -- Update table statistics
    ANALYZE profiles;
    ANALYZE content_items;
    ANALYZE engagement_metrics;
    ANALYZE social_connections;
    ANALYZE audit_logs;
    
    -- Log maintenance completion
    INSERT INTO audit_logs (category, action, description, created_at)
    VALUES ('system', 'maintenance', 'Database maintenance completed', NOW());
END;
$$ LANGUAGE plpgsql;

-- 19. Create a scheduled job for maintenance (requires pg_cron extension)
-- SELECT cron.schedule('daily-maintenance', '0 2 * * *', 'SELECT perform_maintenance();');

-- 20. Create performance monitoring views
CREATE OR REPLACE VIEW slow_queries AS
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements
WHERE mean_time > 100  -- Queries taking more than 100ms on average
ORDER BY mean_time DESC;

-- 21. Create index usage statistics view
CREATE OR REPLACE VIEW index_usage_stats AS
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- 22. Create table size statistics view
CREATE OR REPLACE VIEW table_sizes AS
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 23. Grant necessary permissions
GRANT EXECUTE ON FUNCTION get_user_dashboard_stats(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION get_admin_dashboard_stats() TO service_role;
GRANT EXECUTE ON FUNCTION get_content_analytics(TIMESTAMP, TIMESTAMP) TO authenticated;
GRANT EXECUTE ON FUNCTION perform_maintenance() TO service_role;

-- 24. Create RLS policies for the new functions
ALTER FUNCTION get_user_dashboard_stats(UUID) SECURITY DEFINER;
ALTER FUNCTION get_admin_dashboard_stats() SECURITY DEFINER;
ALTER FUNCTION get_content_analytics(TIMESTAMP, TIMESTAMP) SECURITY DEFINER;
ALTER FUNCTION perform_maintenance() SECURITY DEFINER;

-- 25. Final optimization commands
-- These should be run after all indexes are created
REINDEX DATABASE kolekt;
ANALYZE;
