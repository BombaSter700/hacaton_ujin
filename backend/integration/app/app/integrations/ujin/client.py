
import httpx
from typing import Dict, Any
from app.core.config import settings

class UjinClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(base_url=base_url, headers={"Authorization": f"Bearer {api_key}"})

    async def get_device_state(self, device_id: str) -> Dict[str, Any]:
        # Пример: GET /api/v1/devices/{device_id}
        resp = await self.client.get(f"/api/v1/devices/{device_id}")
        resp.raise_for_status()
        return resp.json()

    async def send_command(self, device_id: str, command: Dict[str, Any]) -> Dict[str, Any]:
        # Пример: POST /api/v1/devices/{device_id}/commands
        resp = await self.client.post(f"/api/v1/devices/{device_id}/commands", json=command)
        resp.raise_for_status()
        return resp.json()