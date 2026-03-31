<!-- Generated: 2026-04-01 | Files scanned: 3 | Token estimate: ~400 -->

# Dependencies

## Backend (Python 3.12)

| Package | Purpose |
|---------|---------|
| fastapi | Web framework |
| uvicorn | ASGI server |
| sqlalchemy | ORM |
| alembic | DB migrations |
| pydantic-settings | Config from .env |
| slowapi | Rate limiting |
| pytest + httpx | Testing |

## Extension (Node.js)

| Package | Purpose |
|---------|---------|
| wxt | Chrome extension framework (Manifest V3) |
| react 19 | UI framework |
| @tanstack/react-router | Hash-based file routing |
| @tanstack/react-query | Server state (scenarios CRUD) |
| react-hook-form + zod 4 | Form validation |
| ky | HTTP client |
| @dnd-kit/* | Drag-and-drop step reordering |
| radix-ui | Headless UI primitives (shadcn) |
| tailwindcss 4 | Styling |
| @medv/finder | CSS selector generation (picker) |
| lucide-react | Icons |
| vitest | Test runner |

## Shared Definitions

```
shared/commands.json     → Backend: command_registry.py
                         → Extension: lib/commands.ts

shared/validations.json  → Backend: validation_registry.py → Pydantic Field()
                         → Extension: lib/validation-registry.ts → Zod schemas

shared/providers.json    → Backend: validation_registry.py (VALID_PROVIDERS)
                         → Extension: lib/validation-registry.ts (autocomplete)
```

## Chrome APIs Used

| API | Permission | Purpose |
|-----|------------|---------|
| chrome.sidePanel | `sidePanel` | Extension UI |
| chrome.tabs | `activeTab`, `tabs` | Tab management |
| chrome.scripting | `scripting` | Content script injection |
| chrome.webNavigation | `webNavigation` | Navigation tracking |
| chrome.webRequest | `webRequest` | Network capture |
| chrome.runtime | — | Messaging (ports + one-shot) |

## External Services

None — fully self-contained. Backend runs locally, extension connects to localhost.
