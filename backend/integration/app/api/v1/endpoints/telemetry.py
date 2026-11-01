from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import timezone
import clickhouse_connect

from app.core.config import settings
from app.core.database.session import get_db
from app.core.dependencies.integration import get_user_info
from app.core.dependencies.crud import device as crud_device
from app.services.state_repo import state_repo

router = APIRouter(prefix="/devices", tags=["telemetry"])


@router.get("/{device_id}/state")
async def get_device_state(
    device_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_user_info),
):
    device = crud_device.get(db, device_id)
    if not device:
        raise HTTPException(404, "Device not found")

    state_data = await state_repo.get_state(str(device_id))

    return {
        "device_id": device.id,
        "name": device.name,
        "status": device.status.value,
        "last_seen_at": device.last_seen_at.replace(tzinfo=timezone.utc)
        if device.last_seen_at
        else None,
        "state_received_at": state_data.get("received_at"),
        "quality": state_data.get("quality", "unknown"),
        "signals": state_data.get("signals", {}),
    }


@router.get("/{device_id}/history")
def get_device_history(
    device_id: UUID,
    signal_name: str = Query(...),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_user_info),
):
    device = crud_device.get(db, device_id)
    if not device:
        raise HTTPException(404, "Device not found")

    client = clickhouse_connect.get_client(
        host=settings.clickhouse_host,
        port=settings.clickhouse_port,
        username=settings.clickhouse_user,
        password=settings.clickhouse_password,
        database=settings.clickhouse_db,
    )
    try:
        query = """
            SELECT measured_at, value, unit, quality
            FROM telemetry
            WHERE device_id = {device_id:UUID} AND metric = {metric:String}
            ORDER BY measured_at DESC LIMIT {limit:UInt32}
        """
        result = client.query(
            query,
            parameters={"device_id": device_id, "metric": signal_name, "limit": limit},
        )
        return [
            {
                "time": row[0].replace(tzinfo=timezone.utc),
                "value": row[1],
                "unit": row[2],
                "quality": row[3],
            }
            for row in result.result_rows
        ]
    except Exception:
        raise HTTPException(500, "Telemetry storage unavailable")
    finally:
        client.close()
