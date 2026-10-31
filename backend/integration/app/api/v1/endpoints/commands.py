from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database.session import get_db
from app.core.dependencies.integration import get_user_info
from app.core.dependencies.crud import device as crud_device
from app.api.v1.schemas.command import CommandRequest, CommandResponse
from app.services.command_service import CommandService

router = APIRouter(prefix="/commands", tags=["commands"])


def get_command_service() -> CommandService:
    return CommandService()


@router.post("/{device_id}/send", response_model=CommandResponse)
async def send_command(
    *,
    db: Session = Depends(get_db),
    device_id: UUID,
    cmd_in: CommandRequest,
    current_user: dict = Depends(get_user_info),
    command_service: CommandService = Depends(get_command_service),
):

    # 1Проверяем, существует ли устройство
    device = crud_device.get(db=db, id=device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # TODO: Проверка прав пользователя на управление этим device (по object_id)

    # Передаем управление сервису
    response = await command_service.process_command(
        db=db,
        device=device,
        cmd_in=cmd_in,
        user_id=current_user["user_id"]
    )

    return response