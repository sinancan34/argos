# Argos

**Open-source Chrome extension for auditing tracking pixels across any website.**

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![Chrome Extension](https://img.shields.io/badge/Chrome-Manifest_V3-4285F4.svg)](https://developer.chrome.com/docs/extensions/mv3/)

---

## What is Argos?

Argos is a universal pixel code audit tool that validates tracking pixels from **any** provider — Google Analytics 4, Meta Pixel, TikTok Pixel, LinkedIn Insight Tag, custom pixels, and more.

**Core workflow:**

1. **Define scenarios** — Create reusable audit scenarios with browser steps and validation rules
2. **Execute steps** — Argos automates browser actions (navigate, click) in a real Chrome tab
3. **Capture network requests** — All outgoing requests are captured during execution
4. **Validate pixel fires** — Captured requests are checked against your defined rules (URL patterns, query parameters)

**Who is it for?**

- **QA teams** verifying pixel implementations across pages and flows
- **Marketing teams** auditing tag setups before and after deployments
- **Developers** testing tracking code during development

## Key Features

- **Scenario-based testing** — Define reusable audit scenarios with steps and validation rules
- **Automated browser actions** — `goto` (navigate) and `click` commands with CSS, XPath, and linkText selectors
- **Network request capture** — Intercepts all outgoing requests during step execution
- **Flexible matching** — 6 match strategies: `exact`, `contains`, `startsWith`, `endsWith`, `regex`, `exists`
- **Parameter validation** — Validate query parameters on captured URLs
- **Drag-and-drop step reordering** — Reorder steps visually
- **Real-time execution progress** — Live step-by-step status updates
- **Extensible command registry** — Add new commands via shared JSON definitions
- **Interactive element picker** — Visual CSS selector generator overlay on target pages
- **Provider-aware suggestions** — Auto-suggest URL patterns and parameters for known tracking providers (GA4, etc.)
- **API rate limiting** — Configurable rate limits on all backend endpoints (default: 60/minute)
- **Consistent error responses** — Structured error envelope with error codes, messages, and validation details
- **Paginated list endpoints** — Server-side pagination, filtering, and sorting with metadata and navigation links
- **Health check endpoint** — Database connectivity check at `/health`

## Architecture

Argos is a monorepo with three components:

```
argos/
├── backend/     # FastAPI REST API + SQLite database
├── extension/   # Chrome extension (DevTools panel UI + background worker + content scripts)
└── shared/      # JSON definitions shared between backend and extension
```

The Chrome extension uses a three-layer messaging architecture:

```
┌────────────────┐     port       ┌────────────────--┐     one-shot     ┌────────────────┐
│ DevTools Panel │ ◄────────────► │   Background SW  │ ◄──────────────► │ Content Script │
│    (React)     │ execution msgs │  (Orchestrator)  │   element cmds   │ (DOM actions)  │
└────────────────┘                └────────────────--┘                  └────────────────┘
```

1. DevTools panel sends execution requests via Chrome port
2. Background service worker orchestrates step execution
3. Content script performs DOM actions (find elements, click)
4. Network capture intercepts outgoing requests during execution
5. Validator checks captured requests against scenario rules

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Backend** | FastAPI 0.135, SQLAlchemy, Alembic, Pydantic, slowapi, Python 3.12, SQLite |
| **Extension** | WXT (Manifest V3), React 19, TypeScript, Tailwind CSS v4, shadcn/ui, Tanstack Router & Query |
| **Shared** | JSON definitions for commands and validation rules |

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- npm
- Google Chrome

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/sinancan34/argos.git
cd argos

# Set up Python virtual environment
cd backend
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env   # Edit .env if needed (DATABASE_URL, CORS_ALLOWED_ORIGINS)

# Run database migrations
alembic upgrade head
```

### Extension Setup

```bash
# From the project root
cd extension

# Install dependencies
npm install

# Configure environment
cp .env.example .env   # Edit .env if needed (VITE_API_BASE_URL, default: http://127.0.0.1:8000)
```

`VITE_API_BASE_URL` is read at build time — rebuild the extension after changing it.

### Running

Both the backend and extension must run simultaneously. Start the backend first, then the extension.

**Start the backend:**

```bash
cd backend
source env/bin/activate  # On Windows: env\Scripts\activate

python -m uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. All resource endpoints are under `/api/v1/` (e.g., `/api/v1/scenarios`). Health check is at `/health`.

**Start the extension** (in a separate terminal):

```bash
cd extension

npm run dev   # Opens Chrome with the extension loaded
```

For a production build:

```bash
cd extension

npm run build
# Load unpacked from extension/output/chrome-mv3/ in Chrome
```

## Project Structure

```
argos/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI app, CORS, rate limiting, exception handlers
│   │   ├── config.py              # Settings (DATABASE_URL, CORS, RATE_LIMIT from .env)
│   │   ├── database.py            # SQLAlchemy engine, session, Base
│   │   ├── models.py              # ORM models (Scenario, TestRun, TestRunResult)
│   │   ├── schemas.py             # Pydantic schemas + enums
│   │   ├── exceptions.py          # AppException + error envelope models (ErrorDetail, ErrorBody, ErrorEnvelope)
│   │   ├── command_registry.py    # Loads shared/commands.json
│   │   ├── validation_registry.py # Loads shared/validations.json
│   │   └── routers/
│   │       ├── scenarios.py       # CRUD + list with pagination, filtering, sorting
│   │       └── health.py          # /health endpoint (API + DB connectivity check)
│   ├── alembic/                   # Database migrations
│   └── requirements.txt
│
├── extension/
│   ├── src/
│   │   ├── app/                   # Shared React app shell (providers + router)
│   │   ├── entrypoints/
│   │   │   ├── devtools/          # DevTools page — registers the "Argos" panel
│   │   │   ├── devtools-panel/    # React SPA (main UI), hosted in the DevTools panel
│   │   │   ├── background/        # Service worker, orchestrator, network capture, validator
│   │   │   ├── content/           # Content script (element finder + click handler)
│   │   │   └── picker.content/    # Element picker overlay for CSS selector generation
│   │   ├── routes/                # Tanstack Router (hash-based)
│   │   ├── components/
│   │   │   ├── ui/                # shadcn/ui components
│   │   │   └── scenarios/         # Scenario domain components
│   │   └── lib/
│   │       ├── api/
│   │       │   ├── client.ts      # ky HTTP client with error hook
│   │       │   ├── scenarios.ts   # Scenario CRUD + list with query params
│   │       │   └── errors.ts      # API error parser + ApiError type guard
│   │       ├── hooks/             # Tanstack Query hooks
│   │       ├── schemas/           # Zod schemas (mirrors backend Pydantic)
│   │       ├── messaging/         # Chrome message types + protocol
│   │       ├── picker/            # Element picker logic
│   │       └── executor/          # Execution result types + matchers
│   ├── .env.example               # Environment template (VITE_API_BASE_URL)
│   └── wxt.config.ts              # Extension manifest config
│
└── shared/
    ├── commands.json               # Command definitions + selector strategies + match types
    ├── validations.json            # Field constraints for scenarios and parameters
    └── providers.json              # Tracking provider definitions + parameter suggestions
```

## How It Works

### Shared Definitions

The `shared/` directory contains JSON files that serve as the **single source of truth** for both backend and extension:

- **`commands.json`** — Defines available commands (`goto`, `click`), selector strategies (`css`, `xpath`, `linkText`), and match types
- **`validations.json`** — Defines field constraints (types, required fields, min/max values, conditional rules)
- **`providers.json`** — Tracking provider definitions (e.g., Google Analytics) with URL patterns and parameter suggestions

Both sides load from these files: the backend converts them to Pydantic validators, and the extension converts them to Zod schemas. To add a new command or validation rule, update the shared JSON — both sides derive from it automatically.

### API

All resource endpoints are under `/api/v1/` (e.g., `/api/v1/scenarios`). Health check is at `/health` (root level).

**Response envelopes:**

| Operation | Shape |
|-----------|-------|
| Single resource | `{ data: {...} }` |
| List resource | `{ data: [...], meta: { page, size, total_count, total_pages }, links: { self, first, last, next, prev } }` |
| Delete | `{ data: { id: "..." } }` |
| Error | `{ error: { code, message, details[] } }` |

**List query parameters:** `page`, `size`, `name` (search), `status` (filter), `sort_by`, `sort_order`.

**Rate limiting:** All endpoints are rate-limited (default: `60/minute`, configurable via `RATE_LIMIT` env var). Exceeding the limit returns `429` with a `Retry-After` header.

### Execution Modes

- **Step Test** — Runs steps only (no network capture or validation). Useful for testing browser automation.
- **Scenario Run** — Runs steps, captures network requests, and evaluates validation rules. Full audit mode.

### Validation Pipeline

Each validation rule defines:
- A **URL match** — Pattern to identify the pixel request (e.g., `contains: "collect"` for GA4, `contains: "tr/"` for Meta)
- **Parameter checks** (optional) — Validate specific query parameters on matched URLs

Match types supported: `exact`, `contains`, `startsWith`, `endsWith`, `regex`, `exists`.

## Contributing

Contributions are welcome! Since no linter or test runner is configured yet, please:

1. Follow the existing code patterns
2. Update shared JSON definitions when adding commands or validation rules
3. Keep Pydantic schemas (backend) and Zod schemas (extension) in sync
4. Use conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, etc.

## License

MIT
