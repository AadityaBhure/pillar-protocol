# Implementation Plan: Payout and Reputation System

## Overview

This implementation plan breaks down the payout and reputation system into discrete coding tasks. The system adds deadline tracking, timeline-based payout logic, and developer reputation scoring to the existing Pillar Protocol platform. Implementation follows a bottom-up approach: database schema first, then core modules, then agent updates, then API endpoints, and finally frontend integration.

## Tasks

- [x] 1. Database schema updates and configuration file
  - [x] 1.1 Add new fields to milestones table
    - Add `deadline` TIMESTAMP field (nullable for backward compatibility)
    - Add `submission_time` TIMESTAMP field (set when status → LOCKED)
    - Add `timeline_status` VARCHAR(20) field with CHECK constraint ('on-time', 'late', or NULL)
    - Create indexes on `deadline` and `timeline_status` columns
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 4.5_
  
  - [x] 1.2 Add reputation fields to users table
    - Add `reputation_score` DECIMAL(5,2) field with DEFAULT 50.00 and CHECK constraint (0-100)
    - Add `total_on_time_deliveries` INTEGER field with DEFAULT 0
    - Add `total_late_deliveries` INTEGER field with DEFAULT 0
    - Add `reputation_history` JSONB field with DEFAULT '[]'
    - Create index on `reputation_score` column
    - _Requirements: 8.1, 8.7, 9.1, 12.1, 12.2_
  
  - [x] 1.3 Create deadline_audit table
    - Create table with fields: id (UUID), milestone_id (FK), old_deadline, new_deadline, changed_at, changed_by (FK to users), reason (TEXT), created_at
    - Create indexes on `milestone_id` and `changed_at` columns
    - _Requirements: 14.5_
  
  - [x] 1.4 Create deadline_config.json configuration file
    - Create file in project root with default values: hours_to_days_ratio = 1.0
    - Add reputation_weights: on_time_bonus = 2, late_penalty = 5, high_quality_bonus = 1, low_quality_penalty = 2
    - _Requirements: 16.1, 16.5, 16.6_
  
  - [x] 1.5 Update DatabaseManager with new methods
    - Add `update_milestone_submission_time(milestone_id, submission_time)` method
    - Add `update_milestone_timeline_status(milestone_id, timeline_status)` method
    - Add `update_milestone_deadline(milestone_id, new_deadline)` method
    - Add `log_deadline_change(milestone_id, old_deadline, new_deadline, changed_at)` method
    - Add `get_user_reputation(user_id)` method (returns reputation_score, counters, history)
    - Add `update_user_reputation_score(user_id, new_score, events)` method
    - Add `increment_on_time_count(user_id)` and `increment_late_count(user_id)` methods
    - Add `get_milestone(milestone_id)` method (returns full milestone data)
    - _Requirements: 2.2, 3.3, 4.5, 8.1, 9.2, 10.1, 12.1, 12.2, 14.2, 14.5_

