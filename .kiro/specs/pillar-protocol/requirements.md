# Requirements Document: Pillar Protocol

## Introduction

The Pillar Protocol is a multi-agent AI platform that transforms vague project ideas into structured milestones, manages payment escrow with state-based locking, validates code submissions against requirements, and maintains developer reputation scores. The system consists of four specialized AI agents (Architect, Banker, Inspector, Bureau) working together to provide a complete workflow from project conception through code delivery and reputation assessment.

## Glossary

- **System**: The complete Pillar Protocol platform including all four agents and supporting infrastructure
- **Architect_Agent**: AI agent responsible for converting user prompts into structured milestone checklists
- **Banker_Agent**: State machine agent managing escrow status and payment locking
- **Inspector_Agent**: Code analysis agent that validates submissions against requirements
- **Bureau_Agent**: Reputation engine that calculates PFI scores and tracks developer performance
- **Milestone**: A structured project deliverable with title, description, requirements, and estimated hours
- **Escrow_Status**: State of a milestone's payment (PENDING, LOCKED, RELEASED, DISPUTED)
- **PFI**: Performance/Financial Index - a reputation score from 0-100
- **Logic_Coverage**: Verification that code implements requirements with actual functionality, not just imports
- **Code_Blob**: Concatenated code files with delimiter tags for analysis
- **Gemini_API**: Google's generative AI service used for prompt analysis and code inspection
- **Supabase**: PostgreSQL database service used for data persistence
- **x402_Protocol**: Simulated payment protocol for escrow management

## Requirements

### Requirement 1: Prompt to Milestone Conversion

**User Story:** As a user, I want to convert vague project ideas into structured milestone checklists, so that I can have a clear project plan.

#### Acceptance Criteria

1. WHEN a user submits a non-empty prompt THEN THE Architect_Agent SHALL generate at least one milestone with valid schema
2. WHEN the Architect_Agent generates milestones THEN THE System SHALL validate each milestone contains id, title, description, requirements list, and estimated_hours
3. WHEN the Gemini_API returns a response THEN THE Architect_Agent SHALL parse it as JSON to prevent hallucinations
4. IF the Gemini_API returns invalid JSON THEN THE System SHALL return an error message and allow retry
5. WHEN milestones are generated THEN THE System SHALL store them in the database with the project_id
6. WHEN milestone requirements are created THEN THE System SHALL ensure the requirements list is non-empty
7. WHEN estimated_hours is set THEN THE System SHALL ensure it is a positive integer

### Requirement 2: Code Submission and File Handling

**User Story:** As a developer, I want to upload code files for milestone validation, so that my work can be evaluated against requirements.

#### Acceptance Criteria

1. WHEN a user uploads code files THEN THE System SHALL accept multiple files in a single submission
2. WHEN files are uploaded THEN THE System SHALL validate file types are supported code formats (.py, .js, .ts, .java, .cpp, .c, .go, .rs)
3. WHEN file size is checked THEN THE System SHALL reject files larger than 10MB
4. WHEN total upload size is checked THEN THE System SHALL reject submissions larger than 50MB
5. WHEN files are processed THEN THE Inspector_Agent SHALL concatenate them with [FILE_START:filename] and [FILE_END:filename] delimiters
6. WHEN files are concatenated THEN THE System SHALL preserve all file content without modification
7. WHEN files are concatenated THEN THE System SHALL maintain the order of files from the upload
8. IF file upload fails THEN THE System SHALL return a 400 error with specific validation message

### Requirement 3: Code Analysis and Logic Coverage

**User Story:** As a project owner, I want uploaded code to be analyzed for logic coverage, so that I can verify requirements are actually implemented.

#### Acceptance Criteria

1. WHEN code is submitted THEN THE Inspector_Agent SHALL analyze it against the milestone requirements list
2. WHEN analyzing code THEN THE Inspector_Agent SHALL verify functions are both defined AND actually used
3. WHEN analyzing code THEN THE Inspector_Agent SHALL check for real functionality, not just imports
4. WHEN analysis completes THEN THE Inspector_Agent SHALL return a coverage_score between 0 and 100
5. WHEN analysis completes THEN THE Inspector_Agent SHALL return a boolean passed status
6. WHEN analysis completes THEN THE Inspector_Agent SHALL provide detailed feedback text
7. IF requirements are not met THEN THE Inspector_Agent SHALL list specific missing_requirements
8. WHEN code is analyzed THEN THE System SHALL generate a SHA256 hash of the code_blob for tracking
9. IF the Gemini_API fails during analysis THEN THE System SHALL return an error and keep the milestone locked for retry

