# Demo Templates for Pillar Protocol

This directory contains example code files for testing the Pillar Protocol system.

## Good Code Example (`good_code_example.py`)

**Purpose**: Demonstrates a complete, working implementation that should pass inspection with 100% coverage.

**Features**:
- All functions are properly implemented with actual logic
- Functions are both defined AND actually called in the code
- Complete image processing pipeline with all steps
- Real functionality, not just imports or stubs

**Expected Result**: ✅ PASS with ~100% coverage score

**Why it passes**:
1. All requirements are implemented with real logic
2. Functions like `load_image()`, `apply_grayscale()`, `apply_blur()`, `resize_image()`, and `save_image()` are all defined
3. All functions are actually used in the `process_pipeline()` method
4. The `if __name__ == "__main__"` block demonstrates actual usage

## Bad Code Example (`bad_code_example.py`)

**Purpose**: Demonstrates incomplete implementation that should fail inspection with specific feedback.

**Issues**:
- `load_image()` has no implementation (just `pass`)
- `apply_grayscale()` is defined but never called
- `apply_blur()` has incomplete implementation (doesn't actually blur)
- `resize_image()` function is completely missing
- `save_image()` has no implementation (just `pass`)

**Expected Result**: ❌ FAIL with specific missing requirements listed

**Why it fails**:
1. Functions are defined but not properly implemented
2. Some functions are never called (unused code)
3. Missing required functionality (resize_image)
4. No real logic, just stubs and pass statements

## Usage Instructions

### Testing with the API

1. **Create a project** with prompt like: "Build an image processing pipeline with grayscale, blur, and resize filters"

2. **Upload good code**:
   ```bash
   curl -X POST http://localhost:8000/submit \
     -F "project_id=<your-project-id>" \
     -F "milestone_id=<your-milestone-id>" \
     -F "files=@templates/good_code_example.py"
   ```
   Expected: Pass with high PFI score

3. **Upload bad code**:
   ```bash
   curl -X POST http://localhost:8000/submit \
     -F "project_id=<your-project-id>" \
     -F "milestone_id=<your-milestone-id>" \
     -F "files=@templates/bad_code_example.py"
   ```
   Expected: Fail with detailed feedback about missing implementations

### Testing with the Frontend

1. Open the dashboard in your browser
2. Create a new project with an image processing prompt
3. Use the file upload to submit either template
4. Watch the PFI gauge animate on successful submission
5. Read the detailed feedback for failed submissions

## Key Differences

| Aspect | Good Code | Bad Code |
|--------|-----------|----------|
| Implementation | Complete | Incomplete/Missing |
| Function Usage | All functions called | Some never used |
| Logic Coverage | 100% | ~40% |
| Real Functionality | Yes | No (stubs) |
| Inspector Result | PASS | FAIL |

## Learning Points

The Inspector Agent checks for:
1. **Logic Coverage**: Are requirements actually implemented?
2. **Function Usage**: Are functions both defined AND called?
3. **Real Functionality**: Is there actual logic, not just imports?

Simply defining functions is not enough - they must be properly implemented and actually used in the code!
