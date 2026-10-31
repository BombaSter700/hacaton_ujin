import uuid
import logging
from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.device import Device
from app.models.integration import Integration
from app.repositories.base import CRUDBase
from app.api.v1.schemas.device import DeviceCreate, DeviceUpdate
from app.services.analytics import analytics

logger = logging.getLogger(__name__)

class CRUDDevice(CRUDBase[Device, DeviceCreate, DeviceUpdate]):
    
    def get_by_external_id(self, db: Session, external_id: str) -> Optional[Device]:
        return db.query(Device).filter(Device.external_id == external_id).first()
        
    def get_by_object_id(self, db: Session, object_id: str) -> List[Device]:
        return db.query(Device).filter(Device.object_id == object_id).all()

    def update_status(self, db: Session, *, device_id: str, status: str) -> Optional[Device]:
        db_obj = self.get(db, device_id)
        if not db_obj:
            return None
            
        old_status = db_obj.status
        if old_status == status:
            return db_obj # Статус не изменился, ничего не делаем

        db_obj.status = status
        
        event_type = "error"
        severity = "error"
        
        if status == "offline":
            db_obj.disconnected_at = datetime.now(timezone.utc).replace(tzinfo=None)
            event_type = "disconnected"
            severity = "warning"
        elif status == "online":
            db_obj.connected_at = datetime.now(timezone.utc).replace(tzinfo=None)
            db_obj.last_seen_at = datetime.now(timezone.utc).replace(tzinfo=None)
            event_type = "connected"
            severity = "info"

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Пытаемся получить organization_id из интеграции
        integration = db.query(Integration).filter(Integration.id == db_obj.integration_id).first()
        org_id = integration.organization_id if integration else uuid.uuid4()

        # Пишем в ClickHouse
        analytics.log_event(
            table="device_events",
            data={
                "organization_id": org_id,
                "building_id": db_obj.object_id,
                "device_id": db_obj.id,
                "event_id": uuid.uuid4(),
                "event_type": event_type,
                "severity": severity,
                "occurred_at": datetime.now(timezone.utc),
                "payload": f'{{"old_status": "{old_status}", "new_status": "{status}"}}'
            }
        )
        
        return db_obj

device = CRUDDevice(Device)