### Requirement 4: Escrow State Management

**User Story:** As a system administrator, I want milestone escrow states to be managed with strict locking rules, so that payments are protected during code review.

#### Acceptance Criteria

1. WHEN a milestone is created THEN THE Banker_Agent SHALL set its status to PENDING
2. WHEN code is submitted for a milestone THEN THE Banker_Agent SHALL change status to LOCKED
3. WHILE a milestone status is LOCKED THEN THE System SHALL prevent deletion of that milestone
4. WHEN a user attempts to delete a locked milestone THEN THE System SHALL return a 403 Forbidden error
5. WHEN code inspection passes THEN THE Banker_Agent SHALL change status to RELEASED
6. WHEN status changes to RELEASED THEN THE Banker_Agent SHALL trigger payment release
7. WHEN milestone status is queried THEN THE Banker_Agent SHALL return one of: PENDING, LOCKED, RELEASED, or DISPUTED
8. WHEN a milestone is in PENDING status THEN THE System SHALL allow deletion

### Requirement 5: PFI Reputation Calculation

**User Story:** As a developer, I want my performance tracked with a reputation score, so that I can demonstrate my track record to potential clients.

#### Acceptance Criteria

1. WHEN code inspection passes THEN THE Bureau_Agent SHALL calculate a PFI score
2. WHEN calculating PFI THEN THE Bureau_Agent SHALL compute a performance_score between 0 and 100
3. WHEN calculating PFI THEN THE Bureau_Agent SHALL compute a financial_score between 0 and 100
4. WHEN calculating combined_pfi THEN THE Bureau_Agent SHALL use 60% performance weight and 40% financial weight
5. WHEN performance_score is calculated THEN THE Bureau_Agent SHALL base it on inspection coverage_score
6. WHEN financial_score is calculated THEN THE Bureau_Agent SHALL base it on project completion rate
7. WHEN a user has historical data THEN THE Bureau_Agent SHALL incorporate average_coverage with 30% weight
8. WHEN a user has historical data THEN THE Bureau_Agent SHALL incorporate success_rate with 30% weight
9. WHEN PFI is calculated THEN THE Bureau_Agent SHALL update the user reputation record in the database
10. WHEN PFI is calculated THEN THE Bureau_Agent SHALL append a PFISnapshot to reputation_history

### Requirement 6: API Endpoint Functionality

**User Story:** As a frontend developer, I want well-defined API endpoints, so that I can build a responsive user interface.

#### Acceptance Criteria

1. WHEN POST /plan is called with valid prompt and user_id THEN THE System SHALL return project_id and milestones list
2. WHEN POST /submit is called with files and milestone_id THEN THE System SHALL return passed status, feedback, and pfi_score
3. WHEN GET /project/{project_id} is called THEN THE System SHALL return project state with all milestones
4. WHEN DELETE /milestone/{milestone_id} is called on unlocked milestone THEN THE System SHALL delete it and return success
5. WHEN DELETE /milestone/{milestone_id} is called on locked milestone THEN THE System SHALL return 403 Forbidden
6. WHEN any endpoint receives invalid input THEN THE System SHALL return appropriate 400 error with message
7. WHEN database connection fails THEN THE System SHALL return 503 Service Unavailable
8. WHEN Gemini_API fails THEN THE System SHALL return 500 error with retry message

### Requirement 7: Frontend Dashboard Interface

**User Story:** As a user, I want an intuitive dashboard with AI startup aesthetic, so that I can easily manage projects and view reputation.

#### Acceptance Criteria

1. WHEN the dashboard loads THEN THE System SHALL display a search interface with tab switching
2. WHEN milestones are rendered THEN THE System SHALL show title, description, requirements, and status for each
3. WHEN a milestone status is LOCKED THEN THE System SHALL disable the delete button for that milestone
4. WHEN a milestone status is PENDING THEN THE System SHALL enable the delete button for that milestone
5. WHEN PFI score is received THEN THE System SHALL animate the PFI gauge using CSS transitions
6. WHEN file upload input is displayed THEN THE System SHALL accept multiple file selection
7. WHEN the user interface renders THEN THE System SHALL use terminal-style styling with glow effects
8. WHEN tabs are switched THEN THE System SHALL update the displayed content without page reload

