import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
import enum
from .base import Base

class IntegrationStatus(str, enum.Enum):
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"

class Integration(Base):
    __tablename__ = "integrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String, nullable=False)
    platform_type = Column(String, nullable=False)  # ujin, modbus, mqtt
    base_url = Column(String, nullable=False)
    
    
    # Пока просто строка, но в будущем нужен шифратор.
    credentials_encrypted = Column(String, nullable=True) 
    
    status = Column(Enum(IntegrationStatus), default=IntegrationStatus.ACTIVE)
    last_sync_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)