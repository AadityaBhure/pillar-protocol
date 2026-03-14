# How to Create Database Tables in Supabase

## The Error
```
Could not find the 'description' column of 'projects' in the schema cache
```

This means the database tables don't exist yet. You need to create them.

## Step-by-Step Instructions

### 1. Open Supabase Dashboard
Go to: https://supabase.com/dashboard

### 2. Select Your Project
Click on your project: `cdflzzmzacrmujdklmyb`

### 3. Open SQL Editor
- Look at the left sidebar
- Click on **SQL Editor** (icon looks like </> or a database)

### 4. Create New Query
- Click the **New Query** button (usually at the top)
- Or click the **+** icon to create a new query

### 5. Copy the Schema
- Open the file `supabase_schema.sql` in your project
- Select ALL the content (Ctrl+A or Cmd+A)
- Copy it (Ctrl+C or Cmd+C)

### 6. Paste into SQL Editor
- Click in the SQL Editor text area
- Paste the schema (Ctrl+V or Cmd+V)
- You should see all the SQL code

### 7. Run the Query
- Click the **Run** button (usually green, at the bottom right)
- Or press Ctrl+Enter (Cmd+Enter on Mac)

### 8. Wait for Completion
You should see messages like:
```
Success. No rows returned
```

And at the bottom:
```
Pillar Protocol database schema created successfully!
Tables created: projects, milestones, inspection_results, user_reputation
Indexes and RLS policies configured
```

### 9. Verify Tables Created
- Click on **Table Editor** in the left sidebar
- You should see 4 tables:
  - ✅ projects
  - ✅ milestones
  - ✅ inspection_results
  - ✅ user_reputation

### 10. Check Table Structure
Click on the **projects** table and verify it has these columns:
- id (UUID)
- user_id (TEXT)
- title (TEXT)
- description (TEXT) ← This is the column that was missing!
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

## After Running the Schema

### Test the Connection
Restart your server:
```bash
python backend/main.py
```

You should see:
```
✅ Connected to Supabase database
```

### Test Creating a Project
1. Open the UI (http://localhost:8000)
2. Go to Planning tab
3. Chat with Architect to create a project
4. Click "Finalize Checklist"
5. It should work without errors!

### Verify Data in Supabase
1. Go back to Supabase dashboard
2. Click **Table Editor** → **projects**
3. You should see your project data!

## Troubleshooting

### "Permission denied" Error
If you see permission errors, make sure you're using the **service_role** key in your `.env` file (not the anon key).

### "Relation already exists" Error
If you see this, it means some tables already exist. You can either:
1. Drop the existing tables first (be careful, this deletes data!)
2. Or modify the schema to use `CREATE TABLE IF NOT EXISTS` (already in the schema)

### Tables Not Showing Up
1. Refresh the page
2. Check if you're in the correct project
3. Try running the schema again

### Still Getting Schema Cache Error
1. Make sure ALL the SQL ran successfully
2. Check for any error messages in the SQL Editor
3. Try refreshing the Supabase schema cache (Settings → API → Reload schema cache)

## Quick Reference

**What the schema creates:**
- 4 tables (projects, milestones, inspection_results, user_reputation)
- Indexes for performance
- Row Level Security (RLS) policies
- Triggers for automatic timestamps
- Foreign key relationships

**Time to complete:** ~30 seconds

**One-time setup:** Yes, you only need to do this once per project
