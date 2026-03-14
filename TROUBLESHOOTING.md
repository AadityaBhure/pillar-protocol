# Troubleshooting Guide

## "Milestone Not Found" Error

### Problem
After payment, submitting code shows "Milestone not found" or "Milestone mismatch" error.

### Solution
The milestone IDs must match exactly. Follow these steps:

#### Option 1: Use Auto-Fill (Recommended)
1. Complete payment successfully
2. Check console logs for auto-filled IDs
3. Go to Submit tab - IDs should be pre-filled
4. Click "Load Milestones" button to see all available milestones
5. Select the milestone you want from the list
6. Submit your code

#### Option 2: Manual ID Entry
1. After payment, note the Project ID
2. Go to Submit tab
3. Enter Project ID
4. Click "Load Milestones" button
5. Click on the milestone you want (this fills the Milestone ID)
6. Submit your code

### Debug Steps
1. Open browser console (F12)
2. Look for logs after payment:
   ```
   Payment successful - IDs auto-filled:
   Project ID: xxx-xxx-xxx
   First Milestone ID: yyy-yyy-yyy
   All Milestones: [...]
   ```
3. Copy these IDs to Submit tab if not auto-filled

### Backend Logs
Check server console for detailed error:
```
Available milestone IDs: [id1, id2, id3]
Looking for milestone ID: your-id
```

This shows exactly which IDs exist vs what you're submitting.

## Common Issues

### 1. Wrong Project ID
**Error:** "Project not found"
**Fix:** Copy the exact Project ID from payment confirmation

### 2. Wrong Milestone ID  
**Error:** "Milestone not found"
**Fix:** Use "Load Milestones" button to see valid IDs

### 3. Milestone Already Locked
**Error:** "Failed to lock milestone"
**Fix:** Milestone was already submitted, choose a different one

### 4. No Files Selected
**Error:** "No files provided"
**Fix:** Upload files or fetch from GitHub first

## Testing Workflow

### Simple Hello World Test
1. **Plan**: Chat "Create a simple hello world program"
2. **Finalize**: Click "Finalize Checklist"
3. **Price**: Click "Show Price"
4. **Pay**: Complete payment (auto-fills test card)
5. **Submit Tab**: IDs should be auto-filled
6. **Load Milestones**: Click button to verify
7. **Upload**: Choose your hello_world.py file
8. **Submit**: Click "Submit for Review"

### Expected Result
- Inspector checks code against requirements
- Shows pass/fail with feedback
- If passed, shows PFI score

## Need Help?

Check these in order:
1. Browser console (F12) for JavaScript errors
2. Server console for backend errors  
3. Network tab to see API responses
4. Toast notifications for user-friendly messages


## "Code analysis failed: expected str instance, int found" Error

### Problem
When submitting code files (especially from GitHub), the Inspector Agent throws a type error:
```
Code analysis failed: expected str instance, int found
```

### Root Cause
The issue was in how GitHub-fetched files were being converted to UploadFile-like objects. The file content type handling was causing mismatches during the concatenation process.

### Solution (Fixed)
This issue has been fixed in the latest version. The fix includes:

1. **Custom GitHubFile Class** (`backend/main.py`)
   - Properly mimics UploadFile interface
   - Handles content encoding correctly
   - Provides async read() and seek() methods

2. **Enhanced Type Checking** (`utils/file_processor.py`)
   - Handles both bytes and string content types
   - Explicit type checking before decoding
   - Better error messages for debugging

3. **Error Logging** (`agents/inspector.py`)
   - Detailed error logging for file processing
   - Stack traces for debugging
   - Clear error messages to users

### Verification
Run the test script to verify the fix:
```bash
python test_type_fix.py
```

Expected output:
```
✅ GitHub file test passed!
✅ Multiple files test passed!
✅ All tests passed!
```

### If Issue Persists
1. Check file encoding (should be UTF-8)
2. Verify file content is text (not binary)
3. Check server logs for detailed error trace
4. Ensure files are valid code files (.py, .js, .ts, etc.)

### Files Modified
- `backend/main.py` - Custom GitHubFile class
- `utils/file_processor.py` - Enhanced type handling
- `agents/inspector.py` - Better error logging

### Status
✅ **Fixed** - Ready for production use
