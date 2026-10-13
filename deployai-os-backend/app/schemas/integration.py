from datetime import datetime

from app.models.enums import ConnectionStatus, IntegrationType
from app.schemas.base import CamelModel


class IntegrationOut(CamelModel):
    id: str
    name: str
    type: IntegrationType
    status: ConnectionStatus
    last_sync: datetime


class IntegrationCreate(CamelModel):
    name: str
    type: IntegrationType
    status: ConnectionStatus = ConnectionStatus.disconnected
