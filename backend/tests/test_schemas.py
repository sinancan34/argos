import pytest
from pydantic import ValidationError

from app.schemas import (
    DeviceCreate,
    DeviceUpdate,
    MatchType,
    ParamCheck,
    ProviderType,
    ScenarioCreate,
    ScenarioUpdate,
    SortBy,
    SortOrder,
    StepSchema,
    UrlCheck,
    ValidationSchema,
)


@pytest.mark.unit
class TestEnums:
    def test_match_type_values(self):
        assert MatchType.exact == "exact"
        assert MatchType.contains == "contains"
        assert MatchType.exists == "exists"
        assert MatchType.regex == "regex"

    def test_sort_by_values(self):
        assert SortBy.name == "name"
        assert SortBy.created_at == "created_at"

    def test_sort_order_values(self):
        assert SortOrder.asc == "asc"
        assert SortOrder.desc == "desc"

    def test_provider_type_includes_custom(self):
        assert ProviderType.custom == "custom"


@pytest.mark.unit
class TestParamCheck:
    def test_valid_with_value(self):
        pc = ParamCheck(key="utm_source", match=MatchType.exact, value="google")
        assert pc.key == "utm_source"
        assert pc.match == MatchType.exact
        assert pc.value == "google"

    def test_valid_exists_without_value(self):
        pc = ParamCheck(key="tid", match=MatchType.exists)
        assert pc.value is None

    def test_value_required_when_not_exists(self):
        with pytest.raises(ValidationError, match="value.*required"):
            ParamCheck(key="tid", match=MatchType.exact)

    def test_value_required_when_not_exists_empty_string(self):
        with pytest.raises(ValidationError, match="value.*required"):
            ParamCheck(key="tid", match=MatchType.contains, value="")


@pytest.mark.unit
class TestUrlCheck:
    def test_valid_with_value(self):
        uc = UrlCheck(match=MatchType.contains, value="google-analytics")
        assert uc.value == "google-analytics"

    def test_valid_exists_without_value(self):
        uc = UrlCheck(match=MatchType.exists)
        assert uc.value is None

    def test_value_required_when_not_exists(self):
        with pytest.raises(ValidationError, match="value.*required"):
            UrlCheck(match=MatchType.exact)


@pytest.mark.unit
class TestStepSchema:
    def test_valid_goto(self):
        step = StepSchema(
            id="s1", command="goto", params={"url": "https://example.com"}
        )
        assert step.command == "goto"

    def test_valid_click(self):
        step = StepSchema(
            id="s1", command="click", params={"selector": "button.submit"}
        )
        assert step.command == "click"

    def test_unknown_command(self):
        with pytest.raises(ValidationError, match="Unknown command"):
            StepSchema(id="s1", command="hover", params={})

    def test_missing_required_param(self):
        with pytest.raises(ValidationError, match="requires param"):
            StepSchema(id="s1", command="goto", params={})

    def test_wrong_param_type(self):
        with pytest.raises(ValidationError, match="must be a string"):
            StepSchema(id="s1", command="goto", params={"url": 123})

    def test_default_empty_params(self):
        # click requires selector, so this should fail
        with pytest.raises(ValidationError, match="requires param"):
            StepSchema(id="s1", command="click", params={})


@pytest.mark.unit
class TestValidationSchema:
    def test_valid_custom_with_url(self):
        vs = ValidationSchema(
            id="v1",
            provider=ProviderType.custom,
            url=UrlCheck(match=MatchType.contains, value="analytics"),
        )
        assert vs.provider == ProviderType.custom

    def test_custom_requires_url(self):
        with pytest.raises(ValidationError, match="url.*required"):
            ValidationSchema(id="v1", provider=ProviderType.custom)

    def test_non_custom_provider_no_url_required(self):
        # Get a non-custom provider if available
        non_custom = [p for p in ProviderType if p != ProviderType.custom]
        if non_custom:
            vs = ValidationSchema(id="v1", provider=non_custom[0])
            assert vs.url is None


