"""Drift guards for app/command_registry.py against shared/commands.json.

Both the backend and the extension derive their command and match-type
vocabularies from the same JSON file. These tests assert the backend's view
matches the file byte-for-byte, so a shared-definition edit that only lands on
one side fails here rather than at runtime.
"""

import json
from pathlib import Path

import pytest

from app.command_registry import (
    COMMAND_PARAMS,
    VALID_COMMANDS,
    VALID_MATCH_TYPES,
)
from app.schemas import MatchType, ProviderType, SortBy, SortOrder
from app.validation_registry import ENUMS, VALID_PROVIDERS

SHARED_DIR = Path(__file__).resolve().parent.parent.parent / "shared"


@pytest.fixture(scope="module")
def commands_json() -> dict:
    """The shared command definitions, read straight from disk."""
    with open(SHARED_DIR / "commands.json", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def providers_json() -> dict:
    """The shared provider definitions, read straight from disk."""
    with open(SHARED_DIR / "providers.json", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.mark.unit
class TestCommandRegistry:
    def test_valid_commands_match_the_shared_file(self, commands_json: dict) -> None:
        # Assert
        assert VALID_COMMANDS == {c["command"] for c in commands_json["commands"]}

    def test_command_params_are_keyed_by_command(self, commands_json: dict) -> None:
        # Assert
        assert set(COMMAND_PARAMS) == VALID_COMMANDS
        for command in commands_json["commands"]:
            assert COMMAND_PARAMS[command["command"]] == command["params"]

    def test_match_types_match_the_shared_file(self, commands_json: dict) -> None:
        # Assert — order matters; the extension renders these as a list
        assert VALID_MATCH_TYPES == commands_json["matchTypes"]

    def test_exists_is_the_only_valueless_match_type(self) -> None:
        # Assert — the conditional validators key off this exact string
        assert "exists" in VALID_MATCH_TYPES

    def test_every_param_declares_name_type_and_required(self) -> None:
        # Assert
        for command, params in COMMAND_PARAMS.items():
            assert params, f"{command} declares no params"
            for param in params:
                assert isinstance(param["name"], str) and param["name"]
                assert param["type"] in {"string", "int"}
                assert isinstance(param["required"], bool)

    def test_param_names_are_unique_per_command(self) -> None:
        # Assert
        for command, params in COMMAND_PARAMS.items():
            names = [p["name"] for p in params]
            assert len(names) == len(set(names)), command


@pytest.mark.unit
class TestGeneratedEnums:
    def test_match_type_enum_mirrors_the_registry(self) -> None:
        # Assert
        assert [m.value for m in MatchType] == VALID_MATCH_TYPES

    def test_provider_enum_mirrors_the_registry(self) -> None:
        # Assert
        assert [p.value for p in ProviderType] == VALID_PROVIDERS

    def test_provider_list_is_custom_plus_the_shared_keys(
        self, providers_json: dict
    ) -> None:
        # Assert — adding a provider means adding a key to providers.json
        assert VALID_PROVIDERS == ["custom", *providers_json.keys()]

    def test_sort_enums_mirror_the_shared_file(self) -> None:
        # Assert
        assert [s.value for s in SortBy] == ENUMS["sortBy"]
        assert [s.value for s in SortOrder] == ENUMS["sortOrder"]

    @pytest.mark.parametrize("sort_by", ["name", "created_at", "updated_at"])
    def test_sort_by_values_are_real_model_columns(self, sort_by: str) -> None:
        # Arrange — list endpoints do getattr(Model, sort_by.value)
        from app.models import Device, Scenario

        # Assert
        assert hasattr(Device, sort_by)
        assert hasattr(Scenario, sort_by)

    def test_enum_members_compare_equal_to_their_strings(self) -> None:
        # Assert — the routers rely on str-enum equality
        assert MatchType.exact == "exact"
        assert ProviderType.custom == "custom"
        assert SortOrder.desc == "desc"
