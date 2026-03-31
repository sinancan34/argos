import pytest


@pytest.mark.integration
class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "healthy"
        assert data["data"]["database"] == "connected"
