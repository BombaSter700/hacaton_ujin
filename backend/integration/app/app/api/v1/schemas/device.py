from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.device import DeviceStatus

class SignalResponse(BaseModel):
    id: UUID
    external_signal_id: str
    name: str
    signal_type: str
    unit: Optional[str]
    is_writable: bool
    min_value: Optional[float]
    max_value: Optional[float]

    model_config = ConfigDict(from_attributes=True)

class DeviceCreate(BaseModel):
    integration_id: UUID
    external_id: str
    object_id: UUID
    room_id: Optional[UUID] = None
    name: str
    device_type: str
    timezone: str = "Europe/Moscow"
    polling_interval_seconds: int = 60
    tags: List[str] = Field(default_factory=list)

class DeviceResponse(BaseModel):
    id: UUID
    integration_id: UUID
    external_id: str
    object_id: UUID
    room_id: Optional[UUID]
    name: str
    device_type: str
    is_active: bool
    status: DeviceStatus
    timezone: str
    polling_interval_seconds: int
    tags: List[str]
    connected_at: Optional[datetime]
    last_seen_at: Optional[datetime]
    disconnected_at: Optional[datetime]
    created_at: datetime
    
    # Вложенные сигналы
    signals: List[SignalResponse] = []

    model_config = ConfigDict(from_attributes=True)

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    room_id: Optional[UUID] = None
    timezone: Optional[str] = None
    polling_interval_seconds: Optional[int] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None