from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database.session import get_db
from app.core.dependencies.integration import get_user_info
from app.core.dependencies.crud import device as crud_device
from app.api.v1.schemas.device import DeviceResponse

router = APIRouter(prefix="/devices", tags=["devices"])

@router.get("/", response_model=List[DeviceResponse])
def read_devices(
    object_id: UUID = Query(..., description="ID объекта недвижимости (дом/квартира)"),
    room_id: Optional[UUID] = Query(None, description="ID помещения"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_user_info)
):

    # TODO: Добавить проверку прав (require_object_access)
    devices = crud_device.get_by_object_id(db=db, object_id=str(object_id))
    
    if room_id:
        devices = [d for d in devices if d.room_id == room_id]
        
    return devices

@router.get("/{device_id}", response_model=DeviceResponse)
def read_device(
    device_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_user_info)
):
    """Получить детали конкретного устройства, включая его сигналы."""
    device = crud_device.get(db=db, id=device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.patch("/{device_id}", response_model=DeviceResponse)
def update_device_metadata(
    *,
    db: Session = Depends(get_db),
    device_id: UUID,
    device_in: dict, # В реальности лучше использовать DeviceUpdate схему
    current_user: dict = Depends(get_user_info)
):
    """
    Обновить метаданные устройства (теги, часовой пояс и т.д.).
    """
    device = crud_device.get(db=db, id=device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return crud_device.update(db=db, db_obj=device, obj_in=device_in)