### Requirement 8: Data Validation and Schema Enforcement

**User Story:** As a system architect, I want strict data validation, so that data integrity is maintained throughout the system.

#### Acceptance Criteria

1. WHEN a project is created THEN THE System SHALL validate id is a valid UUID
2. WHEN a project is created THEN THE System SHALL validate user_id references an existing user
3. WHEN a milestone is created THEN THE System SHALL validate title is non-empty and max 200 characters
4. WHEN a milestone is created THEN THE System SHALL validate requirements list is non-empty
5. WHEN a milestone is created THEN THE System SHALL validate estimated_hours is a positive integer
6. WHEN an InspectionResult is created THEN THE System SHALL validate coverage_score is between 0 and 100
7. WHEN a PFI score is calculated THEN THE System SHALL validate all component scores are between 0 and 100
8. WHEN reputation data is updated THEN THE System SHALL validate counts are non-negative integers

### Requirement 9: Error Handling and Recovery

**User Story:** As a system operator, I want comprehensive error handling, so that the system degrades gracefully and provides clear feedback.

#### Acceptance Criteria

1. IF Gemini_API returns non-JSON response THEN THE System SHALL log the error and return 500 with "Failed to generate plan" message
2. IF file upload is corrupted or wrong format THEN THE System SHALL return 400 with specific validation error
3. IF code inspection fails due to API error THEN THE System SHALL keep milestone LOCKED and allow retry
4. IF database connection is lost THEN THE System SHALL implement exponential backoff retry
5. IF PFI calculation encounters invalid data THEN THE System SHALL use default score of 50.0 and log error
6. WHEN any error occurs THEN THE System SHALL log error details for debugging
7. WHEN recoverable errors occur THEN THE System SHALL provide user-friendly error messages
8. IF transaction fails THEN THE System SHALL rollback to prevent partial data corruption

### Requirement 10: Performance and Scalability

**User Story:** As a system administrator, I want the system to perform efficiently under load, so that users have a responsive experience.

#### Acceptance Criteria

1. WHEN POST /plan is called THEN THE System SHALL respond within 2 seconds
2. WHEN POST /submit is called THEN THE System SHALL respond within 5 seconds
3. WHEN GET /project is called THEN THE System SHALL respond within 500 milliseconds
4. WHEN Gemini_API calls are made THEN THE System SHALL implement 30 second timeout
5. WHEN database queries are executed THEN THE System SHALL use indexed columns for project_id, user_id, and milestone_id
6. WHEN user reputation is queried THEN THE System SHALL use caching with 5 minute TTL
7. WHEN Gemini_API rate limit is exceeded THEN THE System SHALL implement exponential backoff
8. WHEN multiple milestones are created THEN THE System SHALL use batch insert operations

### Requirement 11: Security and Authentication

**User Story:** As a security officer, I want robust security measures, so that user data and payments are protected.

#### Acceptance Criteria

1. WHEN any API endpoint is accessed THEN THE System SHALL require JWT-based authentication
2. WHEN a request is received THEN THE System SHALL validate user_id matches authenticated user
3. WHEN user input is processed THEN THE System SHALL sanitize all inputs to prevent injection attacks
4. WHEN code is uploaded THEN THE System SHALL perform static analysis only without executing code
5. WHEN file uploads are processed THEN THE System SHALL validate paths to prevent traversal attacks
6. WHEN database queries are executed THEN THE System SHALL use parameterized queries
7. WHEN API keys are needed THEN THE System SHALL load them from environment variables
8. WHEN payment state changes THEN THE System SHALL log all transitions for audit
9. WHEN rate limiting is enforced THEN THE System SHALL limit users to 100 requests per hour
10. WHEN content is rendered in frontend THEN THE System SHALL sanitize to prevent XSS attacks

### Requirement 12: x402 Payment Protocol Simulation

**User Story:** As a financial integrator, I want x402 payment protocol simulation, so that escrow payments can be processed.

#### Acceptance Criteria

