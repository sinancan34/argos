from enum import Enum

from pydantic import BaseModel, Field, model_validator

from app.command_registry import (
    COMMAND_PARAMS,
    VALID_COMMANDS,
    VALID_MATCH_TYPES,
    VALID_SELECTOR_STRATEGIES,
)
from app.validation_registry import (
    ENUMS,
    PARAM_CHECK_FIELDS,
    SCENARIO_FIELDS,
    URL_CHECK_FIELDS,
    pydantic_field_kwargs,
)


# --- Enums (generated from shared sources) ---

MatchType = Enum("MatchType", {v: v for v in VALID_MATCH_TYPES}, type=str)

SelectorStrategy = Enum(
    "SelectorStrategy", {v: v for v in VALID_SELECTOR_STRATEGIES}, type=str
)

SortBy = Enum("SortBy", {v: v for v in ENUMS["sortBy"]}, type=str)

SortOrder = Enum("SortOrder", {v: v for v in ENUMS["sortOrder"]}, type=str)


# --- JSON schema models (from spec) ---

_pc_key_kw = pydantic_field_kwargs(PARAM_CHECK_FIELDS["key"])
_pc_cond = PARAM_CHECK_FIELDS["value"].get("conditionalRequired", {})


class ParamCheck(BaseModel):
    key: str = Field(..., **_pc_key_kw)
    match: MatchType
    value: str | None = None

    @model_validator(mode="after")
    def value_required_unless_exists(self) -> "ParamCheck":
        unless_value = _pc_cond.get("unless", {}).get("equals")
        min_len = _pc_cond.get("minLength", 1)
        if self.match.value != unless_value and (
            self.value is None or len(self.value) < min_len
        ):
            raise ValueError(
                f"'value' is required when match type is '{self.match.value}'"
            )
        return self


_uc_cond = URL_CHECK_FIELDS["value"].get("conditionalRequired", {})


class UrlCheck(BaseModel):
    match: MatchType
    value: str | None = None

    @model_validator(mode="after")
    def value_required_unless_exists(self) -> "UrlCheck":
        unless_value = _uc_cond.get("unless", {}).get("equals")
        min_len = _uc_cond.get("minLength", 1)
        if self.match.value != unless_value and (
            self.value is None or len(self.value) < min_len
        ):
            raise ValueError(
                f"'value' is required when match type is '{self.match.value}'"
            )
        return self


class StepSchema(BaseModel):
    id: str
    command: str
    params: dict = {}

    @model_validator(mode="after")
    def validate_command_and_params(self) -> "StepSchema":
        if self.command not in VALID_COMMANDS:
            raise ValueError(
                f"Unknown command: '{self.command}'. "
                f"Valid commands: {sorted(VALID_COMMANDS)}"
            )

        for pdef in COMMAND_PARAMS[self.command]:
            name = pdef["name"]
            ptype = pdef["type"]
            required = pdef["required"]
            value = self.params.get(name)

            if required and (value is None or value == "" or value == []):
                raise ValueError(
                    f"Command '{self.command}' requires param '{name}'"
                )

            if value is None:
                continue

            if ptype == "string" and not isinstance(value, str):
                raise ValueError(f"Param '{name}' must be a string")
            elif ptype == "int" and not isinstance(value, int):
                raise ValueError(f"Param '{name}' must be an integer")
            elif ptype == "selector":
                if not isinstance(value, list) or len(value) == 0:
                    raise ValueError(
                        f"Param '{name}' must be a non-empty list of selectors"
                    )
                for entry in value:
                    if not isinstance(entry, dict):
                        raise ValueError("Each selector must be an object")
                    if entry.get("strategy") not in VALID_SELECTOR_STRATEGIES:
                        raise ValueError(
                            f"Invalid selector strategy: '{entry.get('strategy')}'. "
                            f"Valid: {sorted(VALID_SELECTOR_STRATEGIES)}"
                        )
                    if not entry.get("value"):
                        raise ValueError("Selector value must be non-empty")

        return self


class ValidationSchema(BaseModel):
    id: str
    url: UrlCheck
    params: list[ParamCheck] = Field(default_factory=list)


# --- Request models ---

_name_kw = pydantic_field_kwargs(SCENARIO_FIELDS["name"])
_step_timeout_kw = pydantic_field_kwargs(SCENARIO_FIELDS["step_timeout"])
_validation_timeout_kw = pydantic_field_kwargs(SCENARIO_FIELDS["validation_timeout"])
_status_kw = pydantic_field_kwargs(SCENARIO_FIELDS["status"])
_steps_kw = pydantic_field_kwargs(SCENARIO_FIELDS["steps"])
_validations_kw = pydantic_field_kwargs(SCENARIO_FIELDS["validations"])


class ScenarioCreate(BaseModel):
    name: str = Field(..., **_name_kw)
    description: str | None = None
    status: int = Field(**_status_kw)
    step_timeout: int = Field(**_step_timeout_kw)
    validation_timeout: int = Field(**_validation_timeout_kw)
    steps: list[StepSchema] = Field(..., **_steps_kw)
    validations: list[ValidationSchema] = Field(..., **_validations_kw)


class ScenarioUpdate(BaseModel):
    name: str | None = Field(None, **{k: v for k, v in _name_kw.items() if k != "default"})
    description: str | None = None
    status: int | None = None
    step_timeout: int | None = Field(None, gt=_step_timeout_kw.get("gt", 0))
    validation_timeout: int | None = Field(None, gt=_validation_timeout_kw.get("gt", 0))
    steps: list[StepSchema] | None = Field(None, **{k: v for k, v in _steps_kw.items() if k != "default"})
    validations: list[ValidationSchema] | None = Field(None, **{k: v for k, v in _validations_kw.items() if k != "default"})


# --- Response models ---

class ScenarioResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    name: str
    description: str | None
    status: int
    step_timeout: int
    validation_timeout: int
    steps: list
    validations: list
    created_at: str
    updated_at: str


class PaginationMeta(BaseModel):
    page: int
    size: int
    total_count: int
    total_pages: int


class SingleScenarioEnvelope(BaseModel):
    data: ScenarioResponse


class ScenarioListEnvelope(BaseModel):
    data: list[ScenarioResponse]
    meta: PaginationMeta
