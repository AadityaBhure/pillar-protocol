# 🚀 Deploy to Vercel NOW - Quick Checklist

## ✅ Pre-Deployment Checklist

- [x] `vercel.json` configured (points to `api/index.py`)
- [x] `api/index.py` entry point created
- [x] `requirements.txt` has all dependencies
- [x] `.gitignore` excludes `.env` file
- [x] `.env.example` provided for reference
- [x] Frontend auto-detects environment (local vs production)
- [x] CORS configured for all origins

## 🎯 Deploy in 3 Steps

### Step 1: Push to GitHub (2 minutes)

```bash
# If not already initialized
git init

# Add all files
git add .

# Commit
git commit -m "Ready for Vercel deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Vercel (1 minute)

1. Go to https://vercel.com
2. Click "Add New Project"
3. Import your GitHub repository
4. Click "Deploy" (Vercel auto-detects settings from `vercel.json`)

### Step 3: Add Environment Variables (2 minutes)

In Vercel Dashboard → Your Project → Settings → Environment Variables:

Add these 3 variables:

| Name | Value | Where to get it |
|------|-------|-----------------|
| `SUPABASE_URL` | `https://xxx.supabase.co` | Supabase Dashboard → Project Settings → API |
| `SUPABASE_KEY` | `eyJxxx...` (service_role key) | Supabase Dashboard → Project Settings → API → service_role key |
| `GEMINI_API_KEY` | Your Gemini API key | Google AI Studio |

**After adding variables:** Go to Deployments → Click "..." → Redeploy

## ✅ Verify Deployment

Your app is live at: `https://your-project-name.vercel.app`

Test it:
```bash
# Test health endpoint
curl https://your-project-name.vercel.app/health

# Should return: {"status": "healthy"}
```

## 🎉 Done!

Your app is now live and ready to use!

## 📝 Important Notes

### Local Development
- Start backend: `python -m uvicorn backend.main:app --reload --port 8000`
- Open frontend: `http://localhost:5500` (VS Code Live Server)
- API calls go to: `http://localhost:8000`

### Production (Vercel)
- Everything at: `https://your-project-name.vercel.app`
- API calls use relative URLs (same origin)
- No need to run backend separately

## 🐛 Troubleshooting

### "No fastapi entrypoint found"
✅ Already fixed! `vercel.json` now points to `api/index.py`

### "Module not found"
Check `requirements.txt` has all dependencies

### "Environment variables not working"
1. Add them in Vercel dashboard
2. Redeploy after adding

### Frontend shows errors
1. Check browser console
2. Verify API endpoints are responding
3. Check Vercel deployment logs

## 📚 Full Documentation

See `VERCEL_DEPLOYMENT_GUIDE.md` for detailed information.
