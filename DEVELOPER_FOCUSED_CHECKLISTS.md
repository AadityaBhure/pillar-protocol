# Developer-Focused Checklists

## Overview
The Architect Agent now generates **developer-focused, code-verifiable checklists** instead of client-focused business requirements. This makes verification against actual project files straightforward and objective.

## Key Changes

### Before (Client-Focused) ❌
```json
{
  "title": "User Authentication",
  "description": "Allow users to securely log in to the system",
  "requirements": [
    "User-friendly login interface",
    "Secure authentication",
    "Good user experience",
    "Fast performance"
  ]
}
```

**Problems:**
- Vague, subjective terms
- Not verifiable in code
- No clear technical deliverables
- Inspector Agent can't check these

### After (Developer-Focused) ✅
```json
{
  "title": "Implement User Authentication API",
  "description": "Create JWT-based authentication with user registration and login endpoints",
  "requirements": [
    "Create User model with email, password_hash, created_at fields",
    "Implement POST /api/register endpoint with email validation",
    "Implement POST /api/login endpoint returning JWT token",
    "Add password hashing using bcrypt with salt rounds >= 10",
    "Create authentication middleware to verify JWT tokens",
    "Add error handling for invalid credentials (401 status)"
  ]
}
```

**Benefits:**
- Specific, technical requirements
- Directly verifiable in code
- Clear deliverables
- Inspector Agent can check each requirement

## Requirement Writing Guidelines

### ✅ GOOD Requirements (Code-Verifiable)

**API Endpoints:**
- "Create POST /api/users endpoint accepting JSON body"
- "Implement GET /api/users/:id endpoint returning user object"
- "Add DELETE /api/sessions endpoint for logout"

**Database:**
- "Create users table with columns: id, email, password_hash, created_at"
- "Add foreign key constraint from posts.user_id to users.id"
- "Create index on users.email for faster lookups"

**Functions/Classes:**
- "Implement UserService class with register() and login() methods"
- "Create validateEmail() function using regex pattern"
- "Add hashPassword() function using bcrypt library"

**Error Handling:**
- "Return 400 status code with error message for invalid input"
- "Throw ValidationError when email format is incorrect"
- "Log errors to console with timestamp and stack trace"

**Testing:**
- "Add unit test for login() method with valid credentials"
- "Create integration test for POST /api/register endpoint"
- "Test password hashing produces different hashes for same input"

**Configuration:**
- "Add JWT_SECRET to environment variables"
- "Set token expiration to 24 hours in config"
- "Configure CORS to allow requests from localhost:3000"

### ❌ BAD Requirements (Not Verifiable)

**Vague/Subjective:**
- "User-friendly interface" → Not code-checkable
- "Good performance" → Too vague
- "Secure system" → Not specific
- "Easy to use" → Subjective
- "Professional design" → Not technical

**Business-Focused:**
- "Increase user engagement" → Not a code requirement
- "Improve conversion rate" → Business metric
- "Enhance brand image" → Marketing goal
- "Reduce customer complaints" → Support metric

**Too Broad:**
- "Build authentication" → Too general
- "Add security" → Not specific
- "Implement database" → Needs details
- "Create API" → Which endpoints?

## How Inspector Agent Uses Requirements

### Verification Process

1. **Parse Requirements**: Extract specific technical deliverables
2. **Scan Codebase**: Look for matching implementations
3. **Check Existence**: Verify functions, classes, endpoints exist
4. **Validate Logic**: Ensure actual implementation, not just imports
5. **Generate Report**: List met and unmet requirements

### Example Verification

**Requirement:** "Create POST /api/login endpoint returning JWT token"

**Inspector Checks:**
```python
# ✅ Checks for:
- Route definition: @app.post("/api/login")
- Function implementation: def login(...)
- JWT token generation: jwt.encode(...)
- Return statement with token
- Error handling for invalid credentials

# ❌ Fails if:
- Endpoint doesn't exist
- Function is empty/stub
- No JWT token generation
- No error handling
```

## GitHub Integration Benefits

With developer-focused checklists, the Inspector Agent can:

1. **Fetch GitHub Repository**: Get all code files automatically
2. **Parse Technical Requirements**: Understand what to look for
3. **Scan Code Files**: Search for specific implementations
4. **Verify Each Requirement**: Check if code matches checklist
5. **Generate Detailed Report**: Show exactly what's missing

### Example Flow

