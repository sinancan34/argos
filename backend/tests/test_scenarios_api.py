import pytest

from tests.conftest import make_device_payload, make_scenario_payload


@pytest.mark.integration
class TestCreateScenario:
    def test_create_returns_201(self, client, device_id):
        payload = make_scenario_payload(device_id)
        response = client.post("/api/v1/scenarios", json=payload)
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "Test Scenario"
        assert data["status"] is True
        assert data["step_timeout"] == 5000
        assert data["device_id"] == device_id
        assert "id" in data
        assert "created_at" in data
        assert response.headers.get("Location") is not None

    def test_create_with_custom_name(self, client, device_id):
        payload = make_scenario_payload(device_id, name="Custom Name")
        response = client.post("/api/v1/scenarios", json=payload)
        assert response.status_code == 201
        assert response.json()["data"]["name"] == "Custom Name"

    def test_create_validation_error_empty_name(self, client, device_id):
        payload = make_scenario_payload(device_id, name="")
        response = client.post("/api/v1/scenarios", json=payload)
        assert response.status_code == 422
        error = response.json()["error"]
        assert error["code"] == "VALIDATION_ERROR"

    def test_create_validation_error_empty_steps(self, client, device_id):
        payload = make_scenario_payload(device_id, steps=[])
        response = client.post("/api/v1/scenarios", json=payload)
        assert response.status_code == 422

    def test_create_validation_error_unknown_command(self, client, device_id):
        payload = make_scenario_payload(
            device_id, steps=[{"id": "s1", "command": "hover", "params": {}}]
        )
        response = client.post("/api/v1/scenarios", json=payload)
        assert response.status_code == 422

    def test_create_missing_device_id(self, client, device_id):
        payload = make_scenario_payload(device_id)
        del payload["device_id"]
        response = client.post("/api/v1/scenarios", json=payload)
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    def test_create_nonexistent_device_id(self, client):
        payload = make_scenario_payload("does-not-exist")
        response = client.post("/api/v1/scenarios", json=payload)
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.integration
class TestGetScenario:
    def test_get_existing(self, client, device_id):
        payload = make_scenario_payload(device_id)
        create_resp = client.post("/api/v1/scenarios", json=payload)
        scenario_id = create_resp.json()["data"]["id"]

        response = client.get(f"/api/v1/scenarios/{scenario_id}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == scenario_id
        assert data["name"] == "Test Scenario"
        assert data["device_id"] == device_id

    def test_get_not_found(self, client):
        response = client.get("/api/v1/scenarios/nonexistent-id")
        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "NOT_FOUND"


@pytest.mark.integration
class TestUpdateScenario:
    def test_update_name(self, client, device_id):
        payload = make_scenario_payload(device_id)
        create_resp = client.post("/api/v1/scenarios", json=payload)
        scenario_id = create_resp.json()["data"]["id"]

        response = client.patch(
            f"/api/v1/scenarios/{scenario_id}",
            json={"name": "Updated Name"},
        )
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "Updated Name"

    def test_update_status(self, client, device_id):
        payload = make_scenario_payload(device_id)
        create_resp = client.post("/api/v1/scenarios", json=payload)
        scenario_id = create_resp.json()["data"]["id"]

        response = client.patch(
            f"/api/v1/scenarios/{scenario_id}",
            json={"status": False},
        )
        assert response.status_code == 200
        assert response.json()["data"]["status"] is False

    def test_update_steps(self, client, device_id):
        payload = make_scenario_payload(device_id)
        create_resp = client.post("/api/v1/scenarios", json=payload)
        scenario_id = create_resp.json()["data"]["id"]

        new_steps = [
            {"id": "s1", "command": "goto", "params": {"url": "https://new.com"}},
            {"id": "s2", "command": "click", "params": {"selector": "#btn"}},
        ]
        response = client.patch(
            f"/api/v1/scenarios/{scenario_id}",
            json={"steps": new_steps},
        )
        assert response.status_code == 200
        assert len(response.json()["data"]["steps"]) == 2

    def test_update_device_id(self, client, device_id):
        payload = make_scenario_payload(device_id)
        create_resp = client.post("/api/v1/scenarios", json=payload)
        scenario_id = create_resp.json()["data"]["id"]

        other = client.post(
            "/api/v1/devices", json=make_device_payload(name="Pixel 8")
        )
        other_id = other.json()["data"]["id"]

        response = client.patch(
            f"/api/v1/scenarios/{scenario_id}",
            json={"device_id": other_id},
        )
        assert response.status_code == 200
        assert response.json()["data"]["device_id"] == other_id

    def test_update_nonexistent_device_id(self, client, device_id):
        payload = make_scenario_payload(device_id)
        create_resp = client.post("/api/v1/scenarios", json=payload)
        scenario_id = create_resp.json()["data"]["id"]

        response = client.patch(
            f"/api/v1/scenarios/{scenario_id}",
            json={"device_id": "does-not-exist"},
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    def test_update_not_found(self, client):
        response = client.patch(
            "/api/v1/scenarios/nonexistent-id",
            json={"name": "X"},
        )
        assert response.status_code == 404


@pytest.mark.integration
class TestDeleteScenario:
    def test_delete_existing(self, client, device_id):
        payload = make_scenario_payload(device_id)
        create_resp = client.post("/api/v1/scenarios", json=payload)
        scenario_id = create_resp.json()["data"]["id"]

        response = client.delete(f"/api/v1/scenarios/{scenario_id}")
        assert response.status_code == 200
        assert response.json()["data"]["id"] == scenario_id

        # Verify it's gone
        get_resp = client.get(f"/api/v1/scenarios/{scenario_id}")
        assert get_resp.status_code == 404

    def test_delete_not_found(self, client):
        response = client.delete("/api/v1/scenarios/nonexistent-id")
        assert response.status_code == 404


@pytest.mark.integration
class TestListScenarios:
    def test_list_empty(self, client):
        response = client.get("/api/v1/scenarios")
        assert response.status_code == 200
        body = response.json()
        assert body["data"] == []
        assert body["meta"]["total_count"] == 0
        assert body["meta"]["page"] == 1

    def test_list_with_data(self, client, device_id):
        for i in range(3):
            client.post(
                "/api/v1/scenarios",
                json=make_scenario_payload(device_id, name=f"Scenario {i}"),
            )

        response = client.get("/api/v1/scenarios")
        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]) == 3
        assert body["meta"]["total_count"] == 3

    def test_list_pagination(self, client, device_id):
        for i in range(5):
            client.post(
                "/api/v1/scenarios",
                json=make_scenario_payload(device_id, name=f"Scenario {i}"),
            )

        response = client.get("/api/v1/scenarios?page=1&size=2")
        body = response.json()
        assert len(body["data"]) == 2
        assert body["meta"]["total_count"] == 5
        assert body["meta"]["total_pages"] == 3
        assert body["links"]["next"] is not None
        assert body["links"]["prev"] is None

        # Page 2
        response = client.get("/api/v1/scenarios?page=2&size=2")
        body = response.json()
        assert len(body["data"]) == 2
        assert body["links"]["prev"] is not None

    def test_list_filter_by_name(self, client, device_id):
        client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(device_id, name="Alpha Test"),
        )
        client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(device_id, name="Beta Test"),
        )

        response = client.get("/api/v1/scenarios?name=Alpha")
        body = response.json()
        assert len(body["data"]) == 1
        assert body["data"][0]["name"] == "Alpha Test"

    def test_list_filter_by_status(self, client, device_id):
        client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(device_id, name="Active", status=True),
        )
        client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(device_id, name="Inactive", status=False),
        )

        response = client.get("/api/v1/scenarios?status=false")
        body = response.json()
        assert len(body["data"]) == 1
        assert body["data"][0]["name"] == "Inactive"

    def test_list_sort_by_name_asc(self, client, device_id):
        client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(device_id, name="Zebra"),
        )
        client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(device_id, name="Alpha"),
        )

        response = client.get(
            "/api/v1/scenarios?sort_by=name&sort_order=asc"
        )
        body = response.json()
        names = [s["name"] for s in body["data"]]
        assert names == ["Alpha", "Zebra"]


@pytest.mark.integration
class TestErrorHandling:
    def test_method_not_allowed(self, client):
        response = client.put("/api/v1/scenarios")
        assert response.status_code == 405

    def test_404_unknown_route(self, client):
        response = client.get("/api/v1/unknown")
        assert response.status_code in (404, 405)
