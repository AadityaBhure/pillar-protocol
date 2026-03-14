# How to Get Your Supabase API Key

## The Problem
Your current key `sb_publishable_5o3OSvsq5h8kPtrE0cGJ8Q_kl3AW5tT` is NOT a valid Supabase API key format.

## What You Need
A JWT token that looks like this:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNkZmx6em16YWNybXVqZGtsbXliIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTYxNjE2MTYxNiwiZXhwIjoxOTMxNzM3NjE2fQ.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Notice:
- Starts with `eyJ` (not `sb_`)
- Has three parts separated by dots (.)
- Very long (200+ characters)

## Step-by-Step Instructions

### 1. Open Supabase Dashboard
Go to: https://supabase.com/dashboard

### 2. Select Your Project
Click on your project: `cdflzzmzacrmujdklmyb`

### 3. Go to Settings → API
- Click **Settings** (gear icon) in the left sidebar
- Click **API** in the settings menu

### 4. Find the Keys Section
Scroll down to **Project API keys**

You'll see two keys:

#### Option A: anon (public) key
- Label: "anon public"
- Starts with: `eyJ`
- Use for: Client-side applications
- Permissions: Limited (respects Row Level Security)

#### Option B: service_role (secret) key
- Label: "service_role secret"
- Starts with: `eyJ`
- Use for: Server-side applications (THIS IS WHAT YOU NEED)
- Permissions: Full access (bypasses Row Level Security)

### 5. Copy the service_role Key
1. Find the **service_role** key
2. Click the eye icon to reveal it
3. Click the copy icon to copy the entire key
4. It should be very long (200+ characters)

### 6. Update Your .env File
Replace the current line:
```env
SUPABASE_KEY=sb_publishable_5o3OSvsq5h8kPtrE0cGJ8Q_kl3AW5tT
```

With:
```env
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.YOUR_ACTUAL_KEY_HERE
```

**IMPORTANT:** Paste the ENTIRE key you copied (all 200+ characters)

### 7. Save and Test
1. Save the `.env` file
2. Restart your server:
   ```bash
   python backend/main.py
   ```
3. Look for: `✅ Connected to Supabase database`

## Visual Guide

When you're in Settings → API, you should see something like:

```
Project API keys

anon public
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNkZmx6em16YWNybXVqZGtsbXliIiwicm9sZSI6ImFub24iLCJpYXQiOjE2MTYxNjE2MTYsImV4cCI6MTkzMTczNzYxNn0.xxxxxxxxxx
[Copy icon] [Eye icon]

service_role secret
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNkZmx6em16YWNybXVqZGtsbXliIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTYxNjE2MTYxNiwiZXhwIjoxOTMxNzM3NjE2fQ.xxxxxxxxxx
[Copy icon] [Eye icon]
```

Copy the **service_role secret** key (the second one).

## Why This Matters

The `sb_publishable_` prefix is not a real Supabase key format. It might be:
- A placeholder from documentation
- A corrupted/partial key
- From a different service

Real Supabase keys are JWT tokens that:
- Start with `eyJ`
- Are base64-encoded JSON
- Contain authentication information
- Are validated by Supabase servers

## After You Update

Once you have the correct key:
1. Server will connect to Supabase ✅
2. All projects will be saved to database ✅
3. Milestones will persist ✅
4. You can view data in Supabase Table Editor ✅

## Still Having Issues?

If you still see "Invalid API key" after updating:
1. Make sure you copied the ENTIRE key (no spaces, no line breaks)
2. Make sure it starts with `eyJ`
3. Make sure it has two dots (.) in it
4. Try copying the key again (sometimes copy fails)
5. Check if your Supabase project is active (not paused)
