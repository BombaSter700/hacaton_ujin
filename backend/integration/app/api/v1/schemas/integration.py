from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.integration import IntegrationStatus


class IntegrationBase(BaseModel):
    name: str = Field(..., description="Название интеграции, например 'Ujin Основной'")
    platform_type: str = Field(..., description="Тип платформы: ujin, modbus, mqtt")
    base_url: str = Field(..., description="URL API платформы")
    organization_id: UUID = Field(..., description="ID УК (организации)")


class IntegrationCreate(IntegrationBase):
    # Секрет приходит в открытом виде и шифруется в сервисе перед сохранением
    credentials: str = Field(
        ..., description="API-ключ или токен для доступа к платформе"
    )


class IntegrationUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    credentials: Optional[str] = None  # Если админ хочет сменить токен
    status: Optional[IntegrationStatus] = None


class IntegrationResponse(IntegrationBase):
    id: UUID
    status: IntegrationStatus
    last_sync_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    # поля credentials_encrypted здесь нет, не отдаем секреты в API.
