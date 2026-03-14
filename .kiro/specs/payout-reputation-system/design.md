# Design Document: Payout and Reputation System

## Overview

The Payout and Reputation System extends the Pillar Protocol platform to track milestone deadlines, determine timeline compliance, adjust payouts based on delivery timeliness, and maintain developer reputation scores. This system integrates with existing agents (Architect, Inspector, Banker) and introduces a new Reputation Management module.

The system operates on these core principles:

1. **Time-Bound Milestones**: Every milestone has a deadline calculated from estimated hours
2. **Timeline Tracking**: Submission times are compared against deadlines to determine on-time vs late status
3. **Payout Logic**: Full payment is released for passing submissions, with reputation impact for late deliveries
4. **Reputation Scoring**: Developer reliability is tracked through a 0-100 score based on timeliness and quality
5. **Backward Compatibility**: Legacy milestones without deadlines continue to function normally

### Key Design Decisions

- **1 hour = 1 day conversion**: Simple, conservative deadline calculation that accounts for real-world development constraints
- **Full payment for late work**: Prioritizes developer compensation while tracking reliability through reputation
- **Reputation as separate concern**: Decouples payment from reputation to maintain fairness
- **Configuration-driven policies**: Deadline ratios and reputation weights are externalized to JSON config

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (UI)                            │
│  - Displays deadlines and days remaining                         │
│  - Shows reputation scores and history                           │
│  - Allows deadline adjustments                                   │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ HTTP/JSON
                 │
┌────────────────▼────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
│  - /plan: Create project with milestones                         │
│  - /submit: Submit code for milestone                            │
│  - /reputation/{user_id}: Get reputation data                    │
│  - /milestone/{id}/deadline: Adjust deadline                     │
└─────┬──────────┬──────────┬──────────┬─────────────────────────┘
      │          │          │          │
      │          │          │          │
┌─────▼────┐ ┌──▼──────┐ ┌─▼────────┐ ┌▼──────────────────────┐
│Architect │ │Inspector│ │  Banker  │ │ Reputation Manager    │
│  Agent   │ │  Agent  │ │  Agent   │ │  (New Module)         │
│          │ │         │ │          │ │                       │
│- Generate│ │- Analyze│ │- Lock    │ │- Calculate score      │
│  deadline│ │  code   │ │- Compare │ │- Store history        │
│  from    │ │- Return │ │  times   │ │- Retrieve reputation  │
│  hours   │ │  PFI    │ │- Release │ │                       │
│          │ │         │ │  payment │ │                       │
└─────┬────┘ └──┬──────┘ └─┬────────┘ └┬──────────────────────┘
      │          │          │           │
      │          │          │           │
      └──────────┴──────────┴───────────┴───────────────────────┐
                                                                  │
                                                                  │
                                                        ┌─────────▼──────────┐
                                                        │  Supabase Database │
                                                        │                    │
                                                        │  - projects        │
                                                        │  - milestones      │
                                                        │  - users           │
                                                        │  - reputation      │
                                                        │  - deadline_audit  │
                                                        └────────────────────┘
```

### Data Flow

**Milestone Creation Flow:**
1. User submits project prompt → Architect Agent
2. Architect generates milestones with requirements and estimated_hours
3. Architect calculates deadline = creation_time + (estimated_hours * 1 day)
4. Architect stores milestone with deadline in database
5. Frontend displays milestone with deadline and days_remaining

**Code Submission Flow:**
1. Developer submits code → Backend /submit endpoint
2. Banker locks milestone, records submission_time
3. Inspector analyzes code against requirements
4. If PASS:
   - Banker compares submission_time vs deadline
   - Determines timeline_status ("on-time" or "late")
   - Releases full payment
   - Triggers Reputation Manager with timeline_status
   - Reputation Manager updates score and history
5. If FAIL:
   - Banker unlocks milestone (status → PENDING)
   - Developer can resubmit

**Reputation Update Flow:**
1. Banker triggers reputation update with (user_id, milestone_id, timeline_status, pfi_score)
2. Reputation Manager calculates score_delta based on:
   - Timeline: +2 for on-time, -5 for late
   - Quality: +1 for PFI > 80, -2 for PFI < 50
3. Reputation Manager updates user reputation_score (clamped 0-100)
4. Reputation Manager appends event to reputation_history
5. Database persists updated reputation

## Components and Interfaces

### 1. Architect Agent (Modified)

**New Responsibilities:**
- Calculate realistic deadlines from estimated_hours
- Store deadline as ISO 8601 timestamp

**Interface Changes:**

```python
class ArchitectAgent:
    def generate_checklist(self, prompt: str) -> List[dict]:
        """
        Generate milestones with deadlines.
        
        Returns:
            List of milestone dicts with added 'deadline' field
        """
        # Existing logic...
        milestones = self._generate_from_gemini(prompt)
        
        # NEW: Add deadline calculation
        for milestone in milestones:
            deadline = self._calculate_deadline(
                estimated_hours=milestone['estimated_hours']
            )
            milestone['deadline'] = deadline
        
        return milestones
    
    def _calculate_deadline(self, estimated_hours: int) -> str:
        """
        Calculate deadline using hours_to_days_ratio from config.
        
        Args:
            estimated_hours: Estimated hours for milestone
            
        Returns:
            ISO 8601 timestamp string
        """
        config = self._load_deadline_config()
        ratio = config.get('hours_to_days_ratio', 1.0)
        
        days = estimated_hours * ratio
        deadline_dt = datetime.utcnow() + timedelta(days=days)
        
        return deadline_dt.isoformat() + 'Z'
    
    def _load_deadline_config(self) -> dict:
        """Load deadline_config.json or return defaults"""
        try:
            with open('deadline_config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'hours_to_days_ratio': 1.0,
                'reputation_weights': {
                    'on_time_bonus': 2,
                    'late_penalty': 5,
                    'high_quality_bonus': 1,
                    'low_quality_penalty': 2
                }
            }
