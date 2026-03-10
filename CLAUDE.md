# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Argos is a GA4 Audit Tool built with FastAPI, SQLAlchemy, and Alembic. Python 3.12.

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

**Key patterns:**
- Database sessions via FastAPI dependency injection: `db: Session = Depends(get_db)`
- All ORM models inherit from `Base` (in `database.py`)
- New models must be imported in `alembic/env.py` for autogenerate to detect them
- Config uses Pydantic BaseSettings with `.env` file loading
- SQLite by default (`sqlite:///./argos.db`), configurable via `DATABASE_URL`

## Commit Convention

Conventional commits: `feat:`, `chore:`, `docs:`, `fix:`, etc.
