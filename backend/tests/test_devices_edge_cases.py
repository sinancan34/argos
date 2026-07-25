"""Edge-case coverage matrix for /api/v1/devices.

Field constraints asserted here are read from the shared source of truth
(`shared/validations.json` → "device" block) rather than hard-coded, so the
tests fail loudly if the shared definition and the API drift apart:

    name   → string, required, minLength 1, maxLength 500
    status → boolean, optional, default true
    meta   → object, optional, free-form
"""

import pytest

from app.validation_registry import DEVICE_FIELDS
from tests.conftest import make_device_payload, make_scenario_payload

NAME_MIN: int = DEVICE_FIELDS["name"]["minLength"]
NAME_MAX: int = DEVICE_FIELDS["name"]["maxLength"]

TURKISH = "Ürün Ğğ İıŞş Öö Çç"
EMOJI = "Telefon 📱🇹🇷"
CJK = "デバイス 设备 장치"


@pytest.mark.integration
class TestDeviceNameBoundaries:
    @pytest.mark.parametrize(
        ("label", "name"),
        [
            ("single character", "x"),
            ("exactly at maxLength", "x" * NAME_MAX),
            ("one below maxLength", "x" * (NAME_MAX - 1)),
            ("turkish diacritics", TURKISH),
            ("emoji", EMOJI),
            ("cjk", CJK),
            ("whitespace only", "   "),
            ("tab and newline", "\t\n"),
            ("numeric looking", "0"),
            ("leading and trailing space", "  Padded  "),
            ("sql-ish", "'; DROP TABLE devices; --"),
            ("html-ish", "<script>alert(1)</script>"),
            ("path-ish", "../../etc/passwd"),
            ("null-ish text", "null"),
        ],
    )
    def test_accepted_names_round_trip_verbatim(
        self, client, label: str, name: str
    ) -> None:
        # Act
        response = client.post("/api/v1/devices", json={"name": name})

        # Assert
        assert response.status_code == 201, label
        device_id = response.json()["data"]["id"]
        assert response.json()["data"]["name"] == name
        assert client.get(f"/api/v1/devices/{device_id}").json()["data"]["name"] == name

    @pytest.mark.parametrize(
        ("label", "name"),
        [
            ("empty string", ""),
            ("one over maxLength", "x" * (NAME_MAX + 1)),
            ("very long", "x" * 10_000),
            ("null", None),
            ("integer", 123),
            ("list", ["a"]),
            ("object", {"value": "a"}),
        ],
    )
    def test_rejected_names(self, client, label: str, name: object) -> None:
        # Act
        response = client.post("/api/v1/devices", json={"name": name})

        # Assert
        assert response.status_code == 422, label
        error = response.json()["error"]
        assert error["code"] == "VALIDATION_ERROR"
        assert error["details"][0]["loc"] == ["body", "name"]

    def test_missing_name_is_reported_as_missing(self, client) -> None:
        # Act
        response = client.post("/api/v1/devices", json={})

        # Assert
        assert response.status_code == 422
        assert response.json()["error"]["details"][0]["type"] == "missing"

    def test_multibyte_length_is_counted_in_characters_not_bytes(
        self, client
    ) -> None:
        # Arrange — 500 emoji is 500 characters but ~2000 bytes
        name = "📱" * NAME_MAX

        # Act
        response = client.post("/api/v1/devices", json={"name": name})

        # Assert
        assert response.status_code == 201
        assert len(response.json()["data"]["name"]) == NAME_MAX


