from typing import List
from sqlalchemy.orm import Session
from app.models.integration import Integration
from app.repositories.base import CRUDBase
from app.api.v1.schemas.integration import IntegrationCreate, IntegrationUpdate

class CRUDIntegration(CRUDBase[Integration, IntegrationCreate, IntegrationUpdate]):
    
    def get_by_organization(self, db: Session, organization_id: str) -> List[Integration]:
        return db.query(Integration).filter(Integration.organization_id == organization_id).all()

    def create(self, db: Session, *, obj_in: IntegrationCreate) -> Integration:
        # В реальности здесь нужно использовать шифратор (например, Fernet)
        # Пока просто имитируем шифрование для демонстрации
        encrypted_creds = f"enc_{obj_in.credentials}"
        
        db_obj = Integration(
            name=obj_in.name,
            platform_type=obj_in.platform_type,
            base_url=obj_in.base_url,
            organization_id=obj_in.organization_id,
            credentials_encrypted=encrypted_creds
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

integration = CRUDIntegration(Integration)