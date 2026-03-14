# Type Error Fix - "expected str instance, int found"

## Problem
When submitting code files (especially from GitHub), the Inspector Agent was throwing an error:
```
Code analysis failed: expected str instance, int found
```

## Root Cause
The issue was in how GitHub-fetched files were being converted to UploadFile-like objects in `backend/main.py`. The FastAPI `UploadFile` class was being instantiated incorrectly, causing type mismatches when the file content was being read and decoded.

## Solution

### 1. Created Custom GitHubFile Class (`backend/main.py`)
Instead of trying to use FastAPI's UploadFile directly, created a custom class that properly mimics the UploadFile interface:

```python
class GitHubFile:
    def __init__(self, filename, content):
        self.filename = filename
        self.content_bytes = content.encode('utf-8')
        self.file = BytesIO(self.content_bytes)
    
    async def read(self):
        return self.content_bytes
    
    async def seek(self, position):
        self.file.seek(position)
```

### 2. Enhanced File Concatenation (`utils/file_processor.py`)
Updated `concatenate_upload_files()` to handle both bytes and string content types:

```python
# Read content as bytes
content_bytes = await file.read()

# Decode to string
if isinstance(content_bytes, bytes):
    content = content_bytes.decode('utf-8')
elif isinstance(content_bytes, str):
    content = content_bytes
else:
    raise TypeError(f"Unexpected content type: {type(content_bytes)}")
```

### 3. Added Error Handling (`agents/inspector.py`)
Added try-catch block in `_concatenate_files()` to log detailed errors for debugging.

## Files Modified
1. `backend/main.py` - Custom GitHubFile class
2. `utils/file_processor.py` - Enhanced type handling in concatenate_upload_files()
3. `agents/inspector.py` - Better error logging

## Testing
Test with a simple hello_world.py file:
```python
print("Hello, World!")
```

Both upload methods should now work:
- Direct file upload
- GitHub repository fetch

## Status
✅ Fixed and ready for testing