@pytest.mark.integration
class TestDeviceMetaEdgeCases:
    @pytest.mark.parametrize(
        ("label", "meta"),
        [
            ("empty object", {}),
            ("chrome preset shape", {
                "source": "chrome-devtools",
                "type": "phone",
                "user_agent": "Mozilla/5.0",
                "viewport": {"width": 393, "height": 852, "device_pixel_ratio": 3},
                "capabilities": {"touch": True, "mobile": True},
                "platform": "Android",
                "platform_version": None,
            }),
            ("desktop preset without viewport", {
                "source": "chrome-devtools", "type": "desktop"
            }),
            ("unknown keys", {"totally": "unrecognised", "nested": {"deep": [1, 2]}}),
            ("zero viewport", {"viewport": {"width": 0, "height": 0}}),
            ("negative viewport", {"viewport": {"width": -1, "height": -1}}),
            ("huge integer", {"viewport": {"width": 10**100}}),
            ("float dpr", {"viewport": {"device_pixel_ratio": 2.625}}),
            ("null values", {"user_agent": None, "platform": None}),
            ("empty collections", {"a": [], "b": {}, "c": ""}),
            ("unicode keys and values", {TURKISH: EMOJI}),
            ("long string value", {"user_agent": "M" * 10_000}),
        ],
    )
    def test_free_form_meta_round_trips(self, client, label: str, meta: dict) -> None:
        # Act
        response = client.post(
            "/api/v1/devices", json={"name": f"Device {label}", "meta": meta}
        )

        # Assert
        assert response.status_code == 201, label
        device_id = response.json()["data"]["id"]
        assert response.json()["data"]["meta"] == meta
        stored = client.get(f"/api/v1/devices/{device_id}").json()["data"]["meta"]
        assert stored == meta

    def test_meta_defaults_to_empty_object(self, client) -> None:
        # Act
        response = client.post("/api/v1/devices", json={"name": "Bare"})

        # Assert
        assert response.json()["data"]["meta"] == {}

    @pytest.mark.parametrize(
        ("label", "meta"),
        [
            ("null", None),
            ("list", [{"width": 1}]),
            ("string", "viewport"),
            ("integer", 42),
            ("boolean", True),
        ],
    )
    def test_non_object_meta_is_rejected(
        self, client, label: str, meta: object
    ) -> None:
        # Act
        response = client.post(
            "/api/v1/devices", json={"name": "Bad Meta", "meta": meta}
        )

        # Assert
        assert response.status_code == 422, label
        assert response.json()["error"]["details"][0]["loc"] == ["body", "meta"]


@pytest.mark.integration
class TestDeviceStatus:
    @pytest.mark.parametrize(
        ("sent", "expected"),
        [
            (True, True),
            (False, False),
            ("true", True),
            ("false", False),
            (1, True),
            (0, False),
        ],
    )
    def test_boolean_coercion(self, client, sent: object, expected: bool) -> None:
        # Act
        response = client.post(
            "/api/v1/devices", json={"name": f"Status {sent}", "status": sent}
        )

        # Assert
        assert response.status_code == 201
        assert response.json()["data"]["status"] is expected

    def test_defaults_to_active(self, client) -> None:
        # Act
        response = client.post("/api/v1/devices", json={"name": "Default"})

        # Assert
        assert response.json()["data"]["status"] is True

    @pytest.mark.parametrize("status", ["maybe", 2, None, [], {}])
    def test_invalid_status_is_rejected(self, client, status: object) -> None:
        # Act
        response = client.post(
            "/api/v1/devices", json={"name": "Bad Status", "status": status}
        )

        # Assert
        assert response.status_code == 422


