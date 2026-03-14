# 🚀 GitHub to Vercel Deployment - Complete Guide

## ✅ Your Project is Ready!

All configuration files are in place and verified. Follow these steps to deploy.

---

## 📋 Step-by-Step Deployment

### 1️⃣ Push to GitHub (First Time)

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit - Pillar Protocol ready for deployment"

# Create a new repository on GitHub (github.com/new)
# Then connect it:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 2️⃣ Deploy on Vercel

1. **Go to Vercel**: https://vercel.com
2. **Sign in** with your GitHub account
3. **Click "Add New Project"**
4. **Import your repository**:
   - Select your GitHub repository from the list
   - Click "Import"
5. **Configure Project** (Vercel auto-detects from `vercel.json`):
   - Framework Preset: Other
   - Root Directory: `./`
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
6. **Click "Deploy"**

### 3️⃣ Add Environment Variables

After the first deployment:

1. Go to your project in Vercel
2. Click **Settings** → **Environment Variables**
3. Add these 3 variables:

| Variable Name | Value | Where to Get It |
|--------------|-------|-----------------|
| `SUPABASE_URL` | `https://xxxxx.supabase.co` | Supabase Dashboard → Settings → API → Project URL |
| `SUPABASE_KEY` | `eyJxxx...` | Supabase Dashboard → Settings → API → **service_role** key (not anon!) |
| `GEMINI_API_KEY` | Your API key | Google AI Studio → Get API Key |

4. **Important**: After adding variables, go to **Deployments** → Click **"..."** on latest deployment → **Redeploy**

### 4️⃣ Test Your Deployment

Your app is now live at: `https://your-project-name.vercel.app`

Test it:
```bash
# Test health endpoint
curl https://your-project-name.vercel.app/health

# Expected response:
# {"status":"healthy"}
```

Open in browser: `https://your-project-name.vercel.app`

---

## 🔄 Updating Your Deployment

After making changes:

```bash
# Add changes
git add .

# Commit
git commit -m "Description of changes"

# Push to GitHub
git push

# Vercel automatically redeploys!
```

---

## 🏠 Local Development

### Start Backend
```bash
python -m uvicorn backend.main:app --reload --port 8000
```

### Start Frontend
Open `index.html` with VS Code Live Server (port 5500)

Or use Python:
```bash
python -m http.server 8080
```

### Environment Detection
The app automatically detects:
- **Local**: API calls go to `http://localhost:8000`
- **Production**: API calls use relative URLs (same origin)

---

## 📁 Project Structure

```
project/
├── api/
│   └── index.py          # Vercel entry point
├── backend/
│   ├── main.py           # FastAPI app
│   ├── models.py
│   ├── database.py
│   └── mock_database.py
├── agents/
│   ├── architect.py
│   ├── banker.py
│   ├── inspector.py
│   └── bureau.py
├── utils/
│   └── file_processor.py
├── index.html            # Frontend
├── script.js
├── style.css
├── vercel.json           # Vercel config
├── requirements.txt      # Python deps
├── .env                  # Local env vars (not in git)
└── .env.example          # Template
```

---

## 🐛 Troubleshooting

### Issue: Deployment fails with "No fastapi entrypoint found"
**Solution**: Already fixed! `vercel.json` points to `api/index.py`

### Issue: "Module not found" error
**Solution**: Make sure all dependencies are in `requirements.txt`

### Issue: API returns 500 errors
**Solution**: 
1. Check Vercel logs (Dashboard → Your Project → Deployments → Click deployment → View Function Logs)
2. Verify environment variables are set correctly
3. Make sure you're using `service_role` key, not `anon` key

### Issue: Frontend can't connect to API
**Solution**: 
1. Check browser console for errors
2. Verify the API is responding: `curl https://your-app.vercel.app/health`
3. Check CORS settings in `backend/main.py`

### Issue: Database connection fails
**Solution**:
1. Verify `SUPABASE_URL` and `SUPABASE_KEY` in Vercel environment variables
2. Make sure you're using the **service_role** key (starts with `eyJ`)
3. Check Supabase dashboard to ensure tables exist

---

## 📊 Monitoring

### View Logs
1. Go to Vercel Dashboard
2. Click your project
3. Go to **Deployments**
4. Click on a deployment
5. Click **View Function Logs**

### Check Performance
- Vercel Dashboard → Analytics
- Monitor response times, errors, and usage

---

## 🎯 Quick Reference

| Action | Command |
|--------|---------|
| Run backend locally | `python -m uvicorn backend.main:app --reload --port 8000` |
| Run frontend locally | Open with VS Code Live Server |
| Push to GitHub | `git push` |
| View deployment | `https://your-project-name.vercel.app` |
| View logs | Vercel Dashboard → Deployments → Function Logs |
| Redeploy | Vercel Dashboard → Deployments → Redeploy |

---

## ✅ Deployment Checklist

- [x] `vercel.json` configured
- [x] `api/index.py` entry point created
- [x] All dependencies in `requirements.txt`
- [x] `.env` excluded from git
- [x] Frontend auto-detects environment
- [x] CORS configured
- [ ] Pushed to GitHub
- [ ] Deployed on Vercel
- [ ] Environment variables added
- [ ] Tested production deployment

---

## 🎉 You're All Set!

Your project is fully configured and ready to deploy. Just follow the steps above and you'll be live in minutes!

**Need help?** Check `DEPLOY_NOW.md` or `VERCEL_DEPLOYMENT_GUIDE.md` for more details.
