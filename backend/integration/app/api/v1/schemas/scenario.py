from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
    field_validator,
)

SignalValue = StrictBool | StrictInt | StrictFloat | StrictStr


class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid", allow_inf_nan=False, str_strip_whitespace=True
    )


class SignalCondition(StrictModel):
    kind: Literal["signal"]
    device_id: UUID
    signal_id: UUID
    operator: Literal["eq", "ne", "gt", "gte", "lt", "lte"]
    value: SignalValue


class TimeCondition(StrictModel):
    kind: Literal["time"]
    start_time: str = Field(pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    end_time: str = Field(pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    timezone: str = Field(default="Europe/Moscow", max_length=64)

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value):
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError("Unknown IANA timezone") from None
        return value


Condition = Annotated[SignalCondition | TimeCondition, Field(discriminator="kind")]


class ScenarioAction(StrictModel):
    device_id: UUID
    signal_id: UUID
    value: SignalValue


class ScenarioCreate(StrictModel):
    object_id: UUID
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    enabled: bool = False
    match_mode: Literal["all", "any"] = "all"
    conditions: list[Condition] = Field(min_length=1, max_length=10)
    actions: list[ScenarioAction] = Field(min_length=1, max_length=10)


class ScenarioUpdate(ScenarioCreate):
    expected_revision: int = Field(ge=1)


class ScenarioToggle(StrictModel):
    enabled: bool
    expected_revision: int = Field(ge=1)


class ScenarioResponse(ScenarioCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    revision: int
    created_by: int
    created_at: datetime
    updated_at: datetime


class ScenarioPage(BaseModel):
    items: list[ScenarioResponse]
    total: int
