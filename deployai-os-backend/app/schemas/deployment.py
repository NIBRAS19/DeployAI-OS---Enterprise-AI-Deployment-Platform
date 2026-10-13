from datetime import datetime

from app.models.enums import DeploymentStatus, Environment
from app.schemas.base import CamelModel


class DeploymentOut(CamelModel):
    id: str
    version: str
    environment: Environment
    status: DeploymentStatus
    deployed_by: str
    deployed_at: datetime
    commit: str