1. WHEN payment release is triggered THEN THE Banker_Agent SHALL simulate x402 payment protocol
2. WHEN x402 simulation executes THEN THE System SHALL accept amount and recipient parameters
3. WHEN payment is simulated THEN THE System SHALL return transaction details including status
4. WHEN milestone status changes to RELEASED THEN THE System SHALL trigger payment simulation
5. WHEN payment state transitions occur THEN THE System SHALL enforce state machine rules
6. WHEN escrow amount is set THEN THE System SHALL validate it is a positive number

### Requirement 13: Database Operations and Transactions

**User Story:** As a database administrator, I want reliable data operations with transaction support, so that data consistency is guaranteed.

#### Acceptance Criteria

1. WHEN a project is created THEN THE System SHALL insert project and milestones in a single transaction
2. WHEN milestone status is updated THEN THE System SHALL use atomic database operations
3. WHEN inspection results are saved THEN THE System SHALL link them to the correct milestone_id
4. WHEN user reputation is updated THEN THE System SHALL increment counters atomically
5. WHEN database operations fail THEN THE System SHALL rollback transactions to prevent corruption
6. WHEN Supabase client is initialized THEN THE System SHALL use connection pooling
7. WHEN foreign key constraints exist THEN THE System SHALL enforce referential integrity
8. WHEN concurrent access occurs THEN THE System SHALL handle it without data races

### Requirement 14: Gemini AI Integration

**User Story:** As an AI engineer, I want proper Gemini API integration, so that intelligent analysis is reliable and cost-effective.

#### Acceptance Criteria

1. WHEN Architect_Agent calls Gemini THEN THE System SHALL use Gemini Pro model
2. WHEN Inspector_Agent calls Gemini THEN THE System SHALL use Gemini Flash model
3. WHEN calling Gemini API THEN THE System SHALL include system prompt with schema enforcement
4. WHEN Gemini response is received THEN THE System SHALL strip markdown code blocks if present
5. WHEN Gemini API returns error THEN THE System SHALL implement retry logic with exponential backoff
6. WHEN API key is loaded THEN THE System SHALL validate it is non-empty
7. WHEN rate limits are approached THEN THE System SHALL queue requests appropriately

### Requirement 15: Frontend State Management

**User Story:** As a frontend developer, I want clear state management, so that the UI accurately reflects backend state.

#### Acceptance Criteria

1. WHEN project data is fetched THEN THE System SHALL render all milestones with current status
2. WHEN milestone status changes THEN THE System SHALL update UI elements accordingly
3. WHEN delete button is rendered THEN THE System SHALL set disabled property based on status
4. WHEN file upload completes THEN THE System SHALL display submission results
5. WHEN PFI score is received THEN THE System SHALL trigger gauge animation
6. WHEN errors occur THEN THE System SHALL display user-friendly error notifications
7. WHEN API calls are in progress THEN THE System SHALL show loading indicators


### Requirement 16: Code File Concatenation and Parsing

**User Story:** As a code inspector, I want uploaded files properly concatenated with delimiters, so that individual files can be identified during analysis.

#### Acceptance Criteria

1. WHEN files are concatenated THEN THE System SHALL wrap each file with [FILE_START:filename] tag
2. WHEN files are concatenated THEN THE System SHALL wrap each file with [FILE_END:filename] tag
3. WHEN file content is added THEN THE System SHALL place it between start and end tags
4. WHEN multiple files are processed THEN THE System SHALL separate them with newlines
5. WHEN concatenation completes THEN THE System SHALL verify all files have matching start and end tags
6. FOR ALL files in upload THEN THE System SHALL process each file exactly once
7. WHEN file encoding is detected THEN THE System SHALL decode as UTF-8

### Requirement 17: Milestone Deletion Rules

**User Story:** As a project manager, I want to delete milestones that are no longer needed, so that I can keep my project plan current.

#### Acceptance Criteria

1. WHEN a milestone deletion is requested THEN THE Banker_Agent SHALL check the current status
2. IF milestone status is PENDING THEN THE System SHALL allow deletion
3. IF milestone status is LOCKED THEN THE System SHALL prevent deletion and return error
4. IF milestone status is RELEASED THEN THE System SHALL prevent deletion and return error
5. IF milestone status is DISPUTED THEN THE System SHALL prevent deletion and return error
6. WHEN deletion is allowed THEN THE System SHALL remove the milestone from database
7. WHEN deletion completes THEN THE System SHALL return success confirmation

