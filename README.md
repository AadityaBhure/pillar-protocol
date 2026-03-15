# Pillar Protocol

> **AI-powered freelance escrow platform** — clients describe projects in plain language, AI breaks them into milestones, payments are held in escrow, and funds release automatically after code passes inspection.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-black?style=for-the-badge&logo=vercel)](https://pillar-protocol.vercel.app)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase)](https://supabase.com)

---

## What is Pillar Protocol?

Pillar Protocol solves a core problem in freelancing: **trust between clients and developers**.

- Clients often pay upfront and get nothing back.
- Developers often deliver work and never get paid.

Pillar Protocol puts an **AI agent in the middle** — it plans the project, holds the money, reviews the code, and only releases payment when the work is verified.

---

## Features

### For Clients
- **AI Project Planning** — Chat with the Architect Agent to break your idea into clear, verifiable milestones
- **Developer Marketplace** — Browse registered developers with their hourly rates and reputation scores
- **Escrow Payments** — Pay once, funds held securely until each milestone is delivered
- **Real-time Dashboard** — Track milestone status, deadlines, and deliverables
- **Download Deliverables** — Download submitted code or view GitHub repos directly
- **Chat with Developers** — Built-in messaging between client and developer

### For Developers
- **Work Dashboard** — See all assigned projects and milestone statuses
- **Code Submission** — Upload files directly or fetch from a GitHub repository
- **Automated Code Review** — Inspector Agent reviews code against requirements
- **Payout Tracking** — See earnings per milestone and total income
- **Reputation System** — Build a PFI (Performance Fidelity Index) score based on quality and timeliness
- **Chat with Clients** — Respond to client messages from the Messages tab

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vanilla HTML, CSS, JavaScript |
| Backend | Python 3.11, FastAPI |
| AI / LLM | Groq API (LLaMA 3.3 70B) |
| Database | Supabase (PostgreSQL) |
| Hosting | Vercel (Serverless) |
| Auth | Custom (bcrypt password hashing) |
| Realtime Chat | HTTP Polling (3s interval) |

---

## System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     CLIENT BROWSER                        │
│                                                          │
│   Client UI          Developer UI         Auth UI        │
│   (Plan·Pay·Chat)    (Submit·Payout·Msg)  (Login/Reg)    │
└──────────────────────────┬───────────────────────────────┘
                           │  REST API
                           ▼
┌──────────────────────────────────────────────────────────┐
│              FASTAPI BACKEND (Vercel Serverless)          │
│                                                          │
│  /auth    /plan    /submit    /payment    /chat           │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  Architect   │  │  Inspector   │  │    Banker     │  │
│  │  Agent (LLM) │  │  Agent (LLM) │  │    Agent      │  │
│  │  Milestone   │  │  Code Review │  │  Escrow       │  │
│  │  Planning    │  │  & Scoring   │  │  Release      │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │           Reputation Manager                      │   │
│  │   PFI Score · On-time tracking · History          │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                  SUPABASE (PostgreSQL)                    │
│                                                          │
│  users · projects · milestones · user_reputation         │
│  chat_messages · deadline_audit · inspection_results     │
└──────────────────────────────────────────────────────────┘
```

---

## Agent Pipeline

```
User describes project
        │
        ▼
  Architect Agent          ← Groq LLaMA 3
  - Asks business questions
  - Generates milestones with hours & deadlines
  - Creates smart project title from conversation
        │
        ▼
  Client pays → Escrow locked
        │
        ▼
  Developer submits code
        │
        ▼
  Inspector Agent          ← Groq LLaMA 3
  - Reviews code vs requirements
  - Scores coverage (0–100)
  - Pass / Fail
        │
      Pass
        │
        ▼
  Banker Agent
  - Releases milestone payment
  - Checks on-time vs late delivery
        │
        ▼
  Reputation Manager
  - Updates PFI score
  - Tracks delivery history
```

---

## Project Structure

```
pillar-protocol/
│
├── api/
│   └── index.py              # Vercel entry point
│
├── backend/
│   ├── main.py               # FastAPI app + all endpoints
│   ├── database.py           # Supabase database manager
│   ├── mock_database.py      # Local dev mock DB
│   └── models.py             # Pydantic models
│
├── agents/
│   ├── architect.py          # Milestone planning + title generation
│   ├── inspector.py          # Code review agent
│   ├── banker.py             # Escrow release logic
│   ├── bureau.py             # Deadline audit agent
│   └── reputation_manager.py # PFI score management
│
├── migrations/               # Supabase SQL migrations (001–009)
│
├── index.html                # Single-page frontend
├── script.js                 # All frontend logic
├── style.css                 # Dark theme UI styles
├── vercel.json               # Vercel routing config
└── deadline_config.json      # Deadline calculation rules
```

---

## Database Schema

### `users`
| Column | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| name | TEXT | Full name |
| email | TEXT | Unique email |
| role | TEXT | `client` or `developer` |
| hourly_rate | NUMERIC | Derived from payment threshold |
| payment_threshold | NUMERIC | Monthly income target (INR) |

### `projects`
| Column | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| user_id | UUID | Client who created it |
| assigned_developer_id | UUID | Hired developer |
| title | TEXT | AI-generated project title |
| developer_hourly_rate | NUMERIC | Snapshotted at project creation |

### `milestones`
| Column | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| project_id | UUID | Parent project |
| title | TEXT | Milestone name |
| estimated_hours | NUMERIC | Hours estimated by AI |
| status | TEXT | `PENDING` → `LOCKED` → `RELEASED` |
| deadline | TIMESTAMPTZ | Auto-distributed deadline |
| timeline_status | TEXT | `on-time` or `late` |
| submission_source | TEXT | `local` or `github` |

### `user_reputation`
| Column | Type | Description |
|---|---|---|
| user_id | UUID | Developer |
| reputation_score | NUMERIC | Current PFI score (0–100) |
| on_time_count | INT | On-time deliveries |
| late_count | INT | Late deliveries |
| reputation_history | JSONB | Full event log |

### `chat_messages`
| Column | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| room_id | TEXT | `{user_a_id}_{user_b_id}` (sorted) |
| sender_id | UUID | Message author |
| sender_name | TEXT | Display name |
| message | TEXT | Message content |
| created_at | TIMESTAMPTZ | Timestamp |

---

## Getting Started

### Prerequisites
- Python 3.11+
- A [Supabase](https://supabase.com) project
- A [Groq](https://console.groq.com) API key

### 1. Clone the repo
```bash
git clone https://github.com/AadityaBhure/pillar-protocol.git
cd pillar-protocol
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
Copy `.env.example` to `.env` and fill in:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
GROQ_API_KEY=your-groq-key
```

### 4. Run database migrations
Run each file in `migrations/` in order (001 → 009) in your Supabase SQL Editor.

### 5. Start the backend
```bash
uvicorn backend.main:app --reload --port 8000
```

### 6. Open the frontend
Open `index.html` in your browser or serve it with any static server.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register client or developer |
| POST | `/auth/login` | Login and get user session |
| POST | `/chat/architect` | Chat with Architect Agent |
| POST | `/plan/finalize` | Finalize milestones and create project |
| GET | `/estimate/{project_id}` | Get price breakdown |
| POST | `/payment/confirm` | Confirm payment and lock milestones |
| POST | `/submit` | Submit code for a milestone |
| GET | `/projects/{user_id}` | Get all client projects |
| GET | `/projects/developer/{dev_id}` | Get developer's assigned projects |
| GET | `/users/developers` | List all developers |
| GET | `/developer/{dev_id}/earnings` | Get developer payout summary |
| POST | `/chat/send` | Send a chat message |
| GET | `/chat/history/{room_id}` | Get chat message history |
| GET | `/chat/rooms/{user_id}` | Get all chat rooms for a user |
| GET | `/reputation/{user_id}` | Get developer reputation |

---

## Deployment (Vercel)

1. Push to GitHub
2. Import repo in [Vercel](https://vercel.com)
3. Add environment variables: `SUPABASE_URL`, `SUPABASE_KEY`, `GROQ_API_KEY`
4. Deploy — Vercel auto-detects `vercel.json` routing

> **Note:** SSE (Server-Sent Events) is not supported on Vercel serverless. The chat uses HTTP polling instead, which works fine.

---

## Key Design Decisions

- **Escrow model** — Payment is locked at project start, released per milestone after code passes inspection. Neither party can cheat.
- **AI milestone planning** — The Architect Agent asks high-level business questions (not technical ones) to understand scope, then generates realistic milestones with proportional hours.
- **Reputation system** — PFI score tracks both code quality (Inspector score) and delivery timeliness (deadline comparison). Developers build a verifiable track record.
- **Hourly rate snapshot** — The developer's rate is snapshotted onto the project at creation time so cost calculations remain consistent even if the developer changes their rate later.
- **Decimal hours** — Milestones support 0.5h increments for small tasks, stored as `NUMERIC(10,2)` in the DB.

---

## License

MIT — free to use, modify, and distribute.

---

*Built with FastAPI, Supabase, Groq LLaMA 3, and vanilla JavaScript.*
