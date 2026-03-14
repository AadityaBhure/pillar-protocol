# Supabase Database Setup Guide

## Current Configuration

Your `.env` file already contains Supabase credentials:
```
SUPABASE_URL=https://cdflzzmzacrmujdklmyb.supabase.co
SUPABASE_KEY=sb_publishable_5o3OSvsq5h8kPtrE0cGJ8Q_kl3AW5tT
```

## Setup Steps

### 1. Access Supabase Dashboard
1. Go to https://supabase.com/dashboard
2. Sign in to your account
3. Select your project: `cdflzzmzacrmujdklmyb`

### 2. Create Database Tables
1. In the Supabase dashboard, click on **SQL Editor** in the left sidebar
2. Click **New Query**
3. Copy the entire contents of `supabase_schema.sql`
4. Paste into the SQL editor
5. Click **Run** to execute the schema

This will create:
- ✅ `projects` table
- ✅ `milestones` table
- ✅ `inspection_results` table
- ✅ `user_reputation` table
- ✅ Indexes for performance
- ✅ Row Level Security (RLS) policies
- ✅ Triggers for automatic timestamps

### 3. Verify Tables Created
1. Click on **Table Editor** in the left sidebar
2. You should see all 4 tables listed
3. Click on each table to verify the schema

### 4. Get the Correct API Key

**IMPORTANT:** The key in your `.env` appears to be a publishable key. For full database access, you need the **service role key**:

1. In Supabase dashboard, go to **Settings** → **API**
2. Under **Project API keys**, find the **service_role** key (not anon key)
3. Copy the service_role key
4. Update your `.env` file:

```env
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNkZmx6em16YWNybXVqZGtsbXliIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTYxNjE2MTYxNiwiZXhwIjoxOTMxNzM3NjE2fQ.xxxxxxxxxxxxxxxxxxxxx
```

**Note:** The service_role key starts with `eyJ` and is much longer than the publishable key.

### 5. Test the Connection

Restart your FastAPI server:
```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Look for this message in the console:
```
✅ Connected to Supabase database
```

If you see:
```
⚠️  Supabase not available, using mock database
```

Then check:
1. Is the service_role key correct?
2. Is the SUPABASE_URL correct?
3. Are the tables created in Supabase?

## Database Schema Overview

### Projects Table
Stores project metadata and links to user.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | TEXT | User identifier |
| title | TEXT | Project title |
| description | TEXT | Project description |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update time |

### Milestones Table
Stores individual milestones for each project.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| project_id | UUID | Foreign key to projects |
| title | TEXT | Milestone title |
| description | TEXT | Milestone description |
| requirements | JSONB | Array of requirements |
| estimated_hours | INTEGER | Time estimate |
| status | TEXT | PENDING/LOCKED/RELEASED/DISPUTED |
| escrow_amount | NUMERIC | Payment amount |
| created_at | TIMESTAMP | Creation time |
| submitted_at | TIMESTAMP | Submission time |

### Inspection Results Table
Stores code inspection results for each milestone.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| milestone_id | UUID | Foreign key to milestones |
| passed | BOOLEAN | Pass/fail status |
| coverage_score | NUMERIC | Score 0-100 |
| feedback | TEXT | Detailed feedback |
| missing_requirements | JSONB | Array of unmet requirements |
| analyzed_at | TIMESTAMP | Analysis time |
| code_blob_hash | TEXT | SHA256 hash of code |

### User Reputation Table
Tracks developer reputation and history.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | TEXT | User identifier (unique) |
| current_pfi | NUMERIC | Current PFI score 0-100 |
| total_projects | INTEGER | Total projects count |
| successful_submissions | INTEGER | Successful submissions |
| failed_submissions | INTEGER | Failed submissions |
| average_coverage | NUMERIC | Average coverage score |
| reputation_history | JSONB | Array of PFI snapshots |
| updated_at | TIMESTAMP | Last update time |

## Security Features

### Row Level Security (RLS)
All tables have RLS enabled to ensure users can only access their own data.

### Policies
- Users can only view/edit their own projects
- Users can only view/edit milestones of their projects
- Users can only view their own reputation
- System can insert inspection results

### API Keys
- **Anon key**: For client-side operations (limited access)
- **Service role key**: For server-side operations (full access)

## Troubleshooting

### "Supabase not available" Error
1. Check if service_role key is used (not anon/publishable key)
2. Verify SUPABASE_URL is correct
3. Ensure tables are created in Supabase
4. Check network connectivity

### "Permission denied" Errors
1. Verify RLS policies are created
2. Check if using service_role key (bypasses RLS)
3. Ensure user_id matches in requests

### Connection Timeout
1. Check Supabase project is not paused
2. Verify network/firewall settings
3. Try restarting Supabase project

## Data Persistence

All data is now stored in Supabase PostgreSQL database:
- ✅ Projects persist across server restarts
- ✅ Milestones are saved permanently
- ✅ Inspection results are stored
- ✅ User reputation is tracked over time
- ✅ Payment history is maintained

## Backup and Recovery

Supabase automatically backs up your database. To manually export:
1. Go to **Database** → **Backups** in Supabase dashboard
2. Click **Download** to get a SQL dump
3. Store securely for disaster recovery

## Next Steps

After setup:
1. ✅ Verify all tables exist
2. ✅ Test creating a project via the UI
3. ✅ Check data appears in Supabase Table Editor
4. ✅ Test milestone creation and status updates
5. ✅ Verify inspection results are saved
6. ✅ Check reputation tracking works
