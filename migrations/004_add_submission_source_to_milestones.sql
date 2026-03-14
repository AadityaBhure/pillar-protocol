-- Migration 004: Add submission source columns to milestones table
-- Run this in Supabase SQL Editor

ALTER TABLE milestones
  ADD COLUMN IF NOT EXISTS submission_source TEXT,
  ADD COLUMN IF NOT EXISTS submission_github_url TEXT,
  ADD COLUMN IF NOT EXISTS submission_files JSONB;
