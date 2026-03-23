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

No test runner, linter, or formatter is configured for the backend.

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

No lint, typecheck, or test scripts are configured for the extension.

## Backend Architecture

```
backend/
├── app/
│   ├── main.py        # FastAPI app entry, CORS middleware, root health check
│   ├── config.py      # Pydantic Settings (loads from .env)
│   ├── database.py    # SQLAlchemy engine, Base, SessionLocal, get_db()
│   ├── models.py      # ORM models (inherit from Base)
│   ├── schemas.py     # Pydantic request/response schemas + enums
│   └── routers/       # Route handlers (one file per domain)
│       └── scenarios.py
├── alembic/
│   ├── env.py         # Gets DB URL from app.config.Settings at runtime
│   └── versions/      # Migration scripts
├── alembic.ini        # sqlalchemy.url set by env.py at runtime
├── .env               # DATABASE_URL (required)
└── requirements.txt
```

**Domain model:** `Scenario` → has many `TestRun` → has many `TestRunResult`. All PKs are UUID strings generated in Python. Timestamps are ISO 8601 strings (not SQL datetime), generated via `datetime.now(timezone.utc).isoformat()`. JSON columns store `steps`, `validations` (on Scenario) and `actual_value` (on TestRunResult).

**Response envelope:** Single resource: `{ data: {...} }`. List resource: `{ data: [...], meta: { page, size, total_count, total_pages } }`.

**Key patterns:**
- Database sessions via FastAPI dependency injection: `db: Session = Depends(get_db)`
- All ORM models inherit from `Base` (in `database.py`) and live in `app/models.py`
- Pydantic schemas (request/response) and enums (MatchType, SelectorStrategy, SortBy, SortOrder) live in `app/schemas.py`, separate from ORM models
- New models must be imported in `alembic/env.py` for autogenerate to detect them
- Business logic lives directly in routers (no services layer)
- Config uses Pydantic BaseSettings with `.env` file loading
- SQLite by default (`sqlite:///./argos.db`), configurable via `DATABASE_URL`
- `connect_args={"check_same_thread": False}` is set for SQLite compatibility — must be adjusted if switching to PostgreSQL

## Extension Architecture

```
extension/
├── src/
│   ├── entrypoints/
│   │   ├── sidepanel/     # Main UI (React SPA)
│   │   ├── background/    # Service worker + execution orchestrator
│   │   └── content/       # Content script (element finding + click execution)
│   ├── routes/            # Tanstack Router (hash-based, file-based)
│   │   └── scenarios/     # Scenario CRUD routes
│   ├── components/
│   │   ├── ui/            # shadcn/ui components
│   │   └── scenarios/     # Scenario domain components
│   ├── lib/
│   │   ├── api/           # ky HTTP client + API functions
│   │   ├── hooks/         # Tanstack Query hooks
│   │   ├── schemas/       # Zod schemas (mirrors backend Pydantic schemas)
│   │   ├── messaging/     # Chrome port/message types and protocol helpers
│   │   ├── executor/      # Step execution result types
│   │   └── commands.ts    # Command registry (COMMANDS, COMMAND_MAP, COMMAND_CATEGORIES)
│   └── styles/            # Tailwind CSS globals
├── wxt.config.ts          # Extension manifest, React module, Tailwind Vite plugin
└── components.json        # shadcn/ui config
```

**Key patterns:**
- API base URL via `VITE_API_BASE_URL` env var (build-time, defaults to `http://127.0.0.1:8000`)
- Server state via Tanstack Query (`retry: 1`, `staleTime: 30s`), forms via React Hook Form + Zod
- Hash-based routing (required for extension side panel)
- `@/` path alias maps to `src/`
- Command registry in `lib/commands.ts` defines available commands (goto, click, etc.) with parameter schemas for dynamic form rendering in the step builder
- Zod schemas in `lib/schemas/` mirror backend Pydantic schemas — keep them in sync when changing either side
- Drag-and-drop step reordering via `@dnd-kit`; collapsible steps via Radix primitives

**Chrome permissions** (configured in `wxt.config.ts`): `sidePanel`, `activeTab`, `tabs`, `scripting`, `webNavigation` + host permission `<all_urls>`

## Step Execution Architecture

The extension executes scenario steps via a three-layer messaging system:

```
Side Panel ──port──▶ Background (orchestrator) ──one-shot──▶ Content Script
            ◀──port──                            ◀──response──
```

**Flow:**
1. Side panel connects via `chrome.runtime.connect()` on port `"argos-execution"`
2. Sends `EXECUTE_STEPS` or `EXECUTE_SCENARIO` with steps array and timeouts
3. Background orchestrator creates a new tab, runs steps sequentially
4. For each step: emits `STEP_START` → executes command → emits `STEP_SUCCESS` or `STEP_ERROR`
5. `goto` command: navigates tab + injects content script + waits for `CONTENT_READY`
6. `click` command: sends `EXEC_CLICK` one-shot message to content script with selector entries
7. Content script finds elements via CSS/XPath/linkText strategies and performs the action
8. Final `EXECUTION_COMPLETE` message carries all step results

**Cancellation:** Execution aborts if the port disconnects (side panel closed) or the execution tab is closed. A concurrency guard (`let executing = false`) prevents overlapping runs.

**Key files:** `lib/messaging/types.ts` (message type definitions), `lib/messaging/protocol.ts` (port connection helper), `entrypoints/background/orchestrator.ts` (step execution engine), `lib/executor/types.ts` (result types), `entrypoints/content/index.ts` (element finder + click handler)

## Reference Documents

- `documents/ga4_audit_json_spec.docx` — GA4 audit specification
- `documents/install.md` — Installation guide (Turkish)
- `docs/superpowers/specs/` — Design specs for execution engine and future features

## Commit Convention

Conventional commits: `feat:`, `chore:`, `docs:`, `fix:`, etc.
