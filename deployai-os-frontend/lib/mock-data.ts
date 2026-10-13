import type {
  Organization,
  Project,
  Requirement,
  ArchitectureDecision,
  IntegrationItem,
  DataSourceItem,
  KnowledgeDocument,
  AssistantConfig,
  WorkflowItem,
  DeploymentRecord,
  FeedbackEntry,
  EvaluationRun,
  AuditLogEntry,
  LifecycleStage,
} from "./types";

export const organizations: Organization[] = [
  { id: "org-gulfbridge", name: "GulfBridge Professional Services", industry: "Professional Services / Training / Consultancy", activeProjects: 1 },
  { id: "org-northwind", name: "Northwind Retail Group", industry: "Retail", activeProjects: 0 },
];

export const projects: Project[] = [
  {
    id: "proj-gulfbridge-knowledge-ops",
    name: "Enterprise Knowledge & Operations AI",
    organizationId: "org-gulfbridge",
    customerName: "GulfBridge Professional Services",
    environment: "production",
    status: "active",
    currentStage: "iteration",
  },
];

export function getProject(projectId: string): Project {
  return projects.find((p) => p.id === projectId) ?? projects[0];
}

export const lifecycleStages: { id: LifecycleStage; label: string }[] = [
  { id: "discovery", label: "Discovery" },
  { id: "requirements", label: "Requirements" },
  { id: "architecture", label: "Architecture" },
  { id: "integrations", label: "Integrations" },
  { id: "aiConfig", label: "AI Config" },
  { id: "security", label: "Security" },
  { id: "testing", label: "Testing" },
  { id: "deployment", label: "Deployment" },
  { id: "monitoring", label: "Monitoring" },
  { id: "iteration", label: "Iteration" },
];

export const dashboardSummary = {
  activeCustomers: 12,
  activeProjects: 18,
  productionDeployments: 7,
  aiRequests: 42381,
  integrationHealth: 98.8,
  pendingImprovements: 14,
};

export const aiRequestsTrend = [
  { day: "Mon", requests: 4210 },
  { day: "Tue", requests: 4830 },
  { day: "Wed", requests: 5120 },
  { day: "Thu", requests: 4790 },
  { day: "Fri", requests: 5860 },
  { day: "Sat", requests: 3120 },
  { day: "Sun", requests: 2870 },
];

export const recentDeployments: DeploymentRecord[] = [
  { id: "dep-1", version: "v1.9.0", environment: "production", status: "healthy", deployedBy: "A. Rahman", deployedAt: "Today, 09:12", commit: "8f3c2a1" },
  { id: "dep-2", version: "v1.8.2", environment: "staging", status: "healthy", deployedBy: "A. Rahman", deployedAt: "Yesterday, 17:40", commit: "3b9e0d4" },
  { id: "dep-3", version: "v1.8.1", environment: "production", status: "degraded", deployedBy: "S. Nair", deployedAt: "2 days ago", commit: "1a7f6c9" },
];

export const failedWorkflows = [
  { id: "wf-run-1", workflow: "WhatsApp Support Routing", reason: "Webhook timeout", when: "3h ago" },
  { id: "wf-run-2", workflow: "Email Draft & Approval", reason: "Approval step expired", when: "1d ago" },
];

export const securityEvents = [
  { id: "sec-1", label: "Cross-tenant access attempt blocked", severity: "high", when: "5h ago" },
  { id: "sec-2", label: "Unusual login location flagged", severity: "medium", when: "1d ago" },
];

export const requirements: Requirement[] = [
  { id: "REQ-101", title: "Employees can search internal documentation via chat", type: "Functional", priority: "Critical", status: "Accepted", stakeholder: "Ops Director" },
  { id: "REQ-102", title: "Assistant must never reveal restricted documents", type: "Security", priority: "Critical", status: "Accepted", stakeholder: "Security Reviewer" },
  { id: "REQ-103", title: "All AI answers must cite source documents", type: "AI", priority: "High", status: "Accepted", stakeholder: "Compliance" },
  { id: "REQ-104", title: "Support requests routed automatically by category", type: "Operational", priority: "High", status: "In Development", stakeholder: "Support Lead" },
  { id: "REQ-105", title: "WhatsApp responses require human approval before send", type: "Compliance", priority: "Critical", status: "Accepted", stakeholder: "Compliance" },
  { id: "REQ-106", title: "System maintains full audit trail of AI configuration changes", type: "Non-functional", priority: "High", status: "Accepted", stakeholder: "Security Reviewer" },
];

