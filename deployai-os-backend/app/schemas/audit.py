from datetime import datetime

from app.schemas.base import CamelModel


class AuditLogEntryOut(CamelModel):
    id: str
    actor: str
    action: str
    resource_type: str
    resource_id: str
    ip_address: str
    timestamp: datetime
