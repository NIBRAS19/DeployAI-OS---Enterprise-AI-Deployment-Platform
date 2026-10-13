from app.models.enums import DataSourceStatus
from app.schemas.base import CamelModel


class DataSourceOut(CamelModel):
    id: str
    name: str
    kind: str
    record_count: str
    status: DataSourceStatus


class DataSourceCreate(CamelModel):
    name: str
    kind: str
    record_count: str
    status: DataSourceStatus = DataSourceStatus.disconnected
