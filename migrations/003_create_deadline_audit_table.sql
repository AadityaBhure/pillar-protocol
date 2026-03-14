-- Migration: Create deadline_audit table for tracking deadline changes
-- Feature: payout-reputation-system
-- Task: 1.3 Create deadline_audit table

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create deadline_audit table
CREATE TABLE deadline_audit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    milestone_id UUID NOT NULL REFERENCES milestones(id) ON DELETE CASCADE,
    old_deadline TIMESTAMP WITH TIME ZONE,
    new_deadline TIMESTAMP WITH TIME ZONE NOT NULL,
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    changed_by TEXT,
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for audit queries
CREATE INDEX idx_deadline_audit_milestone ON deadline_audit(milestone_id);
CREATE INDEX idx_deadline_audit_changed_at ON deadline_audit(changed_at);

-- Success message
DO $$
BEGIN
    RAISE NOTICE '==============================================';
    RAISE NOTICE '✅ Deadline audit table created!';
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Table: deadline_audit';
    RAISE NOTICE 'Fields:';
    RAISE NOTICE '  - id (UUID, primary key)';
    RAISE NOTICE '  - milestone_id (UUID, foreign key)';
    RAISE NOTICE '  - old_deadline (TIMESTAMP, nullable)';
    RAISE NOTICE '  - new_deadline (TIMESTAMP, required)';
    RAISE NOTICE '  - changed_at (TIMESTAMP, required)';
    RAISE NOTICE '  - changed_by (TEXT, nullable)';
    RAISE NOTICE '  - reason (TEXT, nullable)';
    RAISE NOTICE '  - created_at (TIMESTAMP, auto)';
    RAISE NOTICE 'Indexes created on milestone_id and changed_at';
    RAISE NOTICE '==============================================';
END $$;
