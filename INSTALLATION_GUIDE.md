# Complete Installation Guide - Pillar Protocol

## All Required Libraries

### Python Backend Libraries

Install all Python dependencies with:
```bash
pip install -r requirements.txt
```

Or install individually:

#### 1. **FastAPI** (v0.115.0)
```bash
pip install fastapi==0.115.0
```
- **Purpose**: Web framework for building the REST API
- **Used for**: All API endpoints (/plan, /submit, /payment, etc.)

#### 2. **Uvicorn** (v0.32.0)
```bash
pip install uvicorn[standard]==0.32.0
```
- **Purpose**: ASGI server to run FastAPI application
- **Used for**: Running the backend server
- **Note**: The `[standard]` includes extra dependencies for better performance

#### 3. **Python-dotenv** (v1.0.1)
```bash
pip install python-dotenv==1.0.1
```
- **Purpose**: Load environment variables from .env file
- **Used for**: Managing API keys and configuration (GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY)

#### 4. **Google Generative AI** (v0.8.3)
```bash
pip install google-generativeai==0.8.3
```
- **Purpose**: Google's Gemini AI SDK
- **Used for**: 
  - Architect Agent (generating milestones)
  - Inspector Agent (analyzing code quality)
  - Chat functionality

#### 5. **Supabase** (v2.10.0)
```bash
pip install supabase==2.10.0
```
- **Purpose**: Supabase Python client
- **Used for**: Database operations (storing projects, milestones, inspection results)
- **Note**: This was added during the Supabase connection fix

#### 6. **Pydantic** (v2.10.3)
```bash
pip install pydantic==2.10.3
```
- **Purpose**: Data validation and settings management
- **Used for**: 
  - API request/response models
  - Data validation (PlanRequest, SubmitResponse, etc.)
  - Type checking

#### 7. **Python-multipart** (v0.0.20)
```bash
pip install python-multipart==0.0.20
```
- **Purpose**: Handle multipart/form-data requests
- **Used for**: File uploads in the /submit endpoint

#### 8. **Pytest** (v8.3.4)
```bash
pip install pytest==8.3.4
```
- **Purpose**: Testing framework
- **Used for**: Unit tests and integration tests

#### 9. **Pytest-asyncio** (v0.24.0)
```bash
pip install pytest-asyncio==0.24.0
```
- **Purpose**: Pytest plugin for async tests
- **Used for**: Testing async FastAPI endpoints

#### 10. **Hypothesis** (v6.122.3)
```bash
pip install hypothesis==6.122.3
```
- **Purpose**: Property-based testing framework
- **Used for**: Generating test cases and edge case testing

---

## Frontend Libraries (CDN - No Installation Required)

The frontend uses CDN links, so no npm/yarn installation needed:

### 1. **Font Awesome** (v6.4.0)
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
```
- **Purpose**: Icon library
- **Used for**: UI icons throughout the application

### 2. **Inter Font** (Google Fonts)
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```
- **Purpose**: Modern sans-serif font
- **Used for**: All text in the UI

---

## Complete Installation Steps

### Step 1: Clone/Setup Project
```bash
# Navigate to your project directory
cd pillar-protocol
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install All Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup Environment Variables
Create a `.env` file with:
```env
GEMINI_API_KEY=your_gemini_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_service_role_key_here
```

### Step 5: Setup Supabase Database
Run the SQL schema:
```bash
# Copy contents of supabase_schema.sql
# Paste into Supabase SQL Editor
# Execute the queries
```

### Step 6: Start the Backend
```bash
# Windows
start.bat

# Linux/Mac
./start.sh

# Or manually
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 7: Open Frontend
Open `index.html` in your browser or use a local server:
```bash
# Using Python's built-in server
python -m http.server 8080

# Then open http://localhost:8080
```

---

## Verification

### Check Python Installation
```bash
python --version  # Should be 3.8+
pip --version
```

### Check Installed Packages
```bash
pip list
```

Should show all packages from requirements.txt

### Test Backend
```bash
# Start backend
uvicorn backend.main:app --reload

# In another terminal, test health endpoint
curl http://localhost:8000/
# Should return: {"status":"ok","message":"Pillar Protocol API is running"}
```

### Test Frontend
Open `http://localhost:8080` (or wherever you're serving index.html)
- Should see the Pillar Protocol UI
- Chat with Architect Agent should work
- All tabs should be accessible

---

## Troubleshooting

### "Module not found" errors
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

### Supabase connection issues
```bash
# Verify supabase is installed
pip show supabase

# Should show version 2.10.0
# If not, install it:
pip install supabase==2.10.0
```

### GEMINI_API_KEY not found
```bash
# Check .env file exists
# Check GEMINI_API_KEY is set
# Restart the backend after adding .env
```

### Port already in use
```bash
# Use a different port
uvicorn backend.main:app --reload --port 8001
```

---

## Dependencies Summary

| Library | Version | Category | Critical? |
|---------|---------|----------|-----------|
| fastapi | 0.115.0 | Backend | ✅ Yes |
| uvicorn | 0.32.0 | Backend | ✅ Yes |
| python-dotenv | 1.0.1 | Config | ✅ Yes |
| google-generativeai | 0.8.3 | AI | ✅ Yes |
| supabase | 2.10.0 | Database | ✅ Yes |
| pydantic | 2.10.3 | Validation | ✅ Yes |
| python-multipart | 0.0.20 | File Upload | ✅ Yes |
| pytest | 8.3.4 | Testing | ⚠️ Optional |
| pytest-asyncio | 0.24.0 | Testing | ⚠️ Optional |
| hypothesis | 6.122.3 | Testing | ⚠️ Optional |

---

## Quick Start (TL;DR)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file with your API keys
# GEMINI_API_KEY=...
# SUPABASE_URL=...
# SUPABASE_KEY=...

# 3. Run backend
uvicorn backend.main:app --reload

# 4. Open index.html in browser
```

Done! 🚀
