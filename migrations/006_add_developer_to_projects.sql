-- Migration 006: Add assigned_developer_id to projects table
-- Run this in Supabase SQL Editor AFTER migration 005

-- Add assigned_developer_id column (references users table)
ALTER TABLE projects
ADD COLUMN IF NOT EXISTS assigned_developer_id UUID REFERENCES users(id) ON DELETE SET NULL;

-- Index for fast developer dashboard queries
CREATE INDEX IF NOT EXISTS idx_projects_developer_id ON projects(assigned_developer_id);
