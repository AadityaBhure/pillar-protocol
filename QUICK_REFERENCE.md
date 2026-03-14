# Quick Reference Guide

## 🚀 Getting Started

### 1. Setup Supabase Database
```bash
# Follow SUPABASE_SETUP.md
1. Go to Supabase dashboard
2. Run supabase_schema.sql in SQL Editor
3. Get service_role key from Settings → API
4. Update .env with service_role key
```

### 2. Start the Server
```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Open the UI
```
http://localhost:8000
# Or open index.html directly
```

## 📋 Key Features

### Interactive Chat Planning
- Chat with Architect Agent to refine milestones
- Typing indicator shows AI is thinking
- Toast notifications instead of alerts
- Developer-focused, code-verifiable requirements

### Payment Flow
- Mock payment gateway with test card
- Auto-fills: `4532 1234 5678 9010`
- 2-second processing simulation
- Transaction ID generation

### Code Submission
- **Upload Files**: Choose local files
- **GitHub Fetch**: Enter repo URL and fetch automatically
- Supports: .py, .js, .ts, .java, .cpp, .c, .go, .rs

### Verification
- Inspector Agent checks code against checklist
- Looks for specific functions, classes, endpoints
- Verifies actual implementation (not just imports)
- Generates detailed pass/fail report

## 🔑 Environment Variables

```env
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Supabase (use service_role key, not anon/publishable)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 📊 Database Tables

| Table | Purpose |
|-------|---------|
| `projects` | Project metadata |
| `milestones` | Individual milestones |
| `inspection_results` | Code review results |
| `user_reputation` | Developer PFI scores |

## 🎯 Developer-Focused Requirements

### ✅ Good Examples
```
"Create POST /api/login endpoint returning JWT token"
"Implement User model with email, password_hash fields"
"Add bcrypt password hashing with salt rounds >= 10"
"Create authentication middleware to verify JWT"
```

### ❌ Bad Examples
```
"User-friendly interface" (not verifiable)
"Good performance" (too vague)
"Secure system" (not specific)
"Easy to use" (subjective)
```

## 🔄 Typical Workflow

1. **Plan**: Chat with Architect Agent
   - Describe project idea
   - Refine milestones through conversation
   - Get developer-focused checklist

2. **Finalize**: Lock in the plan
   - Click "Finalize Checklist"
   - Review milestones
   - Click "Show Price"

3. **Pay**: Complete payment
   - Auto-fills test card details
   - Click "Confirm Payment"
   - Get transaction ID

4. **Submit**: Upload or fetch code
   - Choose "Upload Files" or "Fetch from GitHub"
   - Enter project/milestone IDs
   - Submit for review

5. **Review**: Get results
   - See pass/fail status
   - Read detailed feedback
   - View PFI score (if passed)

## 🛠️ API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat/architect` | POST | Interactive chat |
| `/plan/finalize` | POST | Finalize checklist |
| `/estimate/{id}` | GET | Get price estimate |
| `/payment/confirm` | POST | Process payment |
| `/github/fetch` | POST | Fetch GitHub repo |
| `/submit` | POST | Submit code |
| `/project/{id}` | GET | Get project details |
| `/reputation/{id}` | GET | Get user reputation |

## 🎨 UI Components

### Toast Notifications
```javascript
showToast('Title', 'Message', 'success'); // green
showToast('Title', 'Message', 'error');   // red
showToast('Title', 'Message', 'warning'); // yellow
showToast('Title', 'Message', 'info');    // blue
```

### Typing Indicator
- Automatically shown during AI responses
- Animated dots with "thinking..." message
- Replaces full-screen loading overlay

### Payment Gateway
- Card number, expiry, CVV, name fields
- Auto-validation on submit
- Success/failure screens

## 🔍 Inspector Agent Logic