export const architectureDecisions: ArchitectureDecision[] = [
  {
    id: "ADR-001",
    title: "Use PostgreSQL + pgvector for the MVP vector store",
    context: "Customer wants a unified database and vector store with low operational overhead.",
    decision: "Use pgvector for MVP; keep a VectorStoreInterface so Pinecone can be swapped in later.",
    tradeoffs: "Less specialized vector infrastructure than a dedicated vector DB, but far simpler to operate.",
    status: "Accepted",
  },
  {
    id: "ADR-002",
    title: "Require human approval before any outbound WhatsApp/email send",
    context: "The assistant can draft customer-facing messages, which carries reputational and compliance risk.",
    decision: "All outbound communication actions are routed through a human-approval workflow node.",
    tradeoffs: "Slower response time for customers, in exchange for compliance and trust.",
    status: "Accepted",
  },
  {
    id: "ADR-003",
    title: "Authorize before retrieval, not after",
    context: "A user must never retrieve chunks from documents they are not permitted to see.",
    decision: "Apply document-level access checks before the vector search step, not as a post-filter.",
    tradeoffs: "Slightly more complex query planning, but closes an entire class of data-leak bugs.",
    status: "Accepted",
  },
];

export const integrations: IntegrationItem[] = [
  { id: "int-1", name: "Company Document Upload", type: "File Upload", status: "connected", lastSync: "Continuous" },
  { id: "int-2", name: "Internal REST API", type: "REST API", status: "connected", lastSync: "2 min ago" },
  { id: "int-3", name: "Support Ticket Webhook", type: "Webhook", status: "connected", lastSync: "12 min ago" },
  { id: "int-4", name: "Customer Email Inbox", type: "Email", status: "connected", lastSync: "5 min ago" },
  { id: "int-5", name: "WhatsApp Business API", type: "WhatsApp", status: "error", lastSync: "1h ago" },
];

export const dataSources: DataSourceItem[] = [
  { id: "ds-1", name: "Employee Handbook Repository", kind: "Document store", recordCount: "1,240 docs", status: "connected" },
  { id: "ds-2", name: "CRM (customer records)", kind: "PostgreSQL", recordCount: "8,900 rows", status: "connected" },
  { id: "ds-3", name: "HR / Operations DB", kind: "PostgreSQL", recordCount: "3,150 rows", status: "connected" },
  { id: "ds-4", name: "Legacy ERP export", kind: "CSV feed", recordCount: "Nightly batch", status: "disconnected" },
];

export const knowledgeDocuments: KnowledgeDocument[] = [
  { id: "doc-1", filename: "Employee_Handbook_v3.pdf", department: "HR", classification: "Internal", status: "Indexed", chunks: 184 },
  { id: "doc-2", filename: "Travel_and_Expense_Policy.pdf", department: "Finance", classification: "Internal", status: "Indexed", chunks: 42 },
  { id: "doc-3", filename: "Annual_Leave_Policy.pdf", department: "HR", classification: "Internal", status: "Indexed", chunks: 27 },
  { id: "doc-4", filename: "Executive_Compensation_2026.xlsx", department: "Finance", classification: "Restricted", status: "Indexed", chunks: 9 },
  { id: "doc-5", filename: "Client_Onboarding_Runbook.docx", department: "Operations", classification: "Internal", status: "Processing", chunks: 0 },
  { id: "doc-6", filename: "Support_FAQ_Master.pdf", department: "Support", classification: "Public", status: "Indexed", chunks: 63 },
];

export const assistant: AssistantConfig = {
  id: "asst-1",
  name: "Company Knowledge Assistant",
  model: "claude-sonnet-4-6",
  temperature: 0.2,
  knowledgeBase: "GulfBridge Company Knowledge Base",
  citationMode: "always",
};

export const workflows: WorkflowItem[] = [
  { id: "wf-1", name: "Support Question Routing", status: "active", lastRun: "4 min ago", successRate: 96.2 },
  { id: "wf-2", name: "WhatsApp Customer Response", status: "active", lastRun: "12 min ago", successRate: 88.4 },
  { id: "wf-3", name: "Email Draft & Approval", status: "active", lastRun: "1h ago", successRate: 91.7 },
  { id: "wf-4", name: "Weekly Ops Report", status: "paused", lastRun: "3d ago", successRate: 100 },
];

