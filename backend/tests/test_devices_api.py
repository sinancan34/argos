import pytest

from tests.conftest import make_device_payload, make_scenario_payload


@pytest.mark.integration
class TestCreateDevice:
    def test_create_returns_201(self, client):
        response = client.post("/api/v1/devices", json=make_device_payload())
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "iPhone 15"
        assert data["status"] is True
        assert data["meta"]["viewport_width"] == 390
        assert "id" in data
        assert "created_at" in data
        assert response.headers.get("Location") is not None

    def test_create_defaults_meta_and_status(self, client):
        response = client.post("/api/v1/devices", json={"name": "Bare Device"})
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["meta"] == {}
        assert data["status"] is True

    def test_create_validation_error_empty_name(self, client):
        response = client.post(
            "/api/v1/devices", json=make_device_payload(name="")
        )
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "VALIDATION_ERROR"

    def test_create_validation_error_bad_status(self, client):
        response = client.post(
            "/api/v1/devices", json=make_device_payload(status="not-a-bool")
        )
        assert response.status_code == 422


@pytest.mark.integration
class TestGetDevice:
    def test_get_existing(self, client, device_id):
        response = client.get(f"/api/v1/devices/{device_id}")
        assert response.status_code == 200
        assert response.json()["data"]["id"] == device_id

    def test_get_not_found(self, client):
        response = client.get("/api/v1/devices/nonexistent-id")
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.integration
class TestUpdateDevice:
    def test_update_name(self, client, device_id):
        response = client.patch(
            f"/api/v1/devices/{device_id}", json={"name": "Renamed"}
        )
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "Renamed"

    def test_update_meta(self, client, device_id):
        response = client.patch(
            f"/api/v1/devices/{device_id}",
            json={"meta": {"viewport_width": 1024}},
        )
        assert response.status_code == 200
        assert response.json()["data"]["meta"] == {"viewport_width": 1024}

    def test_update_status(self, client, device_id):
        response = client.patch(
            f"/api/v1/devices/{device_id}", json={"status": False}
        )
        assert response.status_code == 200
        assert response.json()["data"]["status"] is False

    def test_update_not_found(self, client):
        response = client.patch(
            "/api/v1/devices/nonexistent-id", json={"name": "X"}
        )
        assert response.status_code == 404


@pytest.mark.integration
class TestDeleteDevice:
    def test_delete_existing(self, client, device_id):
        response = client.delete(f"/api/v1/devices/{device_id}")
        assert response.status_code == 200
        assert response.json()["data"]["id"] == device_id

        get_resp = client.get(f"/api/v1/devices/{device_id}")
        assert get_resp.status_code == 404

    def test_delete_not_found(self, client):
        response = client.delete("/api/v1/devices/nonexistent-id")
        assert response.status_code == 404

    def test_delete_in_use_blocked(self, client, device_id):
        # Create a scenario that references the device
        client.post(
            "/api/v1/scenarios", json=make_scenario_payload(device_id)
        )

        response = client.delete(f"/api/v1/devices/{device_id}")
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "CONFLICT"

        # Device still exists
        assert client.get(f"/api/v1/devices/{device_id}").status_code == 200

    def test_delete_after_scenario_removed(self, client, device_id):
        create_resp = client.post(
            "/api/v1/scenarios", json=make_scenario_payload(device_id)
        )
        scenario_id = create_resp.json()["data"]["id"]

        # Blocked while referenced
        assert client.delete(f"/api/v1/devices/{device_id}").status_code == 409

        # Remove the scenario, then the device can be deleted
        client.delete(f"/api/v1/scenarios/{scenario_id}")
        assert client.delete(f"/api/v1/devices/{device_id}").status_code == 200


@pytest.mark.integration
class TestListDevices:
    def test_list_empty(self, client):
        response = client.get("/api/v1/devices")
        assert response.status_code == 200
        body = response.json()
        assert body["data"] == []
        assert body["meta"]["total_count"] == 0

    def test_list_with_data(self, client):
        for i in range(3):
            client.post(
                "/api/v1/devices", json=make_device_payload(name=f"Device {i}")
            )
        response = client.get("/api/v1/devices")
        body = response.json()
        assert len(body["data"]) == 3
        assert body["meta"]["total_count"] == 3

    def test_list_pagination(self, client):
        for i in range(5):
            client.post(
                "/api/v1/devices", json=make_device_payload(name=f"Device {i}")
            )
        response = client.get("/api/v1/devices?page=1&size=2")
        body = response.json()
        assert len(body["data"]) == 2
        assert body["meta"]["total_pages"] == 3
        assert body["links"]["next"] is not None
        assert body["links"]["prev"] is None

    def test_list_filter_by_name(self, client):
        client.post("/api/v1/devices", json=make_device_payload(name="Alpha Phone"))
        client.post("/api/v1/devices", json=make_device_payload(name="Beta Tablet"))
        response = client.get("/api/v1/devices?name=Alpha")
        body = response.json()
        assert len(body["data"]) == 1
        assert body["data"][0]["name"] == "Alpha Phone"

    def test_list_filter_by_status(self, client):
        client.post(
            "/api/v1/devices",
            json=make_device_payload(name="On", status=True),
        )
        client.post(
            "/api/v1/devices",
            json=make_device_payload(name="Off", status=False),
        )
        response = client.get("/api/v1/devices?status=false")
        body = response.json()
        assert len(body["data"]) == 1
        assert body["data"][0]["name"] == "Off"

    def test_list_sort_by_name_asc(self, client):
        client.post("/api/v1/devices", json=make_device_payload(name="Zebra"))
        client.post("/api/v1/devices", json=make_device_payload(name="Alpha"))
        response = client.get("/api/v1/devices?sort_by=name&sort_order=asc")
        names = [d["name"] for d in response.json()["data"]]
        assert names == ["Alpha", "Zebra"]
