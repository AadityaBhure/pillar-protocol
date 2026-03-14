# Milestone Status Guide

## Quick Reference

### Milestone States

| Status | Color | Meaning | Can Submit Code? | Can Delete? |
|--------|-------|---------|------------------|-------------|
| **PENDING** | 🟡 Yellow | Ready for code submission | ✅ Yes | ✅ Yes |
| **LOCKED** | 🔵 Blue | Under review - code is being inspected | ❌ No | ❌ No |
| **RELEASED** | 🟢 Green | Completed - payment released | ❌ No | ❌ No |
| **DISPUTED** | 🔴 Red | Disputed - requires resolution | ❌ No | ❌ No |

## What Happens When You Submit Code?

### Successful Submission Flow
```
1. Milestone is PENDING (yellow)
   ↓
2. You submit code
   ↓
3. Milestone becomes LOCKED (blue) - inspection in progress
   ↓
4. Code passes inspection ✅
   ↓
5. Milestone becomes RELEASED (green)
   ↓
6. Payment is released to you!
```

### Failed Submission Flow
```
1. Milestone is PENDING (yellow)
   ↓
2. You submit code
   ↓
3. Milestone becomes LOCKED (blue) - inspection in progress
   ↓
4. Code fails inspection ❌
   ↓
5. Milestone returns to PENDING (yellow)
   ↓
6. You can submit new code immediately!
```

## Common Scenarios

### "I submitted code but it failed. Can I try again?"
**Yes!** When your code fails inspection, the milestone automatically unlocks and returns to PENDING state. You can submit new code right away.

### "Why can't I submit code to this milestone?"
Check the milestone status:
- **LOCKED**: Another submission is currently being reviewed. Wait for it to complete.
- **RELEASED**: This milestone is already completed. You can't resubmit to completed milestones.
- **DISPUTED**: There's a dispute that needs to be resolved first.

### "Can I delete a milestone after submitting code?"
- **PENDING**: Yes, you can delete it
- **LOCKED/RELEASED/DISPUTED**: No, once code is submitted or milestone is completed, it cannot be deleted

## Error Messages Explained

### "This milestone is currently under review"
- **Cause**: Milestone is LOCKED
- **Solution**: Wait for the current inspection to complete, then try again

### "This milestone has already been completed and payment released"
- **Cause**: Milestone is RELEASED
- **Solution**: This milestone is done! Move on to the next milestone or project

### "Failed to lock milestone. Current status: LOCKED"
- **Cause**: Someone else (or you in another tab) is already submitting code
- **Solution**: Wait a moment and try again, or refresh the page to see current status

### "The milestone must be in PENDING state to accept submissions"
- **Cause**: Milestone is not in PENDING state
- **Solution**: Check the milestone status and wait for it to return to PENDING

## Tips for Smooth Workflow

1. **Check Status First**: Before submitting code, verify the milestone is PENDING (yellow badge)

2. **One Submission at a Time**: Don't submit code to the same milestone from multiple tabs/browsers

3. **Failed? Try Again**: If your code fails inspection, read the feedback carefully and submit improved code

4. **Track Your Progress**: Use the View Project tab to see all milestone statuses at a glance

5. **Read Feedback**: When code fails, the feedback tells you exactly what's missing or wrong

## Visual Indicators

### In Milestone List
- Status badge shows current state with color coding
- Hover over badge to see description
- Delete button is disabled for non-PENDING milestones

### In Milestone Selector (Submit Tab)
- PENDING milestones are clickable and fully visible
- Non-PENDING milestones are grayed out and show status description
- Tooltip explains why you can't select locked/completed milestones

### After Submission
- **Success**: Green message box + "Milestone completed and payment released!"
- **Failure**: Red message box + "Milestone unlocked - you can submit new code to try again"

## Need Help?

If you encounter issues:
1. Check the milestone status in the View Project tab
2. Read the error message carefully - it explains what's wrong
3. Check the browser console for detailed logs
4. Verify your Project ID and Milestone ID are correct
