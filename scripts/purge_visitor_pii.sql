-- Database Cleanup Script: Purge PII from visitor_events table
-- Run this ONCE before deploying to production to ensure GDPR compliance
-- 
-- This script removes any legacy personally identifiable information (PII)
-- that may have been stored before the GDPR compliance fixes

-- WARNING: This will modify existing visitor_events data
-- Backup your database before running this script!

-- Option 1: Complete fresh start (recommended for clean deployment)
-- Deletes all existing visitor events
TRUNCATE TABLE visitor_events;

-- Option 2: Sanitize existing events (if you need to preserve analytics)
-- This removes PII from existing records while keeping metadata
/*
UPDATE visitor_events 
SET 
    username = NULL,  -- Remove any stored usernames
    user_id = NULL,   -- Remove any non-hashed user IDs
    details = '{}'::jsonb  -- Clear details field that may contain PII
WHERE 
    -- Find records with potential PII
    username IS NOT NULL 
    OR details::text LIKE '%username%'
    OR details::text LIKE '%email%'
    OR details::text LIKE '%attempted_username%';
*/

-- Verify cleanup (should return 0 rows)
SELECT 
    event_id, 
    event_type, 
    username, 
    user_id,
    details 
FROM visitor_events 
WHERE 
    username IS NOT NULL 
    OR details::text LIKE '%username%'
    OR details::text LIKE '%email%';

-- Set up automatic 90-day retention policy
-- Run this as a cron job or scheduled task
CREATE OR REPLACE FUNCTION cleanup_old_visitor_events() 
RETURNS void AS $$
BEGIN
    DELETE FROM visitor_events 
    WHERE timestamp < NOW() - INTERVAL '90 days';
    
    RAISE NOTICE 'Deleted visitor events older than 90 days';
END;
$$ LANGUAGE plpgsql;

-- Create index for efficient cleanup
CREATE INDEX IF NOT EXISTS idx_visitor_events_timestamp 
ON visitor_events(timestamp);

-- Optional: Create a scheduled cleanup job (PostgreSQL 10+)
-- Requires pg_cron extension
/*
SELECT cron.schedule(
    'cleanup-visitor-events',
    '0 2 * * *',  -- Run daily at 2 AM
    $$SELECT cleanup_old_visitor_events()$$
);
*/

COMMIT;

-- Summary of changes
SELECT 
    COUNT(*) as total_events,
    COUNT(DISTINCT session_id) as unique_sessions,
    MIN(timestamp) as oldest_event,
    MAX(timestamp) as newest_event,
    COUNT(CASE WHEN username IS NOT NULL THEN 1 END) as events_with_username,
    COUNT(CASE WHEN user_id IS NOT NULL THEN 1 END) as events_with_user_id
FROM visitor_events;
