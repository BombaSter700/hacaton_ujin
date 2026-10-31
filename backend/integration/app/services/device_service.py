from typing import List
from app.integrations.ujin.client import UjinClient
from app.api.v1.schemas import Device, CommandRequest, CommandResponse
import uuid


class DeviceService:
    def __init__(self, ujin_client: UjinClient):
        self.ujin = ujin_client

    async def get_user_devices(self, user_id: str, object_id: str) -> List[Device]:
        # TODO: Проверить доступ user_id к object_id
        # Временно возвращаем заглушку для эмулятора
        return [
            Device(
                id="leak-sensor-1",
                name="Датчик протечки",
                integration_id="ujin",
                object_id=object_id,
                signals=[...],
            )
        ]

    async def send_command(
        self, user_id: str, device_id: str, cmd: CommandRequest
    ) -> CommandResponse:
        # TODO: Проверить, что user_id имеет право управлять device_id
        command_id = str(uuid.uuid4())
        try:
            await self.ujin.send_command(
                device_id, {"signal_id": cmd.signal_id, "value": cmd.value}
            )
            return CommandResponse(command_id=command_id, status="success")
        except Exception as e:
            return CommandResponse(
                command_id=command_id, status="error", message=str(e)
            )
