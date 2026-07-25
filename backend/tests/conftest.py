from urllib.parse import urlsplit

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.requests import Request

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def db_engine():
    """In-memory SQLite engine shared by every session within a single test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def session_factory(db_engine):
    """Session factory for code that opens its own sessions (e.g. seed scripts)."""
    return sessionmaker(bind=db_engine)


@pytest.fixture()
def db_session(session_factory):
    """Create an in-memory SQLite database for each test."""
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    """TestClient that uses the in-memory DB session."""

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def client_no_raise(db_session):
    """Like `client`, but returns the 500 envelope instead of re-raising.

    Needed to exercise the app's generic exception handler: the default
    TestClient re-raises unhandled server errors instead of returning them.
    """

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


def make_device_payload(**overrides) -> dict:
    """Return a valid DeviceCreate payload, with optional overrides."""
    base = {
        "name": "iPhone 15",
        "meta": {
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
            "viewport_width": 390,
            "viewport_height": 844,
            "device_scale_factor": 3,
            "is_mobile": True,
            "has_touch": True,
        },
        "status": True,
    }
    base.update(overrides)
    return base


@pytest.fixture()
def device_id(client) -> str:
    """Create a device via the API and return its id for scenario tests."""
    response = client.post("/api/v1/devices", json=make_device_payload())
    return response.json()["data"]["id"]


def make_scenario_payload(device_id: str, **overrides) -> dict:
    """Return a valid ScenarioCreate payload for the given device."""
    base = {
        "name": "Test Scenario",
        "description": "A test scenario",
        "status": True,
        "step_timeout": 5000,
        "validation_timeout": 10000,
        "steps": [
            {"id": "step-1", "command": "goto", "params": {"url": "https://example.com"}},
        ],
        "validations": [
            {
                "id": "val-1",
                "provider": "custom",
                "url": {"match": "contains", "value": "example.com"},
                "params": [],
            },
        ],
        "device_id": device_id,
    }
    base.update(overrides)
    return base


@pytest.fixture()
def scenario_id(client, device_id) -> str:
    """Create a scenario via the API and return its id."""
    response = client.post(
        "/api/v1/scenarios", json=make_scenario_payload(device_id)
    )
    return response.json()["data"]["id"]


def make_request(url: str = "http://testserver/api/v1/devices") -> Request:
    """Build a minimal Starlette Request for helpers that only read `.url`."""
    parts = urlsplit(url)
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "scheme": parts.scheme or "http",
            "server": (parts.hostname or "testserver", parts.port or 80),
            "path": parts.path,
            "raw_path": parts.path.encode(),
            "query_string": parts.query.encode(),
            "root_path": "",
            "headers": [(b"host", (parts.netloc or "testserver").encode())],
            "client": ("testclient", 50000),
        }
    )