export const deployments: DeploymentRecord[] = [
  { id: "dep-h1", version: "v1.9.0", environment: "production", status: "healthy", deployedBy: "A. Rahman", deployedAt: "2026-09-26 09:12", commit: "8f3c2a1" },
  { id: "dep-h2", version: "v1.8.2", environment: "staging", status: "healthy", deployedBy: "A. Rahman", deployedAt: "2026-09-25 17:40", commit: "3b9e0d4" },
  { id: "dep-h3", version: "v1.8.1", environment: "production", status: "degraded", deployedBy: "S. Nair", deployedAt: "2026-09-24 11:05", commit: "1a7f6c9" },
  { id: "dep-h4", version: "v1.8.0", environment: "production", status: "healthy", deployedBy: "A. Rahman", deployedAt: "2026-09-20 08:30", commit: "d4e2b71" },
  { id: "dep-h5", version: "v1.7.4", environment: "production", status: "healthy", deployedBy: "S. Nair", deployedAt: "2026-09-14 10:02", commit: "9a1f0e2" },
];

export const feedbackEntries: FeedbackEntry[] = [
  { id: "fb-1", question: "What is our travel reimbursement policy?", sentiment: "positive", createdAt: "2h ago" },
  { id: "fb-2", question: "How do I reset my company VPN access?", sentiment: "negative", reason: "Missing information", createdAt: "5h ago" },
  { id: "fb-3", question: "What is the process for requesting annual leave?", sentiment: "positive", createdAt: "1d ago" },
  { id: "fb-4", question: "Can you show me executive salaries?", sentiment: "negative", reason: "Security concern", createdAt: "1d ago" },
  { id: "fb-5", question: "Who approves supplier onboarding?", sentiment: "positive", createdAt: "2d ago" },
];

export const feedbackBreakdown = {
  totalResponses: 1284,
  positivePct: 91.3,
  negativePct: 8.7,
  topIssues: [
    { label: "Missing info", count: 34 },
    { label: "Slow response", count: 21 },
    { label: "Bad citation", count: 9 },
    { label: "Security concern", count: 4 },
  ],
};

export const evaluationRuns: EvaluationRun[] = [
  { id: "eval-1", version: "v1.4", date: "2026-08-02", correctness: 86, faithfulness: 89, citationAccuracy: 82, avgLatency: 3.4 },
  { id: "eval-2", version: "v1.5", date: "2026-08-20", correctness: 91, faithfulness: 93, citationAccuracy: 88, avgLatency: 3.1 },
  { id: "eval-3", version: "v1.7", date: "2026-09-10", correctness: 93, faithfulness: 94, citationAccuracy: 90, avgLatency: 2.9 },
  { id: "eval-4", version: "v1.9", date: "2026-09-25", correctness: 95, faithfulness: 96, citationAccuracy: 93, avgLatency: 2.8 },
];

export const auditLogs: AuditLogEntry[] = [
  { id: "log-1", actor: "a.rahman@gulfbridge.com", action: "PROMPT_UPDATED", resourceType: "assistant", resourceId: "asst-1", ipAddress: "10.20.4.11", timestamp: "2026-09-26 09:10" },
  { id: "log-2", actor: "a.rahman@gulfbridge.com", action: "DEPLOYMENT_STARTED", resourceType: "deployment", resourceId: "dep-h1", ipAddress: "10.20.4.11", timestamp: "2026-09-26 09:08" },
  { id: "log-3", actor: "system", action: "DOCUMENT_UPLOADED", resourceType: "document", resourceId: "doc-5", ipAddress: "internal", timestamp: "2026-09-26 08:55" },
  { id: "log-4", actor: "s.nair@gulfbridge.com", action: "USER_PERMISSION_CHANGED", resourceType: "user", resourceId: "usr-221", ipAddress: "10.20.4.44", timestamp: "2026-09-25 15:20" },
  { id: "log-5", actor: "unknown", action: "CROSS_TENANT_ACCESS_BLOCKED", resourceType: "organization", resourceId: "org-northwind", ipAddress: "203.0.113.9", timestamp: "2026-09-25 11:02" },
];

export const monitoringSeries = {
  latency: [
    { time: "00:00", ms: 1800 }, { time: "04:00", ms: 1700 }, { time: "08:00", ms: 2100 },
    { time: "12:00", ms: 2400 }, { time: "16:00", ms: 2200 }, { time: "20:00", ms: 1900 },
  ],
  errorRate: [
    { time: "00:00", pct: 0.4 }, { time: "04:00", pct: 0.3 }, { time: "08:00", pct: 0.9 },
    { time: "12:00", pct: 1.1 }, { time: "16:00", pct: 0.6 }, { time: "20:00", pct: 0.5 },
  ],
  tokenCost: [
    { day: "Mon", cost: 32.1 }, { day: "Tue", cost: 35.8 }, { day: "Wed", cost: 41.2 },
    { day: "Thu", cost: 38.4 }, { day: "Fri", cost: 44.9 }, { day: "Sat", cost: 21.3 }, { day: "Sun", cost: 18.7 },
  ],
};
