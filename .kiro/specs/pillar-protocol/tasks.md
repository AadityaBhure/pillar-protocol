# Implementation Plan: Pillar Protocol

## Overview

This implementation plan covers the complete Pillar Protocol system: a multi-agent AI platform with four specialized agents (Architect, Banker, Inspector, Bureau), FastAPI backend, Supabase database, and vanilla JavaScript frontend. The system transforms project ideas into structured milestones, manages escrow with state-based locking, validates code submissions, and tracks developer reputation scores.

## Tasks

- [ ] 1. Set up project structure and environment configuration
  - Create directory structure: backend/, frontend/, agents/, utils/, templates/
  - Create requirements.txt with FastAPI, Supabase, Gemini AI, pytest dependencies
  - Create .env.example template with GEMINI_API_KEY, SUPABASE_URL, SUPABASE_KEY
  - Create .gitignore to exclude .env, __pycache__, .pytest_cache
  - _Requirements: 22.1, 22.2, 22.3, 22.4, 22.6_

- [ ] 2. Implement database layer and data models
  - [ ] 2.1 Create database.py with Supabase client initialization
    - Implement DatabaseManager class with connection pooling
    - Add methods: create_project(), get_project(), update_milestone_status(), delete_milestone()
    - Add methods: save_inspection_result(), update_user_reputation(), get_user_reputation()
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.6, 22.3, 22.4_
  
  - [ ] 2.2 Write property test for database transaction atomicity
    - **Property 13: Transaction Atomicity**
    - **Validates: Requirements 13.1, 13.5, 27.1, 27.4, 27.5**
  
  - [ ] 2.3 Create models.py with Pydantic data models
    - Define Project, Milestone, InspectionResult, UserReputation, PFISnapshot models
    - Add validation rules for all fields (UUID, non-empty strings, score bounds)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_
  
  - [ ] 2.4 Write property test for milestone schema validation
    - **Property 1: Milestone Schema Validation**
    - **Validates: Requirements 1.2, 1.6, 1.7, 8.3, 8.4, 8.5, 19.4, 19.5, 19.6**

- [ ] 3. Implement the Architect Agent
  - [ ] 3.1 Create architect.py with ArchitectAgent class
    - Initialize Gemini Pro client with API key from environment
    - Implement generate_checklist() method with system prompt for milestone schema
    - Add JSON parsing with json.loads() and markdown code block stripping
    - Implement _validate_milestone_schema() for schema enforcement
    - Add error handling for invalid JSON responses
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 14.1, 14.3, 14.4, 19.1, 19.2, 30.1, 30.3, 30.4, 30.7_
  
  - [ ] 3.2 Write property test for milestone generation guarantee
    - **Property 8: Milestone Generation Guarantee**
    - **Validates: Requirements 1.1, 1.5**
  
  - [ ] 3.3 Write property test for JSON parsing and validation
    - **Property 7: JSON Parsing and Validation**
    - **Validates: Requirements 1.3, 1.4, 19.1, 19.2**
  
  - [ ] 3.4 Write unit tests for Architect Agent
    - Test valid prompt conversion with mocked Gemini responses
    - Test schema validation with missing fields
    - Test empty prompt handling
    - Test JSON parsing errors

- [ ] 4. Implement the Banker Agent
  - [ ] 4.1 Create banker.py with BankerAgent class and EscrowStatus enum
    - Define EscrowStatus enum: PENDING, LOCKED, RELEASED, DISPUTED
    - Implement get_milestone_status(), lock_milestone(), release_payment()
    - Implement can_delete_milestone() with status checking logic
    - Implement simulate_x402_payment() for payment protocol simulation
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7_
  
  - [ ] 4.2 Write property test for state locking invariant
    - **Property 2: State Locking Invariant**
    - **Validates: Requirements 4.3, 4.4, 7.3, 17.3, 17.4, 17.5, 17.6**
  
  - [ ] 4.3 Write property test for deletion permission rules
    - **Property 10: Deletion Permission Rules**
    - **Validates: Requirements 4.8, 17.1, 17.2, 17.3, 17.4, 17.5**
  
  - [ ] 4.4 Write property test for state transition correctness
    - **Property 9: State Transition Correctness**
    - **Validates: Requirements 4.1, 4.2**
  
  - [ ] 4.5 Write unit tests for Banker Agent
    - Test state transitions (PENDING → LOCKED → RELEASED)
    - Test deletion prevention when locked
    - Test x402 payment simulation

