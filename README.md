<div align="center">
  
# 🏛️ The Pillar Protocol
**Autonomous AI Orchestration for Trustless Software Development**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Vercel](https://img.shields.io/badge/Deployed_on-Vercel-black?logo=vercel)](https://vercel.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

*A multi-agent AI platform bridging the gap between natural language project planning, deterministic code validation, state-based escrow, and developer reputation.*

[Live Demo](https://pillar-protocol.vercel.app/) • [API Docs](#-api-architecture) • [Architecture](#-system-architecture)

</div>

---

## 🚀 The Vision

Freelance development and remote collaboration are fundamentally broken. Scope creep, technical debt, and payment disputes plague the industry. **The Pillar Protocol** solves this by removing the human bottleneck in validation and escrow. 

By employing a quad-agent AI architecture, the protocol automatically converts vague client ideas into strict milestones, mathematically verifies the submitted code against those exact milestones, manages the state of the escrow, and adjusts the developer's reputation score—all entirely autonomously.

---

## 🧠 The Four Pillars (Agent Architecture)

The system is orchestrated by four specialized AI agents, each strictly decoupled to ensure deterministic workflows over probabilistic LLM generation.

### 1. 🏗️ Architect Agent (The Planner)
* **Role:** Translates ambiguous user prompts into structured, immutable JSON milestones.
* **Logic:** Analyzes scope, estimates complexity, and generates explicit constraints (e.g., "Must use `main.c`", "Must include input validation").
* **Output:** JSON schema injected directly into the Supabase database.

### 2. 🔍 Inspector Agent (The Auditor)
* **Role:** A ruthless, static-analysis AI that checks code against the Architect's constraints.
* **Logic:** It doesn't just check if code runs; it checks for **Compliance**.
  * *Example:* If a developer names a file `addition.c` instead of `main.c`, the Inspector fails the build.
  * *Example:* If `scanf` is used without checking the input buffer for non-integer values, it fails the build for security vulnerabilities.
* **Output:** Boolean Pass/Fail flag with detailed technical feedback.

### 3. 💰 Banker Agent (The Escrow)
* **Role:** Manages the state machine of the project's financial flow.
* **States:** `PENDING` → `LOCKED` (Code submitted, awaiting Inspector) → `RELEASED` / `DISPUTED`.
* **Security:** Cryptographically prevents the deletion or modification of milestones once code has been submitted for review.

### 4. 🏆 Bureau Agent (The Judge)
* **Role:** Calculates the **PFI (Performance & Financial Index)**.
* **Logic:** A weighted algorithm evaluating a developer's historical success.
  * *Formula:* PFI = (0.6 * Code Coverage/Quality) + (0.4 * Milestone Completion Rate)
* **Output:** A dynamic reputation score updated in real-time upon milestone release.

---

## 🏗️ System Architecture

Designed for high-speed serverless deployment, Pillar Protocol uses a "Flat & Fast" repository structure.

```text
pillar-protocol/
├── index.html          # Vanilla JS/CSS Frontend (Zero-build pipeline)
├── style.css           # Cyberpunk-inspired terminal UI
├── script.js           # REST API client & UI state management
├── vercel.json         # Vercel Serverless Routing & Python Runtime config
├── requirements.txt    # Python dependencies
└── backend/
    ├── main.py         # FastAPI Entrypoint & Routes
    ├── agents.py       # LLM Prompts and Agent Logic
    └── database.py     # Supabase Connection pooling
```
### Tech Stack
* **Frontend:** Vanilla HTML5, CSS3 (Neon/Glow UI), JavaScript (ES6+).
* **Backend:** Python 3.11+, FastAPI, Pydantic (Data Validation).
* **AI Provider:** LLM-Agnostic Setup (Built for Groq, Gemini, or OpenAI via standard SDKs).
* **Database:** Supabase (PostgreSQL).
* **Deployment:** Vercel (Serverless Functions for Python).

### ⚡ Key Features & Demos

| Feature | Description | Technical Implementation |
| :--- | :--- | :--- |
| **Strict Compliance Auditing** | Prevents "lazy coding" from entering production. | Inspector Agent searches for explicit variables, file names, and error handling loops required by the Architect. |
| **Provider-Agnostic AI** | Never get rate-limited or locked into one provider. | Environment variables allow instant hot-swapping between Gemini, Groq (Llama 3), or OpenAI. |
| **State-Based Mutability** | Prevents race conditions during code review. | Database row-level locking via Supabase when a milestone transitions to `LOCKED`. |
| **Real-time PFI Gauge** | Beautiful, dynamic representation of developer trust. | SVG-based circular progress animation mathematically bound to the Bureau Agent's JSON output. |

### 🚀 Quick Start (Local Development)

**1. Clone & Install**
```bash
git clone [https://github.com/AadityaBhure/pillar-protocol.git](https://github.com/AadityaBhure/pillar-protocol.git)
cd pillar-protocol
pip install -r requirements.txt
```

**2. Environment Configuration (.env)**
```bash
Create a .env file in the root directory. The system is designed to use Groq for high-speed, high-limit hackathon testing.
# AI Provider (Choose One)
GROQ_API_KEY=gsk_your_groq_key
SUPABASE_URL=[https://your-project.supabase.co](https://your-project.supabase.co)
SUPABASE_SERVICE_ROLE_KEY=your_secret_role_key
```

**3. Run the Backend**
```bash
uvicorn backend.main:app --reload --port 8000
```

**4. Serve the Frontend**
In a new terminal window:
```bash
python -m http.server 8080
```

Visit http://localhost:8080 to view the dashboard.

###☁️ Cloud Deployment (Vercel)
The repository is pre-configured for Vercel Serverless deployment via vercel.json.

Import the repository into your Vercel Dashboard.

Override the framework preset to Other.

Add your GROQ_API_KEY, SUPABASE_URL, and SUPABASE_SERVICE_ROLE_KEY in the Environment Variables settings.

Deploy. Vercel will automatically route /api/* traffic to the FastAPI backend and serve the frontend statically.

###🔧 API Architecture

POST /api/plan
Generates structured milestones from a natural language prompt.

Payload: {"prompt": "string", "user_id": "string"}

Response: Returns an array of Milestone Objects with requirements and estimated_hours.

POST /api/submit
The core inspection engine. Accepts multi-part form data (Code Blobs).

Payload: project_id, milestone_id, and File[]

Response:
{
  "passed": false,
  "feedback": "Requirement Failed: The primary file must be named 'main.c', received 'addition.c'. Input validation for non-integers is missing.",
  "pfi_impact": -2.5
}

GET /api/reputation/{user_id}
Retrieves the real-time Bureau stats.

Response: Returns current_pfi, total_projects, and a historical array of score changes.

###🛡️ Security & Constraints
No Code Execution: The Inspector Agent performs high-context static analysis. It does not execute untrusted user code, preventing RCE (Remote Code Execution) vulnerabilities.

Secret Management: Strict .gitignore enforcement ensures .env files are never pushed. Keys are injected at runtime via Vercel's secure environment pipeline.

Payload Limits: Vercel serverless functions cap at 4.5MB per request. The protocol enforces file size limits on upload to prevent memory exhaustion.


