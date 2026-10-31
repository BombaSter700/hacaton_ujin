from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.device import Device
from app.repositories.base import CRUDBase
from app.api.v1.schemas.device import DeviceCreate, DeviceUpdate

class CRUDDevice(CRUDBase[Device, DeviceCreate, DeviceUpdate]):
    
    def get_by_external_id(self, db: Session, external_id: str) -> Optional[Device]:
        return db.query(Device).filter(Device.external_id == external_id).first()
        
    def get_by_object_id(self, db: Session, object_id: str) -> List[Device]:
        return db.query(Device).filter(Device.object_id == object_id).all()

    def update_status(self, db: Session, *, device_id: str, status: str) -> Optional[Device]:
        db_obj = self.get(db, device_id)
        if db_obj:
            db_obj.status = status
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

device = CRUDDevice(Device)