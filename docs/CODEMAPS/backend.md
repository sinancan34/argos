<!-- Generated: 2026-04-01 | Files scanned: 10 | Token estimate: ~700 -->

# Backend Architecture

## Routes

```
GET  /health                        → health_check()        → 200/503

POST   /api/v1/scenarios            → create_scenario()     → 201
GET    /api/v1/scenarios            → list_scenarios()      → 200 (paginated)
GET    /api/v1/scenarios/{id}       → get_scenario()        → 200
PATCH  /api/v1/scenarios/{id}       → update_scenario()     → 200
DELETE /api/v1/scenarios/{id}       → delete_scenario()     → 200
```

**List query params:** name, status, sort_by, sort_order, page, size

## Middleware Chain

```
Request → CORS → Rate Limiter (slowapi) → Router → Response
                                            ↓ (on error)
          RateLimitExceeded → 429
          AppException → {status_code}
          RequestValidationError → 422
          HTTPException → {status_code}
          Exception → 500
```

## Key Files

```
app/main.py              (137 lines) — App setup, middleware, exception handlers
app/routers/scenarios.py (223 lines) — CRUD + list with pagination
app/routers/health.py    (45 lines)  — Health check with DB probe
app/schemas.py           (209 lines) — Pydantic models, dynamic enums
app/models.py            (35 lines)  — Scenario ORM model
app/exceptions.py        (34 lines)  — AppException, ErrorEnvelope
app/database.py          (21 lines)  — Engine, SessionLocal, get_db
app/config.py            (12 lines)  — Settings (database_url, cors, rate_limit)
app/command_registry.py  (13 lines)  — Loads shared/commands.json
app/validation_registry.py (38 lines) — Loads shared/validations.json + providers.json
```

## Domain Model

```
Scenario
├── id: str (UUID)
├── name: str
├── description: str?
├── status: "active" | "inactive"
├── step_timeout: int (default 5000)
├── validation_timeout: int (default 10000)
├── steps: JSON
├── validations: JSON
├── created_at: str (ISO 8601)
└── updated_at: str (ISO 8601)
```

## Response Envelope

```
Single:  { data: ScenarioResponse }
List:    { data: [...], meta: {page, size, total_count, total_pages}, links: {self, first, last, next, prev} }
Delete:  { data: { id } }
Error:   { error: { code, message, details[] } }
```

## Schema Validation Flow

```
shared/*.json → command_registry.py / validation_registry.py
                        ↓
              schemas.py (dynamic enums, Pydantic Field() kwargs)
                        ↓
              Request validation via Pydantic models
```

## Tests

```
tests/conftest.py              (66 lines)  — in-memory SQLite, TestClient, factory
tests/test_scenarios_api.py    (236 lines) — CRUD + pagination + error cases
tests/test_schemas.py          (240 lines) — Pydantic validation rules
tests/test_exceptions.py       (49 lines)  — Exception handler coverage
tests/test_validation_registry.py (91 lines) — Registry loading + field kwargs
tests/test_health.py           (11 lines)  — Health endpoint
```

## Migrations

```
1. 2f118cfadda2 — Initial scenarios table
2. 8b25e0a1bbde — Add status column
3. 3db6cd2528c4 — Status int → string enum
```
