from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import OperationalError

from app.database import get_db
from app.main import app


@pytest.fixture()
def failing_db_client(client_no_raise):
    """Client whose session raises on execute(), exercising the 503 branch.

    The dependency itself must still yield — raising inside `get_db` would be
    caught by the app's generic 500 handler instead of the endpoint's own
    try/except.
    """
    broken = MagicMock()
    broken.execute.side_effect = OperationalError("SELECT 1", {}, Exception("gone"))

    def _override_get_db():
        yield broken

    app.dependency_overrides[get_db] = _override_get_db
    yield client_no_raise
    app.dependency_overrides.clear()


@pytest.mark.integration
class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "healthy"
        assert data["data"]["database"] == "connected"

    def test_health_lives_outside_the_version_prefix(self, client) -> None:
        # Assert — monitoring hits /health, not /api/v1/health
        assert client.get("/health").status_code == 200
        assert client.get("/api/v1/health").status_code == 404

    def test_health_probes_the_database(self, client, db_session) -> None:
        # Act
        response = client.get("/health")

        # Assert — a green health check means the session answered a query
        assert response.status_code == 200
        assert db_session.is_active


@pytest.mark.integration
class TestHealthDatabaseFailure:
    def test_returns_503_envelope(self, failing_db_client) -> None:
        # Act
        response = failing_db_client.get("/health")

        # Assert
        assert response.status_code == 503
        assert response.json() == {
            "error": {
                "code": "SERVICE_UNAVAILABLE",
                "message": "Database connection failed",
                "details": [],
            }
        }

    def test_does_not_leak_driver_details(self, failing_db_client) -> None:
        # Act
        response = failing_db_client.get("/health")

        # Assert
        assert "SELECT 1" not in response.text
        assert "gone" not in response.text

    @pytest.mark.parametrize(
        "error",
        [
            RuntimeError("connection pool exhausted"),
            OSError("disk I/O error"),
            TimeoutError("statement timeout"),
        ],
    )
    def test_any_database_error_maps_to_503(
        self, client_no_raise, error: Exception
    ) -> None:
        # Arrange
        broken = MagicMock()
        broken.execute.side_effect = error

        def _override_get_db():
            yield broken

        app.dependency_overrides[get_db] = _override_get_db

        # Act
        response = client_no_raise.get("/health")

        # Assert
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "SERVICE_UNAVAILABLE"