### Requirement 18: Reputation History Tracking

**User Story:** As a developer, I want my reputation history tracked over time, so that I can see my performance trends.

#### Acceptance Criteria

1. WHEN PFI is calculated THEN THE Bureau_Agent SHALL create a PFISnapshot with timestamp
2. WHEN PFISnapshot is created THEN THE System SHALL include pfi_score, project_id, and milestone_id
3. WHEN reputation is updated THEN THE System SHALL append snapshot to reputation_history
4. WHEN reputation_history is queried THEN THE System SHALL return snapshots ordered by timestamp
5. WHEN user has no history THEN THE System SHALL initialize empty reputation_history list
6. WHEN successful submission occurs THEN THE System SHALL increment successful_submissions counter
7. WHEN failed submission occurs THEN THE System SHALL increment failed_submissions counter
8. WHEN average_coverage is calculated THEN THE System SHALL use all historical coverage scores

### Requirement 19: JSON Schema Validation

**User Story:** As a data engineer, I want strict JSON schema validation, so that malformed data is rejected early.

#### Acceptance Criteria

1. WHEN Architect_Agent receives Gemini response THEN THE System SHALL attempt JSON parsing with json.loads()
2. IF JSON parsing fails THEN THE System SHALL raise ValueError with descriptive message
3. WHEN milestone JSON is parsed THEN THE System SHALL validate presence of required fields
4. WHEN milestone JSON is validated THEN THE System SHALL check id field is not null
5. WHEN milestone JSON is validated THEN THE System SHALL check title field is not empty
6. WHEN milestone JSON is validated THEN THE System SHALL check requirements is a non-empty list
7. WHEN milestone JSON is validated THEN THE System SHALL check estimated_hours is positive integer
8. IF schema validation fails THEN THE System SHALL reject the milestone and log error

### Requirement 20: Inspector Feedback Quality

**User Story:** As a developer, I want detailed feedback on code submissions, so that I understand what needs improvement.

#### Acceptance Criteria

1. WHEN code inspection completes THEN THE Inspector_Agent SHALL provide non-empty feedback text
2. WHEN inspection fails THEN THE Inspector_Agent SHALL list specific missing requirements
3. WHEN inspection passes THEN THE Inspector_Agent SHALL provide positive confirmation
4. WHEN coverage is partial THEN THE Inspector_Agent SHALL identify which requirements are met
5. WHEN functions are unused THEN THE Inspector_Agent SHALL mention them in feedback
6. WHEN imports are present without usage THEN THE Inspector_Agent SHALL flag them in feedback
7. WHEN feedback is generated THEN THE System SHALL ensure it is actionable and specific

### Requirement 21: Project State Retrieval

**User Story:** As a user, I want to retrieve complete project state, so that I can see all milestones and their current status.

#### Acceptance Criteria

1. WHEN GET /project/{project_id} is called THEN THE System SHALL return project metadata
2. WHEN project is retrieved THEN THE System SHALL include all associated milestones
3. WHEN milestones are included THEN THE System SHALL include current status for each
4. WHEN milestones are included THEN THE System SHALL include inspection_result if available
5. WHEN project does not exist THEN THE System SHALL return 404 Not Found
6. WHEN project is retrieved THEN THE System SHALL include created_at and updated_at timestamps
7. WHEN project has PFI score THEN THE System SHALL include total_pfi in response

### Requirement 22: Environment Configuration

**User Story:** As a DevOps engineer, I want configuration managed through environment variables, so that deployment is flexible and secure.

#### Acceptance Criteria

1. WHEN System starts THEN THE System SHALL load environment variables from .env file
2. WHEN Gemini_API is initialized THEN THE System SHALL read GEMINI_API_KEY from environment
3. WHEN Supabase is initialized THEN THE System SHALL read SUPABASE_URL from environment
4. WHEN Supabase is initialized THEN THE System SHALL read SUPABASE_KEY from environment
5. IF required environment variable is missing THEN THE System SHALL fail to start with clear error message
6. WHEN .env file is used THEN THE System SHALL ensure it is excluded from version control
7. WHEN API keys are accessed THEN THE System SHALL never log or expose them in responses

