# Requirements Document

## Introduction

The Payout and Reputation System extends the Pillar Protocol platform to include time-bound milestone tracking, deadline-aware payout logic, and developer reputation scoring. This system integrates with existing agents (Architect, Inspector, Banker) to track on-time vs late deliveries, adjust payouts accordingly, and maintain a historical reputation score for each developer based on delivery timeliness and code quality.

## Glossary

- **Milestone**: A unit of work with requirements, estimated hours, deadline, and escrow status
- **Architect_Agent**: AI agent that generates milestones with requirements and timelines
- **Inspector_Agent**: AI agent that validates code submissions and provides PFI scores (0-100)
- **Banker_Agent**: Agent that manages escrow states and payment releases
- **PFI_Score**: Performance-Financial Index score (0-100) measuring code quality
- **Deadline**: The timestamp by which a milestone must be completed
- **Submission_Time**: The timestamp when code is submitted for a milestone
- **Timeline_Status**: Classification of submission as "on-time" or "late"
- **Reputation_Score**: Aggregate score tracking developer reliability and quality
- **Escrow_Status**: Current state of milestone payment (PENDING, LOCKED, RELEASED, DISPUTED)
- **Database**: Supabase database storing projects, milestones, and reputation data
- **Developer**: User who submits code for milestones
- **Completion_Status**: Result from Inspector (PASS or FAIL)

## Requirements

### Requirement 1: Milestone Deadline Generation

**User Story:** As a project owner, I want milestones to include realistic deadlines, so that developers have clear time expectations.

#### Acceptance Criteria

1. WHEN Architect_Agent generates a milestone, THE Architect_Agent SHALL calculate a deadline based on estimated_hours
2. THE Architect_Agent SHALL use a conversion rate of 1 estimated_hour equals 1 calendar day for deadline calculation
3. THE Architect_Agent SHALL store the deadline as an ISO 8601 timestamp in the milestone record
4. THE Architect_Agent SHALL set the deadline relative to the milestone creation timestamp
5. WHERE a milestone has estimated_hours of 8, THE Architect_Agent SHALL set a deadline 8 days from creation

### Requirement 2: Deadline Storage and Retrieval

**User Story:** As a developer, I want to see milestone deadlines, so that I know when work is due.

#### Acceptance Criteria

1. THE Database SHALL store a deadline field for each milestone as a timestamp
2. WHEN a milestone is created, THE Database SHALL persist the deadline value
3. WHEN a milestone is retrieved, THE Database SHALL return the deadline field
4. THE deadline field SHALL be nullable to support legacy milestones without deadlines

### Requirement 3: Submission Time Tracking

**User Story:** As the system, I want to record when code is submitted, so that I can compare against deadlines.

#### Acceptance Criteria

1. WHEN code is submitted for a milestone, THE Banker_Agent SHALL record the submission timestamp
2. THE Banker_Agent SHALL store submission_time as an ISO 8601 timestamp in the milestone record
3. THE submission_time SHALL be set when milestone status transitions to LOCKED
4. WHEN a milestone is resubmitted after failure, THE Banker_Agent SHALL update submission_time to the latest submission

### Requirement 4: Timeline Status Determination

**User Story:** As the system, I want to determine if submissions are on-time or late, so that I can adjust payouts and reputation.

#### Acceptance Criteria

1. WHEN code passes inspection, THE Banker_Agent SHALL compare submission_time against deadline
2. IF submission_time is less than or equal to deadline, THEN THE Banker_Agent SHALL classify Timeline_Status as "on-time"
3. IF submission_time is greater than deadline, THEN THE Banker_Agent SHALL classify Timeline_Status as "late"
4. IF deadline is null, THEN THE Banker_Agent SHALL classify Timeline_Status as "on-time" for backward compatibility
5. THE Banker_Agent SHALL store Timeline_Status in the milestone record

### Requirement 5: On-Time Payout Release

**User Story:** As a developer, I want to receive full payment when I complete work on time, so that I am rewarded for timely delivery.

#### Acceptance Criteria

1. WHEN Completion_Status is PASS and Timeline_Status is "on-time", THE Banker_Agent SHALL release full payment
2. THE Banker_Agent SHALL update milestone Escrow_Status to RELEASED
3. THE Banker_Agent SHALL execute the x402 payment protocol with full milestone amount
4. THE Banker_Agent SHALL log the payment transaction with timestamp and amount

### Requirement 6: Late Payout Release with Reputation Impact

**User Story:** As a project owner, I want late deliveries to affect developer reputation while still releasing payment, so that quality work is compensated but timeliness is tracked.

#### Acceptance Criteria

1. WHEN Completion_Status is PASS and Timeline_Status is "late", THE Banker_Agent SHALL release full payment
2. THE Banker_Agent SHALL update milestone Escrow_Status to RELEASED
3. THE Banker_Agent SHALL trigger a reputation penalty for late delivery
4. THE reputation penalty SHALL be recorded in the developer's reputation history
5. THE Banker_Agent SHALL log the late delivery event with submission_time and deadline

### Requirement 7: Incomplete Submission Handling

**User Story:** As a developer, I want clear feedback when my submission is incomplete, so that I know what to fix.

#### Acceptance Criteria

1. WHEN Completion_Status is FAIL, THE Banker_Agent SHALL not release payment
2. THE Banker_Agent SHALL update milestone Escrow_Status to PENDING to allow resubmission
3. THE Inspector_Agent SHALL return a feedback message listing missing requirements
4. THE Inspector_Agent SHALL return the list of missing_requirements from the inspection
5. THE system SHALL allow the developer to resubmit code for the same milestone

### Requirement 8: Reputation Score Calculation

