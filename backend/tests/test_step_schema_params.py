"""Param-type matrix for StepSchema against synthetic command definitions.

`shared/commands.json` currently declares only required string params, so the
optional-param and integer-param branches of the validator are unreachable
through the API. These tests patch the registry that `app.schemas` imported so
those branches are exercised before a future command needs them.
"""

from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app import schemas
from app.schemas import StepSchema

FAKE_COMMANDS = {"scroll", "wait"}
FAKE_PARAMS = {
    "scroll": [
        {"name": "selector", "type": "string", "required": True},
        {"name": "offset", "type": "int", "required": False},
    ],
    "wait": [
        {"name": "ms", "type": "int", "required": True},
        {"name": "label", "type": "string", "required": False},
    ],
}


@pytest.fixture()
def fake_registry():
    """Swap in synthetic commands covering optional and integer params."""
    with patch.object(schemas, "VALID_COMMANDS", FAKE_COMMANDS), patch.object(
        schemas, "COMMAND_PARAMS", FAKE_PARAMS
    ):
        yield


@pytest.mark.unit
class TestOptionalParams:
    def test_optional_param_may_be_absent(self, fake_registry) -> None:
        # Act
        step = StepSchema(id="s1", command="scroll", params={"selector": "#a"})

        # Assert
        assert step.params == {"selector": "#a"}

    def test_optional_param_may_be_present(self, fake_registry) -> None:
        # Act
        step = StepSchema(
            id="s1", command="scroll", params={"selector": "#a", "offset": 120}
        )

        # Assert
        assert step.params["offset"] == 120

    def test_optional_param_cannot_be_explicitly_null(self, fake_registry) -> None:
        # Act / Assert — `params` is dict[str, str | int], so the field type
        # rejects None before the validator's own None-skip can apply; an
        # optional param must be omitted rather than nulled out.
        with pytest.raises(ValidationError, match=r"params.offset"):
            StepSchema(
                id="s1", command="scroll", params={"selector": "#a", "offset": None}
            )

    def test_optional_param_still_type_checked_when_present(
        self, fake_registry
    ) -> None:
        # Act / Assert
        with pytest.raises(ValidationError, match=r"Param 'offset' must be an integer"):
            StepSchema(
                id="s1", command="scroll", params={"selector": "#a", "offset": "120"}
            )


@pytest.mark.unit
class TestIntegerParams:
    @pytest.mark.parametrize("value", [0, 1, -1, 5000, 2**63 - 1, 10**100])
    def test_any_integer_is_accepted(self, fake_registry, value: int) -> None:
        # Act
        step = StepSchema(id="s1", command="wait", params={"ms": value})

        # Assert
        assert step.params["ms"] == value

    @pytest.mark.parametrize("value", ["1000", "abc", "  "])
    def test_string_values_are_rejected(self, fake_registry, value: str) -> None:
        # Act / Assert
        with pytest.raises(ValidationError, match=r"Param 'ms' must be an integer"):
            StepSchema(id="s1", command="wait", params={"ms": value})

    def test_empty_string_trips_the_required_check_first(self, fake_registry) -> None:
        # Act / Assert — "" is caught as missing, not as a type mismatch
        with pytest.raises(ValidationError, match=r"requires param 'ms'"):
            StepSchema(id="s1", command="wait", params={"ms": ""})

    def test_required_integer_param_must_be_present(self, fake_registry) -> None:
        # Act / Assert
        with pytest.raises(ValidationError, match=r"requires param 'ms'"):
            StepSchema(id="s1", command="wait", params={})

    def test_zero_is_not_treated_as_missing(self, fake_registry) -> None:
        # Act — 0 is falsy but the guard checks None/""/[] explicitly
        step = StepSchema(id="s1", command="wait", params={"ms": 0})

        # Assert
        assert step.params["ms"] == 0

    def test_booleans_pass_the_integer_check(self, fake_registry) -> None:
        # Act — bool is a subclass of int, so isinstance() lets it through
        step = StepSchema(id="s1", command="wait", params={"ms": True})

        # Assert
        assert step.params["ms"] == 1


@pytest.mark.unit
class TestStringParams:
    @pytest.mark.parametrize("value", [123, 0, True])
    def test_integer_values_are_rejected(self, fake_registry, value: object) -> None:
        # Act / Assert
        with pytest.raises(ValidationError, match=r"Param 'selector' must be a string"):
            StepSchema(id="s1", command="scroll", params={"selector": value})

    def test_empty_required_string_is_reported_as_missing(
        self, fake_registry
    ) -> None:
        # Act / Assert
        with pytest.raises(ValidationError, match=r"requires param 'selector'"):
            StepSchema(id="s1", command="scroll", params={"selector": ""})

    def test_unknown_command_is_rejected_before_params(self, fake_registry) -> None:
        # Act / Assert
        with pytest.raises(ValidationError, match=r"Unknown command: 'goto'"):
            StepSchema(id="s1", command="goto", params={"url": "https://e.com"})