- [x] 2. Create Reputation Manager module
  - [x] 2.1 Implement ReputationManager class with core methods
    - Create `agents/reputation_manager.py` file
    - Implement `__init__(db_connection)` with config loading
    - Implement `_load_config()` method to parse deadline_config.json with fallback to defaults
    - Implement `_calculate_timeline_delta(timeline_status)` returning +2 for on-time, -5 for late
    - Implement `_calculate_quality_delta(pfi_score)` returning +1 for PFI>80, -2 for PFI<50, 0 otherwise
    - _Requirements: 8.2, 8.3, 8.4, 8.5, 16.1, 16.6_
  
  - [x] 2.2 Implement reputation update logic
    - Implement `update_reputation(user_id, milestone_id, timeline_status, pfi_score)` method
    - Calculate total_delta = timeline_delta + quality_delta
    - Clamp new_score to [0, 100] range
    - Create reputation_history events with timestamp, event_type, score_change, milestone_id, resulting_score
    - Call database methods to persist score and increment counters
    - Return dict with score_delta, new_score, events
    - _Requirements: 6.3, 6.4, 8.1, 8.6, 9.1, 9.2, 9.3, 9.4, 12.1, 12.2_
  
  - [x] 2.3 Implement reputation retrieval logic
    - Implement `get_reputation(user_id)` method
    - Calculate on_time_percentage = (on_time_count / total) * 100, rounded to 2 decimals
    - Return dict with reputation_score, total_milestones_completed, on_time_count, late_count, on_time_percentage, average_pfi_score, reputation_history
    - Handle new users by returning default values (score=50, counts=0)
    - _Requirements: 8.7, 10.2, 10.4, 10.5, 12.3, 12.4, 12.5_
  
  - [ ]* 2.4 Write property test for reputation score delta calculation
    - **Property 10: Reputation Score Delta Calculation**
    - **Validates: Requirements 8.2, 8.3, 8.4, 8.5**
  
  - [ ]* 2.5 Write property test for reputation score clamping
    - **Property 11: Reputation Score Clamping**
    - **Validates: Requirements 8.1, 8.6**
  
  - [ ]* 2.6 Write unit tests for ReputationManager
    - Test on-time + high quality: +3 total
    - Test late + low quality: -7 total
    - Test score boundary: 99 + 2 = 100
    - Test score boundary: 1 - 5 = 0
    - Test new developer initialization: score = 50
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

- [x] 3. Update Architect Agent with deadline calculation
  - [x] 3.1 Add deadline calculation to generate_checklist method
    - Load deadline_config.json in `_load_deadline_config()` method with fallback to defaults
    - Implement `_calculate_deadline(estimated_hours)` method
    - Calculate days = estimated_hours * hours_to_days_ratio from config
    - Calculate deadline_dt = current_time + timedelta(days=days)
    - Return ISO 8601 timestamp string with 'Z' suffix
    - Add deadline field to each milestone dict before returning
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 16.5_
  
  - [ ]* 3.2 Write property test for deadline calculation
    - **Property 1: Deadline Calculation from Estimated Hours**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**
  
  - [ ]* 3.3 Write unit tests for deadline calculation
    - Test 8 hours → 8 days deadline
    - Test 1 hour → 1 day deadline
    - Test 1000 hours → 1000 days deadline
    - Test custom config: hours_to_days_ratio = 0.5
    - Test ISO 8601 format validation
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 4. Update Banker Agent with timeline tracking
  - [x] 4.1 Update lock_milestone to record submission_time
    - Modify `lock_milestone(milestone_id)` method
    - Generate submission_time = datetime.utcnow().isoformat() + 'Z'
    - Call `db.update_milestone_submission_time(milestone_id, submission_time)` after status update
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [x] 4.2 Implement timeline status determination
    - Implement `_determine_timeline_status(submission_time, deadline)` method
    - Return "on-time" if deadline is None (backward compatibility)
    - Parse ISO 8601 timestamps to datetime objects
    - Return "on-time" if submission_dt <= deadline_dt, else "late"
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 13.1_
  
  - [x] 4.3 Update release_payment to trigger reputation updates
    - Modify `release_payment(milestone_id, user_id, pfi_score)` method signature
    - Get milestone data including deadline and submission_time from database
    - Call `_determine_timeline_status()` to get timeline_status
    - Update milestone timeline_status in database
    - Release payment (full amount regardless of timeline_status)
    - Initialize ReputationManager and call `update_reputation()`
    - Return dict with status, payment, timeline_status, reputation_change
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 6.1, 6.2, 6.3, 6.4, 6.5_
  
  - [x] 4.4 Update submission_time on resubmission
    - Ensure `lock_milestone()` updates submission_time even for resubmissions
    - Verify that failed inspections reset status to PENDING
    - _Requirements: 3.4, 7.2, 7.5_
  
  - [ ]* 4.5 Write property test for timeline status determination
    - **Property 5: Timeline Status Determination**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.5**
  
  - [ ]* 4.6 Write unit tests for Banker Agent updates
    - Test submission_time recording on lock
    - Test timeline status: submission == deadline
    - Test timeline status: 1 second before deadline
    - Test timeline status: 1 second after deadline
    - Test null deadline returns "on-time"
    - Test payment release for on-time submission
    - Test payment release for late submission
    - Test reputation trigger on completion
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4, 5.1, 6.1, 13.1_