```

### 2. Banker Agent (Modified)

**New Responsibilities:**
- Record submission_time when locking milestone
- Compare submission_time vs deadline
- Determine timeline_status
- Trigger reputation updates

**Interface Changes:**

```python
class BankerAgent:
    def lock_milestone(self, milestone_id: str) -> bool:
        """
        Lock milestone and record submission time.
        
        NEW: Records submission_time as ISO 8601 timestamp
        """
        if self.get_milestone_status(milestone_id) != EscrowStatus.PENDING:
            return False
        
        submission_time = datetime.utcnow().isoformat() + 'Z'
        
        self.db.update_milestone_status(milestone_id, EscrowStatus.LOCKED.value)
        self.db.update_milestone_submission_time(milestone_id, submission_time)
        
        return True
    
    def release_payment(
        self, 
        milestone_id: str, 
        user_id: str, 
        pfi_score: float
    ) -> dict:
        """
        Release payment and trigger reputation update.
        
        NEW: Determines timeline_status and triggers reputation update
        
        Returns:
            dict with payment_status, timeline_status, reputation_change
        """
        if self.get_milestone_status(milestone_id) != EscrowStatus.LOCKED:
            return {'status': 'error', 'message': 'Milestone not locked'}
        
        # Get milestone data
        milestone = self.db.get_milestone(milestone_id)
        submission_time = milestone['submission_time']
        deadline = milestone['deadline']
        
        # Determine timeline status
        timeline_status = self._determine_timeline_status(
            submission_time, 
            deadline
        )
        
        # Release payment (full amount regardless of timeline)
        self.db.update_milestone_status(milestone_id, EscrowStatus.RELEASED.value)
        self.db.update_milestone_timeline_status(milestone_id, timeline_status)
        payment_result = self.simulate_x402_payment(
            milestone['escrow_amount'], 
            user_id
        )
        
        # Trigger reputation update
        reputation_change = self.reputation_manager.update_reputation(
            user_id=user_id,
            milestone_id=milestone_id,
            timeline_status=timeline_status,
            pfi_score=pfi_score
        )
        
        return {
            'status': 'success',
            'payment': payment_result,
            'timeline_status': timeline_status,
            'reputation_change': reputation_change
        }
    
    def _determine_timeline_status(
        self, 
        submission_time: str, 
        deadline: Optional[str]
    ) -> str:
        """
        Compare submission time against deadline.
        
        Args:
            submission_time: ISO 8601 timestamp
            deadline: ISO 8601 timestamp or None
            
        Returns:
            "on-time" or "late"
        """
        if deadline is None:
            return "on-time"  # Backward compatibility
        
        submission_dt = datetime.fromisoformat(submission_time.replace('Z', '+00:00'))
        deadline_dt = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
        
        return "on-time" if submission_dt <= deadline_dt else "late"
