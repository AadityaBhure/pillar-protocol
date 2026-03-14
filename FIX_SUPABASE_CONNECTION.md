# Fix Supabase Connection Issue

## Problem
Data is not being saved to Supabase because:
1. The `supabase` Python package was not installed
2. The API key in `.env` is incorrect (using `sb_secret_` instead of service_role JWT)

## Solution

### Step 1: Install Supabase Package ✅ DONE
```bash
pip install supabase==2.10.0
```

### Step 2: Get the Correct API Key

**CRITICAL:** You need the **service_role** key, not the secret key!

1. Go to https://supabase.com/dashboard
2. Sign in and select your project
3. Go to **Settings** → **API** (in the left sidebar)
4. Scroll down to **Project API keys**
5. Find the **service_role** key (NOT the anon key)
6. Click the eye icon to reveal it
7. Copy the entire key (it's very long, starts with `eyJ`)

### Step 3: Update .env File

Replace the current `SUPABASE_KEY` in your `.env` file:

**Current (WRONG):**
```env
SUPABASE_KEY=sb_secret_QxGTsPeEbYsYxe3AZSh74A_tvLiczxV
```

**Should be (CORRECT):**
```env
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNkZmx6em16YWNybXVqZGtsbXliIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTYxNjE2MTYxNiwiZXhwIjoxOTMxNzM3NjE2fQ.YOUR_ACTUAL_SERVICE_ROLE_KEY_HERE
```

**Note:** The service_role key is a JWT token that:
- Starts with `eyJ`
- Is very long (200+ characters)
- Has three parts separated by dots (.)
- Looks like: `eyJ...xxx.eyJ...xxx.xxx...xxx`

### Step 4: Create Database Tables

1. Go to Supabase dashboard
2. Click **SQL Editor** in the left sidebar
3. Click **New Query**
4. Copy the entire contents of `supabase_schema.sql` file
5. Paste into the SQL editor
6. Click **Run** to execute

This creates all 4 tables:
- projects
- milestones
- inspection_results
- user_reputation

### Step 5: Restart Server

```bash
python backend/main.py
```

Look for this message:
```
✅ Connected to Supabase database
```

If you see:
```
⚠️  Supabase not available, using mock database
```

Then the API key is still incorrect.

### Step 6: Test Data Persistence

1. Open the UI (http://localhost:8000)
2. Create a project through the chat
3. Finalize the checklist
4. Go to Supabase dashboard → **Table Editor**
5. Click on **projects** table
6. You should see your project data!

## Verification Checklist

- [ ] Supabase package installed (`pip install supabase`)
- [ ] Service role key copied from Supabase dashboard
- [ ] `.env` file updated with correct key (starts with `eyJ`)
- [ ] Database tables created using `supabase_schema.sql`
- [ ] Server restarted
- [ ] Server logs show "✅ Connected to Supabase database"
- [ ] Test project created and visible in Supabase Table Editor

## Common Mistakes

❌ **Using the wrong key:**
- `sb_secret_...` - This is NOT the service role key
- `sb_publishable_...` - This is the publishable key (wrong)
- Anon key - This has limited permissions (wrong)

✅ **Correct key:**
- Service role key - Starts with `eyJ`, very long JWT token

## Why Service Role Key?

The service role key:
- Has full database access
- Bypasses Row Level Security (RLS)
- Required for server-side operations
- Should NEVER be exposed to clients
- Should only be in `.env` file on server

## After Fix

Once connected, all data will persist:
- Projects saved to `projects` table
- Milestones saved to `milestones` table
- Inspection results saved to `inspection_results` table
- User reputation saved to `user_reputation` table

You can view all data in Supabase dashboard → Table Editor.