### Requirement 23: CORS and Frontend Communication

**User Story:** As a frontend developer, I want proper CORS configuration, so that the dashboard can communicate with the API.

#### Acceptance Criteria

1. WHEN API receives request from frontend THEN THE System SHALL include CORS headers in response
2. WHEN CORS is configured THEN THE System SHALL use whitelist of allowed origins
3. WHEN preflight OPTIONS request is received THEN THE System SHALL respond with allowed methods
4. WHEN API response is sent THEN THE System SHALL include Access-Control-Allow-Origin header
5. WHEN credentials are needed THEN THE System SHALL include Access-Control-Allow-Credentials header
6. WHEN custom headers are used THEN THE System SHALL include them in Access-Control-Allow-Headers

### Requirement 24: Logging and Observability

**User Story:** As a system operator, I want comprehensive logging, so that I can troubleshoot issues and monitor system health.

#### Acceptance Criteria

1. WHEN errors occur THEN THE System SHALL log error details with timestamp and context
2. WHEN Gemini_API is called THEN THE System SHALL log request and response metadata
3. WHEN database operations fail THEN THE System SHALL log connection details and query
4. WHEN payment state changes THEN THE System SHALL log transition with milestone_id
5. WHEN user actions occur THEN THE System SHALL log user_id and action type
6. WHEN API keys are logged THEN THE System SHALL mask sensitive values
7. WHEN logs are written THEN THE System SHALL use structured logging format

### Requirement 25: Testing and Quality Assurance

**User Story:** As a QA engineer, I want comprehensive test coverage, so that system correctness is verified.

#### Acceptance Criteria

1. WHEN unit tests are run THEN THE System SHALL achieve minimum 80% code coverage
2. WHEN Architect_Agent is tested THEN THE System SHALL mock Gemini_API responses
3. WHEN Banker_Agent is tested THEN THE System SHALL verify state transition logic
4. WHEN Inspector_Agent is tested THEN THE System SHALL test file concatenation format
5. WHEN Bureau_Agent is tested THEN THE System SHALL verify PFI calculation formula
6. WHEN integration tests are run THEN THE System SHALL use test database instance
7. WHEN property tests are run THEN THE System SHALL verify invariants hold for arbitrary inputs
8. WHEN end-to-end tests are run THEN THE System SHALL verify complete workflow from prompt to payment

### Requirement 26: Demo Templates and Examples

**User Story:** As a new user, I want demo templates, so that I can understand how the system evaluates code.

#### Acceptance Criteria

1. WHEN demo templates are provided THEN THE System SHALL include "good code" example that passes inspection
2. WHEN demo templates are provided THEN THE System SHALL include "bad code" example that fails inspection
3. WHEN good code template is analyzed THEN THE Inspector_Agent SHALL return 100% coverage
4. WHEN bad code template is analyzed THEN THE Inspector_Agent SHALL identify missing implementations
5. WHEN templates are used THEN THE System SHALL demonstrate function definition and usage requirements
6. WHEN templates are documented THEN THE System SHALL explain why each passes or fails

### Requirement 27: Atomic Transaction Guarantees

**User Story:** As a database administrator, I want atomic transactions for critical operations, so that data consistency is guaranteed.

#### Acceptance Criteria

1. WHEN project and milestones are created THEN THE System SHALL execute in single transaction
2. WHEN inspection completes and passes THEN THE System SHALL update status, save result, and calculate PFI atomically
3. WHEN payment is released THEN THE System SHALL update milestone status and trigger x402 simulation atomically
4. IF any step in transaction fails THEN THE System SHALL rollback all changes
5. WHEN transaction commits THEN THE System SHALL ensure all changes are persisted
6. WHEN concurrent transactions occur THEN THE System SHALL use appropriate isolation level

### Requirement 28: File Type Validation

**User Story:** As a security engineer, I want strict file type validation, so that only code files are processed.

#### Acceptance Criteria

1. WHEN file is uploaded THEN THE System SHALL check file extension against allowed list
2. WHEN file extension is .py, .js, .ts, .java, .cpp, .c, .go, or .rs THEN THE System SHALL accept it
3. WHEN file extension is not in allowed list THEN THE System SHALL reject with 400 error
4. WHEN file is binary THEN THE System SHALL reject it
5. WHEN .zip file is uploaded THEN THE System SHALL extract and validate contained files
6. WHEN file content is checked THEN THE System SHALL verify it is valid UTF-8 text
7. WHEN file validation fails THEN THE System SHALL provide specific error message about which file failed