- [ ] 5. Implement file processing utilities
  - [ ] 5.1 Create utils/file_processor.py with file handling functions
    - Implement parse_zip_file() to extract files from ZIP uploads
    - Implement concatenate_code_files() with [FILE_START] and [FILE_END] delimiters
    - Implement validate_file_types() to check allowed extensions
    - Implement validate_file_sizes() for 10MB per file, 50MB total limits
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 28.1, 28.2, 28.3, 28.4, 28.6_
  
  - [ ] 5.2 Write property test for file concatenation format and preservation
    - **Property 5: File Concatenation Format and Preservation**
    - **Validates: Requirements 2.5, 2.6, 2.7, 16.1, 16.2, 16.3, 16.4, 16.5, 16.6**
  
  - [ ] 5.3 Write property test for file content preservation
    - **Property 17: File Content Preservation**
    - **Validates: Requirements 2.6, 16.3**
  
  - [ ] 5.4 Write property test for file type validation
    - **Property 12: File Type Validation**
    - **Validates: Requirements 2.2, 28.1, 28.2, 28.3, 28.6**

- [ ] 6. Implement the Inspector Agent
  - [ ] 6.1 Create inspector.py with InspectorAgent class
    - Initialize Gemini Flash client with API key from environment
    - Implement analyze_code() method with file concatenation and Gemini analysis
    - Implement _concatenate_files() using file_processor utilities
    - Implement _check_logic_coverage() with system prompt for logic analysis
    - Add SHA256 hash generation for code_blob tracking
    - Return InspectionResult with passed, coverage_score, feedback, missing_requirements
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 14.2, 14.3, 14.4, 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 30.2, 30.3, 30.4, 30.7_
  
  - [ ] 6.2 Write property test for logic coverage analysis
    - **Property 3: Logic Coverage Analysis**
    - **Validates: Requirements 3.1, 3.2, 3.3, 20.2, 20.5, 20.6**
  
  - [ ] 6.3 Write property test for inspection result completeness
    - **Property 11: Inspection Result Completeness**
    - **Validates: Requirements 3.4, 3.5, 3.6, 20.1**
  
  - [ ] 6.4 Write property test for coverage score bounds
    - **Property 16: Coverage Score Bounds**
    - **Validates: Requirements 3.4, 8.6**
  
  - [ ] 6.5 Write unit tests for Inspector Agent
    - Test file concatenation with delimiters
    - Test logic coverage detection (functions defined AND used)
    - Test missing requirements identification

- [ ] 7. Implement the Bureau Agent
  - [ ] 7.1 Create bureau.py with BureauAgent class
    - Implement calculate_pfi() with performance and financial score calculation
    - Use 60% performance weight, 40% financial weight for combined PFI
    - Implement update_reputation() to update user reputation in database
    - Implement get_reputation_history() to retrieve historical PFI snapshots
    - Add PFISnapshot creation with timestamp, pfi_score, project_id, milestone_id
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10, 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7, 18.8_
  
  - [ ] 7.2 Write property test for PFI score bounds and formula
    - **Property 4: PFI Score Bounds and Formula**
    - **Validates: Requirements 5.2, 5.3, 5.4, 8.7**
  
  - [ ] 7.3 Write property test for payment release condition
    - **Property 6: Payment Release Condition**
    - **Validates: Requirements 4.5, 4.6, 5.1, 5.9, 5.10**
  
  - [ ] 7.4 Write property test for reputation history append-only
    - **Property 18: Reputation History Append-Only**
    - **Validates: Requirements 5.10, 18.1, 18.2, 18.3**
  
  - [ ] 7.5 Write unit tests for Bureau Agent
    - Test PFI calculation formula
    - Test score bounds (0-100)
    - Test reputation history updates
    - Test weighted average calculation

