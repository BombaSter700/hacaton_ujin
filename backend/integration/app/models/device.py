import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Float,
    Enum,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from .base import Base
import enum


class DeviceStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    UNKNOWN = "unknown"


class Device(Base):
    __tablename__ = "devices"

    # Защита от дублей
    __table_args__ = (
        UniqueConstraint(
            "integration_id", "external_id", name="uq_integration_external_id"
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(
        UUID(as_uuid=True), ForeignKey("integrations.id"), nullable=False
    )
    external_id = Column(String, nullable=False, index=True)
    # URL эмулятора для отправки команд
    base_url = Column(String, nullable=True)

    object_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    room_id = Column(UUID(as_uuid=True), nullable=True)
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    status = Column(Enum(DeviceStatus), default=DeviceStatus.UNKNOWN)

    connected_at = Column(DateTime, nullable=True)
    last_seen_at = Column(DateTime, nullable=True)
    disconnected_at = Column(DateTime, nullable=True)

    # Метаданные железа
    serial_number = Column(String, nullable=True, index=True)
    mac_address = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    firmware_version = Column(String, nullable=True)
    battery_level = Column(Float, nullable=True)  # Для беспроводных датчиков (0-100)

    created_at = Column(DateTime, default=datetime.utcnow)
    # Часовой пояс
    timezone = Column(String, default="UTC", nullable=False)
    # Если устройство не выходит на связь дольше этого времени - статус OFFLINE
    polling_interval_seconds = Column(Integer, default=60, nullable=False)
    # Теги / Категории (массив строк)
    tags = Column(ARRAY(String), default=list, nullable=False)

    signals = relationship(
        "Signal", back_populates="device", cascade="all, delete-orphan"
    )
    events = relationship(
        "DeviceEventLog", back_populates="device", cascade="all, delete-orphan"
    )


class Signal(Base):
    __tablename__ = "signals"

    # Защита от дублей
    __table_args__ = (
        UniqueConstraint(
            "device_id", "external_signal_id", name="uq_device_external_signal"
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)

    # ID сигнала во внешней системе (Ujin)
    external_signal_id = Column(String, nullable=False)

    name = Column(String, nullable=False)
    signal_type = Column(String, nullable=False)  # temperature, leak, switch
    unit = Column(String, nullable=True)  # °C, %, bool
    is_writable = Column(Boolean, default=False)

    # Для валидации входящих команд
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    value_type = Column(String(10), nullable=False, default="string")
    source_is_writable = Column(Boolean, nullable=False, default=False)
    is_customized = Column(Boolean, nullable=False, default=False)

    device = relationship("Device", back_populates="signals")
