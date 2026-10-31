import asyncio
import logging
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.database.session import SessionLocal
from app.models.device import Device, DeviceStatus
from app.integrations.emulator.client import EmulatorAdapter
from app.services.analytics import analytics
from app.services.state_repo import state_repo 

logger = logging.getLogger(__name__)


async def start_poller():
    while True:
        db: Session = SessionLocal()
        try:
            devices = db.query(Device).filter_by(is_active=True).all()
            tasks = [poll_device(device, db) for device in devices]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Poller loop error: {e}")
        finally:
            db.close()
        await asyncio.sleep(10)


async def poll_device(device: Device, db: Session):
    if not device.base_url:
        return

    adapter = EmulatorAdapter(device.base_url)
    now = datetime.now(timezone.utc)

    try:
        state = await adapter.get_state()
        signals_data = state.get("signals", {})
        await state_repo.update_state(str(device.id), signals_data, quality="good")

        was_offline = device.status != DeviceStatus.ONLINE
        device.status = DeviceStatus.ONLINE
        device.last_seen_at = now
        db.commit()

        if was_offline:
            analytics.log_event("device_events", {
                "organization_id": uuid.uuid4(), "building_id": device.object_id, 
                "device_id": device.id, "event_id": uuid.uuid4(), 
                "event_type": "connected", "severity": "info", 
                "occurred_at": now, "payload": "{}"
            })

        for sig_name, val in signals_data.items():
            if isinstance(val, (int, float, bool)):
                analytics.log_event("telemetry", {
                    "organization_id": uuid.uuid4(), "building_id": device.object_id,
                    "device_id": device.id, "metric": sig_name,
                    "event_id": uuid.uuid4(), "measured_at": now,
                    "received_at": now, "value": float(val), "quality": "good"
                })

    except Exception as e:
        logger.warning(f"Device {device.id} offline: {e}")
        was_online = device.status == DeviceStatus.ONLINE
        device.status = DeviceStatus.OFFLINE
        device.disconnected_at = now
        db.commit()

        await state_repo.update_state(str(device.id), {}, quality="offline")

        if was_online:
            analytics.log_event("device_events", {
                "organization_id": uuid.uuid4(), "building_id": device.object_id, 
                "device_id": device.id, "event_id": uuid.uuid4(), 
                "event_type": "disconnected", "severity": "warning", 
                "occurred_at": now, "payload": str(e)
            })