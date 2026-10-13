"""Populates the database with the GulfBridge Professional Services demo
dataset — the same organization, project, and record IDs the frontend's
lib/mock-data.ts uses, so the two line up conceptually even before they're
wired together over HTTP.

Idempotent: safe to run against an already-seeded database (checks for the
GulfBridge organization first and exits early if found). Run directly:

    python -m app.seed
"""

import json
from datetime import datetime, timezone

from app.core.security import hash_password
from app.database import Base, SessionLocal, engine
from app.models.architecture import ArchitectureDecision
from app.models.assistant import Assistant
from app.models.audit import AuditLogEntry
from app.models.data_source import DataSource
from app.models.deployment import Deployment
from app.models.enums import (
    ArchitectureStatus,
    CitationMode,
    ConnectionStatus,
    DataSourceStatus,
    DeploymentStatus,
    DocumentClassification,
    DocumentStatus,
    Environment,
    FeedbackSentiment,
    IntegrationType,
    LifecycleStage,
    ProjectStatus,
    RequirementPriority,
    RequirementStatus,
    RequirementType,
    UserRole,
    WorkflowStatus,
)
from app.models.evaluation import EvaluationRun
from app.models.feedback import FeedbackEntry
from app.models.integration import Integration
from app.models.knowledge import DocumentChunk, KnowledgeDocument
from app.models.organization import Organization
from app.models.project import Project
from app.models.requirement import Requirement
from app.models.user import User
from app.models.workflow import Workflow
from app.services.chunking import chunk_text
from app.services.embeddings import get_embedding_provider

DEMO_PASSWORD = "GulfBridge!Demo1"

# Real text for the documents that are actually indexed (doc-5 is left as
# "Processing" with no content, matching the frontend's mid-ingestion demo
# state). Chunk counts here are genuine — derived from this content — rather
# than the larger illustrative numbers in the frontend's static mock data.
DOCUMENT_CONTENT: dict[str, str] = {
    "doc-1": """Code of Conduct

All employees are expected to act with integrity, treat colleagues and clients with respect, and comply with applicable laws and company policy in every market GulfBridge operates in.

Working Hours

Standard working hours are 9:00 AM to 6:00 PM, Sunday to Thursday, with a one-hour lunch break. Flexible start times between 8:00 AM and 10:00 AM are permitted with manager approval.

Remote Work

Employees may work remotely up to two days per week, subject to manager approval and team coverage requirements. Fully remote arrangements are evaluated case by case by HR.

IT and Security

Company laptops must have disk encryption and the standard endpoint security agent installed before connecting to any internal system. Report lost or stolen devices to IT Security within one hour.

Benefits Overview

Full-time employees are eligible for health insurance, a retirement savings contribution, and the annual leave and travel policies described in their own dedicated documents.""",
    "doc-2": """Booking Business Travel

All business travel must be booked through the approved corporate travel portal at least five business days in advance where possible. Economy class is standard for flights under six hours; business class requires VP approval.

Expense Reimbursement

Expense reports must be submitted within 30 days of travel completion. Approved reimbursements are paid within 10 business days of manager sign-off, direct to the employee's registered bank account.

Per Diem Rates

Meal per diem is set at 150 AED per day for domestic travel and 220 AED per day for international travel, covering breakfast, lunch, and dinner without itemized receipts required under 50 AED per meal.

Approval Thresholds

Any single expense line over 2,000 AED requires additional Finance approval beyond the direct manager, regardless of category.""",
    "doc-3": """Annual Leave Accrual

All full-time employees accrue 24 days of annual leave per calendar year, credited monthly at a rate of two days per completed month of service. Part-time employees accrue leave on a pro-rated basis.

Requesting Leave

Leave requests must be submitted through the HR portal at least two weeks in advance for periods longer than three consecutive days. Requests are approved by the employee's direct manager and countersigned by HR for periods over ten days.

Carryover Rules

Up to five unused annual leave days may be carried over into the following calendar year. Any balance beyond five days is forfeited unless an exception is granted by HR for documented operational reasons.

Public Holidays

Public holidays observed in the employee's home country are granted in addition to the standard annual leave allowance and do not count against the employee's leave balance.""",
    "doc-4": """Executive Compensation Bands

Base salary bands for the executive leadership team range from 850,000 to 1,650,000 AED annually, reviewed each fiscal year by the Compensation Committee against regional benchmarking data.

Annual Bonus Structure

Executive annual bonus targets range from 40% to 80% of base salary, contingent on company-wide revenue and margin targets set at the start of the fiscal year by the Board.

Equity Grants

Senior executives receive equity grants vesting over four years with a one-year cliff, sized according to role level and approved individually by the Compensation Committee and CEO.

This document is classified Restricted and access is limited to Finance leadership and the executive team. Distribution outside this group requires CEO approval.""",
    "doc-6": """Resetting Your VPN Access

To reset your company VPN credentials, open the IT Self-Service portal, select "Reset VPN Access," and follow the two-factor verification steps. Access is restored within 15 minutes for most requests.

Contacting the IT Helpdesk

The IT helpdesk is available Sunday to Thursday, 8:00 AM to 8:00 PM, via the internal chat widget or by calling extension 4100. Urgent outages can be reported 24/7 through the emergency escalation line.

Common Account Issues

Most login issues are resolved by clearing the browser cache and confirming the account hasn't been locked after repeated failed attempts. Locked accounts unlock automatically after 30 minutes or can be reset immediately by the helpdesk.

General Support Process

Support requests submitted through the customer portal are triaged within one business hour and assigned a priority level based on impact and urgency, following the standard support SLA.""",
}


