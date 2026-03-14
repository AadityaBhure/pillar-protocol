-- Migration: Change estimated_hours from integer to numeric to support decimal values (e.g. 0.5)
ALTER TABLE milestones
ALTER COLUMN estimated_hours TYPE NUMERIC(10,2) USING estimated_hours::NUMERIC(10,2);
