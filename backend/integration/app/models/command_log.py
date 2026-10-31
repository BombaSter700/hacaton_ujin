import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, ForeignKey, DateTime, Enum, JSON, Integer, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
import enum
from .base import Base


class CommandStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class CommandLog(Base):
    __tablename__ = "command_logs"
    __table_args__ = (
        UniqueConstraint('actor_user_id', 'idempotency_key', name='uq_user_idempotency'),
    )
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Кто отправил (ID из JWT). Без ForeignKey, так как юзера в этой БД нет.
    user_id = Column("actor_user_id", Integer, nullable=True, index=True)
    legacy_user_id = Column("user_id", UUID(as_uuid=True), nullable=True)

    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    signal_id = Column(UUID(as_uuid=True), ForeignKey("signals.id"), nullable=False)

    value = Column(JSON, nullable=False)
    idempotency_key = Column(String, nullable=True, index=True)

    status = Column(Enum(CommandStatus), default=CommandStatus.PENDING)
    error_message = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