- [ ] 8. Checkpoint - Ensure all agent tests pass
  - Run pytest on all agent modules
  - Verify all unit tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Implement FastAPI server and API endpoints
  - [ ] 9.1 Create main.py with FastAPI application setup
    - Initialize FastAPI app with CORS middleware
    - Load environment variables with python-dotenv
    - Initialize all agents (Architect, Banker, Inspector, Bureau)
    - Initialize DatabaseManager with Supabase credentials
    - _Requirements: 6.7, 22.1, 22.2, 22.3, 22.4, 23.1, 23.2, 23.3, 23.4, 23.5, 23.6_
  
  - [ ] 9.2 Implement POST /plan endpoint
    - Accept PlanRequest with prompt and user_id
    - Call Architect.generate_checklist() to convert prompt to milestones
    - Call DatabaseManager.create_project() to save project and milestones
    - Return PlanResponse with project_id and milestones list
    - Add error handling for Gemini API failures
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 6.1, 9.1, 9.2_
  
  - [ ] 9.3 Implement POST /submit endpoint
    - Accept files via multipart/form-data with project_id and milestone_id
    - Validate file types and sizes using file_processor utilities
    - Call Banker.lock_milestone() to lock the milestone
    - Call Inspector.analyze_code() to analyze uploaded code
    - Save inspection result to database
    - If passed: call Bureau.calculate_pfi() and Banker.release_payment()
    - Return SubmitResponse with passed, feedback, pfi_score
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.8, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.2, 4.5, 4.6, 5.1, 5.9, 5.10, 6.2, 9.3_
  
  - [ ] 9.4 Implement GET /project/{project_id} endpoint
    - Retrieve project with all milestones from database
    - Include inspection results if available
    - Return project metadata with created_at, updated_at timestamps
    - _Requirements: 6.3, 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7_
  
  - [ ] 9.5 Implement DELETE /milestone/{milestone_id} endpoint
    - Call Banker.can_delete_milestone() to check if deletion allowed
    - If locked, return 403 Forbidden error
    - If allowed, call DatabaseManager.delete_milestone()
    - Return success confirmation
    - _Requirements: 4.3, 4.4, 6.4, 6.5, 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7_
  
  - [ ] 9.6 Add error handling middleware
    - Handle database connection errors with 503 Service Unavailable
    - Handle Gemini API errors with 500 and retry message
    - Handle validation errors with 400 Bad Request
    - Add logging for all errors with context
    - _Requirements: 6.6, 6.7, 6.8, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 24.1, 24.2, 24.3, 24.4, 24.5, 24.6, 24.7_
  
  - [ ] 9.7 Write integration tests for API endpoints
    - Test POST /plan with real Gemini API (staging key)
    - Test POST /submit with file uploads
    - Test GET /project with database queries
    - Test DELETE /milestone with state checks
    - Test error responses and CORS headers

- [ ] 10. Implement frontend HTML structure
  - [ ] 10.1 Create frontend/index.html with dashboard layout
    - Add HTML structure with header, tab navigation, content sections
    - Create "Create Plan" tab with prompt textarea and submit button
    - Create "Submit Code" tab with file upload input and milestone selector
    - Create "View Project" tab with project ID input and milestone list display
    - Add PFI gauge display area with score indicator
    - _Requirements: 7.1, 7.2, 7.6, 15.1_
  
  - [ ] 10.2 Add file upload input with multiple file support
    - Use HTML5 file input with multiple attribute
    - Add file type validation on client side
    - Display selected file names before upload
    - _Requirements: 2.1, 7.6_

