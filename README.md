# 🏛️ Pillar Protocol

<div align="center">

**Trustless software delivery, enforced by AI.**

*A multi-agent escrow platform where clients describe projects in plain English, AI plans and prices them, developers build them, and payments release automatically — only after code passes a strict automated audit.*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)
[![Groq](https://img.shields.io/badge/LLM-Groq%20LLaMA%203-F55036?style=for-the-badge)](https://groq.com)
[![Vercel](https://img.shields.io/badge/Deployed-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com)

</div>

---

## 🎯 The Problem We Solve

Freelance software development is broken by a fundamental trust gap:

- **Clients** pay upfront and hope the developer delivers working code
- **Developers** build and hope the client pays after delivery
- **Both sides** rely on vague contracts, manual reviews, and dispute resolution that takes weeks

**Pillar Protocol eliminates this entirely.** Payment is held in escrow and released *only* when an AI Inspector confirms the submitted code actually implements what was agreed upon. No human arbitration. No ambiguity. Just verifiable delivery.

---

## 🤖 The Four Pillars — AI Agent Architecture

```
Client Prompt
     │
     ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  🏗️  ARCHITECT  │────▶│  🔍  INSPECTOR   │────▶│  💰  BANKER     │────▶│  📊  BUREAU      │
│                 │     │                  │     │                 │     │                  │
│  Interviews     │     │  Reviews code    │     │  Controls       │     │  Calculates PFI  │
│  client, breaks │     │  against reqs,   │     │  PENDING →      │     │  score, updates  │
│  project into   │     │  scores 0–100,   │     │  LOCKED →       │     │  reputation,     │
│  milestones     │     │  pass/fail       │     │  RELEASED       │     │  tracks on-time  │
└─────────────────┘     └──────────────────┘     └─────────────────┘     └──────────────────┘
```

### �️ Architect Agent
The **project planner**. Converts plain-English descriptions into precise, code-verifiable milestone checklists.

- Conducts a conversational interview to understand scope, features, and deadline
- Enforces strict milestone count rules — a "subtraction of two numbers" gets **1 milestone**, not 5
- Supports decimal hour estimates (0.5h minimum) to prevent price inflation
- Actively **scrubs vague requirements** — strips "user-friendly", "clean code", "best practices" before saving
- Generates a smart project title by analysing the full conversation via LLM
- Distributes deadlines proportionally across milestones based on estimated hours
- Powered by **Groq LLaMA 3.3 70B Versatile**

### 🔍 Inspector Agent
The **code auditor**. Reviews submitted code against milestone requirements using LLM analysis.

- Accepts file uploads (`.py`, `.js`, `.ts`, `.java`, `.go`, `.rs`, `.cpp`, `.jsx`, `.tsx`) or full GitHub repo fetches
- Concatenates all files into a single code blob, SHA-256 hashes it for audit integrity
- Returns structured result: `passed` (bool), `coverage_score` (0–100), `feedback`, `missing_requirements`
- Powered by **Groq LLaMA 3.3 70B Versatile**

### 💰 Banker Agent
The **escrow state machine**. Controls the full lifecycle of every milestone payment.

- Manages three states: `PENDING` → `LOCKED` → `RELEASED`
- Records `submission_time` as ISO 8601 timestamp at lock
- Compares submission time against deadline → `on-time` or `late`
- Releases **full payment regardless of timeliness** (reputation tracks the difference)
- Auto-unlocks milestones stuck in `LOCKED` for >5 minutes (graceful failure recovery)
- Simulates the **x402 payment protocol**

### 📊 Bureau / Reputation Manager
The **trust scorer**. Builds a persistent, tamper-evident reputation profile for every developer.

- Calculates **PFI (Performance Fidelity Index)** after every milestone release
- Configurable score weights via `deadline_config.json`:
  - On-time delivery: **+2 pts** | Late delivery: **−5 pts**
  - High quality (PFI > 80): **+1 pt** | Low quality (PFI < 50): **−2 pts**
- Score clamped to 0–100 range
- Full event history (type, delta, timestamp, milestone ID) persisted to Supabase

---

## ⚙️ Tech Stack

| Layer | Technology | Role |
|---|---|---|
| **Frontend** | Vanilla HTML / CSS / JavaScript | Zero-build SPA |
| **Backend** | Python 3.11, FastAPI | REST API + agent orchestration |
| **LLM** | Groq API — LLaMA 3.3 70B | Architect, Inspector, title generation |
| **Database** | Supabase (PostgreSQL) | All persistent data |
| **Auth** | Custom bcrypt | Client + developer accounts |
| **Hosting** | Vercel Serverless Python | Zero-config deployment |
| **Realtime** | HTTP polling (3s) | Chat message delivery |
| **GitHub Integration** | GitHub Trees API + parallel fetch | Code submission from repos |

---

## ✨ Key Features

**For Clients**
- 💬 AI-powered project planning via conversational chat — no technical knowledge required
- 💳 Transparent milestone pricing — developer's hourly rate × estimated hours, shown as full breakdown
- 🔒 Escrow protection — funds locked until code passes inspection
- 🏪 Developer marketplace — browse developers with live hourly rates and reputation scores
- 📨 Real-time client ↔ developer chat
- 📊 Project dashboard — track every milestone status, deadline, cost, and download delivered code

**For Developers**
- 📋 Structured work — every project arrives with clear, code-verifiable requirements
- ⚡ Automatic payment release — pass the Inspector, get paid. No chasing invoices
- ⭐ Verifiable reputation — on-time rate and PFI score visible to all clients
- 🐙 GitHub integration — submit code directly from a repository URL
- 💰 Payout dashboard — total earnings, per-project breakdown, milestone history

**Platform**
- 🛡️ Strict compliance auditing — Inspector rejects code that doesn't implement agreed requirements
- 🔄 Provider-agnostic AI — accepts `GROQ_API_KEY` or `GEMINI_API_KEY`; swap LLMs without code changes
- 🗄️ Mock database fallback — runs fully offline without Supabase for local development
- 📐 Decimal milestone hours — 0.5h increments prevent trivial task inflation
- 🔁 Backward-compatible deadlines — null deadlines treated as on-time (no breaking changes)

---

## 🚀 Quick Start — Local Development

### Prerequisites
- Python 3.11+
- [Groq API key](https://console.groq.com) (free tier available)
- [Supabase](https://supabase.com) project *(optional — mock DB works without it)*

### 1. Clone & install

```bash
git clone https://github.com/AadityaBhure/pillar-protocol.git
cd pillar-protocol

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Required
GROQ_API_KEY=gsk_your_groq_key_here

# Required for production (optional locally — mock DB used if missing)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Optional — prevents GitHub API rate limits on repo fetch
GITHUB_TOKEN=ghp_your_token
```

### 3. Run database migrations

In your **Supabase SQL Editor**, run these files in order:

```
migrations/001_add_deadline_fields_to_milestones.sql
migrations/002_add_reputation_fields_to_users.sql
migrations/003_create_deadline_audit_table.sql
migrations/004_add_submission_source_to_milestones.sql
migrations/005_create_users_table.sql
migrations/006_add_developer_to_projects.sql
migrations/007_add_developer_hourly_rate_to_projects.sql
migrations/008_change_estimated_hours_to_numeric.sql
migrations/009_create_chat_messages.sql
```

### 4. Start the backend

```bash
uvicorn backend.main:app --reload --port 8000
```

API available at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

### 5. Open the frontend

```bash
# Option A — open directly
start index.html

# Option B — serve with Python
python -m http.server 3000
# then visit http://localhost:3000
```

> The frontend auto-detects `localhost` and routes API calls to `http://localhost:8000`.

---

## ☁️ Vercel Deployment

The project is pre-configured for zero-config Vercel deployment via `vercel.json`.

**How routing works:**

```json
{
  "builds": [
    { "src": "api/index.py",  "use": "@vercel/python" },
    { "src": "index.html",    "use": "@vercel/static" },
    { "src": "script.js",     "use": "@vercel/static" },
    { "src": "style.css",     "use": "@vercel/static" }
  ],
  "routes": [
    { "src": "/(auth|plan|chat|submit|project|projects|milestone|reputation|github|estimate|payment|health|users|events|developer)(/.*)?", "dest": "/api/index.py" },
    { "src": "/(.*)", "dest": "/index.html" }
  ]
}
```

**Deploy steps:**

1. Push repo to GitHub
2. Go to [vercel.com](https://vercel.com) → **New Project** → Import repo
3. Add environment variables in Vercel dashboard:
   - `GROQ_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
4. Click **Deploy** — done

> **Note:** Vercel serverless functions have a 10s execution limit on the free tier. The SSE `/events/{user_id}` endpoint is not supported on Vercel — the frontend uses HTTP polling for chat instead.

---

## 📡 API Reference

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register client or developer |
| `POST` | `/auth/login` | Login, receive user profile |
| `GET` | `/auth/user/{user_id}` | Fetch user by ID |

### Planning
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat/architect` | Interactive chat with Architect Agent |
| `POST` | `/plan/finalize` | Save milestones, assign developer, generate title |
| `GET` | `/estimate/{project_id}` | Total cost = hours × developer rate |

### Payment & Escrow
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/payment/confirm` | Confirm payment (milestones stay PENDING) |

### Code Submission
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/submit` | Submit code files or GitHub files for inspection |
| `POST` | `/github/fetch` | Recursively fetch all code from a GitHub repo |

### Projects & Milestones
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/projects/{user_id}` | All projects for a client |
| `GET` | `/projects/developer/{dev_id}` | All projects assigned to a developer |
| `GET` | `/project/{project_id}` | Full project with milestones + inspection results |
| `PATCH` | `/milestone/{milestone_id}/deadline` | Adjust milestone deadline |
| `GET` | `/milestone/{milestone_id}/download` | Download submitted files as ZIP |
| `POST` | `/milestone/{milestone_id}/unlock` | Manually unlock a stuck milestone |

### Users, Reputation & Earnings
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users/developers` | List all developers with rates |
| `GET` | `/reputation/{user_id}` | Full reputation profile + history |
| `GET` | `/developer/{dev_id}/earnings` | Earnings summary |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat/send` | Send a message |
| `GET` | `/chat/history/{room_id}` | Fetch all messages in a room |
| `GET` | `/chat/rooms/{user_id}` | All chat rooms for a user |

---

## 📁 Project Structure

```
pillar-protocol/
├── agents/
│   ├── architect.py          # Milestone planner + LLM title generation
│   ├── inspector.py          # Code review + coverage scoring
│   ├── banker.py             # Escrow state machine + x402 payment sim
│   ├── bureau.py             # PFI calculation
│   └── reputation_manager.py # Score deltas + on-time tracking
├── backend/
│   ├── main.py               # All FastAPI routes
│   ├── database.py           # Supabase query layer
│   ├── mock_database.py      # In-memory fallback for local dev
│   └── models.py             # Pydantic models
├── api/
│   └── index.py              # Vercel serverless entry point
├── migrations/               # SQL migration files (001–009)
├── utils/
│   └── file_processor.py     # File validation + ZIP creation
├── index.html                # Single-page frontend
├── script.js                 # All frontend logic
├── style.css                 # Dark theme design system
├── vercel.json               # Serverless deployment config
└── deadline_config.json      # Configurable reputation weights
```

---

## 🏆 Built For

Pillar Protocol was built as a hackathon project demonstrating:

- **Multi-agent AI orchestration** — four agents with distinct LLM-powered roles
- **Trustless escrow via AI** — automated code verification replaces human arbitration
- **Provider-agnostic LLM** — works with Groq, OpenAI, or any compatible API
- **Full-stack serverless** — FastAPI + Vanilla JS on Vercel, zero infrastructure

---

*Built with ❤️ — Powered by Groq LLaMA 3, FastAPI, and Supabase.*
*Made By: Aaditya Bhure, Reyon Bose*
