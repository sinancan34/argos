"""Edge-case coverage matrix for /api/v1/scenarios.

Constraints come from the shared source of truth rather than literals:

    shared/validations.json → scenario name (1..500), positive timeouts,
                              steps/validations (minItems 1), device_id (1..)
    shared/commands.json    → goto(url: string), click(selector: string),
                              match types exact/contains/startsWith/
                              endsWith/regex/exists
    shared/providers.json   → provider enum is ["custom", *providers.keys()]
"""

import pytest

from app.command_registry import COMMAND_PARAMS, VALID_COMMANDS, VALID_MATCH_TYPES
from app.validation_registry import SCENARIO_FIELDS, VALID_PROVIDERS
from tests.conftest import make_device_payload, make_scenario_payload

NAME_MIN: int = SCENARIO_FIELDS["name"]["minLength"]
NAME_MAX: int = SCENARIO_FIELDS["name"]["maxLength"]
NON_CUSTOM_PROVIDERS = [p for p in VALID_PROVIDERS if p != "custom"]

TURKISH = "Senaryo Ğğ İıŞş"
EMOJI = "Senaryo 📱"

# Mirrors the default step/validation produced by make_scenario_payload().
GOTO_STEP = {
    "id": "step-1",
    "command": "goto",
    "params": {"url": "https://example.com"},
}
CUSTOM_VALIDATION = {
    "id": "val-1",
    "provider": "custom",
    "url": {"match": "contains", "value": "example.com"},
    "params": [],
}


@pytest.mark.integration
class TestScenarioNameAndDescription:
    @pytest.mark.parametrize(
        "name",
        ["x", "x" * NAME_MAX, TURKISH, EMOJI, "   ", "0", "'; DROP TABLE scenarios; --"],
    )
    def test_accepted_names(self, client, device_id, name: str) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios", json=make_scenario_payload(device_id, name=name)
        )

        # Assert
        assert response.status_code == 201
        assert response.json()["data"]["name"] == name

    @pytest.mark.parametrize("name", ["", "x" * (NAME_MAX + 1), "x" * 10_000, None, 123])
    def test_rejected_names(self, client, device_id, name: object) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios", json=make_scenario_payload(device_id, name=name)
        )

        # Assert
        assert response.status_code == 422
        assert response.json()["error"]["details"][0]["loc"] == ["body", "name"]

    @pytest.mark.parametrize(
        "description", [None, "", "   ", "x" * 10_000, TURKISH, EMOJI]
    )
    def test_description_is_unconstrained(
        self, client, device_id, description: object
    ) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(device_id, description=description),
        )

        # Assert
        assert response.status_code == 201
        assert response.json()["data"]["description"] == description

    def test_description_defaults_to_null(self, client, device_id) -> None:
        # Arrange
        payload = make_scenario_payload(device_id)
        del payload["description"]

        # Act
        response = client.post("/api/v1/scenarios", json=payload)

        # Assert
        assert response.json()["data"]["description"] is None