- [ ] 11. Implement frontend CSS styling with AI startup aesthetic
  - [ ] 11.1 Create frontend/style.css with terminal-style theme
    - Define CSS variables for colors (dark background, neon accents)
    - Add glow effects using box-shadow and text-shadow
    - Style buttons with hover effects and transitions
    - Style milestone cards with status indicators
    - _Requirements: 7.7_
  
  - [ ] 11.2 Style PFI gauge with CSS transitions
    - Create circular gauge using CSS and SVG
    - Add CSS transitions for smooth animation (2 second duration)
    - Implement color scheme: green (>80), yellow (50-80), red (<50)
    - Add glow effects matching AI startup aesthetic
    - _Requirements: 7.5, 29.1, 29.2, 29.3, 29.4, 29.5, 29.6, 29.7, 29.8_
  
  - [ ] 11.3 Style milestone list with status-based delete button states
    - Style delete buttons with disabled state (grayed out when locked)
    - Add visual indicators for milestone status (PENDING, LOCKED, RELEASED)
    - _Requirements: 7.3, 7.4, 15.3_

- [ ] 12. Implement frontend JavaScript functionality
  - [ ] 12.1 Create frontend/script.js with API client class
    - Implement PillarAPIClient class with base URL configuration
    - Add methods: createPlan(), submitCode(), getProject(), deleteMilestone()
    - Use Fetch API for all HTTP requests
    - Add error handling and user-friendly error messages
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 15.6_
  
  - [ ] 12.2 Implement tab switching functionality
    - Add event listeners for tab buttons
    - Show/hide content sections based on active tab
    - Update UI without page reload
    - _Requirements: 7.1, 7.8, 15.2_
  
  - [ ] 12.3 Implement milestone rendering with state synchronization
    - Render milestone cards with title, description, requirements, status
    - Set delete button disabled property based on milestone status
    - Update UI when milestone status changes
    - _Requirements: 7.2, 7.3, 7.4, 15.1, 15.2, 15.3_
  
  - [ ] 12.4 Write property test for frontend state synchronization
    - **Property 15: Frontend State Synchronization**
    - **Validates: Requirements 7.3, 7.4, 15.3**
  
  - [ ] 12.5 Implement PFI gauge animation
    - Animate gauge from 0 to final score on submission success
    - Use CSS transitions for smooth motion
    - Display numeric value alongside visual indicator
    - _Requirements: 7.5, 15.5, 29.1, 29.2, 29.3, 29.4_
  
  - [ ] 12.6 Implement file upload handling
    - Read files from HTML input
    - Create FormData with files and metadata
    - Send to POST /submit endpoint
    - Display submission results (passed, feedback, PFI score)
    - _Requirements: 2.1, 15.4_
  
  - [ ] 12.7 Add loading indicators and error notifications
    - Show loading spinner during API calls
    - Display success/error notifications with feedback
    - Handle network errors gracefully
    - _Requirements: 15.6, 15.7_

- [ ] 13. Create demo templates for testing
  - [ ] 13.1 Create templates/good_code_example.py
    - Implement complete image processing pipeline with all functions
    - Ensure all functions are defined AND actually called
    - Should pass inspection with 100% coverage
    - _Requirements: 26.1, 26.3, 26.5_
  
  - [ ] 13.2 Create templates/bad_code_example.py
    - Implement incomplete pipeline with missing implementations
    - Include unused functions and imports without usage
    - Should fail inspection with specific missing requirements
    - _Requirements: 26.2, 26.4, 26.5_
  
  - [ ] 13.3 Create templates/README.md documenting demo templates
    - Explain why good code passes (all requirements met, functions used)
    - Explain why bad code fails (missing implementations, unused functions)
    - Provide usage instructions for testing
    - _Requirements: 26.6_

