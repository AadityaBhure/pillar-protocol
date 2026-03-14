# Vercel Deployment Guide

## Quick Deploy to Vercel

### Step 1: Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Pillar Protocol"

# Add your GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main
```

### Step 2: Deploy to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your GitHub repository
4. Vercel will auto-detect the configuration from `vercel.json`
5. Click "Deploy"

### Step 3: Add Environment Variables

After deployment, go to your project settings and add these environment variables:

**Required Variables:**
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase service_role key (starts with `eyJ`)
- `GEMINI_API_KEY` - Your Google Gemini API key

**How to add:**
1. Go to Project Settings → Environment Variables
2. Add each variable with its value
3. Click "Save"
4. Redeploy the project (Deployments → Click "..." → Redeploy)

### Step 4: Test Your Deployment

Your app will be live at: `https://your-project-name.vercel.app`

Test the API:
```bash
curl https://your-project-name.vercel.app/health
```

## How It Works

### File Structure for Vercel

```
project/
├── api/
│   └── index.py          # Vercel entry point (imports from backend)
├── backend/
│   └── main.py           # Main FastAPI app
├── vercel.json           # Vercel configuration
└── requirements.txt      # Python dependencies
```

### Vercel Configuration (`vercel.json`)

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### Entry Point (`api/index.py`)

This file imports the FastAPI app from `backend/main.py` and exposes it to Vercel:

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.main import app
```

### Frontend Configuration

The frontend (`script.js`) automatically detects the environment:

```javascript
const API_BASE_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8000'  // Local development
    : '';                       // Production (same origin)
```

## Troubleshooting

### Issue: "No fastapi entrypoint found"

**Solution:** Make sure `vercel.json` points to `api/index.py`, not `backend/main.py`

### Issue: "Module not found"

**Solution:** Check that all dependencies are in `requirements.txt`

### Issue: "Environment variables not working"

**Solution:** 
1. Add variables in Vercel dashboard (Project Settings → Environment Variables)
2. Redeploy after adding variables

### Issue: "CORS errors in production"

**Solution:** The app already has CORS configured for all origins. If you still see errors, check browser console for specific issues.

## Local Development vs Production

### Local Development
- Backend runs on `http://localhost:8000`
- Frontend served from `http://localhost:5500` (VS Code Live Server) or `http://localhost:8080` (Python server)
- API calls go to `http://localhost:8000`

### Production (Vercel)
- Everything served from same domain (e.g., `https://your-app.vercel.app`)
- API calls use relative URLs (empty `API_BASE_URL`)
- No CORS issues because same-origin

## Next Steps After Deployment

1. ✅ Test all endpoints
2. ✅ Verify database connection (Supabase)
3. ✅ Test the full workflow (Plan → Payment → Submit)
4. ✅ Monitor logs in Vercel dashboard
5. ✅ Set up custom domain (optional)

## Support

If you encounter issues:
1. Check Vercel deployment logs
2. Check browser console for frontend errors
3. Verify environment variables are set correctly
4. Test API endpoints directly using curl or Postman
