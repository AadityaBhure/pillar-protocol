# 🚀 Pillar Protocol

A multi-agent AI platform that orchestrates project planning, escrow management, code inspection, and reputation tracking through four specialized AI agents.

## 🏗️ Architecture

The Pillar Protocol consists of **Four Pillars** (AI Agents):

1. **🏗️ Architect Agent** - Converts vague prompts into structured milestone checklists
2. **💰 Banker Agent** - Manages escrow status with state-based locking
3. **🔍 Inspector Agent** - Analyzes code for logic coverage (not just imports!)
4. **🏆 Bureau Agent** - Calculates PFI (Performance/Financial Index) reputation scores

## ✨ Features

- **AI-Powered Planning**: Transform vague ideas into structured milestones using Gemini AI
- **Smart Code Analysis**: Logic coverage verification ensures functions are actually used
- **State-Based Escrow**: Milestone locking prevents deletion during code review
- **Reputation System**: PFI scoring tracks developer performance over time
- **Beautiful UI**: Terminal-style dashboard with glows and animations
- **Real-time Updates**: Live PFI gauge animation on successful submissions

## 📋 Prerequisites

- Python 3.11+
- Gemini API Key (from Google AI Studio)
- Supabase account (optional - uses mock database if not configured)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

The `.env` file is already configured with your Gemini API key. If you want to use Supabase (optional):

```bash
# Add to .env file
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
```

**Note**: If Supabase is not configured, the system will automatically use an in-memory mock database for testing.

### 3. Start the Server

```bash
python backend/main.py
```

Or using uvicorn directly:

```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`

### 4. Open the Dashboard

Open `index.html` in your browser, or serve it with a simple HTTP server:

```bash
# Python 3
python -m http.server 8080

# Then open http://localhost:8080
```

## 📖 Usage Guide

### Creating a Project

1. Go to the **Create Plan** tab
2. Enter your User ID (e.g., `demo-user-123`)
3. Describe your project idea (e.g., "Build an image processing pipeline with filters")
4. Click **Generate Milestones**
5. The Architect Agent will create structured milestones with requirements

### Submitting Code

1. Go to the **Submit Code** tab
2. Enter the Project ID and Milestone ID (auto-filled from plan creation)
3. Upload your code files (supports .py, .js, .ts, .java, .cpp, .c, .go, .rs)
4. Click **Analyze Code**
5. The Inspector Agent will check for logic coverage
6. If passed, watch the PFI gauge animate!

### Viewing Projects

1. Go to the **View Project** tab
2. Enter a Project ID
3. Click **Load Project**
4. See all milestones with their status (PENDING, LOCKED, RELEASED)
5. Delete unlocked milestones if needed

### Checking Reputation

1. Go to the **Reputation** tab
2. Enter a User ID
3. Click **Load Reputation**
4. View PFI score, submission history, and performance metrics

## 🧪 Testing with Demo Templates

The `templates/` directory contains example code for testing:

### Good Code Example
```bash
# Upload templates/good_code_example.py
# Expected: ✅ PASS with ~100% coverage
```

This demonstrates:
- All functions properly implemented
- Functions both defined AND used
- Real logic, not just stubs

### Bad Code Example
```bash
# Upload templates/bad_code_example.py
# Expected: ❌ FAIL with specific feedback
```

This demonstrates:
- Missing implementations
- Unused functions
- Incomplete logic

See `templates/README.md` for detailed explanations.

## 🔧 API Endpoints

### POST /plan
Create a project with structured milestones

**Request:**
```json
{
  "prompt": "Build an image processing pipeline",
  "user_id": "demo-user-123"
}
```

**Response:**
```json
{
  "project_id": "uuid",
  "milestones": [...]
}
```

### POST /submit
Submit code for inspection

**Request:** multipart/form-data
- `project_id`: string
- `milestone_id`: string
- `files`: file uploads

**Response:**
```json
{
  "passed": true,
  "feedback": "All requirements met!",
  "pfi_score": 87.5
}
```

### GET /project/{project_id}
Retrieve project with all milestones

### DELETE /milestone/{milestone_id}
Delete milestone (only if status is PENDING)

### GET /reputation/{user_id}
Get user reputation and history

## 🎨 UI Features

- **Terminal Aesthetic**: Cyberpunk-inspired design with glows
- **Tab Navigation**: Smooth transitions between sections
- **PFI Gauge**: Animated circular gauge with color coding
  - Green (>80): Excellent
  - Yellow (50-80): Good
  - Red (<50): Needs Improvement
- **Status Badges**: Visual indicators for milestone states
- **Responsive Design**: Works on desktop and tablet

## 🔒 Security Features

- Input sanitization to prevent injection attacks
- File type validation (only code files allowed)
- File size limits (10MB per file, 50MB total)
- Static analysis only (no code execution)
- State-based locking prevents unauthorized deletions

## 🧠 How It Works

### 1. Prompt → Milestones (Architect)
```
User: "Build an image processing pipeline"
↓
Gemini Pro analyzes prompt
↓
Returns structured JSON with milestones
↓
Validated and stored in database
```

### 2. Code → Analysis (Inspector)
```
User uploads code files
↓
Files concatenated with [FILE_START]/[FILE_END] tags
↓
Gemini Flash checks logic coverage
↓
Verifies functions are defined AND used
↓
Returns pass/fail with feedback
```

### 3. Success → PFI (Bureau)
```
Code inspection passes
↓
Calculate performance score (coverage)
↓
Calculate financial score (completion rate)
↓
Combined PFI = 60% performance + 40% financial
↓
Update user reputation
```

### 4. Payment → Release (Banker)
```
Milestone status: PENDING
↓
Code submitted → LOCKED
↓
Inspection passes → RELEASED
↓
x402 payment simulation triggered
```

## 📊 Database Schema

### Projects Table
- id, user_id, title, description
- created_at, updated_at

### Milestones Table
- id, project_id, title, description
- requirements (array), estimated_hours
- status (PENDING/LOCKED/RELEASED/DISPUTED)
- escrow_amount, created_at, submitted_at

### Inspection Results Table
- milestone_id, passed, coverage_score
- feedback, missing_requirements
- analyzed_at, code_blob_hash

### User Reputation Table
- user_id, current_pfi
- total_projects, successful_submissions, failed_submissions
- average_coverage, reputation_history (JSON)
- updated_at

## 🐛 Troubleshooting

### "GEMINI_API_KEY not found"
- Check that `.env` file exists in the project root
- Verify the key is named `GEMINI_API_KEY` or `gemini_api_key`

### "Failed to generate plan"
- Check your Gemini API key is valid
- Ensure you have internet connection
- Try a simpler prompt

### "Cannot delete locked milestone"
- This is expected! Locked milestones cannot be deleted
- Only PENDING milestones can be deleted

### CORS errors in browser
- Make sure the API server is running on port 8000
- Check that `API_BASE_URL` in `script.js` matches your server

## 🚀 Deployment

### Backend (FastAPI)
```bash
# Production server
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Frontend
Serve the static files (index.html, style.css, script.js) with any web server:
- Nginx
- Apache
- Vercel
- Netlify

### Environment Variables
Set these in your production environment:
- `GEMINI_API_KEY`: Your Gemini API key
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase API key

## 📝 License

MIT License - feel free to use this project for learning and development!

## 🙏 Acknowledgments

- Powered by Google Gemini AI
- Built with FastAPI and vanilla JavaScript
- Inspired by the future of AI-assisted development

---

**Built with ⚡ by the Pillar Protocol Team**
