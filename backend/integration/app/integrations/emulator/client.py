import logging
import httpx
from typing import Dict, Any

logger = logging.getLogger(__name__)


class EmulatorAdapter:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def get_state(self) -> Dict[str, Any]:
        """GET /state -> JSON с текущими значениями сигналов."""
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{self.base_url}/state")
            resp.raise_for_status()
            return {"signals": resp.json()}

    async def send_command(self, signal_name: str, value: Any) -> bool:
        """POST /command (application/x-www-form-urlencoded)"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            data = {
                "signal": signal_name,
                "value": str(value)
            }
            resp = await client.post(f"{self.base_url}/command", data=data)
            # Эмулятор может вернуть 200, даже если команда не применилась.
            if resp.status_code != 200:
                logger.error(f"Command HTTP error {resp.status_code}: {resp.text}")
                return False
            return resp.json().get("error") == 0
