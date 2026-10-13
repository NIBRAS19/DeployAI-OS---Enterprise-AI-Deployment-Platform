from app.models.enums import Environment, LifecycleStage, ProjectStatus
from app.schemas.base import CamelModel


class ProjectOut(CamelModel):
    id: str
    name: str
    organization_id: str
    customer_name: str
    environment: Environment
    status: ProjectStatus
    current_stage: LifecycleStage


class ProjectCreate(CamelModel):
    name: str
    customer_name: str
    environment: Environment = Environment.development