### What It Checks
1. **Endpoints**: Looks for route definitions
2. **Functions**: Verifies function exists and has logic
3. **Classes**: Checks class definition and methods
4. **Database**: Looks for table/model definitions
5. **Error Handling**: Verifies status codes and error messages
6. **Tests**: Checks for test files and test functions

### What It Ignores
- Comments and documentation
- Code style and formatting
- Variable naming conventions
- Performance optimizations

### Pass Criteria
- All requirements have matching code
- Functions are actually implemented (not stubs)
- Logic is present (not just imports)
- Error handling exists where specified

## 📈 PFI Score Calculation

```
Performance Score (60%):
- Based on code coverage score
- Weighted with historical average

Financial Score (40%):
- Based on project completion rate
- Weighted with success rate

Combined PFI = (Performance × 0.6) + (Financial × 0.4)
```

## 🐛 Troubleshooting

### "Supabase not available"
- Check service_role key (not anon/publishable)
- Verify tables are created
- Restart server

### "404 Not Found" on chat
- Server not running
- Wrong port (should be 8000)
- Check console for errors

### GitHub fetch fails
- Check repo URL format
- Verify repo is public
- Check branch name (default: main)

### Payment doesn't work
- Fill all card fields
- Check project is finalized
- Verify estimated price is set

## 📚 Documentation Files

- `SUPABASE_SETUP.md` - Database setup guide
- `DEVELOPER_FOCUSED_CHECKLISTS.md` - Requirement writing guide
- `IMPROVEMENTS.md` - UI/UX improvements summary
- `supabase_schema.sql` - Database schema
- `QUICK_REFERENCE.md` - This file

## 🎓 Best Practices

### For Clients
- Describe project in plain English
- Focus on what you want built
- Let AI handle technical details
- Review milestones for completeness

### For Developers
- Review generated requirements
- Add technical details if needed
- Ensure requirements are verifiable
- Test with actual code submission

### For Verification
- Use specific technical terms
- Reference actual code artifacts
- Include file/function names
- Specify error codes and messages

## 🚦 Status Indicators

| Status | Meaning | Can Delete? |
|--------|---------|-------------|
| PENDING | Not started | ✅ Yes |
| LOCKED | Under review | ❌ No |
| RELEASED | Completed | ❌ No |
| DISPUTED | Issue found | ❌ No |

## 💡 Tips

1. **Be Specific**: More detail = better verification
2. **Use Technical Terms**: Functions, classes, endpoints
3. **Test Locally First**: Before submitting to GitHub
4. **Review Feedback**: Inspector provides detailed reports
5. **Iterate**: Refine requirements through chat
6. **Save Project IDs**: For future reference
7. **Check Reputation**: Track your PFI score over time


## 🧪 Testing the Type Error Fix

### Test Case 1: Simple Hello World (File Upload)
1. Go to Planning tab
2. Chat with Architect: "Create a simple hello world project"
3. Click "Finalize Checklist"
4. Click "Show Estimated Price"
5. Go to Payment tab and complete payment
6. Go to Submit tab
7. Create a file `hello_world.py`:
   ```python
   print("Hello, World!")
   ```
8. Upload the file and submit

**Expected**: ✅ No "expected str instance, int found" error

### Test Case 2: GitHub Repository Fetch
1. Complete steps 1-6 from Test Case 1
2. In Submit tab, switch to "Fetch from GitHub"
3. Enter a GitHub URL (e.g., `https://github.com/username/repo`)
4. Click "Fetch Repository"
5. Submit for inspection

**Expected**: ✅ Code analysis completes successfully

## 🔧 Recent Fixes

### Type Error Fix (Latest)
**Problem**: "Code analysis failed: expected str instance, int found"

**Solution**:
- Created custom `GitHubFile` class for proper file handling
- Enhanced type checking in `concatenate_upload_files()`
- Added detailed error logging in Inspector Agent

**Files Modified**:
- `backend/main.py` - Custom GitHubFile class
- `utils/file_processor.py` - Type handling
- `agents/inspector.py` - Error logging

**Status**: ✅ Fixed and tested