def _steps():
    return [
        StepSchema(id="s1", command="goto", params={"url": "https://example.com"})
    ]


def _validations():
    return [
        ValidationSchema(
            id="v1",
            provider=ProviderType.custom,
            url=UrlCheck(match=MatchType.contains, value="example"),
        )
    ]


@pytest.mark.unit
class TestScenarioCreate:
    def test_valid_payload(self):
        sc = ScenarioCreate(
            name="Test",
            steps=_steps(),
            validations=_validations(),
            device_id="dev-1",
        )
        assert sc.name == "Test"
        assert sc.status is True
        assert sc.step_timeout == 5000
        assert sc.validation_timeout == 10000
        assert sc.device_id == "dev-1"

    def test_missing_device_id_rejected(self):
        with pytest.raises(ValidationError):
            ScenarioCreate(
                name="Test",
                steps=_steps(),
                validations=_validations(),
            )

    def test_empty_device_id_rejected(self):
        with pytest.raises(ValidationError):
            ScenarioCreate(
                name="Test",
                steps=_steps(),
                validations=_validations(),
                device_id="",
            )

    def test_name_too_long(self):
        with pytest.raises(ValidationError):
            ScenarioCreate(
                name="x" * 501,
                steps=_steps(),
                validations=_validations(),
                device_id="dev-1",
            )

    def test_empty_name(self):
        with pytest.raises(ValidationError):
            ScenarioCreate(
                name="",
                steps=_steps(),
                validations=_validations(),
                device_id="dev-1",
            )

    def test_empty_steps_rejected(self):
        with pytest.raises(ValidationError):
            ScenarioCreate(
                name="Test",
                steps=[],
                validations=_validations(),
                device_id="dev-1",
            )

    def test_empty_validations_rejected(self):
        with pytest.raises(ValidationError):
            ScenarioCreate(
                name="Test",
                steps=_steps(),
                validations=[],
                device_id="dev-1",
            )


@pytest.mark.unit
class TestScenarioUpdate:
    def test_partial_update_name_only(self):
        su = ScenarioUpdate(name="Updated Name")
        data = su.model_dump(exclude_unset=True)
        assert data == {"name": "Updated Name"}

    def test_partial_update_status(self):
        su = ScenarioUpdate(status=False)
        data = su.model_dump(exclude_unset=True)
        assert data == {"status": False}

    def test_partial_update_device_id(self):
        su = ScenarioUpdate(device_id="dev-2")
        data = su.model_dump(exclude_unset=True)
        assert data == {"device_id": "dev-2"}

    def test_all_fields_none_by_default(self):
        su = ScenarioUpdate()
        data = su.model_dump(exclude_unset=True)
        assert data == {}


@pytest.mark.unit
class TestDeviceCreate:
    def test_valid_payload(self):
        dc = DeviceCreate(name="iPhone 15", meta={"viewport_width": 390})
        assert dc.name == "iPhone 15"
        assert dc.meta == {"viewport_width": 390}
        assert dc.status is True

    def test_defaults(self):
        dc = DeviceCreate(name="Bare")
        assert dc.meta == {}
        assert dc.status is True

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError):
            DeviceCreate(name="")

    def test_name_too_long_rejected(self):
        with pytest.raises(ValidationError):
            DeviceCreate(name="x" * 501)

    def test_invalid_status_rejected(self):
        with pytest.raises(ValidationError):
            DeviceCreate(name="Phone", status="not-a-bool")


@pytest.mark.unit
class TestDeviceUpdate:
    def test_partial_update_name_only(self):
        du = DeviceUpdate(name="Renamed")
        data = du.model_dump(exclude_unset=True)
        assert data == {"name": "Renamed"}

    def test_partial_update_meta(self):
        du = DeviceUpdate(meta={"has_touch": True})
        data = du.model_dump(exclude_unset=True)
        assert data == {"meta": {"has_touch": True}}

    def test_all_fields_none_by_default(self):
        du = DeviceUpdate()
        data = du.model_dump(exclude_unset=True)
        assert data == {}
