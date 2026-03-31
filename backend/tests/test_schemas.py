import pytest
from pydantic import ValidationError

from app.schemas import (
    MatchType,
    ParamCheck,
    ProviderType,
    ScenarioCreate,
    ScenarioStatus,
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

    def test_scenario_status_values(self):
        assert ScenarioStatus.active == "active"
        assert ScenarioStatus.inactive == "inactive"

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


@pytest.mark.unit
class TestScenarioCreate:
    def test_valid_payload(self):
        sc = ScenarioCreate(
            name="Test",
            steps=[
                StepSchema(
                    id="s1", command="goto", params={"url": "https://example.com"}
                )
            ],
            validations=[
                ValidationSchema(
                    id="v1",
                    provider=ProviderType.custom,
                    url=UrlCheck(match=MatchType.contains, value="example"),
                )
            ],
        )
        assert sc.name == "Test"
        assert sc.status == ScenarioStatus.active
        assert sc.step_timeout == 5000
        assert sc.validation_timeout == 10000

    def test_name_too_long(self):
        with pytest.raises(ValidationError):
            ScenarioCreate(
                name="x" * 501,
                steps=[
                    StepSchema(
                        id="s1",
                        command="goto",
                        params={"url": "https://example.com"},
                    )
                ],
                validations=[
                    ValidationSchema(
                        id="v1",
                        provider=ProviderType.custom,
                        url=UrlCheck(match=MatchType.contains, value="x"),
                    )
                ],
            )

    def test_empty_name(self):
        with pytest.raises(ValidationError):
            ScenarioCreate(
                name="",
                steps=[
                    StepSchema(
                        id="s1",
                        command="goto",
                        params={"url": "https://example.com"},
                    )
                ],
                validations=[
                    ValidationSchema(
                        id="v1",
                        provider=ProviderType.custom,
                        url=UrlCheck(match=MatchType.contains, value="x"),
                    )
                ],
            )

    def test_empty_steps_rejected(self):
        with pytest.raises(ValidationError):
            ScenarioCreate(
                name="Test",
                steps=[],
                validations=[
                    ValidationSchema(
                        id="v1",
                        provider=ProviderType.custom,
                        url=UrlCheck(match=MatchType.contains, value="x"),
                    )
                ],
            )

    def test_empty_validations_rejected(self):
        with pytest.raises(ValidationError):
            ScenarioCreate(
                name="Test",
                steps=[
                    StepSchema(
                        id="s1",
                        command="goto",
                        params={"url": "https://example.com"},
                    )
                ],
                validations=[],
            )


@pytest.mark.unit
class TestScenarioUpdate:
    def test_partial_update_name_only(self):
        su = ScenarioUpdate(name="Updated Name")
        data = su.model_dump(exclude_unset=True)
        assert data == {"name": "Updated Name"}

    def test_partial_update_status(self):
        su = ScenarioUpdate(status=ScenarioStatus.inactive)
        data = su.model_dump(exclude_unset=True)
        assert data == {"status": ScenarioStatus.inactive}

    def test_all_fields_none_by_default(self):
        su = ScenarioUpdate()
        data = su.model_dump(exclude_unset=True)
        assert data == {}