- [ ] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Add API endpoints for reputation and deadline management
  - [x] 6.1 Implement GET /reputation/{user_id} endpoint
    - Create endpoint in `backend/main.py`
    - Initialize ReputationManager with database connection
    - Call `reputation_manager.get_reputation(user_id)`
    - Return JSON response with reputation_score, total_milestones_completed, on_time_count, late_count, on_time_percentage, average_pfi_score, reputation_history
    - Return 404 if user not found
    - Handle exceptions with 500 error
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [x] 6.2 Implement PATCH /milestone/{milestone_id}/deadline endpoint
    - Create endpoint in `backend/main.py`
    - Accept request body with `new_deadline` field (ISO 8601 timestamp)
    - Validate ISO 8601 format, return 400 if invalid
    - Get milestone from database, return 404 if not found
    - Check milestone status, return 400 if RELEASED
    - Update deadline in database and log audit trail
    - Return response with status, milestone_id, old_deadline, new_deadline, changed_at
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_
  
  - [x] 6.3 Update POST /submit endpoint to include reputation change
    - Modify `submit_code()` endpoint in `backend/main.py`
    - Update `banker.release_payment()` call to pass user_id and pfi_score
    - Include reputation_change in SubmitResponse
    - Update SubmitResponse model to include optional reputation_change field
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5_
  
  - [x] 6.4 Update milestone API responses to include deadline and days_remaining
    - Modify `get_project()` endpoint to include deadline field in milestone data
    - Calculate days_remaining = (deadline - current_time).days for each milestone
    - Set overdue flag if days_remaining < 0
    - Return null for deadline if not set (backward compatibility)
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [ ]* 6.5 Write unit tests for API endpoints
    - Test GET /reputation/{user_id} with existing user
    - Test GET /reputation/{user_id} with non-existent user (404)
    - Test PATCH /milestone/{id}/deadline with valid timestamp
    - Test PATCH /milestone/{id}/deadline with invalid timestamp (400)
    - Test PATCH /milestone/{id}/deadline on released milestone (400)
    - Test POST /submit includes reputation_change in response
    - Test milestone response includes deadline and days_remaining
    - Test overdue flag when days_remaining < 0
    - _Requirements: 10.1, 10.3, 11.1, 11.4, 11.5, 14.1, 14.3, 15.4_

- [x] 7. Update models and error handling
  - [x] 7.1 Update Pydantic models in backend/models.py
    - Add optional `deadline` field to Milestone model (str or None)
    - Add optional `submission_time` field to Milestone model (datetime or None)
    - Add optional `timeline_status` field to Milestone model (Literal["on-time", "late"] or None)
    - Add optional `reputation_change` field to SubmitResponse model (dict or None)
    - _Requirements: 2.4, 3.2, 4.5, 15.2_
  
  - [x] 7.2 Implement error handling for deadline operations
    - Add validation for ISO 8601 timestamps in API endpoints
    - Add error handling for missing deadline_config.json (use defaults)
    - Add error handling for malformed deadline_config.json (log error, use defaults)
    - Add error messages for milestone status conflicts (LOCKED, RELEASED, DISPUTED)
    - Add error handling for reputation score constraint violations (clamp to [0, 100])
    - _Requirements: 7.1, 7.2, 13.1, 13.2, 13.3, 14.3_
  
  - [ ]* 7.3 Write unit tests for error handling
    - Test submission to LOCKED milestone (400)
    - Test submission to RELEASED milestone (400)
    - Test invalid ISO 8601 timestamp format
    - Test missing deadline_config.json (uses defaults)
    - Test malformed deadline_config.json (uses defaults)
    - Test reputation score clamping on constraint violation