@pytest.mark.integration
class TestScenarioTimeouts:
    @pytest.mark.parametrize("timeout", [1, 500, 5000, 2**31 - 1, 2**63 - 1])
    def test_positive_timeouts_are_accepted(
        self, client, device_id, timeout: int
    ) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(
                device_id, step_timeout=timeout, validation_timeout=timeout
            ),
        )

        # Assert
        assert response.status_code == 201
        assert response.json()["data"]["step_timeout"] == timeout

    @pytest.mark.parametrize("field", ["step_timeout", "validation_timeout"])
    @pytest.mark.parametrize("timeout", [0, -1, -5000])
    def test_non_positive_timeouts_are_rejected(
        self, client, device_id, field: str, timeout: int
    ) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(device_id, **{field: timeout}),
        )

        # Assert
        assert response.status_code == 422
        assert response.json()["error"]["details"][0]["loc"] == ["body", field]

    @pytest.mark.parametrize("timeout", ["5000", 1.5, None, [5000]])
    def test_non_integer_timeouts_are_rejected_or_coerced(
        self, client, device_id, timeout: object
    ) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(device_id, step_timeout=timeout),
        )

        # Assert — "5000" coerces, everything else fails validation
        if timeout == "5000":
            assert response.status_code == 201
            assert response.json()["data"]["step_timeout"] == 5000
        else:
            assert response.status_code == 422

    def test_defaults_come_from_the_shared_registry(self, client, device_id) -> None:
        # Arrange
        payload = make_scenario_payload(device_id)
        del payload["step_timeout"]
        del payload["validation_timeout"]

        # Act
        response = client.post("/api/v1/scenarios", json=payload)

        # Assert
        data = response.json()["data"]
        assert data["step_timeout"] == SCENARIO_FIELDS["step_timeout"]["default"]
        assert (
            data["validation_timeout"]
            == SCENARIO_FIELDS["validation_timeout"]["default"]
        )

    def test_timeout_beyond_sqlite_int_range_returns_500(
        self, client_no_raise, device_id
    ) -> None:
        # Act
        response = client_no_raise.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(device_id, step_timeout=10**100),
        )

        # KNOWN DEFECT: shared/validations.json declares step_timeout only as
        # "positive", so an arbitrarily large int passes Pydantic and then
        # raises OverflowError in the SQLite driver. A "max" constraint would
        # turn this into a 422.
        assert response.status_code == 500
        assert response.json()["error"]["code"] == "INTERNAL_ERROR"


@pytest.mark.integration
class TestScenarioSteps:
    @pytest.mark.parametrize("command", sorted(VALID_COMMANDS))
    def test_every_registered_command_is_accepted(
        self, client, device_id, command: str
    ) -> None:
        # Arrange — fill each declared param with a valid string
        params = {p["name"]: "value" for p in COMMAND_PARAMS[command]}

        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(
                device_id, steps=[{"id": "s1", "command": command, "params": params}]
            ),
        )

        # Assert
        assert response.status_code == 201
        assert response.json()["data"]["steps"][0]["command"] == command

    @pytest.mark.parametrize(
        "command", ["hover", "GOTO", "goto ", "", "click()", "scroll"]
    )
    def test_unregistered_commands_are_rejected(
        self, client, device_id, command: str
    ) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(
                device_id, steps=[{"id": "s1", "command": command, "params": {}}]
            ),
        )

        # Assert
        assert response.status_code == 422
        assert "Unknown command" in response.json()["error"]["details"][0]["message"]

    @pytest.mark.parametrize("command", sorted(VALID_COMMANDS))
    @pytest.mark.parametrize("missing", [{}, {"url": ""}, {"selector": ""}])
    def test_required_params_must_be_present_and_non_empty(
        self, client, device_id, command: str, missing: dict
    ) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(
                device_id,
                steps=[{"id": "s1", "command": command, "params": missing}],
            ),
        )

        # Assert
        assert response.status_code == 422
        assert "requires param" in response.json()["error"]["details"][0]["message"]

    @pytest.mark.parametrize("value", [123, True, 0])
    def test_integer_params_are_rejected_for_string_commands(
        self, client, device_id, value: object
    ) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(
                device_id,
                steps=[{"id": "s1", "command": "click", "params": {"selector": value}}],
            ),
        )

        # Assert
        assert response.status_code == 422
        message = response.json()["error"]["details"][0]["message"]
        assert "must be a string" in message or "requires param" in message

    @pytest.mark.parametrize("value", [1.5, None, ["a"], {"a": 1}])
    def test_unsupported_param_types_are_rejected(
        self, client, device_id, value: object
    ) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(
                device_id,
                steps=[{"id": "s1", "command": "goto", "params": {"url": value}}],
            ),
        )

        # Assert
        assert response.status_code == 422

    def test_undeclared_params_are_preserved(self, client, device_id) -> None:
        # Act — only declared params are validated; extras ride along
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(
                device_id,
                steps=[
                    {
                        "id": "s1",
                        "command": "goto",
                        "params": {"url": "https://e.com", "timeout": 100},
                    }
                ],
            ),
        )

        # Assert
        assert response.status_code == 201
        assert response.json()["data"]["steps"][0]["params"]["timeout"] == 100

    def test_params_defaults_to_empty_for_optional_only_commands(
        self, client, device_id
    ) -> None:
        # Arrange — every current command has a required param, so omitting
        # params must fail rather than silently produce an unusable step
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(
                device_id, steps=[{"id": "s1", "command": "goto"}]
            ),
        )

        # Assert
        assert response.status_code == 422

    @pytest.mark.parametrize("count", [1, 2, 25])
    def test_step_lists_of_varying_length(
        self, client, device_id, count: int
    ) -> None:
        # Arrange
        steps = [
            {"id": f"s{i}", "command": "goto", "params": {"url": f"https://e{i}.com"}}
            for i in range(count)
        ]

        # Act
        response = client.post(
            "/api/v1/scenarios", json=make_scenario_payload(device_id, steps=steps)
        )

        # Assert
        assert response.status_code == 201
        assert len(response.json()["data"]["steps"]) == count

    @pytest.mark.parametrize("steps", [[], None])
    def test_empty_or_null_step_list_is_rejected(
        self, client, device_id, steps: object
    ) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios", json=make_scenario_payload(device_id, steps=steps)
        )

        # Assert
        assert response.status_code == 422
        assert response.json()["error"]["details"][0]["loc"] == ["body", "steps"]

    def test_step_order_is_preserved(self, client, device_id) -> None:
        # Arrange
        steps = [
            {"id": "first", "command": "goto", "params": {"url": "https://a.com"}},
            {"id": "second", "command": "click", "params": {"selector": "#b"}},
            {"id": "third", "command": "click", "params": {"selector": "#c"}},
        ]

        # Act
        response = client.post(
            "/api/v1/scenarios", json=make_scenario_payload(device_id, steps=steps)
        )

        # Assert
        assert [s["id"] for s in response.json()["data"]["steps"]] == [
            "first",
            "second",
            "third",
        ]