def _dt(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.get(Organization, "org-gulfbridge"):
            print("Already seeded (org-gulfbridge exists) — skipping.")
            return

        db.add_all(
            [
                Organization(
                    id="org-gulfbridge",
                    name="GulfBridge Professional Services",
                    industry="Professional Services / Training / Consultancy",
                ),
                Organization(id="org-northwind", name="Northwind Retail Group", industry="Retail"),
            ]
        )
        db.flush()

        db.add_all(
            [
                User(
                    id="usr-demo-admin",
                    name="Demo Engineer",
                    email="demo.engineer@gulfbridge.example",
                    password_hash=hash_password(DEMO_PASSWORD),
                    role=UserRole.admin,
                    organization_id="org-gulfbridge",
                ),
                User(
                    id="usr-demo-employee",
                    name="Sara Employee",
                    email="employee.demo@gulfbridge.example",
                    password_hash=hash_password(DEMO_PASSWORD),
                    role=UserRole.employee,
                    organization_id="org-gulfbridge",
                ),
            ]
        )

        db.add(
            Project(
                id="proj-gulfbridge-knowledge-ops",
                name="Enterprise Knowledge & Operations AI",
                organization_id="org-gulfbridge",
                customer_name="GulfBridge Professional Services",
                environment=Environment.production,
                status=ProjectStatus.active,
                current_stage=LifecycleStage.iteration,
            )
        )
        db.flush()
        project_id = "proj-gulfbridge-knowledge-ops"

        db.add_all(
            [
                Requirement(id="REQ-101", project_id=project_id, title="Employees can search internal documentation via chat", type=RequirementType.functional, priority=RequirementPriority.critical, status=RequirementStatus.accepted, stakeholder="Ops Director"),
                Requirement(id="REQ-102", project_id=project_id, title="Assistant must never reveal restricted documents", type=RequirementType.security, priority=RequirementPriority.critical, status=RequirementStatus.accepted, stakeholder="Security Reviewer"),
                Requirement(id="REQ-103", project_id=project_id, title="All AI answers must cite source documents", type=RequirementType.ai, priority=RequirementPriority.high, status=RequirementStatus.accepted, stakeholder="Compliance"),
                Requirement(id="REQ-104", project_id=project_id, title="Support requests routed automatically by category", type=RequirementType.operational, priority=RequirementPriority.high, status=RequirementStatus.in_development, stakeholder="Support Lead"),
                Requirement(id="REQ-105", project_id=project_id, title="WhatsApp responses require human approval before send", type=RequirementType.compliance, priority=RequirementPriority.critical, status=RequirementStatus.accepted, stakeholder="Compliance"),
                Requirement(id="REQ-106", project_id=project_id, title="System maintains full audit trail of AI configuration changes", type=RequirementType.non_functional, priority=RequirementPriority.high, status=RequirementStatus.accepted, stakeholder="Security Reviewer"),
            ]
        )

        db.add_all(
            [
                ArchitectureDecision(id="ADR-001", project_id=project_id, title="Use PostgreSQL + pgvector for the MVP vector store", context="Customer wants a unified database and vector store with low operational overhead.", decision="Use pgvector for MVP; keep a VectorStoreInterface so Pinecone can be swapped in later.", tradeoffs="Less specialized vector infrastructure than a dedicated vector DB, but far simpler to operate.", status=ArchitectureStatus.accepted),
                ArchitectureDecision(id="ADR-002", project_id=project_id, title="Require human approval before any outbound WhatsApp/email send", context="The assistant can draft customer-facing messages, which carries reputational and compliance risk.", decision="All outbound communication actions are routed through a human-approval workflow node.", tradeoffs="Slower response time for customers, in exchange for compliance and trust.", status=ArchitectureStatus.accepted),
                ArchitectureDecision(id="ADR-003", project_id=project_id, title="Authorize before retrieval, not after", context="A user must never retrieve chunks from documents they are not permitted to see.", decision="Apply document-level access checks before the vector search step, not as a post-filter.", tradeoffs="Slightly more complex query planning, but closes an entire class of data-leak bugs.", status=ArchitectureStatus.accepted),
            ]
        )

        db.add_all(
            [
                Integration(id="int-1", project_id=project_id, name="Company Document Upload", type=IntegrationType.file_upload, status=ConnectionStatus.connected, last_sync=datetime.now(timezone.utc)),
                Integration(id="int-2", project_id=project_id, name="Internal REST API", type=IntegrationType.rest_api, status=ConnectionStatus.connected, last_sync=datetime.now(timezone.utc)),
                Integration(id="int-3", project_id=project_id, name="Support Ticket Webhook", type=IntegrationType.webhook, status=ConnectionStatus.connected, last_sync=datetime.now(timezone.utc)),
                Integration(id="int-4", project_id=project_id, name="Customer Email Inbox", type=IntegrationType.email, status=ConnectionStatus.connected, last_sync=datetime.now(timezone.utc)),
                Integration(id="int-5", project_id=project_id, name="WhatsApp Business API", type=IntegrationType.whatsapp, status=ConnectionStatus.error, last_sync=datetime.now(timezone.utc)),
            ]
        )

        db.add_all(
            [
                DataSource(id="ds-1", project_id=project_id, name="Employee Handbook Repository", kind="Document store", record_count="1,240 docs", status=DataSourceStatus.connected),
                DataSource(id="ds-2", project_id=project_id, name="CRM (customer records)", kind="PostgreSQL", record_count="8,900 rows", status=DataSourceStatus.connected),
                DataSource(id="ds-3", project_id=project_id, name="HR / Operations DB", kind="PostgreSQL", record_count="3,150 rows", status=DataSourceStatus.connected),
                DataSource(id="ds-4", project_id=project_id, name="Legacy ERP export", kind="CSV feed", record_count="Nightly batch", status=DataSourceStatus.disconnected),
            ]
        )

        documents = [
            ("doc-1", "Employee_Handbook_v3.pdf", "HR", DocumentClassification.internal, True),
            ("doc-2", "Travel_and_Expense_Policy.pdf", "Finance", DocumentClassification.internal, True),
            ("doc-3", "Annual_Leave_Policy.pdf", "HR", DocumentClassification.internal, True),
            ("doc-4", "Executive_Compensation_2026.xlsx", "Finance", DocumentClassification.restricted, True),
            ("doc-5", "Client_Onboarding_Runbook.docx", "Operations", DocumentClassification.internal, False),
            ("doc-6", "Support_FAQ_Master.pdf", "Support", DocumentClassification.public, True),
        ]
        provider = get_embedding_provider()
        for doc_id, filename, department, classification, indexed in documents:
            document = KnowledgeDocument(
                id=doc_id,
                project_id=project_id,
                filename=filename,
                department=department,
                classification=classification,
                status=DocumentStatus.indexed if indexed else DocumentStatus.processing,
            )
            db.add(document)
            db.flush()
            if indexed:
                for position, piece in enumerate(chunk_text(DOCUMENT_CONTENT[doc_id])):
                    db.add(
                        DocumentChunk(
                            document_id=doc_id,
                            project_id=project_id,
                            classification=classification,
                            position=position,
                            content=piece,
                            embedding=json.dumps(provider.embed(piece)),
                        )
                    )

        db.add(
            Assistant(
                id="asst-1",
                project_id=project_id,
                name="Company Knowledge Assistant",
                model="claude-sonnet-4-6",
                temperature=0.2,
                knowledge_base="GulfBridge Company Knowledge Base",
                citation_mode=CitationMode.always,
            )
        )

        db.add_all(
            [
                Workflow(id="wf-1", project_id=project_id, name="Support Question Routing", status=WorkflowStatus.active, last_run=datetime.now(timezone.utc), success_rate=96.2),
                Workflow(id="wf-2", project_id=project_id, name="WhatsApp Customer Response", status=WorkflowStatus.active, last_run=datetime.now(timezone.utc), success_rate=88.4),
                Workflow(id="wf-3", project_id=project_id, name="Email Draft & Approval", status=WorkflowStatus.active, last_run=datetime.now(timezone.utc), success_rate=91.7),
                Workflow(id="wf-4", project_id=project_id, name="Weekly Ops Report", status=WorkflowStatus.paused, last_run=datetime.now(timezone.utc), success_rate=100),
            ]
        )

        db.add_all(
            [
                Deployment(id="dep-h1", project_id=project_id, version="v1.9.0", environment=Environment.production, status=DeploymentStatus.healthy, deployed_by="A. Rahman", deployed_at=_dt("2026-09-26 09:12"), commit="8f3c2a1"),
                Deployment(id="dep-h2", project_id=project_id, version="v1.8.2", environment=Environment.staging, status=DeploymentStatus.healthy, deployed_by="A. Rahman", deployed_at=_dt("2026-09-25 17:40"), commit="3b9e0d4"),
                Deployment(id="dep-h3", project_id=project_id, version="v1.8.1", environment=Environment.production, status=DeploymentStatus.degraded, deployed_by="S. Nair", deployed_at=_dt("2026-09-24 11:05"), commit="1a7f6c9"),
                Deployment(id="dep-h4", project_id=project_id, version="v1.8.0", environment=Environment.production, status=DeploymentStatus.healthy, deployed_by="A. Rahman", deployed_at=_dt("2026-09-20 08:30"), commit="d4e2b71"),
                Deployment(id="dep-h5", project_id=project_id, version="v1.7.4", environment=Environment.production, status=DeploymentStatus.healthy, deployed_by="S. Nair", deployed_at=_dt("2026-09-14 10:02"), commit="9a1f0e2"),
            ]
        )

        db.add_all(
            [
                FeedbackEntry(id="fb-1", project_id=project_id, question="What is our travel reimbursement policy?", sentiment=FeedbackSentiment.positive, created_at=datetime.now(timezone.utc)),
                FeedbackEntry(id="fb-2", project_id=project_id, question="How do I reset my company VPN access?", sentiment=FeedbackSentiment.negative, reason="Missing information", created_at=datetime.now(timezone.utc)),
                FeedbackEntry(id="fb-3", project_id=project_id, question="What is the process for requesting annual leave?", sentiment=FeedbackSentiment.positive, created_at=datetime.now(timezone.utc)),
                FeedbackEntry(id="fb-4", project_id=project_id, question="Can you show me executive salaries?", sentiment=FeedbackSentiment.negative, reason="Security concern", created_at=datetime.now(timezone.utc)),
                FeedbackEntry(id="fb-5", project_id=project_id, question="Who approves supplier onboarding?", sentiment=FeedbackSentiment.positive, created_at=datetime.now(timezone.utc)),
            ]
        )

        db.add_all(
            [
                EvaluationRun(id="eval-1", project_id=project_id, version="v1.4", date=datetime(2026, 8, 2, tzinfo=timezone.utc), correctness=86, faithfulness=89, citation_accuracy=82, avg_latency=3.4),
                EvaluationRun(id="eval-2", project_id=project_id, version="v1.5", date=datetime(2026, 8, 20, tzinfo=timezone.utc), correctness=91, faithfulness=93, citation_accuracy=88, avg_latency=3.1),
                EvaluationRun(id="eval-3", project_id=project_id, version="v1.7", date=datetime(2026, 9, 10, tzinfo=timezone.utc), correctness=93, faithfulness=94, citation_accuracy=90, avg_latency=2.9),
                EvaluationRun(id="eval-4", project_id=project_id, version="v1.9", date=datetime(2026, 9, 25, tzinfo=timezone.utc), correctness=95, faithfulness=96, citation_accuracy=93, avg_latency=2.8),
            ]
        )

        db.add_all(
            [
                AuditLogEntry(id="log-1", project_id=project_id, actor="a.rahman@gulfbridge.com", action="PROMPT_UPDATED", resource_type="assistant", resource_id="asst-1", ip_address="10.20.4.11", timestamp=_dt("2026-09-26 09:10")),
                AuditLogEntry(id="log-2", project_id=project_id, actor="a.rahman@gulfbridge.com", action="DEPLOYMENT_STARTED", resource_type="deployment", resource_id="dep-h1", ip_address="10.20.4.11", timestamp=_dt("2026-09-26 09:08")),
                AuditLogEntry(id="log-3", project_id=project_id, actor="system", action="DOCUMENT_UPLOADED", resource_type="document", resource_id="doc-5", ip_address="internal", timestamp=_dt("2026-09-26 08:55")),
                AuditLogEntry(id="log-4", project_id=project_id, actor="s.nair@gulfbridge.com", action="USER_PERMISSION_CHANGED", resource_type="user", resource_id="usr-demo-employee", ip_address="10.20.4.44", timestamp=_dt("2026-09-25 15:20")),
                AuditLogEntry(id="log-5", project_id=None, actor="unknown", action="CROSS_TENANT_ACCESS_BLOCKED", resource_type="organization", resource_id="org-northwind", ip_address="203.0.113.9", timestamp=_dt("2026-09-25 11:02")),
            ]
        )

        db.commit()
        print("Seed complete: GulfBridge Professional Services demo dataset loaded.")
        print(f"Demo accounts (password for both: {DEMO_PASSWORD}):")
        print("  admin    demo.engineer@gulfbridge.example")
        print("  employee employee.demo@gulfbridge.example")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