@pytest.mark.integration
class TestDeviceListFiltering:
    @pytest.mark.parametrize(
        ("stored", "query", "should_match"),
        [
            ("100% Coverage", "100%", True),
            ("100 Coverage", "100%", False),
            ("snake_case", "_case", True),
            ("snakeXcase", "_case", False),
            ("back\\slash", "\\", True),
            ("plain", "\\", False),
            ("50%_off", "%_", True),
        ],
    )
    def test_like_wildcards_are_matched_literally(
        self, client, stored: str, query: str, should_match: bool
    ) -> None:
        # Arrange
        client.post("/api/v1/devices", json={"name": stored})

        # Act
        response = client.get("/api/v1/devices", params={"name": query})

        # Assert
        names = [d["name"] for d in response.json()["data"]]
        assert (stored in names) is should_match

    def test_ascii_filtering_is_case_insensitive(self, client) -> None:
        # Arrange
        client.post("/api/v1/devices", json={"name": "MiXeD CaSe"})

        # Act
        response = client.get("/api/v1/devices", params={"name": "mixed"})

        # Assert
        assert len(response.json()["data"]) == 1

    def test_non_ascii_filtering_is_case_sensitive(self, client) -> None:
        # Arrange
        client.post("/api/v1/devices", json={"name": "Ürün Listesi"})

        # Act
        exact = client.get("/api/v1/devices", params={"name": "Ürün"})
        folded = client.get("/api/v1/devices", params={"name": "ürün"})

        # Assert — SQLite's lower() is ASCII-only, so Turkish case does not fold
        assert len(exact.json()["data"]) == 1
        assert folded.json()["data"] == []

    @pytest.mark.parametrize("query", [EMOJI, CJK, TURKISH])
    def test_unicode_substring_filtering(self, client, query: str) -> None:
        # Arrange
        client.post("/api/v1/devices", json={"name": f"prefix {query} suffix"})

        # Act
        response = client.get("/api/v1/devices", params={"name": query})

        # Assert
        assert len(response.json()["data"]) == 1

    def test_empty_name_param_disables_the_filter(self, client) -> None:
        # Arrange
        for name in ("A", "B"):
            client.post("/api/v1/devices", json={"name": name})

        # Act
        response = client.get("/api/v1/devices", params={"name": ""})

        # Assert
        assert len(response.json()["data"]) == 2

    def test_whitespace_name_param_matches_nothing(self, client) -> None:
        # Arrange
        client.post("/api/v1/devices", json={"name": "NoSpaces"})

        # Act
        response = client.get("/api/v1/devices", params={"name": "  "})

        # Assert
        assert response.json()["data"] == []

    def test_name_and_status_filters_combine(self, client) -> None:
        # Arrange
        client.post("/api/v1/devices", json={"name": "Pixel A", "status": True})
        client.post("/api/v1/devices", json={"name": "Pixel B", "status": False})

        # Act
        response = client.get("/api/v1/devices?name=Pixel&status=false")

        # Assert
        body = response.json()
        assert body["meta"]["total_count"] == 1
        assert body["data"][0]["name"] == "Pixel B"

    def test_filters_survive_in_pagination_links(self, client) -> None:
        # Arrange
        for i in range(3):
            client.post("/api/v1/devices", json={"name": f"Tablet {i}"})

        # Act
        response = client.get("/api/v1/devices?name=Tablet&size=1&page=1")

        # Assert
        assert "name=Tablet" in response.json()["links"]["next"]


