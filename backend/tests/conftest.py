import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def db_session():
    """Create an in-memory SQLite database for each test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


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