```

### 3. Reputation Manager (New Module)

**Responsibilities:**
- Calculate reputation score changes
- Store reputation history events
- Retrieve reputation data for API

**Interface:**

```python
class ReputationManager:
    def __init__(self, db_connection):
        self.db = db_connection
        self.config = self._load_config()
    
    def update_reputation(
        self,
        user_id: str,
        milestone_id: str,
        timeline_status: str,
        pfi_score: float
    ) -> dict:
        """
        Update user reputation based on timeline and quality.
        
        Args:
            user_id: Developer user ID
            milestone_id: Completed milestone ID
            timeline_status: "on-time" or "late"
            pfi_score: PFI score from Inspector (0-100)
            
        Returns:
            dict with score_delta, new_score, events
        """
        current_reputation = self.db.get_user_reputation(user_id)
        current_score = current_reputation['reputation_score'] if current_reputation else 50
        
        # Calculate score changes
        timeline_delta = self._calculate_timeline_delta(timeline_status)
        quality_delta = self._calculate_quality_delta(pfi_score)
        total_delta = timeline_delta + quality_delta
        
        # Apply changes (clamp to 0-100)
        new_score = max(0, min(100, current_score + total_delta))
        
        # Create history events
        events = []
        if timeline_delta != 0:
            events.append({
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'event_type': 'on_time_delivery' if timeline_status == 'on-time' else 'late_delivery',
                'score_change': timeline_delta,
                'milestone_id': milestone_id,
                'resulting_score': new_score
            })
        
        if quality_delta != 0:
            event_type = 'high_quality' if pfi_score > 80 else 'low_quality'
            events.append({
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'event_type': event_type,
                'score_change': quality_delta,
                'milestone_id': milestone_id,
                'resulting_score': new_score
            })
        
        # Persist to database
        self.db.update_user_reputation_score(user_id, new_score, events)
        
        # Update timeline counters
        if timeline_status == 'on-time':
            self.db.increment_on_time_count(user_id)
        else:
            self.db.increment_late_count(user_id)
        
        return {
            'score_delta': total_delta,
            'new_score': new_score,
            'events': events
        }
    
    def _calculate_timeline_delta(self, timeline_status: str) -> int:
        """Calculate reputation change from timeline status"""
        weights = self.config['reputation_weights']
        if timeline_status == 'on-time':
            return weights['on_time_bonus']
        else:
            return -weights['late_penalty']
    
    def _calculate_quality_delta(self, pfi_score: float) -> int:
        """Calculate reputation change from PFI score"""
        weights = self.config['reputation_weights']
        if pfi_score > 80:
            return weights['high_quality_bonus']
        elif pfi_score < 50:
            return -weights['low_quality_penalty']
        else:
            return 0
    
    def get_reputation(self, user_id: str) -> dict:
        """
        Retrieve complete reputation data for user.
        
        Returns:
            dict with reputation_score, total_milestones_completed,
            on_time_count, late_count, on_time_percentage, 
            average_pfi_score, reputation_history
        """
        reputation = self.db.get_user_reputation(user_id)
        if not reputation:
            return {
                'user_id': user_id,
                'reputation_score': 50,
                'total_milestones_completed': 0,
                'on_time_count': 0,
                'late_count': 0,
                'on_time_percentage': 0.0,
                'average_pfi_score': 0.0,
                'reputation_history': []
            }
        
        # Calculate metrics
        total = reputation['on_time_count'] + reputation['late_count']
        on_time_pct = (reputation['on_time_count'] / total * 100) if total > 0 else 0.0
        
        return {
            'user_id': user_id,
            'reputation_score': reputation['reputation_score'],
            'total_milestones_completed': total,
            'on_time_count': reputation['on_time_count'],
            'late_count': reputation['late_count'],
            'on_time_percentage': round(on_time_pct, 2),
            'average_pfi_score': reputation.get('average_pfi_score', 0.0),
            'reputation_history': reputation['reputation_history']
        }
    
    def _load_config(self) -> dict:
        """Load deadline_config.json"""
        try:
            with open('deadline_config.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'hours_to_days_ratio': 1.0,
                'reputation_weights': {
                    'on_time_bonus': 2,
                    'late_penalty': 5,
                    'high_quality_bonus': 1,
                    'low_quality_penalty': 2
                }
            }
```

### 4. API Endpoints (New/Modified)

**New Endpoints:**

```python
@app.get("/reputation/{user_id}")
async def get_reputation(user_id: str):
    """
    Retrieve developer reputation data.
    
    Response:
    {
        "user_id": "user-123",
        "reputation_score": 75.0,
        "total_milestones_completed": 10,
        "on_time_count": 8,
        "late_count": 2,
        "on_time_percentage": 80.0,
        "average_pfi_score": 85.5,
        "reputation_history": [
            {
                "timestamp": "2024-01-15T10:30:00Z",
                "event_type": "on_time_delivery",
                "score_change": 2,
                "milestone_id": "milestone-abc",
                "resulting_score": 75
            }
        ]
    }
    """
    reputation = reputation_manager.get_reputation(user_id)
    if not reputation:
        raise HTTPException(status_code=404, detail="User not found")
    return reputation