@pytest.mark.integration
class TestScenarioValidations:
    @pytest.mark.parametrize("provider", VALID_PROVIDERS)
    def test_every_registered_provider_is_accepted(
        self, client, device_id, provider: str
    ) -> None:
        # Arrange — only "custom" requires its own url check
        rule = {"id": "v1", "provider": provider, "params": []}
        if provider == "custom":
            rule["url"] = {"match": "exists"}

        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(device_id, validations=[rule]),
        )

        # Assert
        assert response.status_code == 201
        assert response.json()["data"]["validations"][0]["provider"] == provider

    @pytest.mark.parametrize("provider", ["meta_pixel", "CUSTOM", "", "google-analytics"])
    def test_unregistered_providers_are_rejected(
        self, client, device_id, provider: str
    ) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(
                device_id,
                validations=[
                    {"id": "v1", "provider": provider, "url": {"match": "exists"}}
                ],
            ),
        )

        # Assert
        assert response.status_code == 422

    def test_custom_provider_requires_a_url_check(self, client, device_id) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(
                device_id, validations=[{"id": "v1", "provider": "custom"}]
            ),
        )

        # Assert
        assert response.status_code == 422
        assert "'url' is required" in response.json()["error"]["details"][0]["message"]

    def test_provider_defaults_to_custom(self, client, device_id) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(
                device_id,
                validations=[{"id": "v1", "url": {"match": "exists"}}],
            ),
        )

        # Assert
        assert response.json()["data"]["validations"][0]["provider"] == "custom"

    @pytest.mark.skipif(
        not NON_CUSTOM_PROVIDERS, reason="no non-custom providers registered"
    )
    def test_non_custom_providers_need_no_url_check(self, client, device_id) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(
                device_id,
                validations=[
                    {
                        "id": "v1",
                        "provider": NON_CUSTOM_PROVIDERS[0],
                        "params": [{"key": "tid", "match": "exists"}],
                    }
                ],
            ),
        )

        # Assert
        assert response.status_code == 201
        assert response.json()["data"]["validations"][0]["url"] is None

    @pytest.mark.parametrize("match", VALID_MATCH_TYPES)
    def test_url_check_match_types(self, client, device_id, match: str) -> None:
        # Arrange — "exists" is the only match type that needs no value
        url_check = {"match": match}
        if match != "exists":
            url_check["value"] = "collect"

        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(
                device_id,
                validations=[{"id": "v1", "provider": "custom", "url": url_check}],
            ),
        )

        # Assert
        assert response.status_code == 201

    @pytest.mark.parametrize(
        "match", [m for m in VALID_MATCH_TYPES if m != "exists"]
    )
    @pytest.mark.parametrize("value", [None, ""])
    def test_url_check_value_required_unless_exists(
        self, client, device_id, match: str, value: object
    ) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(
                device_id,
                validations=[
                    {
                        "id": "v1",
                        "provider": "custom",
                        "url": {"match": match, "value": value},
                    }
                ],
            ),
        )

        # Assert
        assert response.status_code == 422
        assert "'value' is required" in response.json()["error"]["details"][0]["message"]

    @pytest.mark.parametrize(
        "match", [m for m in VALID_MATCH_TYPES if m != "exists"]
    )
    def test_param_check_value_required_unless_exists(
        self, client, device_id, match: str
    ) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(
                device_id,
                validations=[
                    {
                        "id": "v1",
                        "provider": "custom",
                        "url": {"match": "exists"},
                        "params": [{"key": "tid", "match": match}],
                    }
                ],
            ),
        )

        # Assert
        assert response.status_code == 422

    def test_param_check_exists_needs_no_value(self, client, device_id) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(
                device_id,
                validations=[
                    {
                        "id": "v1",
                        "provider": "custom",
                        "url": {"match": "exists"},
                        "params": [{"key": "tid", "match": "exists"}],
                    }
                ],
            ),
        )

        # Assert
        assert response.status_code == 201
        assert response.json()["data"]["validations"][0]["params"][0]["value"] is None

    @pytest.mark.parametrize(
        "key",
        ["tid", "pr1.nm", "pr12.c2", "utm_source", "en", TURKISH, "a" * 1000],
    )
    def test_param_keys_including_ga4_dot_notation(
        self, client, device_id, key: str
    ) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(
                device_id,
                validations=[
                    {
                        "id": "v1",
                        "provider": "custom",
                        "url": {"match": "exists"},
                        "params": [{"key": key, "match": "exact", "value": "x"}],
                    }
                ],
            ),
        )

        # Assert
        assert response.status_code == 201
        assert response.json()["data"]["validations"][0]["params"][0]["key"] == key

    def test_empty_param_key_is_rejected(self, client, device_id) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(
                device_id,
                validations=[
                    {
                        "id": "v1",
                        "provider": "custom",
                        "url": {"match": "exists"},
                        "params": [{"key": "", "match": "exists"}],
                    }
                ],
            ),
        )

        # Assert
        assert response.status_code == 422

    @pytest.mark.parametrize(
        "value", ["^https://.*\\.com$", "a|b", "[0-9]{3}", "(unclosed"]
    )
    def test_regex_values_are_stored_verbatim(
        self, client, device_id, value: str
    ) -> None:
        # Act — the API stores patterns; compilation happens in the extension
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(
                device_id,
                validations=[
                    {
                        "id": "v1",
                        "provider": "custom",
                        "url": {"match": "regex", "value": value},
                    }
                ],
            ),
        )

        # Assert
        assert response.status_code == 201
        assert response.json()["data"]["validations"][0]["url"]["value"] == value

    @pytest.mark.parametrize("match", ["EXACT", "fuzzy", "", "starts_with"])
    def test_unknown_match_types_are_rejected(
        self, client, device_id, match: str
    ) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(
                device_id,
                validations=[
                    {"id": "v1", "provider": "custom", "url": {"match": match}}
                ],
            ),
        )

        # Assert
        assert response.status_code == 422

    @pytest.mark.parametrize("validations", [[], None])
    def test_empty_or_null_validation_list_is_rejected(
        self, client, device_id, validations: object
    ) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios",
            json=make_scenario_payload(device_id, validations=validations),
        )

        # Assert
        assert response.status_code == 422
        assert response.json()["error"]["details"][0]["loc"] == ["body", "validations"]


