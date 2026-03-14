# Milestone Status Fix

## Problem
1. Milestones were being locked immediately after payment, preventing code submission
2. When code inspection failed, milestone stayed LOCKED, preventing resubmission

## Root Causes
1. The `/payment/confirm` endpoint was locking ALL milestones immediately after payment
2. Failed inspections didn't unlock the milestone for retry

## Correct Flow

### Before Fix (WRONG):
1. Create project → Milestones: PENDING
2. Pay → Milestones: LOCKED ❌
3. Submit code → Error: "Already locked"

### After Fix (CORRECT):
1. Create project → Milestones: PENDING ✅
2. Pay → Milestones: PENDING ✅ (payment confirmed, but milestones stay open)
3. Submit code → Milestones: LOCKED ✅ (locked during submission)
4. Code analyzed:
   - **If PASSED** → Milestones: RELEASED ✅ (payment released)
   - **If FAILED** → Milestones: PENDING ✅ (unlocked for resubmission)

## Milestone States Explained

### PENDING
- **Meaning**: Ready for code submission
- **Can submit code**: ✅ Yes
- **Can delete**: ✅ Yes
- **When**: 
  - After project creation
  - After payment
  - After failed inspection (allows retry)

### LOCKED
- **Meaning**: Under review - code submitted and being analyzed
- **Can submit code**: ❌ No (already under review)
- **Can delete**: ❌ No
- **When**: During code submission and analysis (temporary state)

### RELEASED
- **Meaning**: Completed - payment released to developer
- **Can submit code**: ❌ No (already completed)
- **Can delete**: ❌ No
- **When**: After successful code inspection

### DISPUTED
- **Meaning**: Issue found - requires resolution
- **Can submit code**: ❌ No (needs dispute resolution)
- **Can delete**: ❌ No
- **When**: When inspection fails or issues arise (future feature)

## Changes Made

### 1. Fixed Payment Endpoint
**File**: `backend/main.py`

**Before**:
```python
# Lock all milestones
for milestone in project["milestones"]:
    banker.lock_milestone(milestone["id"])
```

**After**:
```python
# NOTE: Milestones are NOT locked here
# They remain in PENDING state until code is actually submitted
```

### 2. Added Unlock on Failed Inspection
**File**: `backend/main.py`

**New**:
```python
if inspection_result.passed:
    # Release payment
    banker.release_payment(milestone_id)
else:
    # Unlock milestone for resubmission
    db.update_milestone_status(milestone_id, EscrowStatus.PENDING.value)
```

### 3. Added Better Error Messages
Now shows specific error for each state:
- LOCKED: "Already under review"
- RELEASED: "Already completed"
- DISPUTED: "Currently disputed"

### 4. Added Status Check Endpoint
New endpoint: `GET /milestone/{milestone_id}/status`

Returns:
```json
{
  "milestone_id": "xxx",
  "status": "PENDING",
  "can_submit": true,
  "can_delete": true,
  "description": "Ready for code submission"
}
```

## How to Test

### 1. Create Fresh Project
```bash
# Start server
python backend/main.py

# Open UI
http://localhost:8000
```

### 2. Complete Payment
- Go through planning
- Finalize checklist
- Complete payment
- **Check**: Milestones should still be PENDING

### 3. Submit Code (First Attempt - Fail)
- Go to Submit tab
- Upload incomplete/wrong code
- **Check**: Milestone changes to LOCKED during submission
- **Check**: After analysis fails, changes back to PENDING
- **Check**: You can submit again!

### 4. Submit Code (Second Attempt - Pass)
- Fix your code
- Submit again
- **Check**: Milestone changes to LOCKED during submission
- **Check**: After analysis passes, changes to RELEASED
- **Check**: Cannot submit again (already completed)

## Resubmission Flow

```
PENDING → Submit Code → LOCKED → Analysis
                                     ↓
                          ┌──────────┴──────────┐
                          ↓                     ↓
                       FAILED                PASSED
                          ↓                     ↓
                      PENDING              RELEASED
                    (can retry)         (completed)
```

## For Existing Locked Milestones

If you have milestones stuck in LOCKED state from before the fix:

### Option 1: Create New Project (Recommended)
Start fresh with a new project

### Option 2: Reset in Supabase
1. Go to Supabase dashboard
2. Table Editor → milestones
3. Find your milestone
4. Change `status` from "LOCKED" to "PENDING"
5. Try submitting again

## Status
✅ Fixed - Milestones now:
- Stay PENDING until code submission
- Return to PENDING after failed inspection (allows retry)
- Change to RELEASED only after successful inspection
