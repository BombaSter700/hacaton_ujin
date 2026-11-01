from uuid import NAMESPACE_URL, uuid5

from app.models.device import Device
from app.models.integration import Integration

DEMO_NAME = "Демонстрационный дом"
ORGANIZATION_ID = uuid5(NAMESPACE_URL, "ujin-hackathon/demo/organization")
OBJECT_ID = uuid5(NAMESPACE_URL, "ujin-hackathon/demo/object")


def get_demo_context(db):
    row = (
        db.query(Integration.organization_id, Device.object_id)
        .join(Device, Device.integration_id == Integration.id)
        .filter(Integration.platform_type == "emulator")
        .order_by(Integration.created_at, Integration.id, Device.object_id)
        .first()
    )
    if row:
        organization_id, object_id = row
    else:
        integration = (
            db.query(Integration)
            .filter_by(organization_id=ORGANIZATION_ID, platform_type="emulator")
            .first()
        )
        organization_id = (
            integration.organization_id if integration else ORGANIZATION_ID
        )
        object_id = OBJECT_ID
    return {
        "organization_id": organization_id,
        "object_id": object_id,
        "name": DEMO_NAME,
    }