@app.patch("/milestone/{milestone_id}/deadline")
async def adjust_deadline(milestone_id: str, request: dict):
    """
    Adjust milestone deadline.
    
    Request body:
    {
        "new_deadline": "2024-02-01T23:59:59Z"
    }
    
    Response:
    {
        "status": "success",
        "milestone_id": "milestone-abc",
        "old_deadline": "2024-01-25T23:59:59Z",
        "new_deadline": "2024-02-01T23:59:59Z",
        "changed_at": "2024-01-20T14:30:00Z"
    }
    """
    new_deadline = request.get('new_deadline')
    
    # Validate ISO 8601 format
    try:
        datetime.fromisoformat(new_deadline.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ISO 8601 timestamp")
    
    # Check milestone status
    milestone = db.get_milestone(milestone_id)
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    if milestone['status'] == EscrowStatus.RELEASED.value:
        raise HTTPException(
            status_code=400, 
            detail="Cannot adjust deadline for released milestone"
        )
    
    # Update deadline and log audit trail
    old_deadline = milestone['deadline']
    changed_at = datetime.utcnow().isoformat() + 'Z'
    
    db.update_milestone_deadline(milestone_id, new_deadline)
    db.log_deadline_change(milestone_id, old_deadline, new_deadline, changed_at)
    
    return {
        'status': 'success',
        'milestone_id': milestone_id,
        'old_deadline': old_deadline,
        'new_deadline': new_deadline,
        'changed_at': changed_at
    }
```

**Modified Endpoints:**

```python
@app.post("/submit")
async def submit_code(...):
    """
    Modified to include reputation impact in response.
    
    Response now includes:
    {
        "passed": true,
        "feedback": "All requirements met",
        "pfi_score": 85.0,
        "reputation_change": {
            "score_delta": 3,
            "new_score": 78,
            "reason": "On-time delivery bonus (+2) and high quality bonus (+1)"
        }
    }
    """
    # Existing logic...
    
    if inspection_result.passed:
        payment_result = banker.release_payment(
            milestone_id, 
            user_id, 
            pfi_score
        )
        
        return SubmitResponse(
            passed=True,
            feedback=inspection_result.feedback,
            pfi_score=pfi_score,
            reputation_change=payment_result['reputation_change']
        )
```

## Data Models

### Database Schema Changes

**milestones table (modified):**

```sql
CREATE TABLE milestones (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    requirements JSONB NOT NULL,
    estimated_hours INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    escrow_amount DECIMAL(10, 2),
    created_at TIMESTAMP NOT NULL,
    
    -- NEW FIELDS
    deadline TIMESTAMP,  -- ISO 8601 timestamp, nullable for backward compatibility
    submission_time TIMESTAMP,  -- Recorded when status → LOCKED
    timeline_status VARCHAR(20),  -- "on-time" or "late"
    
    CONSTRAINT valid_status CHECK (status IN ('PENDING', 'LOCKED', 'RELEASED', 'DISPUTED')),
    CONSTRAINT valid_timeline_status CHECK (timeline_status IN ('on-time', 'late') OR timeline_status IS NULL)
);

-- Index for deadline queries
CREATE INDEX idx_milestones_deadline ON milestones(deadline);
CREATE INDEX idx_milestones_timeline_status ON milestones(timeline_status);
```

**users table (modified):**

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL,
    
    -- NEW FIELDS
    reputation_score DECIMAL(5, 2) NOT NULL DEFAULT 50.00,  -- 0.00 to 100.00
    total_on_time_deliveries INTEGER NOT NULL DEFAULT 0,
    total_late_deliveries INTEGER NOT NULL DEFAULT 0,
    reputation_history JSONB NOT NULL DEFAULT '[]',  -- Array of reputation events
    
    CONSTRAINT valid_reputation_score CHECK (reputation_score >= 0 AND reputation_score <= 100)
);

-- Index for reputation queries
CREATE INDEX idx_users_reputation_score ON users(reputation_score);
```

**deadline_audit table (new):**

```sql
CREATE TABLE deadline_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    milestone_id UUID REFERENCES milestones(id),
    old_deadline TIMESTAMP,
    new_deadline TIMESTAMP NOT NULL,
    changed_at TIMESTAMP NOT NULL,
    changed_by UUID REFERENCES users(id),
    reason TEXT,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Index for audit queries
CREATE INDEX idx_deadline_audit_milestone ON deadline_audit(milestone_id);
CREATE INDEX idx_deadline_audit_changed_at ON deadline_audit(changed_at);
```

### Reputation History Event Schema

```json
{
    "timestamp": "2024-01-15T10:30:00Z",
    "event_type": "on_time_delivery" | "late_delivery" | "high_quality" | "low_quality",
    "score_change": 2,  // Can be negative
    "milestone_id": "milestone-abc-123",
    "resulting_score": 75.0
}
```

### Configuration File Schema

**deadline_config.json:**

```json
{
    "hours_to_days_ratio": 1.0,
    "reputation_weights": {
        "on_time_bonus": 2,
        "late_penalty": 5,
        "high_quality_bonus": 1,
        "low_quality_penalty": 2
    }
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I identified several areas of redundancy:

1. **Deadline calculation and storage** (1.1, 1.2, 1.4, 1.5): These can be combined into a single comprehensive property about deadline calculation
2. **Database persistence** (2.2, 2.3): Both test round-trip persistence, can be combined
3. **Escrow status transitions** (5.2, 6.2): Same behavior for on-time and late cases, can be unified
4. **ISO 8601 format validation** (1.3, 3.2, 11.2): Can be combined into a single format validation property
5. **Timeline status determination** (4.2, 4.3): These are complementary cases of the same comparison logic, can be combined
6. **Reputation score changes** (8.2, 8.3, 8.4, 8.5): Can be combined into a single property about score delta calculation
7. **Response structure validation** (10.2, 15.2): Multiple properties checking response fields can be consolidated

The following properties represent the unique, non-redundant validation requirements:

### Property 1: Deadline Calculation from Estimated Hours

*For any* milestone with estimated_hours, the calculated deadline SHALL equal creation_time plus (estimated_hours * hours_to_days_ratio) days, stored as an ISO 8601 timestamp.

**Validates: Requirements 1.1, 1.2, 1.3, 1.4**

### Property 2: Milestone Persistence Round-Trip

*For any* milestone with a deadline, storing it to the database and then retrieving it SHALL return the same deadline value.

**Validates: Requirements 2.1, 2.2, 2.3**

### Property 3: Submission Time Recording on Lock

*For any* milestone, when its status transitions to LOCKED, the submission_time field SHALL be set to the current timestamp in ISO 8601 format.

**Validates: Requirements 3.1, 3.2, 3.3**

### Property 4: Submission Time Update on Resubmission

*For any* milestone that fails inspection and is resubmitted, the submission_time SHALL be updated to the timestamp of the latest submission.

**Validates: Requirements 3.4**

### Property 5: Timeline Status Determination

*For any* milestone with non-null deadline and submission_time, the timeline_status SHALL be "on-time" if submission_time ≤ deadline, and "late" if submission_time > deadline.

**Validates: Requirements 4.1, 4.2, 4.3, 4.5**

### Property 6: Payment Release for Passing Submissions

*For any* milestone where inspection passes (regardless of timeline_status), the Banker SHALL release full payment, update escrow_status to RELEASED, and execute the x402 payment protocol.

**Validates: Requirements 5.1, 5.2, 5.3, 6.1, 6.2**

### Property 7: Reputation Update Trigger on Completion

*For any* milestone that passes inspection, the system SHALL trigger a reputation update with the timeline_status and pfi_score, resulting in a reputation_history entry.

**Validates: Requirements 6.3, 6.4**

### Property 8: No Payment on Failed Inspection

*For any* milestone where inspection fails, the Banker SHALL NOT release payment and SHALL update escrow_status to PENDING to allow resubmission.

**Validates: Requirements 7.1, 7.2, 7.5**

### Property 9: Inspection Feedback Structure

*For any* failed inspection, the Inspector SHALL return feedback containing a list of missing_requirements.

**Validates: Requirements 7.3, 7.4**

### Property 10: Reputation Score Delta Calculation

*For any* completed milestone, the reputation score change SHALL be calculated as: timeline_delta (on-time: +2, late: -5) plus quality_delta (PFI > 80: +1, PFI < 50: -2, else: 0).

**Validates: Requirements 8.2, 8.3, 8.4, 8.5**

### Property 11: Reputation Score Clamping

*For any* reputation score update, the resulting score SHALL be clamped to the range [0, 100], regardless of the magnitude of bonuses or penalties applied.

**Validates: Requirements 8.1, 8.6**

### Property 12: New Developer Initialization

*For any* new developer account, the initial reputation_score SHALL be set to 50.

**Validates: Requirements 8.7**

### Property 13: Reputation History Append

*For any* reputation score change, the system SHALL append exactly one entry to reputation_history containing timestamp, event_type, score_change, milestone_id, and resulting_score.

**Validates: Requirements 9.1, 9.2, 9.3**

### Property 14: Event Type Enumeration

*For any* reputation history entry, the event_type field SHALL be one of: "on_time_delivery", "late_delivery", "high_quality", or "low_quality".

**Validates: Requirements 9.4**

### Property 15: Reputation API Response Structure

*For any* valid user_id, the GET /reputation/{user_id} endpoint SHALL return a JSON object containing reputation_score, total_milestones_completed, on_time_count, late_count, on_time_percentage, average_pfi_score, and reputation_history.

**Validates: Requirements 10.2, 10.4, 10.5**

### Property 16: Milestone API Response Includes Deadline

*For any* milestone returned by the API, the response SHALL include a deadline field (ISO 8601 timestamp or null) and a days_remaining field calculated as (deadline - current_time) in days.

**Validates: Requirements 11.1, 11.2, 11.4**

### Property 17: Overdue Flag for Negative Days Remaining

*For any* milestone where days_remaining is negative, the milestone SHALL be marked as overdue.

**Validates: Requirements 11.5**

### Property 18: Timeline Delivery Counter Increments

*For any* completed milestone, the system SHALL increment either total_on_time_deliveries or total_late_deliveries based on timeline_status.

**Validates: Requirements 12.1, 12.2**

### Property 19: On-Time Percentage Calculation

*For any* developer with completed milestones, the on_time_percentage SHALL equal (total_on_time_deliveries / (total_on_time_deliveries + total_late_deliveries)) * 100, rounded to 2 decimal places.

**Validates: Requirements 12.3, 12.4, 12.5**

### Property 20: Inspector Validates Regardless of Deadline

*For any* milestone (including those with null deadline), the Inspector SHALL perform code validation against requirements.

**Validates: Requirements 13.3**

### Property 21: Deadline Update Round-Trip

*For any* milestone with status != RELEASED, updating its deadline via PATCH /milestone/{id}/deadline SHALL persist the new deadline and create an audit log entry with old_deadline, new_deadline, and changed_at.

**Validates: Requirements 14.2, 14.4, 14.5**

### Property 22: Submission Response Includes Reputation Change

*For any* passing submission, the response SHALL include a reputation_change object containing score_delta, new_score, and reason.

**Validates: Requirements 15.1, 15.2, 15.3, 15.4, 15.5**

### Property 23: Configuration Round-Trip

*For any* valid deadline_config.json object, parsing then pretty-printing then parsing SHALL produce an equivalent object.

**Validates: Requirements 16.4**

### Property 24: Configuration Usage in Deadline Calculation

*For any* milestone, the Architect SHALL use hours_to_days_ratio from deadline_config.json when calculating the deadline.

**Validates: Requirements 16.5**

### Property 25: Configuration Usage in Reputation Calculation

*For any* reputation update, the system SHALL use reputation_weights from deadline_config.json when calculating score deltas.

**Validates: Requirements 16.6**

## Error Handling

### Deadline Calculation Errors

**Invalid Estimated Hours:**
- If estimated_hours ≤ 0, reject milestone creation with 400 error
- Error message: "estimated_hours must be a positive integer"

**Configuration File Errors:**
- If deadline_config.json is missing, use default values (hours_to_days_ratio = 1.0)
- If deadline_config.json is malformed, log error and use defaults
- Error message: "Invalid deadline configuration, using defaults"

### Submission Errors

**Milestone Status Conflicts:**
- If milestone status != PENDING when submitting, reject with 400 error
- Error messages:
  - LOCKED: "Milestone is currently under review"
  - RELEASED: "Milestone already completed"
  - DISPUTED: "Milestone is disputed, resolve before resubmitting"

**Missing Deadline Data:**
- If deadline is null, treat as on-time (backward compatibility)
- Log warning: "Legacy milestone without deadline, treating as on-time"

### Reputation Update Errors

**User Not Found:**
- If user_id doesn't exist when updating reputation, create new reputation record with initial score 50
- Log: "Created new reputation record for user {user_id}"

**Score Calculation Overflow:**
- If calculated score < 0, clamp to 0
- If calculated score > 100, clamp to 100
- Log: "Reputation score clamped to valid range [0, 100]"

### API Errors

**GET /reputation/{user_id}:**
- 404 if user_id not found
- 500 if database query fails

**PATCH /milestone/{id}/deadline:**
- 400 if new_deadline is not valid ISO 8601
- 400 if milestone status is RELEASED
- 404 if milestone_id not found
- 500 if database update fails

**POST /submit:**
- 400 if milestone status != PENDING
- 404 if milestone_id or project_id not found
- 500 if inspection or payment processing fails

### Database Errors

**Connection Failures:**
- Retry database operations up to 3 times with exponential backoff
- If all retries fail, return 503 Service Unavailable
- Log: "Database connection failed after 3 retries"

**Constraint Violations:**
- If reputation_score constraint violated, clamp to [0, 100] and retry
- If timeline_status constraint violated, log error and use "on-time" as default
- Log: "Constraint violation, applied fallback value"

## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests to ensure comprehensive coverage:

**Unit Tests** focus on:
- Specific examples of deadline calculations (e.g., 8 hours → 8 days)
- Edge cases (null deadlines, released milestones, invalid timestamps)
- Error conditions (invalid config, missing users, constraint violations)
- Integration points between components

**Property-Based Tests** focus on:
- Universal properties that hold for all inputs
- Comprehensive input coverage through randomization
- Invariants that must be maintained across operations

### Property-Based Testing Configuration

**Library Selection:**
- Python: Use `hypothesis` library for property-based testing
- Install: `pip install hypothesis`

**Test Configuration:**
- Minimum 100 iterations per property test
- Each test must reference its design document property
- Tag format: `# Feature: payout-reputation-system, Property {number}: {property_text}`

**Example Property Test Structure:**

```python
from hypothesis import given, strategies as st
import hypothesis.strategies as st
from datetime import datetime, timedelta

# Feature: payout-reputation-system, Property 1: Deadline Calculation from Estimated Hours
@given(estimated_hours=st.integers(min_value=1, max_value=1000))
def test_deadline_calculation_from_estimated_hours(estimated_hours):
    """
    For any milestone with estimated_hours, the calculated deadline 
    SHALL equal creation_time plus (estimated_hours * hours_to_days_ratio) days
    """
    architect = ArchitectAgent(api_key=TEST_API_KEY)
    creation_time = datetime.utcnow()
    
    milestone = architect.generate_milestone_with_deadline(
        estimated_hours=estimated_hours,
        creation_time=creation_time
    )
    
    expected_deadline = creation_time + timedelta(days=estimated_hours * 1.0)
    actual_deadline = datetime.fromisoformat(milestone['deadline'].replace('Z', '+00:00'))
    
    # Allow 1 second tolerance for execution time
    assert abs((actual_deadline - expected_deadline).total_seconds()) < 1


# Feature: payout-reputation-system, Property 5: Timeline Status Determination
@given(
    deadline=st.datetimes(min_value=datetime(2024, 1, 1)),
    time_offset=st.integers(min_value=-100, max_value=100)
)
def test_timeline_status_determination(deadline, time_offset):
    """
    For any milestone with non-null deadline and submission_time,
    timeline_status SHALL be "on-time" if submission_time <= deadline,
    and "late" if submission_time > deadline
    """
    submission_time = deadline + timedelta(hours=time_offset)
    
    banker = BankerAgent(db=mock_db)
    timeline_status = banker._determine_timeline_status(
        submission_time.isoformat() + 'Z',
        deadline.isoformat() + 'Z'
    )
    
    if submission_time <= deadline:
        assert timeline_status == "on-time"
    else:
        assert timeline_status == "late"


# Feature: payout-reputation-system, Property 10: Reputation Score Delta Calculation
@given(
    timeline_status=st.sampled_from(["on-time", "late"]),
    pfi_score=st.floats(min_value=0, max_value=100)
)
def test_reputation_score_delta_calculation(timeline_status, pfi_score):
    """
    For any completed milestone, reputation score change SHALL be calculated as:
    timeline_delta (on-time: +2, late: -5) plus quality_delta 
    (PFI > 80: +1, PFI < 50: -2, else: 0)
    """
    reputation_manager = ReputationManager(db=mock_db)
    
    timeline_delta = reputation_manager._calculate_timeline_delta(timeline_status)
    quality_delta = reputation_manager._calculate_quality_delta(pfi_score)
    
    # Verify timeline delta
    if timeline_status == "on-time":
        assert timeline_delta == 2
    else:
        assert timeline_delta == -5
    
    # Verify quality delta
    if pfi_score > 80:
        assert quality_delta == 1
    elif pfi_score < 50:
        assert quality_delta == -2
    else:
        assert quality_delta == 0


# Feature: payout-reputation-system, Property 11: Reputation Score Clamping
@given(
    initial_score=st.floats(min_value=0, max_value=100),
    score_delta=st.integers(min_value=-200, max_value=200)
)
def test_reputation_score_clamping(initial_score, score_delta):
    """
    For any reputation score update, the resulting score SHALL be clamped 
    to the range [0, 100]
    """
    reputation_manager = ReputationManager(db=mock_db)
    
    new_score = reputation_manager._apply_score_change(initial_score, score_delta)
    
    assert 0 <= new_score <= 100
    
    # Verify clamping behavior
    expected = max(0, min(100, initial_score + score_delta))
    assert new_score == expected


# Feature: payout-reputation-system, Property 23: Configuration Round-Trip
@given(
    hours_to_days_ratio=st.floats(min_value=0.1, max_value=10.0),
    on_time_bonus=st.integers(min_value=0, max_value=10),
    late_penalty=st.integers(min_value=0, max_value=20),
    high_quality_bonus=st.integers(min_value=0, max_value=5),
    low_quality_penalty=st.integers(min_value=0, max_value=10)
)
def test_configuration_round_trip(
    hours_to_days_ratio,
    on_time_bonus,
    late_penalty,
    high_quality_bonus,
    low_quality_penalty
):
    """
    For any valid deadline_config.json object, parsing then pretty-printing 
    then parsing SHALL produce an equivalent object
    """
    original_config = {
        'hours_to_days_ratio': hours_to_days_ratio,
        'reputation_weights': {
            'on_time_bonus': on_time_bonus,
            'late_penalty': late_penalty,
            'high_quality_bonus': high_quality_bonus,
            'low_quality_penalty': low_quality_penalty
        }
    }
    
    # Serialize to JSON
    json_str = json.dumps(original_config, indent=2)
    
    # Parse back
    parsed_config = json.loads(json_str)
    
    # Verify equivalence
    assert parsed_config == original_config
```

### Unit Test Coverage

**Deadline Calculation:**
- Test specific example: 8 hours → 8 days deadline
- Test edge case: 1 hour → 1 day deadline
- Test large value: 1000 hours → 1000 days deadline
- Test with custom config: hours_to_days_ratio = 0.5

**Timeline Status:**
- Test exact deadline match (submission_time == deadline)
- Test 1 second before deadline
- Test 1 second after deadline
- Test null deadline (backward compatibility)

**Reputation Updates:**
- Test on-time + high quality (PFI 90): +3 total
- Test late + low quality (PFI 40): -7 total
- Test score at boundary (99 + 2 = 100, not 101)
- Test score at boundary (1 - 5 = 0, not -4)

**API Endpoints:**
- Test GET /reputation/{user_id} with existing user
- Test GET /reputation/{user_id} with non-existent user (404)
- Test PATCH /milestone/{id}/deadline with valid timestamp
- Test PATCH /milestone/{id}/deadline with invalid timestamp (400)
- Test PATCH /milestone/{id}/deadline on released milestone (400)

**Error Handling:**
- Test submission to LOCKED milestone (400)
- Test submission to RELEASED milestone (400)
- Test invalid ISO 8601 timestamp format
- Test missing deadline_config.json (uses defaults)
- Test malformed deadline_config.json (uses defaults)

### Integration Tests

**End-to-End Submission Flow:**
1. Create project with milestones (deadlines generated)
2. Submit code before deadline
3. Verify payment released
4. Verify timeline_status = "on-time"
5. Verify reputation increased by 2
6. Verify reputation_history contains event

**Late Submission Flow:**
1. Create milestone with deadline in past
2. Submit code
3. Verify payment released
4. Verify timeline_status = "late"
5. Verify reputation decreased by 5
6. Verify reputation_history contains penalty event

**Resubmission Flow:**
1. Submit code that fails inspection
2. Verify status = PENDING
3. Verify submission_time recorded
4. Resubmit code
5. Verify submission_time updated to latest
6. Verify payment released on pass

**Deadline Adjustment Flow:**
1. Create milestone with deadline
2. Adjust deadline via PATCH endpoint
3. Verify deadline updated in database
4. Verify audit log entry created
5. Attempt to adjust deadline on released milestone
6. Verify 400 error returned

### Test Data Generators

**Hypothesis Strategies:**

```python
# Generate valid ISO 8601 timestamps
iso_timestamps = st.datetimes(
    min_value=datetime(2024, 1, 1),
    max_value=datetime(2030, 12, 31)
).map(lambda dt: dt.isoformat() + 'Z')

# Generate milestone data
milestones = st.fixed_dictionaries({
    'id': st.uuids().map(str),
    'title': st.text(min_size=1, max_size=200),
    'estimated_hours': st.integers(min_value=1, max_value=1000),
    'deadline': iso_timestamps
})

# Generate reputation events
reputation_events = st.fixed_dictionaries({
    'timestamp': iso_timestamps,
    'event_type': st.sampled_from([
        'on_time_delivery', 
        'late_delivery', 
        'high_quality', 
        'low_quality'
    ]),
    'score_change': st.integers(min_value=-20, max_value=20),
    'milestone_id': st.uuids().map(str),
    'resulting_score': st.floats(min_value=0, max_value=100)
})

# Generate deadline configs
deadline_configs = st.fixed_dictionaries({
    'hours_to_days_ratio': st.floats(min_value=0.1, max_value=10.0),
    'reputation_weights': st.fixed_dictionaries({
        'on_time_bonus': st.integers(min_value=0, max_value=10),
        'late_penalty': st.integers(min_value=0, max_value=20),
        'high_quality_bonus': st.integers(min_value=0, max_value=5),
        'low_quality_penalty': st.integers(min_value=0, max_value=10)
    })
})
```

### Test Execution

**Run all tests:**
```bash
pytest tests/ -v --hypothesis-show-statistics
```

**Run only property-based tests:**
```bash
pytest tests/ -v -k "property" --hypothesis-show-statistics
```

**Run with increased iterations:**
```bash
pytest tests/ -v --hypothesis-seed=random --hypothesis-max-examples=1000
```

**Generate coverage report:**
```bash
pytest tests/ --cov=agents --cov=backend --cov-report=html
```

### Success Criteria

- All property-based tests pass with 100+ iterations
- All unit tests pass
- Code coverage ≥ 85% for new modules
- Integration tests pass end-to-end
- No regressions in existing functionality
- All edge cases handled gracefully
