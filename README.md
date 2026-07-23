# Argos

**Open-source pixel code audit tool — automate browser actions in a real Chrome tab and validate tracking pixel fires against your rules.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Chrome Extension](https://img.shields.io/badge/Chrome-Manifest_V3-4285F4.svg)](https://developer.chrome.com/docs/extensions/mv3/)

## What is Argos?

Argos audits tracking pixels the way a QA engineer would — but automated and repeatable. Everything runs locally: a FastAPI backend persists devices and scenarios, and the UI lives in a Chrome DevTools panel.

1. **Define a scenario** — browser steps plus the pixel fires you expect
2. **Execute** — Argos drives a real Chrome tab under an emulated device profile
3. **Capture** — every outgoing network request during the run, including POST bodies
4. **Validate** — captured traffic is checked against your rules

Argos ships with provider presets (currently Google Analytics) and audits any other pixel — Meta, TikTok, LinkedIn, first-party endpoints — through custom URL rules. Built for QA engineers verifying pixel implementations, marketing teams auditing tag setups, and developers testing tracking code.

## Key Features

- **Scenario-based audits** with two modes: **Step Test** (browser steps only) and **Scenario Run** (steps + network capture + validation)
- **Browser automation** — `goto` and `click` commands driven by CSS selectors
- **Device emulation** — viewport, user agent, and touch from Chrome DevTools device presets, applied via `chrome.debugger`/CDP; if emulation is skipped or fails, the run continues at the default viewport
- **Interactive element picker** — click an element on the target page to generate its CSS selector
- **Network capture including POST bodies** — raw and form-data payloads are decoded and validated per event line
- **Flexible validation** — six match types (`exact`, `contains`, `startsWith`, `endsWith`, `regex`, `exists`) on URLs and parameters, plus GA4 item parsing (`pr1.nm`, `pr1.id`, …)
- **Provider presets + custom rules** — Google Analytics preset today, any pixel via custom URL rules; extensible through `shared/providers.json`
- **Drag-and-drop step builder** with live execution progress
- **REST API** with pagination, filtering, sorting, rate limiting, and consistent response envelopes

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+ and npm
- Google Chrome

### 1. Backend

```bash
git clone https://github.com/sinancan34/argos.git
cd argos/backend

python -m venv env
source env/bin/activate           # Windows: env\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # defaults work out of the box
alembic upgrade head              # create the database
python -m scripts.seed_devices   # seed device presets
```

> [!IMPORTANT]
> Every scenario belongs to a device — seed devices before creating scenarios. Seeding is idempotent, so it is safe to re-run.

### 2. Extension

```bash
cd ../extension

npm install
cp .env.example .env              # VITE_API_BASE_URL, defaults to http://127.0.0.1:8000
```

`VITE_API_BASE_URL` is read at build time — rebuild the extension after changing it.

### 3. Run

Start the backend first, then the extension (two terminals):

```bash
# Terminal 1 — API at http://127.0.0.1:8000
cd backend && source env/bin/activate
python -m uvicorn app.main:app --reload

# Terminal 2 — opens Chrome with the extension loaded
cd extension
npm run dev
```

For a production build: `npm run build`, then load `extension/output/chrome-mv3/` as an unpacked extension.

### 4. First audit

Argos lives in Chrome DevTools — there is no popup or side panel. Open DevTools on any page and switch to the **Argos** panel, then:

1. Create a scenario and pick a device
2. Add steps — use the element picker to grab selectors
3. Add validation rules — a provider preset or a custom URL match, plus optional parameter checks
4. Hit **Run**

## Architecture

Argos is a monorepo with three components:

| Component | Stack |
|-----------|-------|
| `backend/` | FastAPI · SQLAlchemy 2 · Alembic · Pydantic · slowapi · Python 3.12 · SQLite |
| `extension/` | WXT (Manifest V3) · React 19 · TypeScript · Tailwind CSS v4 · shadcn/ui · Tanstack Router & Query · Zod |
| `shared/` | JSON definitions — the single source of truth for both sides |

**Domain model:** `Device` (an emulation profile seeded from Chrome DevTools presets) has many `Scenario`; every scenario requires a device.

The extension uses three-layer messaging:

```
┌────────────────┐      port      ┌──────────────────┐     one-shot     ┌────────────────┐
│ DevTools Panel │ ◄────────────► │  Background SW   │ ◄──────────────► │ Content Script │
│    (React)     │ execution msgs │  (orchestrator)  │   element cmds   │  (DOM actions) │
└────────────────┘                └──────────────────┘                  └────────────────┘
```

The background service worker hosts the orchestrator, device emulation (CDP), network capture, and validator.

## How It Works

**Shared definitions.** The JSON files in `shared/` define the available commands (`goto`, `click`), field constraints, and tracking providers. The backend derives Pydantic validators from them; the extension derives Zod schemas. Adding a command or provider starts with editing the shared JSON — both sides pick it up.

**Execution.** In scenario-run mode the orchestrator opens a fresh tab, applies device emulation, runs the steps, and captures all outgoing requests — URLs plus decoded POST bodies. Each body line becomes its own parameter set, and GA4's compact item tokens (`pr1`, `pr2`, …) expand into dot-notation keys like `pr1.nm`.

**Validation.** Each rule identifies the pixel request by provider preset or a custom URL match (e.g., `contains: "/g/collect"` for GA4), then optionally checks parameters. A rule passes if any captured request has any parameter set satisfying all its checks. Match types: `exact`, `contains`, `startsWith`, `endsWith`, `regex`, `exists`.

**API.** Resources live under `/api/v1/scenarios` and `/api/v1/devices` (CRUD + paginated lists); `/health` reports API and database status. Responses use consistent envelopes — `{ data }` for single resources, `{ data, meta, links }` for lists, `{ error: { code, message, details } }` for errors — and all endpoints are rate-limited (default `60/minute`, configurable via `RATE_LIMIT`). Interactive API docs are at `http://127.0.0.1:8000/docs` while the backend is running.

## Project Structure

```
argos/
├── backend/
│   ├── app/              # FastAPI app — models, schemas, registries, routers (scenarios, devices, health)
│   ├── alembic/          # Database migrations
│   ├── scripts/          # Device seeder + Chrome DevTools presets
│   └── tests/            # pytest suite
├── extension/
│   └── src/
│       ├── entrypoints/  # devtools-panel (UI), background (orchestrator, emulation, capture, validator),
│       │                 # content + picker.content (in-page scripts)
│       ├── lib/          # API client, Zod schemas, executor, devices, messaging, picker
│       ├── components/   # shadcn/ui + scenario components
│       └── routes/       # Tanstack Router (hash-based)
└── shared/               # commands.json, validations.json, providers.json
```

## Development & Testing

Both sides have test suites:

```bash
# Backend (from backend/, venv active)
pytest                                       # or: pytest --cov=app --cov-report=term-missing

# Extension (from extension/)
npm test                                     # or: npm run test:coverage
```

No linter or CI is configured yet.

## Contributing

Contributions are welcome!

1. Run both test suites before submitting
2. When adding commands, validation rules, or providers, update the `shared/` JSON first — backend Pydantic and extension Zod schemas derive from it and must stay in sync
3. Use conventional commits: `feat:`, `fix:`, `docs:`, `chore:`, …

## License

MIT — see [LICENSE](LICENSE).