@pytest.mark.integration
class TestScenarioUpdateBranches:
    def test_patch_steps_serialises_each_step(self, client, scenario_id) -> None:
        # Arrange
        steps = [
            {"id": "s1", "command": "goto", "params": {"url": "https://new.com"}},
            {"id": "s2", "command": "click", "params": {"selector": "#buy"}},
        ]

        # Act
        response = client.patch(
            f"/api/v1/scenarios/{scenario_id}", json={"steps": steps}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["data"]["steps"] == steps

    def test_patch_validations_serialises_each_rule(
        self, client, scenario_id
    ) -> None:
        # Arrange
        validations = [
            {
                "id": "v9",
                "provider": "custom",
                "url": {"match": "startsWith", "value": "https://analytics"},
                "params": [{"key": "pr1.nm", "match": "exact", "value": "barista"}],
            }
        ]

        # Act
        response = client.patch(
            f"/api/v1/scenarios/{scenario_id}", json={"validations": validations}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["data"]["validations"] == validations

    def test_patch_validations_revalidates_the_rules(
        self, client, scenario_id
    ) -> None:
        # Act
        response = client.patch(
            f"/api/v1/scenarios/{scenario_id}",
            json={"validations": [{"id": "v9", "provider": "custom"}]},
        )

        # Assert
        assert response.status_code == 422

    def test_patch_steps_revalidates_the_commands(self, client, scenario_id) -> None:
        # Act
        response = client.patch(
            f"/api/v1/scenarios/{scenario_id}",
            json={"steps": [{"id": "s1", "command": "hover", "params": {}}]},
        )

        # Assert
        assert response.status_code == 422

    @pytest.mark.parametrize("field", ["steps", "validations"])
    def test_patch_rejects_empty_collections(
        self, client, scenario_id, field: str
    ) -> None:
        # Act
        response = client.patch(
            f"/api/v1/scenarios/{scenario_id}", json={field: []}
        )

        # Assert
        assert response.status_code == 422

    def test_patch_multiple_fields_at_once(self, client, scenario_id) -> None:
        # Act
        response = client.patch(
            f"/api/v1/scenarios/{scenario_id}",
            json={
                "name": "Renamed",
                "status": False,
                "step_timeout": 1234,
                "description": "new description",
            },
        )

        # Assert
        data = response.json()["data"]
        assert data["name"] == "Renamed"
        assert data["status"] is False
        assert data["step_timeout"] == 1234
        assert data["description"] == "new description"

    def test_empty_patch_body_changes_nothing(self, client, scenario_id) -> None:
        # Arrange
        before = client.get(f"/api/v1/scenarios/{scenario_id}").json()["data"]

        # Act
        response = client.patch(f"/api/v1/scenarios/{scenario_id}", json={})

        # Assert
        after = response.json()["data"]
        assert response.status_code == 200
        assert after["name"] == before["name"]
        assert after["steps"] == before["steps"]
        assert after["validations"] == before["validations"]

    def test_patch_device_id_validates_the_target(self, client, scenario_id) -> None:
        # Act
        response = client.patch(
            f"/api/v1/scenarios/{scenario_id}", json={"device_id": "ghost"}
        )

        # Assert
        assert response.status_code == 422
        error = response.json()["error"]
        assert error["details"][0]["loc"] == ["body", "device_id"]
        assert error["details"][0]["message"] == "Device not found"

    def test_patch_device_id_to_a_real_device(self, client, scenario_id) -> None:
        # Arrange
        other = client.post(
            "/api/v1/devices", json=make_device_payload(name="Pixel 9")
        ).json()["data"]["id"]

        # Act
        response = client.patch(
            f"/api/v1/scenarios/{scenario_id}", json={"device_id": other}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["data"]["device_id"] == other

    def test_patch_leaves_created_at_and_advances_updated_at(
        self, client, scenario_id
    ) -> None:
        # Arrange
        before = client.get(f"/api/v1/scenarios/{scenario_id}").json()["data"]

        # Act
        after = client.patch(
            f"/api/v1/scenarios/{scenario_id}", json={"name": "Touched"}
        ).json()["data"]

        # Assert
        assert after["created_at"] == before["created_at"]
        assert after["updated_at"] >= before["updated_at"]

    @pytest.mark.parametrize(
        "field", ["name", "status", "step_timeout", "steps", "validations", "device_id"]
    )
    def test_explicit_null_returns_500(
        self, client_no_raise, scenario_id, field: str
    ) -> None:
        # Act
        response = client_no_raise.patch(
            f"/api/v1/scenarios/{scenario_id}", json={field: None}
        )

        # KNOWN DEFECT: `ScenarioUpdate` types every field as `X | None`, so an
        # explicit null passes validation and is written straight to a NOT NULL
        # column. The device_id case additionally skips `_require_device`,
        # whose guard is `payload.device_id is not None`. Should be 422.
        assert response.status_code == 500
        assert response.json()["error"]["code"] == "INTERNAL_ERROR"


@pytest.mark.integration
class TestScenarioDeviceReference:
    @pytest.mark.parametrize("device_ref", ["ghost", "", " ", "x" * 1000])
    def test_unknown_device_is_reported_on_the_device_id_field(
        self, client, device_ref: str
    ) -> None:
        # Act
        response = client.post(
            "/api/v1/scenarios", json=make_scenario_payload(device_ref)
        )

        # Assert
        assert response.status_code == 422
        assert response.json()["error"]["details"][0]["loc"] == ["body", "device_id"]

    def test_no_scenario_is_persisted_when_the_device_is_missing(
        self, client
    ) -> None:
        # Act
        client.post("/api/v1/scenarios", json=make_scenario_payload("ghost"))

        # Assert
        assert client.get("/api/v1/scenarios").json()["meta"]["total_count"] == 0

    def test_many_scenarios_can_share_one_device(self, client, device_id) -> None:
        # Act
        for i in range(3):
            client.post(
                "/api/v1/scenarios",
                json=make_scenario_payload(device_id, name=f"Shared {i}"),
            )

        # Assert
        body = client.get("/api/v1/scenarios").json()
        assert body["meta"]["total_count"] == 3
        assert {s["device_id"] for s in body["data"]} == {device_id}


@pytest.mark.integration
class TestScenarioListEdgeCases:
    @pytest.mark.parametrize(
        ("stored", "query", "should_match"),
        [
            ("Checkout 100%", "100%", True),
            ("Checkout 1000", "100%", False),
            ("add_to_cart", "_cart", True),
            ("addXtoXcart", "_cart", False),
        ],
    )
    def test_like_wildcards_are_matched_literally(
        self, client, device_id, stored: str, query: str, should_match: bool
    ) -> None:
        # Arrange
        client.post("/api/v1/scenarios", json=make_scenario_payload(device_id, name=stored))

        # Act
        response = client.get("/api/v1/scenarios", params={"name": query})

        # Assert
        names = [s["name"] for s in response.json()["data"]]
        assert (stored in names) is should_match

    @pytest.mark.parametrize(
        ("query", "loc"),
        [
            ("page=0", "page"),
            ("size=0", "size"),
            ("size=101", "size"),
            ("sort_by=bogus", "sort_by"),
            ("sort_order=sideways", "sort_order"),
        ],
    )
    def test_invalid_query_params_are_rejected(
        self, client, query: str, loc: str
    ) -> None:
        # Act
        response = client.get(f"/api/v1/scenarios?{query}")

        # Assert
        assert response.status_code == 422
        assert response.json()["error"]["details"][0]["loc"] == ["query", loc]

    def test_page_past_the_end_returns_an_empty_window(
        self, client, device_id
    ) -> None:
        # Arrange
        client.post("/api/v1/scenarios", json=make_scenario_payload(device_id))

        # Act
        body = client.get("/api/v1/scenarios?page=50&size=10").json()

        # Assert
        assert body["data"] == []
        assert body["meta"]["total_count"] == 1
        assert body["links"]["next"] is None

    def test_steps_and_validations_survive_the_list_view(
        self, client, device_id
    ) -> None:
        # Arrange
        client.post("/api/v1/scenarios", json=make_scenario_payload(device_id))

        # Act
        listed = client.get("/api/v1/scenarios").json()["data"][0]

        # Assert — JSON columns are returned fully, not truncated
        assert listed["steps"] == [GOTO_STEP]
        assert listed["validations"] == [CUSTOM_VALIDATION]

    def test_unicode_names_are_filterable(self, client, device_id) -> None:
        # Arrange
        client.post(
            "/api/v1/scenarios", json=make_scenario_payload(device_id, name=TURKISH)
        )

        # Act
        response = client.get("/api/v1/scenarios", params={"name": "Ğğ"})

        # Assert
        assert len(response.json()["data"]) == 1