- [x] 8. Frontend updates for deadline and reputation display
  - [x] 8.1 Update milestone display to show deadline and days remaining
    - Modify milestone rendering in `script.js` to display deadline field
    - Calculate and display days_remaining for each milestone
    - Add visual indicator for overdue milestones (days_remaining < 0)
    - Format deadline as human-readable date string
    - _Requirements: 11.1, 11.4, 11.5_
  
  - [x] 8.2 Add reputation display section
    - Create reputation display component showing reputation_score
    - Display on_time_percentage, total_milestones_completed, on_time_count, late_count
    - Add reputation_history timeline visualization
    - Fetch reputation data from GET /reputation/{user_id} endpoint
    - _Requirements: 10.2, 10.4, 10.5, 12.3, 12.4_
  
  - [x] 8.3 Add deadline adjustment UI
    - Create deadline adjustment form for project owners
    - Call PATCH /milestone/{id}/deadline endpoint
    - Display success/error messages
    - Disable adjustment for RELEASED milestones
    - _Requirements: 14.1, 14.2, 14.3_
  
  - [x] 8.4 Update submission feedback to show reputation impact
    - Display reputation_change in submission response
    - Show score_delta, new_score, and reason to developer
    - Add visual feedback for reputation increase/decrease
    - _Requirements: 15.1, 15.2, 15.3, 15.5_

- [ ] 9. Integration testing and backward compatibility
  - [ ]* 9.1 Write integration test for on-time submission flow
    - Create project with milestones (deadlines generated)
    - Submit code before deadline
    - Verify payment released
    - Verify timeline_status = "on-time"
    - Verify reputation increased by 2
    - Verify reputation_history contains event
    - _Requirements: 1.1, 3.1, 4.2, 5.1, 6.3, 8.2, 9.2_
  
  - [ ]* 9.2 Write integration test for late submission flow
    - Create milestone with deadline in past
    - Submit code
    - Verify payment released
    - Verify timeline_status = "late"
    - Verify reputation decreased by 5
    - Verify reputation_history contains penalty event
    - _Requirements: 4.3, 6.1, 6.3, 8.3, 9.2_
  
  - [ ]* 9.3 Write integration test for resubmission flow
    - Submit code that fails inspection
    - Verify status = PENDING
    - Verify submission_time recorded
    - Resubmit code
    - Verify submission_time updated to latest
    - Verify payment released on pass
    - _Requirements: 3.4, 7.2, 7.5_
  
  - [ ]* 9.4 Write integration test for deadline adjustment flow
    - Create milestone with deadline
    - Adjust deadline via PATCH endpoint
    - Verify deadline updated in database
    - Verify audit log entry created
    - Attempt to adjust deadline on released milestone
    - Verify 400 error returned
    - _Requirements: 14.2, 14.4, 14.5_
  
  - [ ]* 9.5 Write integration test for backward compatibility
    - Create legacy milestone with null deadline
    - Submit code
    - Verify timeline_status = "on-time"
    - Verify payment released
    - Verify no timeline-based reputation adjustment
    - Verify Inspector validates code regardless of deadline
    - _Requirements: 13.1, 13.2, 13.3, 13.4_
  
  - [ ]* 9.6 Write property test for configuration round-trip
    - **Property 23: Configuration Round-Trip**
    - **Validates: Requirements 16.4**

- [ ] 10. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- Integration tests verify end-to-end flows
- Backward compatibility is maintained for legacy milestones without deadlines
- Full payment is released for both on-time and late deliveries; reputation tracks timeliness
- Configuration file allows policy adjustments without code changes