```
User: "Build a REST API for user management"

Architect Agent generates:
├── Milestone 1: User Model and Database
│   ├── Create User model with id, email, password_hash
│   ├── Add database migration for users table
│   └── Implement password hashing with bcrypt
├── Milestone 2: Registration Endpoint
│   ├── Create POST /api/register endpoint
│   ├── Validate email format with regex
│   └── Return 201 status with user object
└── Milestone 3: Login Endpoint
    ├── Create POST /api/login endpoint
    ├── Verify password with bcrypt.compare()
    └── Generate JWT token with 24h expiration

User submits GitHub repo: github.com/user/api-project

Inspector Agent:
✅ Found User model in models/user.py
✅ Found migration in migrations/001_create_users.sql
✅ Found bcrypt usage in utils/auth.py
✅ Found POST /api/register in routes/auth.py
✅ Found email validation in validators/email.py
✅ Found 201 status return in auth.py
✅ Found POST /api/login in routes/auth.py
✅ Found bcrypt.compare() in utils/auth.py
✅ Found JWT generation in utils/tokens.py

Result: 9/9 requirements met → PASSED
```

## Prompt Engineering

### System Prompt Structure

The Architect Agent uses this approach:

```
You are a technical project planning AI for DEVELOPERS.

CRITICAL: Write from DEVELOPER'S perspective for CODE VERIFICATION.

Requirements must be:
1. Specific and technical
2. Verifiable in actual code
3. Map to code artifacts (functions, classes, endpoints)
4. Checkable by inspecting codebase

GOOD: "Create UserController class with login() method"
BAD: "User-friendly interface"
```

### Conversation Context

When refining milestones through chat:
- Maintains developer focus
- Suggests technical improvements
- Adds missing technical details
- Ensures all requirements are verifiable

## Benefits Summary

### For Developers
- Clear technical specifications
- No ambiguity about deliverables
- Easy to implement from checklist
- Objective pass/fail criteria

### For Clients
- Can still understand progress
- Milestone titles are clear
- Descriptions explain what's being built
- Technical depth ensures quality

### For Inspector Agent
- Can verify each requirement
- Objective code checking
- Detailed feedback on missing items
- No subjective judgments

### For Project Success
- Reduces miscommunication
- Clear acceptance criteria
- Automated verification possible
- Quality assurance built-in

## Real-World Example

### Project: "E-commerce Shopping Cart"

**Developer-Focused Checklist:**

```json
[
  {
    "title": "Implement Cart Data Model",
    "description": "Create database schema and models for shopping cart functionality",
    "requirements": [
      "Create carts table with columns: id, user_id, created_at, updated_at",
      "Create cart_items table with: id, cart_id, product_id, quantity, price",
      "Add foreign key constraints: cart_items.cart_id → carts.id",
      "Add foreign key constraints: cart_items.product_id → products.id",
      "Create Cart model class with addItem(), removeItem(), getTotal() methods",
      "Implement CartItem model with quantity validation (min: 1, max: 99)"
    ],
    "estimated_hours": 4
  },
  {
    "title": "Build Cart API Endpoints",
    "description": "Create RESTful API for cart operations",
    "requirements": [
      "Implement GET /api/cart endpoint returning current user's cart",
      "Implement POST /api/cart/items endpoint to add product to cart",
      "Implement PUT /api/cart/items/:id endpoint to update quantity",
      "Implement DELETE /api/cart/items/:id endpoint to remove item",
      "Add authentication middleware requiring valid JWT token",
      "Return 404 status when cart or item not found",
      "Return 400 status when quantity is invalid (< 1 or > 99)"
    ],
    "estimated_hours": 6
  },
  {
    "title": "Implement Cart Business Logic",
    "description": "Add cart calculation and validation logic",
    "requirements": [
      "Create calculateTotal() function summing all item prices",
      "Implement validateStock() function checking product availability",
      "Add applyDiscount() function for coupon codes",
      "Create clearCart() function removing all items",
      "Implement mergeCarts() function for guest-to-user cart transfer",
      "Add unit tests for all calculation functions"
    ],
    "estimated_hours": 5
  }
]
```

**Inspector Agent can verify:**
- ✅ Tables exist in database schema
- ✅ Models have required methods
- ✅ API endpoints are implemented
- ✅ Authentication middleware is present
- ✅ Error handling returns correct status codes
- ✅ Business logic functions exist
- ✅ Unit tests are written

**Result:** Objective, automated verification against GitHub repository!
