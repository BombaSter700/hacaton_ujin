import uuid
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from .base import Base


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    object_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    description = Column(String(2000), nullable=False, default="")
    enabled = Column(Boolean, nullable=False, default=False)
    match_mode = Column(String(3), nullable=False, default="all")
    conditions = Column(JSON, nullable=False)
    actions = Column(JSON, nullable=False)
    created_by = Column(Integer, nullable=False)
    revision = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
