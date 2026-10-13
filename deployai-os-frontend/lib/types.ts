export type LifecycleStage =
  | "discovery"
  | "requirements"
  | "architecture"
  | "integrations"
  | "aiConfig"
  | "security"
  | "testing"
  | "deployment"
  | "monitoring"
  | "iteration";

export interface Organization {
  id: string;
  name: string;
  industry: string;
  activeProjects: number;
}

export interface Project {
  id: string;
  name: string;
  organizationId: string;
  customerName: string;
  environment: "development" | "staging" | "production";
  status: "active" | "paused" | "completed";
  currentStage: LifecycleStage;
}

export interface Requirement {
  id: string;
  title: string;
  type: "Functional" | "Non-functional" | "Security" | "Integration" | "AI" | "Operational" | "Compliance";
  priority: "Low" | "Medium" | "High" | "Critical";
  status: "Draft" | "Validated" | "In Development" | "Testing" | "Accepted" | "Rejected";
  stakeholder: string;
}

export interface ArchitectureDecision {
  id: string;
  title: string;
  context: string;
  decision: string;
  tradeoffs: string;
  status: "Proposed" | "Accepted" | "Superseded";
}

export interface IntegrationItem {
  id: string;
  name: string;
  type: "REST API" | "Webhook" | "Email" | "WhatsApp" | "File Upload" | "PostgreSQL";
  status: "connected" | "disconnected" | "error";
  lastSync: string;
}

export interface DataSourceItem {
  id: string;
  name: string;
  kind: string;
  recordCount: string;
  status: "connected" | "disconnected";
}

export interface KnowledgeDocument {
  id: string;
  filename: string;
  department: string;
  classification: "Public" | "Internal" | "Confidential" | "Restricted";
  status: "Uploaded" | "Processing" | "Processed" | "Indexed" | "Failed";
  chunks: number;
}

export interface AssistantConfig {
  id: string;
  name: string;
  model: string;
  temperature: number;
  knowledgeBase: string;
  citationMode: "always" | "when-available";
}

export interface WorkflowItem {
  id: string;
  name: string;
  status: "active" | "paused" | "draft";
  lastRun: string;
  successRate: number;
}

export interface DeploymentRecord {
  id: string;
  version: string;
  environment: "development" | "staging" | "production";
  status: "healthy" | "degraded" | "failed";
  deployedBy: string;
  deployedAt: string;
  commit: string;
}

export interface FeedbackEntry {
  id: string;
  question: string;
  sentiment: "positive" | "negative";
  reason?: string;
  createdAt: string;
}

export interface EvaluationRun {
  id: string;
  version: string;
  date: string;
  correctness: number;
  faithfulness: number;
  citationAccuracy: number;
  avgLatency: number;
}

export interface AuditLogEntry {
  id: string;
  actor: string;
  action: string;
  resourceType: string;
  resourceId: string;
  ipAddress: string;
  timestamp: string;
}
