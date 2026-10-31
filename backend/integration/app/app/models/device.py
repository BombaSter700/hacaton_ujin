import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Float, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from .base import Base
class Device(Base):
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(UUID(as_uuid=True), ForeignKey("integrations.id"), nullable=False)
    external_id = Column(String, nullable=False, index=True) 
    object_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    room_id = Column(UUID(as_uuid=True), nullable=True)
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    status = Column(Enum(DeviceStatus), default=DeviceStatus.UNKNOWN)
    
    # Когда устройство впервые появилось в системе / было привязано
    connected_at = Column(DateTime, nullable=True) 
    
    # Когда устройство последний раз выходило на связь (heartbeat/polling)
    last_seen_at = Column(DateTime, nullable=True) 
    
    # Если устройство отключено (is_active=False), когда это произошло
    disconnected_at = Column(DateTime, nullable=True) 

    # Метаданные "железа" (часто приходят из Ujin API)
    serial_number = Column(String, nullable=True, index=True)
    mac_address = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    firmware_version = Column(String, nullable=True)
    battery_level = Column(Float, nullable=True) # Для беспроводных датчиков (0-100)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    # Часовой пояс (IANA формат, например "Europe/Moscow")
    timezone = Column(String, default="UTC", nullable=False)
    # Если устройство не выходит на связь дольше этого времени -> статус OFFLINE
    polling_interval_seconds = Column(Integer, default=60, nullable=False)
    # Теги / Категории (массив строк)
    tags = Column(ARRAY(String), default=list, nullable=False)
    
    signals = relationship("Signal", back_populates="device", cascade="all, delete-orphan")
    events = relationship("DeviceEventLog", back_populates="device", cascade="all, delete-orphan")


class Signal(Base):
    __tablename__ = "signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    
    # ID сигнала во внешней системе (Ujin)
    external_signal_id = Column(String, nullable=False)
    
    name = Column(String, nullable=False)
    signal_type = Column(String, nullable=False) # temperature, leak, switch
    unit = Column(String, nullable=True)         # °C, %, bool
    is_writable = Column(Boolean, default=False)
    
    # Для валидации входящих команд
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)

    device = relationship("Device", back_populates="signals")