@pytest.mark.integration
class TestDeviceListPagination:
    @pytest.mark.parametrize(
        ("page", "size", "expected_len"),
        [(1, 1, 1), (1, 5, 5), (2, 3, 2), (2, 5, 0), (1, 100, 5)],
    )
    def test_page_windows(
        self, client, page: int, size: int, expected_len: int
    ) -> None:
        # Arrange
        for i in range(5):
            client.post("/api/v1/devices", json={"name": f"Device {i}"})

        # Act
        response = client.get(f"/api/v1/devices?page={page}&size={size}")

        # Assert
        assert len(response.json()["data"]) == expected_len

    @pytest.mark.parametrize(
        ("query", "loc"),
        [
            ("page=0", "page"),
            ("page=-1", "page"),
            ("page=abc", "page"),
            ("page=1.5", "page"),
            ("size=0", "size"),
            ("size=-1", "size"),
            ("size=101", "size"),
            ("size=1000", "size"),
            ("size=abc", "size"),
        ],
    )
    def test_out_of_range_pagination_is_rejected(
        self, client, query: str, loc: str
    ) -> None:
        # Act
        response = client.get(f"/api/v1/devices?{query}")

        # Assert
        assert response.status_code == 422
        assert response.json()["error"]["details"][0]["loc"] == ["query", loc]

    @pytest.mark.parametrize("size", [1, 100])
    def test_size_boundaries_are_inclusive(self, client, size: int) -> None:
        # Act
        response = client.get(f"/api/v1/devices?size={size}")

        # Assert
        assert response.status_code == 200
        assert response.json()["meta"]["size"] == size

    def test_page_past_the_end_returns_an_empty_window(self, client) -> None:
        # Arrange
        client.post("/api/v1/devices", json={"name": "Only"})

        # Act
        response = client.get("/api/v1/devices?page=999&size=20")

        # Assert
        body = response.json()
        assert body["data"] == []
        assert body["meta"]["page"] == 999
        assert body["meta"]["total_count"] == 1
        assert body["meta"]["total_pages"] == 1
        assert body["links"]["next"] is None
        assert body["links"]["prev"] is not None

    def test_empty_collection_meta(self, client) -> None:
        # Act
        response = client.get("/api/v1/devices")

        # Assert
        body = response.json()
        assert body["meta"] == {
            "page": 1,
            "size": 20,
            "total_count": 0,
            "total_pages": 0,
        }
        assert body["links"]["next"] is None
        assert body["links"]["prev"] is None

    def test_total_pages_rounds_up(self, client) -> None:
        # Arrange
        for i in range(7):
            client.post("/api/v1/devices", json={"name": f"D{i}"})

        # Act
        response = client.get("/api/v1/devices?size=3")

        # Assert
        assert response.json()["meta"]["total_pages"] == 3


@pytest.mark.integration
class TestDeviceSorting:
    @pytest.mark.parametrize("sort_by", ["name", "created_at", "updated_at"])
    @pytest.mark.parametrize("sort_order", ["asc", "desc"])
    def test_every_enum_combination_is_accepted(
        self, client, sort_by: str, sort_order: str
    ) -> None:
        # Arrange
        for name in ("Alpha", "Zebra"):
            client.post("/api/v1/devices", json={"name": name})

        # Act
        response = client.get(
            f"/api/v1/devices?sort_by={sort_by}&sort_order={sort_order}"
        )

        # Assert
        assert response.status_code == 200
        assert len(response.json()["data"]) == 2

    def test_name_sorting_is_reversible(self, client) -> None:
        # Arrange
        for name in ("Beta", "Alpha", "Zebra"):
            client.post("/api/v1/devices", json={"name": name})

        # Act
        asc = client.get("/api/v1/devices?sort_by=name&sort_order=asc")
        desc = client.get("/api/v1/devices?sort_by=name&sort_order=desc")

        # Assert
        asc_names = [d["name"] for d in asc.json()["data"]]
        desc_names = [d["name"] for d in desc.json()["data"]]
        assert asc_names == ["Alpha", "Beta", "Zebra"]
        assert desc_names == list(reversed(asc_names))

    @pytest.mark.parametrize(
        ("query", "loc"),
        [("sort_by=bogus", "sort_by"), ("sort_order=sideways", "sort_order")],
    )
    def test_invalid_enum_values_are_rejected(
        self, client, query: str, loc: str
    ) -> None:
        # Act
        response = client.get(f"/api/v1/devices?{query}")

        # Assert
        assert response.status_code == 422
        assert response.json()["error"]["details"][0]["loc"] == ["query", loc]


