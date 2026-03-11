# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Argos is a GA4 Audit Tool with a FastAPI backend and Chrome extension frontend.

- **Backend:** FastAPI + SQLAlchemy + Alembic, Python 3.12
- **Extension:** WXT (Manifest V3) + React 19 + TypeScript + Tailwind CSS v4 + shadcn/ui

## Commands

All backend commands run from `backend/` with the virtual environment activated (`source env/bin/activate`).

```bash
# Run dev server
python -m uvicorn app.main:app --reload

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1

# Install dependencies
pip install -r requirements.txt
```

## Architecture

```
backend/
├── app/
│   ├── main.py        # FastAPI app entry point, routes
│   ├── config.py      # Pydantic Settings (loads from .env)
│   └── database.py    # SQLAlchemy engine, Base, SessionLocal, get_db()
├── alembic/
│   ├── env.py         # Gets DB URL from app.config.Settings at runtime
│   └── versions/      # Migration scripts
├── alembic.ini        # sqlalchemy.url set by env.py at runtime
├── .env               # DATABASE_URL (required)
└── requirements.txt
```

**Domain model:** `Scenario` → has many `TestRun` → has many `TestRunResult`. All PKs are UUID strings generated in Python. Timestamps are ISO 8601 strings (not SQL datetime), generated via `datetime.now(timezone.utc).isoformat()`. JSON columns store `steps`, `validations` (on Scenario) and `actual_value` (on TestRunResult).

**Key patterns:**
- Database sessions via FastAPI dependency injection: `db: Session = Depends(get_db)`
- All ORM models inherit from `Base` (in `database.py`) and live in `app/models.py`
- New models must be imported in `alembic/env.py` for autogenerate to detect them
- Config uses Pydantic BaseSettings with `.env` file loading
- SQLite by default (`sqlite:///./argos.db`), configurable via `DATABASE_URL`
- `connect_args={"check_same_thread": False}` is set for SQLite compatibility — must be adjusted if switching to PostgreSQL

## Extension Commands

All extension commands run from `extension/`.

```bash
# Dev mode (opens Chrome with extension loaded)
npm run dev

# Production build
npm run build
# Load unpacked from extension/.output/chrome-mv3/

# Install dependencies
npm install
```

## Extension Architecture

```
extension/
├── src/
│   ├── entrypoints/
│   │   ├── sidepanel/     # Main UI (React SPA)
│   │   └── background/    # Service worker (side panel open)
│   ├── routes/            # Tanstack Router (hash-based)
│   ├── components/
│   │   ├── ui/            # shadcn/ui components
│   │   └── scenarios/     # Scenario CRUD components
│   ├── lib/
│   │   ├── api/           # ky HTTP client + API functions
│   │   ├── hooks/         # Tanstack Query hooks
│   │   └── schemas/       # Zod schemas (mirrors backend)
│   └── messaging/         # Chrome message passing (future engine)
├── wxt.config.ts
└── components.json        # shadcn/ui config
```

**Key patterns:**
- API base URL via `VITE_API_BASE_URL` env var (build-time)
- Server state via Tanstack Query, forms via React Hook Form + Zod
- Hash-based routing (required for extension side panel)
- `@/` path alias maps to `src/`

## Commit Convention

Conventional commits: `feat:`, `chore:`, `docs:`, `fix:`, etc.
