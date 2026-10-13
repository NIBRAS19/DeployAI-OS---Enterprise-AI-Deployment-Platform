"""Enum definitions shared across models.

Values are kept identical (verbatim, including casing) to the string unions
already established in the frontend's lib/types.ts, so a record round-trips
through the API with no translation layer on either side.
"""

import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    employee = "employee"


class Environment(str, enum.Enum):
    development = "development"
    staging = "staging"
    production = "production"


class ProjectStatus(str, enum.Enum):
    active = "active"
    paused = "paused"
    completed = "completed"


class LifecycleStage(str, enum.Enum):
    discovery = "discovery"
    requirements = "requirements"
    architecture = "architecture"
    integrations = "integrations"
    ai_config = "aiConfig"
    security = "security"
    testing = "testing"
    deployment = "deployment"
    monitoring = "monitoring"
    iteration = "iteration"


class RequirementType(str, enum.Enum):
    functional = "Functional"
    non_functional = "Non-functional"
    security = "Security"
    integration = "Integration"
    ai = "AI"
    operational = "Operational"
    compliance = "Compliance"


class RequirementPriority(str, enum.Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"


class RequirementStatus(str, enum.Enum):
    draft = "Draft"
    validated = "Validated"
    in_development = "In Development"
    testing = "Testing"
    accepted = "Accepted"
    rejected = "Rejected"


class ArchitectureStatus(str, enum.Enum):
    proposed = "Proposed"
    accepted = "Accepted"
    superseded = "Superseded"


class IntegrationType(str, enum.Enum):
    rest_api = "REST API"
    webhook = "Webhook"
    email = "Email"
    whatsapp = "WhatsApp"
    file_upload = "File Upload"
    postgresql = "PostgreSQL"


class ConnectionStatus(str, enum.Enum):
    connected = "connected"
    disconnected = "disconnected"
    error = "error"


class DataSourceStatus(str, enum.Enum):
    connected = "connected"
    disconnected = "disconnected"


class DocumentClassification(str, enum.Enum):
    public = "Public"
    internal = "Internal"
    confidential = "Confidential"
    restricted = "Restricted"


class DocumentStatus(str, enum.Enum):
    uploaded = "Uploaded"
    processing = "Processing"
    processed = "Processed"
    indexed = "Indexed"
    failed = "Failed"


class CitationMode(str, enum.Enum):
    always = "always"
    when_available = "when-available"


class WorkflowStatus(str, enum.Enum):
    active = "active"
    paused = "paused"
    draft = "draft"


class WorkflowRunOutcome(str, enum.Enum):
    success = "success"
    failed = "failed"


class DeploymentStatus(str, enum.Enum):
    healthy = "healthy"
    degraded = "degraded"
    failed = "failed"


class FeedbackSentiment(str, enum.Enum):
    positive = "positive"
    negative = "negative"


# Classification -> the roles allowed to retrieve documents at that level.
# This is the enforcement table behind ADR-003 (authorize before retrieval).
CLASSIFICATION_ACCESS: dict[DocumentClassification, set[UserRole]] = {
    DocumentClassification.public: {UserRole.admin, UserRole.manager, UserRole.employee},
    DocumentClassification.internal: {UserRole.admin, UserRole.manager, UserRole.employee},
    DocumentClassification.confidential: {UserRole.admin, UserRole.manager},
    DocumentClassification.restricted: {UserRole.admin},
}
