from app.models.enums import RequirementPriority, RequirementStatus, RequirementType
from app.schemas.base import CamelModel


class RequirementOut(CamelModel):
    id: str
    title: str
    type: RequirementType
    priority: RequirementPriority
    status: RequirementStatus
    stakeholder: str


class RequirementCreate(CamelModel):
    title: str
    type: RequirementType
    priority: RequirementPriority
    stakeholder: str
    status: RequirementStatus = RequirementStatus.draft
