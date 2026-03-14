-- Pillar Protocol Supabase Database Schema
-- Run this in your Supabase SQL Editor to create all required tables
-- IMPORTANT: Using service_role key bypasses RLS, so policies are optional

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if they exist (clean slate)
DROP TABLE IF EXISTS inspection_results CASCADE;
DROP TABLE IF EXISTS milestones CASCADE;
DROP TABLE IF EXISTS user_reputation CASCADE;
DROP TABLE IF EXISTS projects CASCADE;

-- Projects Table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Milestones Table
CREATE TABLE milestones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    requirements JSONB NOT NULL DEFAULT '[]',
    estimated_hours INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    escrow_amount NUMERIC(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    submitted_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT status_check CHECK (status IN ('PENDING', 'LOCKED', 'RELEASED', 'DISPUTED'))
);

-- Inspection Results Table
CREATE TABLE inspection_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    milestone_id UUID NOT NULL REFERENCES milestones(id) ON DELETE CASCADE,
    passed BOOLEAN NOT NULL,
    coverage_score NUMERIC(5, 2) NOT NULL,
    feedback TEXT NOT NULL,
    missing_requirements JSONB DEFAULT '[]',
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    code_blob_hash TEXT NOT NULL,
    CONSTRAINT coverage_check CHECK (coverage_score >= 0 AND coverage_score <= 100)
);

-- User Reputation Table
CREATE TABLE user_reputation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL UNIQUE,
    current_pfi NUMERIC(5, 2) NOT NULL DEFAULT 0,
    total_projects INTEGER NOT NULL DEFAULT 0,
    successful_submissions INTEGER NOT NULL DEFAULT 0,
    failed_submissions INTEGER NOT NULL DEFAULT 0,
    average_coverage NUMERIC(5, 2) NOT NULL DEFAULT 0,
    reputation_history JSONB DEFAULT '[]',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT pfi_check CHECK (current_pfi >= 0 AND current_pfi <= 100)
);

-- Create Indexes for Performance
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_milestones_project_id ON milestones(project_id);
CREATE INDEX idx_milestones_status ON milestones(status);
CREATE INDEX idx_inspection_results_milestone_id ON inspection_results(milestone_id);
CREATE INDEX idx_user_reputation_user_id ON user_reputation(user_id);

-- Create Updated At Trigger Function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add Triggers for Updated At
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_reputation_updated_at BEFORE UPDATE ON user_reputation
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Success message
DO $$
BEGIN
    RAISE NOTICE '==============================================';
    RAISE NOTICE '✅ Pillar Protocol database created!';
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Tables: projects, milestones, inspection_results, user_reputation';
    RAISE NOTICE 'Indexes: Created for performance';
    RAISE NOTICE 'Triggers: Auto-update timestamps';
    RAISE NOTICE 'Ready to use with service_role key!';
    RAISE NOTICE '==============================================';
END $$;