- [ ] 14. Set up Supabase database schema
  - [ ] 14.1 Create database migration script or SQL schema
    - Define projects table with id, user_id, title, description, created_at, updated_at
    - Define milestones table with id, project_id, title, description, requirements, estimated_hours, status, escrow_amount, created_at, submitted_at
    - Define inspection_results table with milestone_id, passed, coverage_score, feedback, missing_requirements, analyzed_at, code_blob_hash
    - Define user_reputation table with user_id, current_pfi, total_projects, successful_submissions, failed_submissions, average_coverage, reputation_history, updated_at
    - Add foreign key constraints and indexes
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 13.7_
  
  - [ ] 14.2 Configure Supabase Row Level Security (RLS) policies
    - Add RLS policies for user-specific data access
    - Ensure users can only access their own projects and reputation
    - _Requirements: 11.1, 11.2_

- [ ] 15. Checkpoint - Integration testing
  - Run end-to-end workflow test: prompt → milestones → code upload → inspection → PFI
  - Test frontend-backend integration with file uploads
  - Verify state locking and deletion prevention
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 16. Implement security features
  - [ ] 16.1 Add input sanitization and validation
    - Sanitize all user inputs (prompts, filenames) to prevent injection attacks
    - Validate file paths to prevent traversal attacks
    - Escape special characters in database queries (use parameterized queries)
    - _Requirements: 11.3, 11.5, 11.6_
  
  - [ ] 16.2 Implement rate limiting middleware
    - Add rate limiting per user (100 requests per hour)
    - Return 429 Too Many Requests when limit exceeded
    - _Requirements: 11.9_
  
  - [ ] 16.3 Add Content Security Policy and XSS prevention
    - Implement CSP headers in FastAPI responses
    - Sanitize all rendered content in frontend to prevent XSS
    - _Requirements: 11.10_
  
  - [ ] 16.4 Write property test for no code execution security
    - **Property 14: No Code Execution Security**
    - **Validates: Requirements 11.4**

- [ ] 17. Add logging and observability
  - [ ] 17.1 Implement structured logging throughout the application
    - Log all errors with timestamp and context
    - Log Gemini API calls with request/response metadata (mask API keys)
    - Log database operations and failures
    - Log payment state transitions with milestone_id
    - Log user actions with user_id and action type
    - _Requirements: 9.6, 24.1, 24.2, 24.3, 24.4, 24.5, 24.6, 24.7_

- [ ] 18. Create documentation
  - [ ] 18.1 Create README.md with setup and usage instructions
    - Document environment setup (.env configuration)
    - Document installation steps (pip install -r requirements.txt)
    - Document how to run the server (uvicorn main:app)
    - Document API endpoints with examples
    - Document demo template usage
    - _Requirements: All_
  
  - [ ] 18.2 Create API documentation with FastAPI automatic docs
    - Add docstrings to all API endpoints
    - Configure OpenAPI schema with descriptions
    - Test /docs and /redoc endpoints

- [ ] 19. Final testing and validation
  - [ ] 19.1 Run all property-based tests
    - Execute all property tests with Hypothesis
    - Verify all invariants hold for arbitrary inputs
  
  - [ ] 19.2 Run complete integration test suite
    - Test end-to-end workflow from prompt to payment
    - Test error scenarios and recovery
    - Test concurrent access scenarios
  
  - [ ] 19.3 Perform manual testing with demo templates
    - Test good code example (should pass with 100% coverage)
    - Test bad code example (should fail with specific feedback)
    - Verify PFI gauge animation
    - Verify delete button disable/enable logic
  
  - [ ] 19.4 Validate security measures
    - Test input sanitization with malicious inputs
    - Test rate limiting enforcement
    - Verify no code execution occurs during analysis
    - Test file type validation

- [ ] 20. Final checkpoint - Production readiness
  - Verify all tests pass (unit, property, integration)
  - Confirm all API endpoints work correctly
  - Validate frontend UI matches AI startup aesthetic
  - Ensure error handling is comprehensive
  - Verify logging is in place
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- The user already has .env file with GEMINI_API_KEY configured
- Implementation uses Python for backend and vanilla JavaScript for frontend
- All agents use Gemini AI: Architect uses Gemini Pro, Inspector uses Gemini Flash
- Database uses Supabase (PostgreSQL) with Row Level Security
- Frontend uses "AI Startup" aesthetic with terminal styling and glow effects
