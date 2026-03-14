# Quick Fix: Create Database Tables

## The Problem
Error: `Could not find the 'description' column of 'projects' in the schema cache`

**Cause:** Database tables don't exist in Supabase yet.

## The Solution (5 minutes)

### Step 1: Go to Supabase
https://supabase.com/dashboard → Select project `cdflzzmzacrmujdklmyb`

### Step 2: Open SQL Editor
Left sidebar → Click **SQL Editor**

### Step 3: Run the Schema
1. Click **New Query** button
2. Open `supabase_schema.sql` file in your code editor
3. Copy ALL the content (Ctrl+A, Ctrl+C)
4. Paste into Supabase SQL Editor (Ctrl+V)
5. Click **Run** button (or press Ctrl+Enter)

### Step 4: Verify Success
Look for this message at the bottom:
```
Pillar Protocol database schema created successfully!
```

### Step 5: Check Tables
Left sidebar → Click **Table Editor**

You should see:
- ✅ projects
- ✅ milestones  
- ✅ inspection_results
- ✅ user_reputation

### Step 6: Restart Server
```bash
python backend/main.py
```

### Step 7: Test
Try creating a project again - it should work!

## Done!
Your database is now set up and ready to use.
