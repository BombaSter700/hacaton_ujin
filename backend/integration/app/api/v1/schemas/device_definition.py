from typing import Literal
from uuid import UUID
from pydantic import Field, model_validator
from .scenario import StrictModel


class SignalDefinition(StrictModel):
    id: UUID
    name: str = Field(min_length=1, max_length=120)
    value_type: Literal["number", "string", "boolean"]
    unit: str | None = Field(default=None, max_length=30)
    is_writable: bool
    min_value: float | None = None
    max_value: float | None = None

    @model_validator(mode="after")
    def validate_range(self):
        if self.value_type != "number" and (self.min_value is not None or self.max_value is not None):
            raise ValueError("Only numeric signals have a range")
        if self.min_value is not None and self.max_value is not None and self.min_value > self.max_value:
            raise ValueError("Minimum must not exceed maximum")
        return self


class DeviceDefinition(StrictModel):
    name: str = Field(min_length=1, max_length=120)
    signals: list[SignalDefinition] = Field(max_length=100)

    @model_validator(mode="after")
    def unique_signals(self):
        if len({signal.id for signal in self.signals}) != len(self.signals):
            raise ValueError("Duplicate signal IDs")
        return self
