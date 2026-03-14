-- Migration: Add deadline tracking fields to milestones table
-- Feature: payout-reputation-system
-- Task: 1.1 Add new fields to milestones table

-- Add new fields to milestones table
ALTER TABLE milestones
ADD COLUMN deadline TIMESTAMP WITH TIME ZONE,
ADD COLUMN submission_time TIMESTAMP WITH TIME ZONE,
ADD COLUMN timeline_status VARCHAR(20);

-- Add CHECK constraint for timeline_status
ALTER TABLE milestones
ADD CONSTRAINT timeline_status_check 
CHECK (timeline_status IN ('on-time', 'late') OR timeline_status IS NULL);

-- Create indexes for performance
CREATE INDEX idx_milestones_deadline ON milestones(deadline);
CREATE INDEX idx_milestones_timeline_status ON milestones(timeline_status);

-- Success message
DO $$
BEGIN
    RAISE NOTICE '==============================================';
    RAISE NOTICE '✅ Milestone deadline fields added!';
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'New fields:';
    RAISE NOTICE '  - deadline (TIMESTAMP, nullable)';
    RAISE NOTICE '  - submission_time (TIMESTAMP, nullable)';
    RAISE NOTICE '  - timeline_status (VARCHAR(20), nullable)';
    RAISE NOTICE 'Indexes created for deadline and timeline_status';
    RAISE NOTICE '==============================================';
END $$;
