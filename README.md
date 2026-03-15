# Pillar Protocol

> AI-powered freelance escrow platform — clients describe projects, AI plans them, developers build them, code is auto-reviewed, and payments release automatically.

## What It Does

Pillar Protocol removes the trust problem in freelancing. Instead of clients hoping developers deliver and developers hoping clients pay, the platform enforces both sides through an AI-driven escrow system.

1. **Client** describes a project in plain English
2. **Architect Agent** (LLM) breaks it into milestones with time estimates
3. **Client pays upfront** — funds locked in escrow per milestone
4. **Developer submits code** for each milestone
5. **Inspector Agent** (LLM) reviews code against requirements
6. **Banker Agent** releases payment on pass — tracks on-time vs late
7. **Reputation score** updates automatically after every delivery

## Features

- AI chat-based project planning (Groq / LLaMA 3)
- Milestone-based escrow with automatic payment release
- Code inspection via LLM (coverage scoring, requirement matching)
- Developer reputation system (PFI score, on-time rate)
- Per-developer hourly rate with realistic milestone pricing
- Client ↔ Developer real-time chat
- GitHub repo fetch for code submission
- INR currency throughout
- Vercel deployment (serverless)

## Tech Stack

| Layer     | Technology                  |
|-----------|-----------------------------|
| Frontend  | HTML / CSS / Vanilla JS     |
| Backend   | Python, FastAPI             |
| AI / LLM  | Groq API (LLaMA 3)          |
| Database  | Supabase (PostgreSQL)       |
| Hosting   | Vercel (Serverless)         |
| Auth      | Custom (bcrypt)             |

## Project Structure

```
pillar-protocol/
├── agents/
│   ├── architect.py       # Milestone planning + project title generation
│   ├── inspector.py       # Code review agent
│   ├── banker.py          # Payment release + timeline check
│   ├── bureau.py          # Deadline audit
│   └── reputation_manager.py  # PFI score tracking
├── backend/
│   ├── main.py            # FastAPI routes
│   ├── database.py        # Supabase queries
│   ├── models.py          # Pydantic models
│   └── mock_database.py   # Local dev fallback
├── api/
│   └── index.py           # Vercel serverless entry point
├── migrations/            # SQL migration files (run in Supabase)
├── index.html             # Single-page frontend
├── script.js              # All frontend logic
├── style.css              # Dark theme UI
└── vercel.json            # Deployment config
```

## Setup

### 1. Clone & install

```bash
git clone https://github.com/AadityaBhure/pillar-protocol.git
cd pillar-protocol
pip install -r requirements.txt
```

### 2. Environment variables

Copy `.env.example` to `.env` and fill in:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
GROQ_API_KEY=your_groq_api_key
```

### 3. Run database migrations

Run all files in `/migrations/` in order (001 → 009) in your Supabase SQL Editor.

### 4. Run locally

```bash
uvicorn backend.main:app --reload --port 8000
```

Open `index.html` in your browser.

## Deployment (Vercel)

1. Push to GitHub
2. Import repo in Vercel
3. Add environment variables in Vercel dashboard
4. Deploy — routes are pre-configured in `vercel.json`

## Architecture

See `ARCHITECTURE.md` or open `architecture_diagram.html` in a browser for visual diagrams.

## License

MIT
