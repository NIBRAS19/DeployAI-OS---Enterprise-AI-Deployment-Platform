"""Import every model so Base.metadata is fully populated for
create_all() and for Alembic's autogenerate to see the whole schema."""

from app.models.architecture import ArchitectureDecision
from app.models.assistant import Assistant
from app.models.audit import AuditLogEntry
from app.models.data_source import DataSource
from app.models.deployment import Deployment
from app.models.evaluation import EvaluationRun
from app.models.feedback import FeedbackEntry
from app.models.integration import Integration
from app.models.knowledge import DocumentChunk, KnowledgeDocument
from app.models.organization import Organization
from app.models.project import Project
from app.models.requirement import Requirement
from app.models.user import User
from app.models.workflow import Workflow, WorkflowRun

__all__ = [
    "ArchitectureDecision",
    "Assistant",
    "AuditLogEntry",
    "DataSource",
    "Deployment",
    "EvaluationRun",
    "FeedbackEntry",
    "Integration",
    "DocumentChunk",
    "KnowledgeDocument",
    "Organization",
    "Project",
    "Requirement",
    "User",
    "Workflow",
    "WorkflowRun",
]
