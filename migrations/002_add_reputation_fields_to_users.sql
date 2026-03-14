-- Migration: Add reputation tracking fields to user_reputation table
-- Feature: payout-reputation-system
-- Task: 1.2 Add reputation fields to users table

-- Add new reputation fields to user_reputation table
ALTER TABLE user_reputation
ADD COLUMN reputation_score DECIMAL(5, 2) NOT NULL DEFAULT 50.00,
ADD COLUMN total_on_time_deliveries INTEGER NOT NULL DEFAULT 0,
ADD COLUMN total_late_deliveries INTEGER NOT NULL DEFAULT 0;

-- Note: reputation_history JSONB field already exists in the table

-- Add CHECK constraint for reputation_score (0-100 range)
ALTER TABLE user_reputation
ADD CONSTRAINT reputation_score_check 
CHECK (reputation_score >= 0 AND reputation_score <= 100);

-- Create index for reputation queries
CREATE INDEX idx_user_reputation_score ON user_reputation(reputation_score);

-- Success message
DO $$
BEGIN
    RAISE NOTICE '==============================================';
    RAISE NOTICE '✅ User reputation fields added!';
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'New fields:';
    RAISE NOTICE '  - reputation_score (DECIMAL(5,2), default 50.00)';
    RAISE NOTICE '  - total_on_time_deliveries (INTEGER, default 0)';
    RAISE NOTICE '  - total_late_deliveries (INTEGER, default 0)';
    RAISE NOTICE 'Constraint: reputation_score must be 0-100';
    RAISE NOTICE 'Index created on reputation_score';
    RAISE NOTICE '==============================================';
END $$;