### Requirement 29: PFI Gauge Animation

**User Story:** As a user, I want smooth PFI gauge animation, so that reputation changes are visually engaging.

#### Acceptance Criteria

1. WHEN PFI score is received THEN THE System SHALL animate gauge from 0 to final score
2. WHEN gauge animates THEN THE System SHALL use CSS transitions for smooth motion
3. WHEN animation duration is set THEN THE System SHALL complete within 2 seconds
4. WHEN gauge displays score THEN THE System SHALL show numeric value alongside visual indicator
5. WHEN score is high (>80) THEN THE System SHALL use green color scheme
6. WHEN score is medium (50-80) THEN THE System SHALL use yellow color scheme
7. WHEN score is low (<50) THEN THE System SHALL use red color scheme
8. WHEN gauge renders THEN THE System SHALL include glow effects matching AI startup aesthetic

### Requirement 30: System Prompt Engineering

**User Story:** As an AI engineer, I want well-crafted system prompts, so that Gemini responses are reliable and structured.

#### Acceptance Criteria

1. WHEN Architect_Agent calls Gemini THEN THE System SHALL include system prompt enforcing milestone schema
2. WHEN Inspector_Agent calls Gemini THEN THE System SHALL include system prompt defining logic coverage criteria
3. WHEN system prompt is used THEN THE System SHALL specify required JSON output format
4. WHEN system prompt is used THEN THE System SHALL instruct model to return only JSON without additional text
5. WHEN system prompt includes examples THEN THE System SHALL demonstrate correct output format
6. WHEN prompt injection is attempted THEN THE System SHALL isolate user input from system instructions
7. WHEN Gemini response is parsed THEN THE System SHALL handle markdown code block wrapping

---

## Non-Functional Requirements

### NFR-1: Availability
THE System SHALL maintain 99.5% uptime during business hours (9 AM - 5 PM UTC)

### NFR-2: Response Time
THE System SHALL respond to 95% of API requests within target latency (2s for /plan, 5s for /submit, 500ms for /project)

### NFR-3: Scalability
THE System SHALL support at least 100 concurrent users without performance degradation

### NFR-4: Data Retention
THE System SHALL retain project data and reputation history for minimum 2 years

### NFR-5: API Rate Limiting
THE System SHALL enforce rate limit of 100 requests per hour per authenticated user

### NFR-6: Code Analysis Accuracy
THE Inspector_Agent SHALL achieve minimum 90% accuracy in detecting missing requirements

### NFR-7: Security Compliance
THE System SHALL follow OWASP Top 10 security best practices

### NFR-8: Browser Compatibility
THE Frontend SHALL support Chrome, Firefox, Safari, and Edge (latest 2 versions)

### NFR-9: Mobile Responsiveness
THE Frontend SHALL be usable on devices with minimum 768px width

### NFR-10: Accessibility
THE Frontend SHALL meet WCAG 2.1 Level AA guidelines where feasible

---

## Traceability Matrix

| Requirement | Design Component | Correctness Property |
|-------------|------------------|---------------------|
| Req 1 | Architect Agent | Property 1 |
| Req 2, 16 | Inspector Agent | Property 5 |
| Req 3 | Inspector Agent | Property 3 |
| Req 4, 17 | Banker Agent | Property 2 |
| Req 5, 18 | Bureau Agent | Property 4 |
| Req 6 | FastAPI Server | - |
| Req 7, 15, 29 | Frontend Dashboard | - |
| Req 8, 19 | Data Models | Property 1 |
| Req 9 | Error Handling | - |
| Req 10 | Performance | - |
| Req 11, 28 | Security | - |
| Req 12 | Banker Agent | Property 6 |
| Req 13, 27 | Database Layer | - |
| Req 14, 30 | Gemini Integration | - |
| Req 20 | Inspector Agent | Property 3 |
| Req 21 | FastAPI Server | - |
| Req 22 | Configuration | - |
| Req 23 | FastAPI Server | - |
| Req 24 | Logging | - |
| Req 25 | Testing Strategy | All Properties |
| Req 26 | Demo Templates | - |