@pytest.mark.integration
class TestDeviceUpdateEdgeCases:
    def test_empty_patch_body_changes_nothing(self, client, device_id) -> None:
        # Arrange
        before = client.get(f"/api/v1/devices/{device_id}").json()["data"]

        # Act
        response = client.patch(f"/api/v1/devices/{device_id}", json={})

        # Assert
        after = response.json()["data"]
        assert response.status_code == 200
        assert after["name"] == before["name"]
        assert after["meta"] == before["meta"]
        assert after["status"] == before["status"]

    def test_unknown_fields_are_ignored(self, client, device_id) -> None:
        # Act
        response = client.patch(
            f"/api/v1/devices/{device_id}", json={"bogus": "value"}
        )

        # Assert
        assert response.status_code == 200
        assert "bogus" not in response.json()["data"]

    def test_patching_one_field_leaves_the_others(self, client, device_id) -> None:
        # Arrange
        before = client.get(f"/api/v1/devices/{device_id}").json()["data"]

        # Act
        response = client.patch(
            f"/api/v1/devices/{device_id}", json={"name": "Renamed Only"}
        )

        # Assert
        after = response.json()["data"]
        assert after["name"] == "Renamed Only"
        assert after["meta"] == before["meta"]
        assert after["created_at"] == before["created_at"]
        assert after["updated_at"] >= before["updated_at"]

    def test_meta_is_replaced_not_merged(self, client, device_id) -> None:
        # Act
        response = client.patch(
            f"/api/v1/devices/{device_id}", json={"meta": {"only": "key"}}
        )

        # Assert
        assert response.json()["data"]["meta"] == {"only": "key"}

    @pytest.mark.parametrize("name", ["x", "x" * NAME_MAX, TURKISH])
    def test_patch_accepts_valid_names(self, client, device_id, name: str) -> None:
        # Act
        response = client.patch(f"/api/v1/devices/{device_id}", json={"name": name})

        # Assert
        assert response.status_code == 200
        assert response.json()["data"]["name"] == name

    @pytest.mark.parametrize("name", ["", "x" * (NAME_MAX + 1)])
    def test_patch_enforces_the_same_name_constraints(
        self, client, device_id, name: str
    ) -> None:
        # Act
        response = client.patch(f"/api/v1/devices/{device_id}", json={"name": name})

        # Assert
        assert response.status_code == 422

    @pytest.mark.parametrize("field", ["name", "meta", "status"])
    def test_explicit_null_returns_500(
        self, client_no_raise, client, device_id, field: str
    ) -> None:
        # Act
        response = client_no_raise.patch(
            f"/api/v1/devices/{device_id}", json={field: None}
        )

        # KNOWN DEFECT: `DeviceUpdate` types every field as `X | None`, so an
        # explicit null passes validation, reaches setattr, and violates the
        # NOT NULL column constraint. This should be a 422, not a 500.
        assert response.status_code == 500
        assert response.json()["error"]["code"] == "INTERNAL_ERROR"


@pytest.mark.integration
class TestDeviceDeleteEdgeCases:
    def test_deleting_twice_returns_404(self, client, device_id) -> None:
        # Act
        first = client.delete(f"/api/v1/devices/{device_id}")
        second = client.delete(f"/api/v1/devices/{device_id}")

        # Assert
        assert first.status_code == 200
        assert second.status_code == 404

    @pytest.mark.parametrize(
        "device_ref", ["missing", TURKISH, "x" * 500, "00000000-0000-0000-0000-000000000000"]
    )
    def test_unknown_ids_return_404(self, client, device_ref: str) -> None:
        # Act
        response = client.get(f"/api/v1/devices/{device_ref}")

        # Assert
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "NOT_FOUND"

    def test_conflict_counts_every_referencing_scenario(
        self, client, device_id
    ) -> None:
        # Arrange
        for i in range(3):
            client.post(
                "/api/v1/scenarios",
                json=make_scenario_payload(device_id, name=f"S{i}"),
            )

        # Act
        response = client.delete(f"/api/v1/devices/{device_id}")

        # Assert
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "CONFLICT"

    def test_other_devices_are_unaffected_by_a_conflict(self, client) -> None:
        # Arrange
        used = client.post(
            "/api/v1/devices", json=make_device_payload(name="Used")
        ).json()["data"]["id"]
        free = client.post(
            "/api/v1/devices", json=make_device_payload(name="Free")
        ).json()["data"]["id"]
        client.post("/api/v1/scenarios", json=make_scenario_payload(used))

        # Act
        blocked = client.delete(f"/api/v1/devices/{used}")
        allowed = client.delete(f"/api/v1/devices/{free}")

        # Assert
        assert blocked.status_code == 409
        assert allowed.status_code == 200
