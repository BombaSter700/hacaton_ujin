from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class SignalType(str, Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    LEAK = "leak"
    SWITCH = "switch"

class Signal(BaseModel):
    id: str
    name: str
    type: SignalType
    value: float | str | bool
    unit: Optional[str] = None
    measured_at: datetime
    received_at: datetime
    quality: str = "good"  # good, unknown, offline
    is_writable: bool = False

class Device(BaseModel):
    id: str
    name: str
    integration_id: str
    object_id: str
    room_id: Optional[str] = None
    signals: List[Signal] = []

class CommandRequest(BaseModel):
    signal_id: str
    value: float | str | bool

class CommandResponse(BaseModel):
    command_id: str
    status: str  # success, error, pending
    message: Optional[str] = None