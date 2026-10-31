from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database.session import get_db
from app.core.dependencies.integration import require_admin, get_user_info
from app.core.dependencies.crud import integration as crud_integration
from app.api.v1.schemas.integration import (
    IntegrationCreate,
    IntegrationResponse,
    IntegrationUpdate,
)

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.post(
    "/", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED
)
def create_integration(
    *,
    db: Session = Depends(get_db),
    integration_in: IntegrationCreate,
    current_user: dict = Depends(require_admin),
):
    """Создать новое подключение к IoT-платформе (только админ)."""
    return crud_integration.create(db=db, obj_in=integration_in)


@router.get("/", response_model=List[IntegrationResponse])
def read_integrations(
    organization_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_user_info),  # Доступно всем авторизованным
):
    """Получить список интеграций для конкретной УК (организации)."""
    return crud_integration.get_by_organization(
        db=db, organization_id=str(organization_id)
    )


@router.get("/{integration_id}", response_model=IntegrationResponse)
def read_integration(
    integration_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_user_info),
):
    """Получить детали интеграции по ID."""
    integration = crud_integration.get(db=db, id=integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration


@router.patch("/{integration_id}", response_model=IntegrationResponse)
def update_integration(
    *,
    db: Session = Depends(get_db),
    integration_id: UUID,
    integration_in: IntegrationUpdate,
    current_user: dict = Depends(require_admin),
):
    """Обновить настройки интеграции (только админ)."""
    integration = crud_integration.get(db=db, id=integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return crud_integration.update(db=db, db_obj=integration, obj_in=integration_in)


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_integration(
    *,
    db: Session = Depends(get_db),
    integration_id: UUID,
    current_user: dict = Depends(require_admin),
):
    """Удалить интеграцию (только админ)."""
    integration = crud_integration.get(db=db, id=integration_id)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    crud_integration.remove(db=db, id=integration_id)


from pydantic import BaseModel
from app.models.integration import Integration
from app.services.device_sync import sync_emulators
from app.core.config import settings

class EmulatorSyncRequest(BaseModel):
    organization_id: UUID
    object_id: UUID

@router.post("/emulators/sync")
async def import_emulators(payload: EmulatorSyncRequest, db: Session = Depends(get_db), user: dict = Depends(require_admin)):
    integration = db.query(Integration).filter_by(organization_id=payload.organization_id, platform_type="emulator").first()
    if not integration:
        integration = Integration(organization_id=payload.organization_id, platform_type="emulator", name="Emulators", base_url=settings.emulator_fleet_url)
        db.add(integration)
        db.flush()
    try:
        count = await sync_emulators(db, integration, payload.object_id)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(409, str(exc)) from None
    except Exception:
        db.rollback()
        raise HTTPException(503, "Emulator synchronization unavailable") from None
    return {"integration_id": integration.id, "object_id": payload.object_id, "devices_count": count}
