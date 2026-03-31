<!-- Generated: 2026-04-01 (updated) | Files scanned: 5 | Token estimate: ~300 -->

# Data Architecture

## Database

- **Engine:** SQLite (default: `sqlite:///./argos.db`)
- **ORM:** SQLAlchemy (declarative base)
- **Migrations:** Alembic (1 migration — reset to single initial)
- **Config:** `check_same_thread=False` for SQLite; adjust for PostgreSQL

## Tables

```
scenarios
├── id               VARCHAR  PK  (UUID v4, generated in Python)
├── name             VARCHAR  NOT NULL
├── description       VARCHAR  NULL
├── status           VARCHAR  NOT NULL  CHECK('active','inactive')  DEFAULT 'active'
├── step_timeout     INTEGER  NOT NULL  DEFAULT 5000
├── validation_timeout INTEGER NOT NULL DEFAULT 10000
├── steps            JSON     NOT NULL
├── validations      JSON     NOT NULL
├── created_at       VARCHAR  NOT NULL  (ISO 8601 UTC)
└── updated_at       VARCHAR  NOT NULL  (ISO 8601 UTC, auto-updated)
```

## JSON Column: steps

```json
[
  {
    "id": "uuid",
    "command": "goto | click",
    "params": {
      "url": "https://...",          // goto
      "selectorEntries": [...]       // click
    }
  }
]
```

## JSON Column: validations

```json
[
  {
    "id": "uuid",
    "provider": "custom | google_analytics | ...",
    "url": { "match": "contains", "value": "analytics" },
    "params": [
      { "key": "tid", "match": "exact", "value": "UA-123" }
    ]
  }
]
```

## Migration History

| Rev | Description |
|-----|-------------|
| `7206bb3041ed` | Initial schema (full current model) |

## Session Management

- `SessionLocal = sessionmaker(bind=engine)`
- Injected via `Depends(get_db)` — yields session, closes in finally
- Tests use in-memory SQLite with `StaticPool`
