import uuid
from datetime import datetime
from sqlalchemy import Column, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from .base import Base


class DeviceEventType(str, enum.Enum):
    CONNECTED = "connected"  # Устройство вышло на связь
    DISCONNECTED = "disconnected"  # Потеря связи (timeout)
    MANUAL_DISCONNECT = "manual_disconnect"  # Отвязали вручную
    ERROR = "error"  # Ошибка оборудования/протокола
    FIRMWARE_UPDATED = "firmware_updated"
    BATTERY_LOW = "battery_low"


class DeviceEventLog(Base):
    __tablename__ = "device_event_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(
        UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False, index=True
    )

    event_type = Column(Enum(DeviceEventType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Дополнительный контекст (например, текст ошибки или код отключения)
    details = Column(JSON, nullable=True)

    device = relationship("Device", back_populates="events")
