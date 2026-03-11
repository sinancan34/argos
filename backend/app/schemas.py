from enum import Enum

from pydantic import BaseModel, Field, model_validator


# --- Enums ---

class MatchType(str, Enum):
    exact = "exact"
    contains = "contains"
    starts_with = "startsWith"
    ends_with = "endsWith"
    regex = "regex"
    exists = "exists"


class SelectorStrategy(str, Enum):
    css = "css"
    xpath = "xpath"
    id = "id"
    name = "name"
    link_text = "linkText"
    partial_link_text = "partialLinkText"
    tag_name = "tagName"
    class_name = "className"


class SortBy(str, Enum):
    name = "name"
    created_at = "created_at"
    updated_at = "updated_at"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


# --- JSON schema models (from spec) ---

class Selector(BaseModel):
    strategy: SelectorStrategy
    value: str


class ParamCheck(BaseModel):
    key: str
    match: MatchType
    value: str | None = None

    @model_validator(mode="after")
    def value_required_unless_exists(self) -> "ParamCheck":
        if self.match != MatchType.exists and self.value is None:
            raise ValueError(f"'value' is required when match type is '{self.match.value}'")
        return self


class StepSchema(BaseModel):
    id: str
    command: str
    params: dict = {}
    timeout: int | None = None


class ValidationSchema(BaseModel):
    id: str
    params: list[ParamCheck] = Field(..., min_length=1)


# --- Request models ---

class ScenarioCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    step_timeout: int = 5000
    validation_timeout: int = 10000
    steps: list[StepSchema] = Field(..., min_length=1)
    validations: list[ValidationSchema] = Field(..., min_length=1)


class ScenarioUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    step_timeout: int | None = None
    validation_timeout: int | None = None
    steps: list[StepSchema] | None = None
    validations: list[ValidationSchema] | None = None


# --- Response models ---

class ScenarioResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    name: str
    description: str | None
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
