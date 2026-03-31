import pytest

from app.validation_registry import (
    ENUMS,
    PARAM_CHECK_FIELDS,
    SCENARIO_FIELDS,
    URL_CHECK_FIELDS,
    VALID_PROVIDERS,
    pydantic_field_kwargs,
)


@pytest.mark.unit
class TestPydanticFieldKwargs:
    def test_min_length(self):
        result = pydantic_field_kwargs({"minLength": 1})
        assert result == {"min_length": 1}

    def test_max_length(self):
        result = pydantic_field_kwargs({"maxLength": 500})
        assert result == {"max_length": 500}

    def test_min_value(self):
        result = pydantic_field_kwargs({"min": 0})
        assert result == {"ge": 0}

    def test_max_value(self):
        result = pydantic_field_kwargs({"max": 100})
        assert result == {"le": 100}

    def test_positive(self):
        result = pydantic_field_kwargs({"positive": True})
        assert result == {"gt": 0}

    def test_positive_false_ignored(self):
        result = pydantic_field_kwargs({"positive": False})
        assert result == {}

    def test_default_value(self):
        result = pydantic_field_kwargs({"default": 5000})
        assert result == {"default": 5000}

    def test_min_items(self):
        result = pydantic_field_kwargs({"minItems": 1})
        assert result == {"min_length": 1}

    def test_combined_fields(self):
        result = pydantic_field_kwargs({
            "minLength": 1,
            "maxLength": 500,
            "default": "hello",
        })
        assert result == {"min_length": 1, "max_length": 500, "default": "hello"}

    def test_empty_definition(self):
        result = pydantic_field_kwargs({})
        assert result == {}

    def test_unknown_keys_ignored(self):
        result = pydantic_field_kwargs({"type": "string", "required": True})
        assert result == {}


@pytest.mark.unit
class TestRegistryConstants:
    def test_enums_has_sort_by(self):
        assert "sortBy" in ENUMS
        assert "name" in ENUMS["sortBy"]
        assert "created_at" in ENUMS["sortBy"]

    def test_enums_has_sort_order(self):
        assert "sortOrder" in ENUMS
        assert "asc" in ENUMS["sortOrder"]
        assert "desc" in ENUMS["sortOrder"]

    def test_scenario_fields_has_name(self):
        assert "name" in SCENARIO_FIELDS
        assert SCENARIO_FIELDS["name"]["type"] == "string"
        assert SCENARIO_FIELDS["name"]["required"] is True

    def test_url_check_fields_has_match(self):
        assert "match" in URL_CHECK_FIELDS
        assert URL_CHECK_FIELDS["match"]["type"] == "enum"

    def test_param_check_fields_has_key(self):
        assert "key" in PARAM_CHECK_FIELDS
        assert PARAM_CHECK_FIELDS["key"]["minLength"] == 1

    def test_valid_providers_includes_custom(self):
        assert "custom" in VALID_PROVIDERS
        assert VALID_PROVIDERS[0] == "custom"
