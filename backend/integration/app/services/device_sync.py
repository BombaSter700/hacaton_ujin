
import logging
import httpx
from sqlalchemy.orm import Session
from app.models.device import Device, Signal, DeviceStatus
from app.models.integration import Integration
from app.core.config import settings

logger = logging.getLogger(__name__)


async def sync_emulators(db: Session, integration: Integration, object_id: str):
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(settings.emulator_fleet_url)
            resp.raise_for_status()
            devices_data = resp.json()
        except Exception as e:
            logger.error(f"Failed to fetch fleet: {e}")
            raise

        for dev_info in devices_data:
            base_url = dev_info["url"]
            serial = dev_info["serial"]
            try:
                decl_resp = await client.get(f"{base_url}/declaration")
                decl_resp.raise_for_status()
                decl = decl_resp.json()
            except Exception as e:
                logger.warning(f"Skip {serial}: failed to get declaration ({e})")
                continue
            device = db.query(Device).filter_by(
                integration_id=integration.id, external_id=serial
            ).first()
            
            if not device:
                device = Device(
                    integration_id=integration.id,
                    external_id=serial,
                    base_url=base_url,
                    object_id=object_id,
                    name=decl.get("title", serial),
                    device_type=decl.get("type", "unknown"),
                    status=DeviceStatus.UNKNOWN
                )
                db.add(device)
                db.flush() # Чтобы получить device.id для сигналов

            for sig_data in decl.get("signals", []):
                sig = db.query(Signal).filter_by(
                    device_id=device.id, external_signal_id=sig_data["name"]
                ).first()
                
                if not sig:
                    sig = Signal(
                        device_id=device.id,
                        external_signal_id=sig_data["name"],
                        name=sig_data.get("title", sig_data["name"]),
                        signal_type=sig_data.get("kind", "unknown"),
                        unit=sig_data.get("unit"),
                        is_writable=sig_data.get("control") in ("rw", "w"),
                        min_value=sig_data.get("min"),
                        max_value=sig_data.get("max")
                    )
                    db.add(sig)
            
        db.commit()
        logger.info("Device synchronization complete.")