**User Story:** As a platform administrator, I want to track developer reputation based on delivery and quality, so that reliable developers are identifiable.

#### Acceptance Criteria

1. THE Database SHALL store a reputation_score field for each developer as a float between 0 and 100
2. WHEN a milestone is completed on-time, THE Database SHALL increase reputation_score by 2 points
3. WHEN a milestone is completed late, THE Database SHALL decrease reputation_score by 5 points
4. WHEN a milestone achieves PFI_Score above 80, THE Database SHALL increase reputation_score by 1 point
5. WHEN a milestone achieves PFI_Score below 50, THE Database SHALL decrease reputation_score by 2 points
6. THE reputation_score SHALL not exceed 100 or fall below 0
7. THE Database SHALL initialize new developers with reputation_score of 50

### Requirement 9: Reputation History Tracking

**User Story:** As a developer, I want to see my reputation history, so that I can track my performance over time.

#### Acceptance Criteria

1. THE Database SHALL store a reputation_history array for each developer
2. WHEN reputation_score changes, THE Database SHALL append an entry to reputation_history
3. EACH reputation_history entry SHALL include timestamp, event_type, score_change, milestone_id, and resulting_score
4. THE event_type field SHALL be one of: "on_time_delivery", "late_delivery", "high_quality", "low_quality"
5. THE Database SHALL retain all reputation_history entries indefinitely

### Requirement 10: Reputation Retrieval API

**User Story:** As a frontend application, I want to retrieve developer reputation data, so that I can display it to users.

#### Acceptance Criteria

1. THE API SHALL provide a GET endpoint at /reputation/{user_id}
2. WHEN the endpoint is called, THE API SHALL return reputation_score, total_milestones_completed, on_time_count, late_count, and reputation_history
3. IF the user_id does not exist, THEN THE API SHALL return a 404 status code
4. THE API SHALL return reputation data in JSON format
5. THE response SHALL include average_pfi_score calculated from all completed milestones

### Requirement 11: Deadline Display in Milestone Data

**User Story:** As a frontend application, I want milestone data to include deadlines, so that I can show them to developers.

#### Acceptance Criteria

1. WHEN the API returns milestone data, THE API SHALL include the deadline field
2. THE deadline field SHALL be formatted as an ISO 8601 timestamp string
3. WHEN a milestone has no deadline, THE API SHALL return null for the deadline field
4. THE API SHALL include a days_remaining field calculated as deadline minus current time in days
5. IF days_remaining is negative, THE milestone SHALL be marked as overdue

### Requirement 12: Timeline Compliance Metrics

**User Story:** As a platform administrator, I want aggregate timeline metrics, so that I can monitor platform performance.

#### Acceptance Criteria

1. THE Database SHALL track total_on_time_deliveries for each developer
2. THE Database SHALL track total_late_deliveries for each developer
3. THE Database SHALL calculate on_time_percentage as (total_on_time_deliveries / total_deliveries) * 100
4. WHEN reputation data is retrieved, THE API SHALL include on_time_percentage in the response
5. THE on_time_percentage SHALL be rounded to 2 decimal places

### Requirement 13: Backward Compatibility for Legacy Milestones

**User Story:** As a system maintainer, I want existing milestones without deadlines to continue functioning, so that the system remains stable.

#### Acceptance Criteria

1. WHEN a milestone has a null deadline, THE Banker_Agent SHALL treat it as on-time for payout purposes
2. WHEN a milestone has a null deadline, THE reputation calculation SHALL not apply timeline-based adjustments
3. THE Inspector_Agent SHALL continue to validate code regardless of deadline presence
4. THE API SHALL return legacy milestones with deadline field set to null

### Requirement 14: Deadline Adjustment API

**User Story:** As a project owner, I want to adjust milestone deadlines when scope changes, so that deadlines remain realistic.

#### Acceptance Criteria

1. THE API SHALL provide a PATCH endpoint at /milestone/{milestone_id}/deadline
2. WHEN the endpoint is called with a new deadline timestamp, THE Database SHALL update the milestone deadline
3. IF the milestone Escrow_Status is RELEASED, THEN THE API SHALL return a 400 status code with error message
4. THE API SHALL validate that the new deadline is a valid ISO 8601 timestamp
5. THE Database SHALL log deadline changes in an audit trail with old_deadline, new_deadline, and changed_at timestamp

### Requirement 15: Reputation Impact Notification

**User Story:** As a developer, I want to be notified when my reputation changes, so that I understand the impact of my work.

#### Acceptance Criteria

1. WHEN reputation_score changes, THE API SHALL include reputation_change in the submission response
2. THE reputation_change field SHALL include score_delta, new_score, and reason
3. THE reason field SHALL describe why reputation changed (e.g., "On-time delivery bonus" or "Late delivery penalty")
4. WHEN Completion_Status is PASS, THE submission response SHALL include the reputation impact
5. THE submission response SHALL include the updated reputation_score

### Requirement 16: Parser and Pretty Printer for Deadline Configuration

**User Story:** As a system administrator, I want to configure deadline calculation rules via a configuration file, so that I can adjust policies without code changes.

#### Acceptance Criteria

1. THE system SHALL parse a deadline_config.json file containing hours_to_days_ratio and reputation_weights
2. WHEN the configuration file is invalid, THE Parser SHALL return a descriptive error message
3. THE Pretty_Printer SHALL format deadline configuration objects back into valid JSON files
4. FOR ALL valid deadline configuration objects, parsing then printing then parsing SHALL produce an equivalent object (round-trip property)
5. THE Architect_Agent SHALL use the hours_to_days_ratio from configuration when calculating deadlines
6. THE Database SHALL use reputation_weights from configuration when adjusting reputation scores
