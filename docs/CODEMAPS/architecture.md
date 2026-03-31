<!-- Generated: 2026-04-01 | Files scanned: 45 | Token estimate: ~600 -->

# Architecture Overview

## System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ Chrome Extension (WXT + React 19 + TypeScript)              │
│                                                             │
│  Side Panel ──port──▶ Background SW ──one-shot──▶ Content   │
│  (UI/Forms)  ◀──port──  (Orchestrator)  ◀──response── Script│
│                              │                              │
│                    ┌─────────┴─────────┐                    │
│                    │ Network Capture   │                    │
│                    │ Validator         │                    │
│                    └──────────────────-┘                    │
└─────────────────────────────────────────────────────────────┘
           │ HTTP (ky)
           ▼
┌──────────────────────────────────┐
│ FastAPI Backend (Python 3.12)    │
│ /api/v1/*                        │
│ SQLite (SQLAlchemy + Alembic)    │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ shared/  (Single Source of Truth)│
│ commands.json · validations.json │
│ providers.json                   │
└──────────────────────────────────┘
```

## Data Flow

1. User creates scenarios (steps + validation rules) via Side Panel UI
2. Backend persists scenarios to SQLite via REST API
3. Execution: Side Panel → Background orchestrator → Content Script
4. Background captures network requests during execution
5. Validator checks captured URLs/params against scenario rules
6. Results streamed back to Side Panel via port messages

## Project Structure

```
argos/
├── backend/          767 LOC app, 693 LOC tests
│   ├── app/          FastAPI app (routers, models, schemas)
│   ├── alembic/      3 migrations
│   └── tests/        pytest (6 test files)
├── extension/        ~5,390 LOC
│   └── src/
│       ├── components/   UI (scenarios/, ui/)
│       ├── entrypoints/  background, sidepanel, content, picker
│       ├── lib/          api, executor, hooks, messaging, schemas
│       └── routes/       TanStack Router (hash-based)
└── shared/           73 LOC (3 JSON definition files)
```

## Key Architectural Decisions

- **SQLite** default DB (configurable via DATABASE_URL)
- **Hash-based routing** required for Chrome extension side panel
- **Three-layer messaging**: Side Panel ↔ Background ↔ Content Script
- **Shared JSON definitions** drive both backend validation (Pydantic) and frontend schemas (Zod)
- **No services layer** — business logic lives in routers
