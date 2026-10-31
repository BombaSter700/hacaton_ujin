import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    integration_id = Column(UUID(as_uuid=True), ForeignKey("integrations.id"), nullable=False)
    
    # ID устройства во внешней системе (Ujin)
    external_id = Column(String, nullable=False, index=True) 
    
    # Привязка к бизнес-сущностям УК
    object_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    room_id = Column(UUID(as_uuid=True), nullable=True)
    
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связь с сигналами (один ко многим)
    signals = relationship("Signal", back_populates="device", cascade="all, delete-orphan")


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