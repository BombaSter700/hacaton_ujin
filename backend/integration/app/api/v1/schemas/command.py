from pydantic import BaseModel, Field
from typing import Optional, Union
from uuid import UUID
from datetime import datetime


class CommandRequest(BaseModel):
    signal_id: UUID = Field(
        ..., description="ID сигнала (из таблицы signals), на который шлем команду"
    )
    value: Union[float, str, bool] = Field(
        ..., description="Новое значение (например, 25.5, 'ON', True)"
    )
    idempotency_key: Optional[str] = Field(
        None,
        description="Уникальный ключ для защиты от дублей. Если отправить два раза с одним ключом, команда выполнится один раз.",
    )


class CommandResponse(BaseModel):
    command_id: UUID
    status: str  # pending, success, failed, timeout
    message: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
