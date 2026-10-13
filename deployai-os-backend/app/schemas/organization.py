from app.schemas.base import CamelModel


class OrganizationOut(CamelModel):
    id: str
    name: str
    industry: str
    active_projects: int
