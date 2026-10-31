"""Import the configured internal emulator fleet, without accepting device URLs from users."""
from datetime import datetime, timezone
from urllib.parse import urlsplit
import httpx
from sqlalchemy.orm import Session
from app.models.device import Device, Signal, DeviceStatus
from app.models.integration import Integration
from app.core.config import settings

async def sync_emulators(db: Session, integration: Integration, object_id):
    host = urlsplit(settings.emulator_fleet_url).hostname
    count = 0
    async with httpx.AsyncClient(timeout=5, trust_env=False) as client:
        response = await client.get(settings.emulator_fleet_url)
        response.raise_for_status()
        fleet = response.json()["devices"]
        for item in fleet:
            port = int(item["port"])
            if not 8099 <= port <= 8107:
                raise ValueError("Unexpected emulator port")
            base_url = f"http://{host}:{port}"
            response = await client.get(base_url + "/declaration")
            response.raise_for_status()
            declarations = response.json()
            device = db.query(Device).filter_by(integration_id=integration.id, external_id=item["serial"]).first()
            if not device:
                device = Device(integration_id=integration.id, external_id=item["serial"],
                    object_id=object_id, name=item["family"], device_type=item["family"], status=DeviceStatus.UNKNOWN)
                db.add(device)
                db.flush()
            elif device.object_id != object_id:
                raise ValueError("Fleet already belongs to another object")
            device.base_url = base_url
            for data in declarations:
                signal = db.query(Signal).filter_by(device_id=device.id, external_signal_id=data["name"]).first()
                if not signal:
                    signal = Signal(device_id=device.id, external_signal_id=data["name"])
                    db.add(signal)
                signal.name = data.get("title", data["name"])
                signal.signal_type = data.get("control", "text")
                signal.unit = data.get("measure")
                signal.is_writable = data.get("management") in ("rw", "w")
                signal.min_value = data.get("min")
                signal.max_value = data.get("max")
            count += 1
        integration.last_sync_at = datetime.now(timezone.utc)
        db.commit()
    return count
