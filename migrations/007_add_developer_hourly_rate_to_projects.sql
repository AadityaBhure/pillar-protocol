-- Migration 007: Add developer_hourly_rate to projects
-- Snapshots the developer's hourly rate at project creation time
-- so cost calculations remain accurate even if the developer changes their rate later.

ALTER TABLE projects
ADD COLUMN IF NOT EXISTS developer_hourly_rate NUMERIC(10, 2);
