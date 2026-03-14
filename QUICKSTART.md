# ⚡ Quick Start Guide - Pillar Protocol

Get up and running in 3 minutes!

## Step 1: Install Dependencies (30 seconds)

```bash
pip install -r requirements.txt
```

## Step 2: Start the Backend (10 seconds)

### Windows:
```bash
start.bat
```

### Mac/Linux:
```bash
chmod +x start.sh
./start.sh
```

Or manually:
```bash
python backend/main.py
```

The API will start on `http://localhost:8000`

## Step 3: Open the Dashboard (10 seconds)

### Option A: Direct File Open
Simply open `index.html` in your browser

### Option B: Local Server (Recommended)
In a new terminal:
```bash
python -m http.server 8080
```

Then open `http://localhost:8080` in your browser

## 🎯 Try It Out!

### Test 1: Create a Project (1 minute)

1. Click **Create Plan** tab
2. Enter prompt: `Build an image processing pipeline with grayscale, blur, and resize filters`
3. Click **Generate Milestones**
4. Copy the Project ID and Milestone ID

### Test 2: Submit Good Code (1 minute)

1. Click **Submit Code** tab
2. Paste the Project ID and Milestone ID
3. Upload `templates/good_code_example.py`
4. Click **Analyze Code**
5. Watch the PFI gauge animate! ✨

### Test 3: Submit Bad Code (1 minute)

1. Create another project or use a different milestone
2. Upload `templates/bad_code_example.py`
3. See detailed feedback about what's missing

## 🎨 What You'll See

- **Architect Agent**: Converts your idea into structured milestones
- **Inspector Agent**: Analyzes code for logic coverage
- **PFI Gauge**: Animated reputation score (0-100)
- **Status Badges**: PENDING → LOCKED → RELEASED

## 🔧 Troubleshooting

### Port 8000 already in use?
```bash
# Use a different port
uvicorn backend.main:app --port 8001
```

Then update `API_BASE_URL` in `script.js` to `http://localhost:8001`

### Can't see the dashboard?
Make sure you're serving the HTML file through a web server (not just opening the file directly), or update the CORS settings if needed.

### API errors?
Check that:
1. Backend server is running (`http://localhost:8000` should show `{"status":"ok"}`)
2. `.env` file has your Gemini API key
3. You have internet connection (for Gemini API calls)

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out [templates/README.md](templates/README.md) to understand the demo code
- Explore the API docs at `http://localhost:8000/docs`
- Try creating your own project ideas!

## 🚀 Pro Tips

1. **Save Project IDs**: Copy them to a text file for easy access
2. **Use Demo Templates**: They're perfect for testing the system
3. **Watch the Logs**: The backend terminal shows detailed processing info
4. **Try Different Prompts**: The Architect Agent works with any project idea!

---

**Ready to build? Let's go! 🎉**
