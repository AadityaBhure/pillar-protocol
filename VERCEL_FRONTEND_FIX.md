# ✅ Vercel Frontend Fix - Serving HTML/CSS/JS

## Problem
When deploying to Vercel, the API works (`{"status":"ok"}`) but the frontend (index.html) doesn't load.

## Solution
Updated `backend/main.py` to serve static files (HTML, CSS, JS) directly from FastAPI.

## What Changed

### Added File Serving Endpoints

```python
@app.get("/")
async def root():
    """Serve the main HTML page"""
    index_path = os.path.join(BASE_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"status": "ok", "message": "Pillar Protocol API is running"}

@app.get("/script.js")
async def serve_script():
    """Serve the JavaScript file"""
    script_path = os.path.join(BASE_DIR, "script.js")
    if os.path.exists(script_path):
        return FileResponse(script_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="Script not found")

@app.get("/style.css")
async def serve_style():
    """Serve the CSS file"""
    style_path = os.path.join(BASE_DIR, "style.css")
    if os.path.exists(style_path):
        return FileResponse(style_path, media_type="text/css")
    raise HTTPException(status_code=404, detail="Style not found")
```

## How It Works

1. **Root URL (`/`)**: Serves `index.html`
2. **`/script.js`**: Serves JavaScript file
3. **`/style.css`**: Serves CSS file
4. **`/health`**: API health check endpoint
5. **All other routes**: API endpoints (`/plan`, `/submit`, etc.)

## Testing Locally

```bash
# Start backend
python -m uvicorn backend.main:app --reload --port 8000

# Test in browser
# Open: http://localhost:8000
# Should show the full Pillar Protocol UI
```

## Deploy to Vercel

```bash
# Commit changes
git add backend/main.py
git commit -m "Add static file serving for frontend"
git push origin main

# Vercel will automatically redeploy
```

## Verify Deployment

After deploying:

1. **Visit your Vercel URL**: `https://your-app.vercel.app`
2. **Should see**: Full Pillar Protocol UI (not just JSON)
3. **Test API**: `https://your-app.vercel.app/health` (should return JSON)

## File Structure

```
https://your-app.vercel.app/
├── /                    → index.html (Frontend UI)
├── /script.js           → JavaScript file
├── /style.css           → CSS file
├── /health              → API health check
├── /plan                → API endpoint
├── /submit              → API endpoint
└── /chat/architect      → API endpoint
```

## Why This Works

- **Vercel** routes all requests to `api/index.py`
- **`api/index.py`** imports the FastAPI app from `backend/main.py`
- **FastAPI** serves static files (HTML/CSS/JS) for frontend routes
- **FastAPI** handles API requests for `/plan`, `/submit`, etc.
- **Everything** runs from a single entry point

## No Separate Static Hosting Needed

Unlike traditional setups where you need:
- Separate static hosting for frontend
- Separate API hosting for backend
- CORS configuration between them

With this setup:
- ✅ Everything served from same domain
- ✅ No CORS issues
- ✅ Single deployment
- ✅ Simpler configuration

## Next Steps

1. Push changes to GitHub
2. Vercel auto-deploys
3. Visit your Vercel URL
4. Should see full UI!

## Troubleshooting

### Still seeing JSON instead of HTML?
- Clear browser cache (Ctrl+F5)
- Check Vercel deployment logs
- Verify files are in repository root

### CSS/JS not loading?
- Check browser console for 404 errors
- Verify file paths in `index.html`
- Make sure files are committed to git

### API endpoints not working?
- Check environment variables in Vercel
- View function logs in Vercel dashboard
- Test with curl: `curl https://your-app.vercel.app/health`
