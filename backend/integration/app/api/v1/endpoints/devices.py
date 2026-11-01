from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID

from app.core.database.session import get_db
from app.core.dependencies.integration import get_user_info
from app.core.dependencies.crud import device as crud_device
from app.api.v1.schemas.device import DeviceResponse
from app.models.device import Device
from app.models.scenario import Scenario
from app.api.v1.schemas.device_definition import DeviceDefinition
from app.api.v1.schemas.scenario import ScenarioCreate
from app.services.scenario_validation import validate_definition
from pydantic import BaseModel
from app.services.demo import get_demo_context

router = APIRouter(prefix="/devices", tags=["devices"])


class DeviceObjectResponse(BaseModel):
    object_id: UUID
    devices_count: int
    name: str


@router.get("/objects", response_model=List[DeviceObjectResponse])
def read_device_objects(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_user_info),
):
    rows = (
        db.query(Device.object_id, func.count(Device.id))
        .group_by(Device.object_id)
        .order_by(Device.object_id)
        .all()
    )
    demo = get_demo_context(db)
    return [
        {
            "object_id": object_id,
            "devices_count": count,
            "name": demo["name"]
            if object_id == demo["object_id"]
            else f"Объект {index + 1}",
        }
        for index, (object_id, count) in enumerate(rows)
    ]


@router.get("/", response_model=List[DeviceResponse])
def read_devices(
    object_id: UUID = Query(..., description="ID объекта недвижимости (дом/квартира)"),
    room_id: Optional[UUID] = Query(None, description="ID помещения"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_user_info),
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
    current_user: dict = Depends(get_user_info),
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
    device_in: dict,  # В реальности лучше использовать DeviceUpdate схему
    current_user: dict = Depends(get_user_info),
):
    """
    Обновить метаданные устройства (теги, часовой пояс и т.д.).
    """
    device = crud_device.get(db=db, id=device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return crud_device.update(db=db, db_obj=device, obj_in=device_in)


@router.put("/{device_id}/definition", response_model=DeviceResponse)
def update_device_definition(
    device_id: UUID,
    payload: DeviceDefinition,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_info),
):
    device = db.query(Device).filter(Device.id == device_id).with_for_update().first()
    if not device:
        raise HTTPException(404, "Device not found")
    signals = {signal.id: signal for signal in device.signals}
    if set(signals) != {signal.id for signal in payload.signals}:
        raise HTTPException(
            422,
            "Provide exactly the existing device signals; import new capabilities from the device",
        )
    for definition in payload.signals:
        signal = signals[definition.id]
        if definition.is_writable and not signal.source_is_writable:
            raise HTTPException(
                422, f"{signal.name}: device does not support writing this signal"
            )
        for key, value in definition.model_dump(exclude={"id"}).items():
            setattr(signal, key, value)
        signal.is_customized = True
    device.name = payload.name
    # Do not silently invalidate enabled saved rules when changing signal types/ranges.
    for scenario in (
        db.query(Scenario).filter_by(object_id=device.object_id, enabled=True).all()
    ):
        if any(
            item.get("device_id") == str(device.id)
            for item in scenario.conditions + scenario.actions
        ):
            try:
                validate_definition(
                    db, ScenarioCreate.model_validate(scenario, from_attributes=True)
                )
            except HTTPException as exc:
                db.rollback()
                raise HTTPException(
                    409,
                    f"Disable or edit scenario '{scenario.name}' first: {exc.detail}",
                ) from None
    db.commit()
    db.refresh(device)
    return device
