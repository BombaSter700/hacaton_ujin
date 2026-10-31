from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.api.v1.schemas import Device, CommandRequest, CommandResponse
from app.core.dependencies.integration import get_user_info
from app.services.device_service import DeviceService
from app.integrations.ujin.client import UjinClient

router = APIRouter(prefix="/devices", tags=["devices"])

def get_device_service() -> DeviceService:
    # TODO: Инициализировать из настроек/DI-контейнера
    ujin = UjinClient(base_url="http://localhost:8099", api_key="test")
    return DeviceService(ujin)

@router.get("/", response_model=List[Device])
async def list_devices(
    object_id: str,
    user: dict = Depends(get_user_info),
    service: DeviceService = Depends(get_device_service)
):
    # 1. панель запрашивает устройства пользователя
    # 2. сервис проверяет identity (get_user_info) и доступ к объекту (внутри сервиса)
    return await service.get_user_devices(user["user_id"], object_id)

@router.post("/{device_id}/command", response_model=CommandResponse)
async def send_command(
    device_id: str,
    cmd: CommandRequest,
    user: dict = Depends(get_user_info),
    service: DeviceService = Depends(get_device_service)
):
    # 5. команда проходит серверную проверку прав и схемы сигнала
    return await service.send_command(user["user_id"], device_id, cmd)