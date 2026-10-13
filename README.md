# DeployAI OS

**A full-stack reference implementation of an enterprise AI deployment platform** — a Next.js workspace UI plus a FastAPI backend with role-aware retrieval-augmented generation (RAG) — built around a fictional customer engagement to show what it takes to carry an AI deployment from discovery through to monitored production.

> **How to read this document.** Behavior described here was checked against the repository's source files and, wherever practical, by running it. The checks, dates, and environment are listed in [Appendix A](#appendix-a-verification-log). Anything that could not be verified is labelled **Not verified**, **To be confirmed**, or **Not implemented**; proposals are labelled as suggestions.

> [!WARNING]
> **This is a demo/reference project, not a production system.** As implemented, anyone who can reach the API can obtain an `admin` token (open self-registration, plus an unauthenticated `POST /auth/demo` endpoint), and authorization never considers which organization a user belongs to. Do not expose the backend to untrusted networks or load real data into it. Details and fixes: [Security and Privacy](#15-security-and-privacy) and [Known Limitations](#19-known-limitations-and-roadmap).

## At a glance

| | |
|---|---|
| **What it is** | Two independently runnable applications in one repository: `frontend/` (Next.js 14 UI over mock data) and `backend/` (FastAPI REST API on SQLite or PostgreSQL). |
| **Core idea** | Retrieval is authorization-aware: document chunks above the caller's clearance are excluded *in the retrieval query itself*, before any similarity scoring ("authorize before retrieval"). |
| **Domain** | A fictional customer, *GulfBridge Professional Services*, and the ten-stage lifecycle of deploying an internal knowledge assistant for it. |
| **Backend** | 33 operations over 27 paths · 16 tables · Alembic migration · 17 automated tests (85% line coverage) |
| **Frontend** | 22 authored routes · 14 project modules · 2 interactive demo widgets · type-checks and builds cleanly · no automated tests |
| **Integration status** | **The frontend does not call the backend.** It renders its own mock data (`frontend/lib/mock-data.ts`). |
| **Project status** | Reference implementation / portfolio project. No releases, no CI, no license file. |

**Quick start** (details in [Getting Started](#6-getting-started)):

```bash
# Terminal 1 — backend (SQLite, no external services needed)
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m app.seed                     # load the demo dataset
uvicorn app.main:app --reload          # API on http://localhost:8000 (interactive docs: /docs)

# Terminal 2 — frontend
cd frontend
npm install
npm run dev                            # UI on http://localhost:3000
```

## Table of Contents

- [1. Project Overview](#1-project-overview)
  - [1.1 What DeployAI OS is](#11-what-deployai-os-is)
  - [1.2 The problem and why it matters](#12-the-problem-and-why-it-matters)
  - [1.3 Objectives and value proposition](#13-objectives-and-value-proposition)
  - [1.4 Target users and use cases](#14-target-users-and-use-cases)
  - [1.5 Key capabilities](#15-key-capabilities)
  - [1.6 Current status: what is real and what is illustrative](#16-current-status-what-is-real-and-what-is-illustrative)
  - [1.7 About the fictional customer and the demo data](#17-about-the-fictional-customer-and-the-demo-data)
- [2. Features](#2-features)
  - [2.1 Frontend (Next.js UI)](#21-frontend-nextjs-ui)
  - [2.2 Backend (FastAPI)](#22-backend-fastapi)
- [3. Technology Stack](#3-technology-stack)
  - [3.1 Backend](#31-backend)
  - [3.2 Data stores and infrastructure](#32-data-stores-and-infrastructure)
  - [3.3 AI and retrieval](#33-ai-and-retrieval)
  - [3.4 Frontend](#34-frontend)
  - [3.5 Not present](#35-not-present)
- [4. Architecture and System Design](#4-architecture-and-system-design)
  - [4.1 High-level architecture](#41-high-level-architecture)
  - [4.2 Backend layering and request lifecycle](#42-backend-layering-and-request-lifecycle)
  - [4.3 Authentication and authorization flow](#43-authentication-and-authorization-flow)
  - [4.4 Data flow](#44-data-flow)
  - [4.5 Error handling and logging](#45-error-handling-and-logging)
  - [4.6 Background jobs and real-time communication](#46-background-jobs-and-real-time-communication)
  - [4.7 Deployment architecture (provided, not executed)](#47-deployment-architecture-provided-not-executed)
- [5. Project Structure](#5-project-structure)
- [6. Getting Started](#6-getting-started)
  - [6.1 Prerequisites](#61-prerequisites)
  - [6.2 Get the code](#62-get-the-code)
  - [6.3 Run the backend (SQLite, zero configuration)](#63-run-the-backend-sqlite-zero-configuration)
  - [6.4 Run the frontend](#64-run-the-frontend)
  - [6.5 Optional: use PostgreSQL](#65-optional-use-postgresql)
  - [6.6 Seed data and demo accounts](#66-seed-data-and-demo-accounts)
  - [6.7 Optional: enable live Claude replies](#67-optional-enable-live-claude-replies)
- [7. Configuration](#7-configuration)
  - [7.1 Backend environment variables](#71-backend-environment-variables)
  - [7.2 Docker Compose variables (`backend/docker-compose.yml`)](#72-docker-compose-variables-backenddocker-composeyml)
  - [7.3 Frontend](#73-frontend)
- [8. Using the Application](#8-using-the-application)
  - [8.1 Frontend tour](#81-frontend-tour)
  - [8.2 Backend: interactive documentation](#82-backend-interactive-documentation)
  - [8.3 Backend: the "authorize before retrieval" walkthrough with cURL](#83-backend-the-authorize-before-retrieval-walkthrough-with-curl)
  - [8.4 Role-specific workflows](#84-role-specific-workflows)
  - [8.5 When something goes wrong](#85-when-something-goes-wrong)
  - [8.6 Ending a session](#86-ending-a-session)
- [9. Roles and Permissions](#9-roles-and-permissions)
  - [9.1 Roles](#91-roles)
  - [9.2 Retrieval clearance (the only role-dependent behavior)](#92-retrieval-clearance-the-only-role-dependent-behavior)
  - [9.3 Endpoint permissions](#93-endpoint-permissions)
  - [9.4 Authentication versus authorization](#94-authentication-versus-authorization)
- [10. API Reference](#10-api-reference)
  - [10.1 Conventions](#101-conventions)
  - [10.2 Endpoint summary](#102-endpoint-summary)
  - [10.3 Allowed values](#103-allowed-values)
  - [10.4 Verified examples](#104-verified-examples)
- [11. Database Design and Data Model](#11-database-design-and-data-model)
  - [11.1 Overview](#111-overview)
  - [11.2 Entity-relationship diagram](#112-entity-relationship-diagram)
  - [11.3 Tables and columns](#113-tables-and-columns)
  - [11.4 Constraints, validation, and ORM behavior](#114-constraints-validation-and-orm-behavior)
  - [11.5 Migrations](#115-migrations)
  - [11.6 Seeding](#116-seeding)
- [12. Core Business Logic and Workflows](#12-core-business-logic-and-workflows)
  - [12.1 Registration and token issuance](#121-registration-and-token-issuance)
  - [12.2 Retrieval and authorization](#122-retrieval-and-authorization)
  - [12.3 Knowledge ingestion](#123-knowledge-ingestion)
  - [12.4 Assistant chat](#124-assistant-chat)
  - [12.5 Workflow runs, rollbacks, and evaluation runs](#125-workflow-runs-rollbacks-and-evaluation-runs)
- [13. Development Commands](#13-development-commands)
  - [13.1 Backend (run from `backend/`)](#131-backend-run-from-backend)
  - [13.2 Frontend (run from `frontend/`)](#132-frontend-run-from-frontend)
- [14. Testing and Quality Assurance](#14-testing-and-quality-assurance)
  - [14.1 Strategy and setup](#141-strategy-and-setup)
  - [14.2 Test inventory (17 tests)](#142-test-inventory-17-tests)
  - [14.3 Coverage](#143-coverage)
  - [14.4 Not covered by automated tests](#144-not-covered-by-automated-tests)
  - [14.5 Known warnings in the test output](#145-known-warnings-in-the-test-output)
- [15. Security and Privacy](#15-security-and-privacy)
  - [15.1 Implemented controls](#151-implemented-controls)
  - [15.2 Gaps (verified, or evident from the code)](#152-gaps-verified-or-evident-from-the-code)
  - [15.3 Handling secrets](#153-handling-secrets)
  - [15.4 Privacy](#154-privacy)
- [16. Integrations and External Services](#16-integrations-and-external-services)
  - [16.1 Anthropic Messages API (optional)](#161-anthropic-messages-api-optional)
  - [16.2 PostgreSQL](#162-postgresql)
  - [16.3 pgvector](#163-pgvector)
  - [16.4 Redis](#164-redis)
  - [16.5 Frontend ↔ backend](#165-frontend--backend)
- [17. Deployment and Production](#17-deployment-and-production)
  - [17.1 What exists and what was verified](#171-what-exists-and-what-was-verified)
  - [17.2 Production checklist (recommendations, none implemented)](#172-production-checklist-recommendations-none-implemented)
  - [17.3 Frontend hosting](#173-frontend-hosting)
- [18. Troubleshooting and FAQ](#18-troubleshooting-and-faq)
  - [FAQ](#faq)
- [19. Known Limitations and Roadmap](#19-known-limitations-and-roadmap)
  - [19.1 Known limitations](#191-known-limitations)
  - [19.2 Roadmap (suggestions, not commitments)](#192-roadmap-suggestions-not-commitments)
- [20. Contributing](#20-contributing)
- [21. License, Credits, and Contact](#21-license-credits-and-contact)
- [Appendix A. Verification Log](#appendix-a-verification-log)


---

## 1. Project Overview

### 1.1 What DeployAI OS is

DeployAI OS simulates the working surface of a *forward-deployed engineering* engagement: the artifacts and decisions that accumulate while an AI assistant is taken from a customer's first workshop to a monitored production deployment. It has two halves that share one domain model (same customer, same record IDs, same field names):

- **`frontend/`** — a Next.js workspace with a dashboard and a 14-module project view (overview, discovery, requirements, architecture decisions, integrations, data sources, knowledge base, assistants, workflows, deployments, monitoring, feedback, evaluations, audit). It runs entirely on in-repo mock data.
- **`backend/`** — a FastAPI service with JWT authentication, a project data model, a lightweight RAG pipeline (chunking, embeddings, vector search), an optional call to Anthropic's Claude API, and audit logging.

### 1.2 The problem and why it matters

Most AI demonstrations stop at "a chatbot over some documents". In an enterprise deployment the harder questions sit *around* the model: Who is allowed to retrieve which document? What does the assistant do when someone asks for something above their clearance? How is a bad release rolled back? Can any of it be audited afterwards? Where is the evidence that quality is improving between versions?

This project puts those concerns in one codebase so they can be read, run, and criticised. Its centerpiece is a concrete, tested version of one of them — classification-aware retrieval — documented in [§2.2.2](#222-authorization-aware-retrieval-the-centerpiece) and [§12](#12-core-business-logic-and-workflows).

### 1.3 Objectives and value proposition

1. **Show the whole lifecycle in one navigable workspace** (frontend), from discovery to iteration.
2. **Provide a working, tested example of authorization-aware retrieval** (backend), including the case where it refuses to answer.
3. **Offer a readable reference layout** for a FastAPI + SQLAlchemy + Alembic service and a Next.js App Router frontend that share a data contract (camelCase JSON matching the frontend's TypeScript interfaces).
4. **Be explicit about what is simulated.** Workflow runs and evaluation runs are simulated; embeddings are a lightweight hashing technique; the frontend is not connected to the backend. See [§1.6](#16-current-status-what-is-real-and-what-is-illustrative).

### 1.4 Target users and use cases

**Intended audience:** engineers and technical reviewers who want to see how such a platform can be structured; developers looking for a starting point; and the project author, as a portfolio piece. It is **not** intended for end customers or production use.

**Main use cases**

| # | Use case | Where |
|---|---|---|
| 1 | Walk through the lifecycle of a deployment as a set of linked records | Frontend project workspace |
| 2 | Demonstrate "authorize before retrieval": the same question gets an answer for one role and a refusal for another | Backend `POST …/knowledge/search` and `POST …/assistants/chat`; frontend widgets (simulated) |
| 3 | Study or reuse the FastAPI/SQLAlchemy/Alembic structure, including a swappable vector-store interface | `backend/app/` |
| 4 | Use as scaffolding for a real platform (after addressing [§19](#19-known-limitations-and-roadmap)) | Whole repository |

### 1.5 Key capabilities

- Classification-aware retrieval with three roles and four document classifications, enforced in the retrieval query ([§2.2.2](#222-authorization-aware-retrieval-the-centerpiece)).
- A self-contained RAG pipeline — paragraph chunking, hashing-trick embeddings, cosine ranking — that needs no external services.
- Optional grounded answers from Claude when `ANTHROPIC_API_KEY` is set, with a deterministic offline fallback and a `generatedBy` field that tells clients which path produced a reply.
- An audit trail for selected actions ([§2.2.9](#229-audit-log)).
- The same code runs on SQLite (default) and PostgreSQL 16 (verified); schema managed by Alembic.
- A consistent JSON contract: camelCase on the wire, enum values identical to the frontend's string unions.

### 1.6 Current status: what is real and what is illustrative

| Area | Status | Evidence / notes |
|---|---|---|
| Backend REST API | **Implemented** | 33 operations; every route group exercised against a live server on SQLite and on PostgreSQL 16 ([Appendix A](#appendix-a-verification-log)). |
| Authorization-aware retrieval | **Implemented; partly covered by tests** | Automated tests cover the keyword layer and the admin/employee outcomes. The SQL-level filter and the `manager` role were verified by manual runs on SQLite and PostgreSQL; there is no dedicated automated test for them yet. |
| Embeddings | **Implemented (lightweight)** | Feature hashing over ASCII words, 256 dimensions. Weak semantics; non-ASCII scripts (e.g. Arabic) produce empty vectors. |
| Claude integration | **Implemented; never run live** | No API key was available during development; only the offline fallback is exercised by tests. |
| Workflow and evaluation runs | **Simulated** | Random outcome / nudged metrics; no real execution or evaluation harness. |
| Frontend UI | **Implemented over mock data** | `npm run typecheck` and `npm run build` succeed; all 22 authored routes return the expected content from the production build. Not exercised in a browser. |
| Frontend ↔ backend | **Not implemented** | The frontend makes no network calls. |
| Authentication in the UI | **Not implemented** | Login/register forms validate input and navigate; no session exists. |
| Docker Compose | **Provided; not executed** | No Docker daemon was available. The equivalent steps (migrate, seed, serve) were verified against a native PostgreSQL 16 install. |
| Redis | **Provisioned; unused** | Present in `docker-compose.yml`; no application code reads it. |
| pgvector | **Not wired in** | Extension verified in an ad-hoc test; the repository's `PgVectorStore` class fails as written ([§16](#16-integrations-and-external-services)). |
| CI/CD, linting, frontend tests | **Not implemented** | — |

### 1.7 About the fictional customer and the demo data

*GulfBridge Professional Services* is invented for this project; so are all people, e-mail addresses (on `.example` or illustrative domains), figures, and policies. The two halves carry **different illustrative policy text** (for example the frontend's leave policy says 22 days and 5 business days' notice, while the backend's seeded document says 24 days and two weeks' notice), because they were authored separately and are not connected.

---

## 2. Features

Each feature below is described the same way: **What** it does, **Why** it exists, **How** it works, **Who** can use it, its **Inputs → outputs**, the **Rules** it enforces, and its **Limitations**.

### 2.1 Frontend (Next.js UI)

#### 2.1.1 Authentication screens

- **What:** `/login` and `/register` forms. `/` redirects to `/login`: the root page is prerendered, so it answers with HTTP 307 and a body carrying a `NEXT_REDIRECT … /login` instruction instead of a `Location` header. The Next.js client runtime is expected to perform the navigation in a browser (not verified in a browser); `curl` does not follow it.
- **Why:** Mirror the entry points of a real product and demonstrate schema-validated forms.
- **How:** React Hook Form with Zod (`@hookform/resolvers/zod`). *Login:* valid e-mail, password ≥ 6 characters. *Register:* name ≥ 2, valid e-mail, organization ≥ 2, password ≥ 6, confirmation must match. A valid submit calls `router.push("/dashboard")`; the **Continue as Demo Engineer** button does the same without validation.
- **Who:** anyone.
- **Inputs → outputs:** form fields → inline validation messages, or navigation to the dashboard.
- **Limitations:** **No request is sent and no session, token, or cookie is created.** There is no `middleware.ts`, so `(app)` routes such as `/dashboard` are reachable without "logging in".

#### 2.1.2 App shell, dashboard, and organization pages

- **What:** A sidebar (Dashboard, Organizations, Projects, Settings), a topbar (static customer name, a bell icon with no action, static user "Demo Engineer"), and four top-level pages.
- **How:** All data comes from `lib/mock-data.ts`.
  - **Dashboard** — six stat cards (Active Customers 12, Active Projects 18, Production Deployments 7, AI Requests (7d) 42,381, Integration Health 98.8%, Pending Improvements 14), a request-volume line chart, and lists of recent deployments, failed workflow runs, and security events.
  - **Organizations** — two cards (GulfBridge, Northwind Retail Group).
  - **Projects** — one project, linking into its workspace.
  - **Settings** — read-only organization fields, four static security rows, and a masked API key with a **Regenerate** button.
- **Limitations:** The dashboard figures are static numbers, not derived from the other mock data (12 "customers" versus two listed organizations). The **New Organization**, **Regenerate**, and deployment **Rollback** buttons have no handler.

#### 2.1.3 Project workspace (14 modules)

`/projects/<projectId>/<module>` renders a header (project name, environment and status badges, customer) and 14 tabs. Any project id resolves to the same GulfBridge project (`getProject` falls back to the first project), and `/projects/<projectId>` redirects to `overview`.

| Module | What it shows | Source |
|---|---|---|
| Overview | Ten-stage lifecycle stepper (current stage: Iteration), project summary, five-layer architecture sketch | `lifecycleStages`, `getProject()`; layers hard-coded in the page |
| Discovery | Eight finding cards (goal, process, pain points, users, systems, constraints, security, metrics) and a five-step timeline | Hard-coded in the page |
| Requirements | Table of 6 requirements with priority/status badges | `requirements` |
| Architecture | Three Architecture Decision Records (ADR-001 to ADR-003) with context, decision, trade-offs | `architectureDecisions` |
| Integrations | Five connection cards with status (one in `error`) | `integrations` |
| Data Sources | Table of 4 sources | `dataSources` |
| Knowledge | Table of 6 documents with classification and status, plus the retrieval tester ([§2.1.4](#214-knowledge-retrieval-tester-interactive)) | `knowledgeDocuments` + widget |
| Assistants | Assistant configuration card plus the chat preview ([§2.1.5](#215-assistant-chat-preview-interactive)) | `assistant` + widget |
| Workflows | Static eight-step "approval-gated WhatsApp response" diagram and a table of 4 workflows | Steps hard-coded; `workflows` |
| Deployments | Production/staging/development cards and a release history table | `deployments` |
| Monitoring | Latency and error-rate line charts, token-cost bar chart | `monitoringSeries` |
| Feedback | Three stat cards, a top-issues chart, recent feedback | `feedbackBreakdown`, `feedbackEntries` |
| Evaluations | Latest-run metric cards and a version-over-version table (v1.4 → v1.9) | `evaluationRuns` |
| Audit | Table of 5 audit events | `auditLogs` |

All modules are read-only. The Development environment card shows "No pipeline deployments" because no mock deployment targets it.

#### 2.1.4 Knowledge retrieval tester (interactive)

- **What:** A search box on the Knowledge tab that shows ranked chunks with scores, or an "Access denied before retrieval" panel.
- **Why:** Make the authorize-before-retrieval idea tangible without a backend.
- **How:** `runMockRetrieval` in `components/knowledge-search-tester.tsx` lower-cases the query and applies **first-match-wins substring rules**: (1) `leave` / `vacation` / `pto` → two leave-policy chunks; (2) `travel` / `reimburs` / `expense` → two travel-policy chunks; (3) `salary` / `compensation` / `executive` → restricted refusal; (4) anything else → one generic demo chunk. Submit with the button or Enter; blank input is ignored.
- **Who:** anyone. **Inputs → outputs:** query text → hard-coded chunks and scores.
- **Limitations:** Nothing is retrieved — results are canned and scores are fixed. Substring matching has false positives (`pto` also matches *laptop*), and rule order matters (*"executive travel expenses"* matches the travel rule, not the restriction). The refusal rule has no `payroll` trigger, unlike the backend. The same stand-in user is always used.

#### 2.1.5 Assistant chat preview (interactive)

- **What:** A chat panel on the Assistants tab that answers with citations or refuses.
- **How:** `mockAssistantReply` in `components/assistant-chat-preview.tsx` uses the same rule order as the tester, appends the user message and a canned reply immediately (no network), and shows a document/section citation or a "Blocked by document-level authorization" label. The fallback reply says it could not find a confident answer.
- **Who / inputs → outputs / limitations:** as above; conversation state is local to the page and lost on reload.

### 2.2 Backend (FastAPI)

#### 2.2.1 Accounts and authentication

- **What:** Register, log in, log in as the demo user, and look up the current user.
- **Why:** Identify the caller so role-dependent rules can be applied.
- **How:** Passwords are hashed with `bcrypt`. Access tokens are HS256 JWTs carrying `sub` (user id), `role`, and `exp` (default 60 minutes). `get_current_user` (`app/core/deps.py`) validates the bearer token and **reloads the user from the database on every request**, so a role change takes effect immediately without a new token.
- **Who:** `POST /auth/register`, `POST /auth/login`, `POST /auth/demo` are public; `GET /auth/me` needs a token.
- **Inputs → outputs:** register `{name, email, organization, password}` → `201` + `{accessToken, tokenType, user}`; login `{email, password}` → `200` + the same shape; demo (no body) → `200` + token for the seeded admin; me → the user.
- **Rules:** duplicate e-mail → `409`. The first account registered under a **new** organization name becomes `admin` (the organization is created with industry "Unspecified"). Registering under an **existing** name (case-insensitive) joins that organization as `employee`. Nothing in the API assigns the `manager` role; it can only be set in the database.
- **Limitations:** e-mail format is not validated; there is no password policy; passwords longer than 72 bytes cause an unhandled `500` with the `bcrypt` 5.x series observed here; there is no refresh, logout, or revocation; `POST /auth/demo` returns an **admin** token without credentials; organization matching uses `ILIKE` without escaping, so `Gulf%` matched GulfBridge in testing; and every new-organization registration yields an admin.

#### 2.2.2 Authorization-aware retrieval (the centerpiece)

- **What:** Given a question, return up to three ranked chunks the caller may see, or a refusal.
- **Why:** An assistant must not surface text above a user's clearance. The design decision is recorded as ADR-003 in the seed data: *authorize before retrieval, not after.*
- **How:** Implemented in `app/services/rag.py` and `app/services/vector_store.py` in two deliberately redundant layers (flow in [§12.2](#122-retrieval-and-authorization)):
  1. **Keyword guard.** If the lower-cased query contains `salary`, `compensation`, `executive`, or `payroll` and the user's role is not cleared for *Restricted*, return `restricted: true` with a message and run no search (audited as `RETRIEVAL_BLOCKED_UNAUTHORIZED` by the search endpoint and `ASSISTANT_CHAT_BLOCKED` by chat).
  2. **Query-level filter.** The vector-store query selects only chunks of the requested project whose `classification` is in the role's allowed set. Higher-classified chunks are never loaded or scored.
  The remaining candidates are scored by cosine similarity in Python, sorted, truncated to the top 3, and any with a non-positive score are dropped.
- **Who:** any authenticated user; clearance is decided by role ([§9](#9-roles-and-permissions)).
- **Inputs → outputs:** `{query}` → `{restricted, message, chunks:[{chunkId, documentFilename, classification, content, score}]}`.
- **Rules:** `admin` → all four classifications; `manager` → Public, Internal, Confidential; `employee` → Public, Internal.
- **Limitations:** the keyword guard is coarse (an employee asking about the leave policy for *executive assistants* was refused); authorization is **by role only — not by organization or project membership** (a user from another organization retrieved GulfBridge data in testing); there is no relevance threshold, so even a nonsense query returns three low-scoring chunks; the document *list* endpoint is not filtered by classification, so restricted filenames are visible to every authenticated user.

#### 2.2.3 Knowledge ingestion

- **What:** Upload a text file with a department and a classification; it is chunked, embedded, and indexed.
- **How:** Multipart upload; the whole file is read into memory and decoded as UTF-8 (otherwise `400`). Paragraphs (split on blank lines) are grouped into chunks of at most 600 characters; a single longer paragraph is word-wrapped. Each chunk is embedded (see *Embeddings* below) and stored as JSON text together with a copy of the document's classification. The document moves to `Indexed` (or `Processed` when it produced no chunks) within the same request.
- **Embeddings:** `app/services/embeddings.py` lower-cases the text, extracts words matching `[a-zA-Z0-9']+`, hashes each word with MD5 into one of 256 buckets, counts, and L2-normalizes. The default provider is deterministic and dependency-free; `EmbeddingProvider` is the seam for a real model.
- **Who:** any authenticated user, with any classification (there is no role check on upload).
- **Inputs → outputs:** file + `department` + `classification` (default `Internal`) → `{document, chunksCreated}`.
- **Limitations:** plain text only (the seeded filenames end in `.pdf`/`.xlsx`/`.docx`, but no parsing exists); no size limit; processing is synchronous; ASCII-only tokenization means **Arabic or other non-Latin text embeds to a zero vector and is indexed but can never be retrieved** (verified); the `Uploaded` and `Failed` statuses are defined but never set by code; the top-ranked chunk for "How many annual leave days do I get?" was the carry-over chunk rather than the accrual chunk in the example run ([§10](#10-api-reference)), illustrating the weak semantics of hashing embeddings.

#### 2.2.4 Assistant chat

- **What:** Answer a question using retrieved chunks, citing the sources.
- **How:** `POST …/assistants/chat` runs the same retrieval as [§2.2.2](#222-authorization-aware-retrieval-the-centerpiece). A restricted outcome returns the refusal text directly (the model is never called). Otherwise, with `ANTHROPIC_API_KEY` set, `app/services/llm.py` posts to the Anthropic Messages API with a system prompt that contains the numbered passages and instructs the model to answer only from them and cite them; any `httpx.HTTPError` falls back silently to the offline reply. Without a key the reply is `"Based on <filename>: <top chunk text>"`. The response's `generatedBy` is `"claude"` only when the API call succeeded, otherwise `"mock"`.
- **Who:** any authenticated user. **Inputs → outputs:** `{message}` → `{reply, restricted, sources[], generatedBy}`.
- **Limitations:** the live Claude path has **never been executed** here; the model name (`claude-sonnet-4-6`), `max_tokens` (500) and timeout (20 s) are constants in `llm.py`; the stored assistant configuration (model, temperature, citation mode, knowledge base) is returned by `GET …/assistants` but **is not read by the chat endpoint**; only `httpx.HTTPError` is caught (a malformed API response would surface as a `500`); with no relevant chunk the offline reply still quotes the best low-scoring chunk.

#### 2.2.5 Project records

- **What:** Organizations (read), projects (list/get/create), and per-project requirements, architecture decisions, integrations, data sources, and feedback (list/create).
- **Why:** The records a deployment team accumulates; they back the frontend modules of the same names.
- **How:** Thin routers in `app/routers/` validate request bodies with Pydantic enums and write SQLAlchemy models. `OrganizationOut.activeProjects` is computed (count of `active` projects). A new project gets id `proj-<slug>-<6 hex>`, belongs to the caller's organization, starts `active` at stage `discovery`, and is audited (`PROJECT_CREATED`).
- **Who:** any authenticated user — **no endpoint checks roles** (`require_role` exists in `app/core/deps.py` but is not used anywhere).
- **Limitations:** no update or delete endpoints and no pagination; the project id in nested paths is **not validated** — posting to a nonexistent project creates an orphan row on SQLite (foreign keys are not enforced there) and fails with an unhandled `500` on PostgreSQL.

#### 2.2.6 Workflow runs (simulated)

- **What:** List workflows, trigger a run, and list a workflow's run history.
- **How:** `POST …/workflows/{id}/run` draws a random number and succeeds with probability equal to the workflow's `successRate`; it appends a `WorkflowRun` with a fixed message, sets `lastRun`, promotes a `draft` workflow to `active`, and updates `successRate` as a running average over the *stored* runs. Audited as `WORKFLOW_RUN_SUCCEEDED` / `WORKFLOW_RUN_FAILED`.
- **Limitations:** nothing real executes. Because seeded workflows have no run history, **the first run replaces the seeded rate with 100.0 or 0.0** (seeded 96.2 → 100.0 in testing). A `paused` workflow can still be run and stays paused. There is no endpoint to create or edit a workflow.

#### 2.2.7 Deployments and rollback

- **What:** List deployment records and "roll back" to an earlier one.
- **How:** Rollback does not mutate history; it appends a new `healthy` record that copies the target's version, environment, and commit, with `deployedBy` set to the caller's display name. Audited as `DEPLOYMENT_ROLLED_BACK`.
- **Limitations:** nothing is deployed; any record can be the target (including a `failed` one, and one that is already current).

#### 2.2.8 Evaluation runs (simulated)

- **What:** List evaluation runs (oldest first) and add a new one.
- **How:** `POST …/evaluations/run` takes the latest run by date and raises correctness, faithfulness, and citation accuracy by a random 0.1–1.2 points (capped at 99.5), lowers average latency by up to 0.15 s (floor 0.6), and increments the last version segment (`v1.9` → `v1.10`). With no prior run it starts from 85.0 / 88.0 / 90.0 / 2.4 s as `v1.0`.
- **Limitations:** the numbers are invented; no evaluation harness exists. Not audited.

#### 2.2.9 Audit log

- **What:** An append-only list of selected actions, newest first.
- **How:** `app/core/audit.py::log_action` writes `actor` (the user's **display name**), `action`, `resourceType`, `resourceId`, `ipAddress`, `timestamp`. Audited actions: `PROJECT_CREATED`, `DOCUMENT_UPLOADED`, `RETRIEVAL_BLOCKED_UNAUTHORIZED`, `ASSISTANT_CHAT`, `ASSISTANT_CHAT_BLOCKED`, `WORKFLOW_RUN_SUCCEEDED`, `WORKFLOW_RUN_FAILED`, `DEPLOYMENT_ROLLED_BACK`.
- **Who:** any authenticated user can read any project's log.
- **Limitations:** `ipAddress` is **always `127.0.0.1`** (callers never pass the request address); registration/login, record creation (requirements, ADRs, integrations, data sources), feedback, evaluation runs, and *successful* searches are not logged; chat messages and blocked queries are stored (first 120 characters) in `resourceId` and are readable through this endpoint; entries are not protected against modification at the database level (the API has no update/delete, but nothing in the schema enforces immutability).

#### 2.2.10 Platform plumbing

`GET /health` returns `{"status":"ok"}`. Interactive OpenAPI docs are served at `/docs` (Swagger UI) and `/redoc`, with the schema at `/openapi.json`. CORS allows the origins in `CORS_ORIGINS` (default `http://localhost:3000`). Tables are created at startup (`Base.metadata.create_all`) *and* defined by an Alembic migration; `python -m app.seed` loads the demo dataset idempotently.

---

## 3. Technology Stack

Backend versions are those resolved by a **clean** `pip install -r requirements-dev.txt` in a fresh virtual environment during verification; `requirements.txt` only sets minimum versions (`>=`), so a later install may resolve newer releases. Frontend versions come from `package-lock.json` (`npm ls`).

### 3.1 Backend

| Technology | Version | Role | Where it is used |
|---|---|---|---|
| Python | 3.12.3 tested (3.10+ required by the code's `X \| None` annotations) | Runtime | Everything under `backend/` |
| FastAPI | 0.143.0 | Web framework: routing, dependency injection, request validation, OpenAPI docs | `app/main.py`, `app/routers/*` |
| Starlette | 1.7.0 (transitive) | ASGI toolkit beneath FastAPI; CORS middleware and the test client | `app/main.py`, `tests/conftest.py` |
| Uvicorn (`uvicorn[standard]`) | 0.54.0 | ASGI server | Run commands, `Dockerfile` `CMD` |
| Pydantic | 2.14.0 | Request/response schemas; camelCase aliasing via `alias_generator=to_camel` | `app/schemas/*` |
| pydantic-settings | 2.15.0 | Typed settings from environment variables and `.env` | `app/config.py` |
| SQLAlchemy | 2.1.4 | ORM using 2.0-style typed models (`Mapped`, `mapped_column`) | `app/models/*`, `app/database.py` |
| Alembic | 1.20.0 | Schema migrations (one initial migration) | `alembic/` |
| PyJWT | 2.15.1 | Encode/decode HS256 access tokens | `app/core/security.py` |
| bcrypt | 5.0.0 | Password hashing | `app/core/security.py` |
| python-multipart | 0.0.32 | Multipart form parsing for file upload | `POST …/knowledge/upload` |
| httpx | 0.28.1 | HTTP client for the Anthropic API; also required by the test client | `app/services/llm.py`, tests |
| psycopg2-binary | 2.9.13 | PostgreSQL driver (only used when `DATABASE_URL` is a PostgreSQL URL) | `app/database.py` via SQLAlchemy |
| pytest / pytest-cov | 9.1.1 / 7.1.0 | Test runner and coverage | `tests/` |

> **Declared but unused in application code:** `email-validator` (no `EmailStr` fields exist) and the `pgvector` Python package (the reference `PgVectorStore` issues raw SQL instead). They can be removed from `requirements.txt` or put to use.

### 3.2 Data stores and infrastructure

| Technology | Version | Role | Status |
|---|---|---|---|
| SQLite | bundled with Python | Default database (`sqlite:///./deployai.db`, relative to the working directory) | Verified (tests and live API) |
| PostgreSQL | 16.15 (native install used for verification) | Production-style database | Migration, seed, and live API verified; **Compose image not run** |
| pgvector extension | 0.6.0 (verified ad hoc) | Vector similarity in PostgreSQL | **Not used by the application** ([§16](#16-integrations-and-external-services)) |
| Redis | `redis:7-alpine` in Compose | — | **Provisioned but unused**: no application code reads it |
| Docker / Docker Compose | — | `backend/Dockerfile` (`python:3.12-slim`) and `backend/docker-compose.yml` (`db`, `redis`, `api`) | **Provided; not executed** (no Docker daemon available) |

### 3.3 AI and retrieval

| Technology | Role | Where | Status |
|---|---|---|---|
| Anthropic Messages API (`https://api.anthropic.com/v1/messages`, header `anthropic-version: 2023-06-01`, model `claude-sonnet-4-6`) | Optional grounded, cited answers | `app/services/llm.py` | Implemented; **never executed live** |
| Feature-hashing embeddings (stdlib `hashlib`, 256 dimensions) | Deterministic text vectors with no external service | `app/services/embeddings.py` | Verified; weak semantics, ASCII-only |
| In-memory cosine vector store | Scores pre-filtered chunks in Python | `app/services/vector_store.py` | Verified (default) |
| `PgVectorStore` | Reference SQL for pgvector | `app/services/vector_store.py` | **Fails as written**; not wired in |

### 3.4 Frontend

| Technology | Version | Role | Where it is used |
|---|---|---|---|
| Node.js | 22.22.2 tested (Next.js 14.2.35 requires ≥ 18.17.0) | Runtime for build/dev/serve | — |
| Next.js (App Router) | 14.2.35 | Framework: routing, layouts, server rendering | `frontend/app/` |
| React / react-dom | 18.3.1 | UI library | `frontend/app/`, `frontend/components/` |
| TypeScript | 5.9.3 (`^5.4.5` in `package.json`) | Static typing; `npm run typecheck` runs `tsc --noEmit` | whole frontend |
| Tailwind CSS (+ PostCSS 8.5.28, Autoprefixer 10.6.1) | 3.4.19 | Styling; custom `brand` colour scale in `tailwind.config.ts` | `app/globals.css`, class names |
| Recharts | 2.15.4 | Line and bar charts | `components/charts/*` |
| lucide-react | 0.383.0 | Icons | components and pages |
| React Hook Form / Zod / @hookform/resolvers | 7.89.0 / 3.25.76 / 3.10.0 | Form state and schema validation | `app/login`, `app/register` |
| clsx / tailwind-merge | 2.1.1 / 2.6.1 | Class-name composition (`cn` helper) | `lib/utils.ts` |

The UI primitives in `components/ui/*` are hand-written, shadcn-style components — the shadcn CLI is **not** used. There is no data-fetching or state-management library, no ESLint/Prettier configuration (the build sets `eslint.ignoreDuringBuilds: true`), and no test runner.

### 3.5 Not present

Background workers or queues, WebSockets/real-time channels, scheduled jobs, a frontend Dockerfile, CI/CD configuration, and any observability stack (metrics, tracing, structured logging).

---

## 4. Architecture and System Design

### 4.1 High-level architecture

```mermaid
flowchart LR
    user(["Browser"]) --> fe["frontend/ Next.js 14<br/>mock data in lib/mock-data.ts"]
    fe -. "no network calls today" .-> api
    tools(["curl, Swagger UI, pytest"]) --> api["backend/ FastAPI<br/>app.main:app"]
    api --> db[("SQLite default<br/>or PostgreSQL 16")]
    api -. "optional: only if ANTHROPIC_API_KEY is set" .-> claude["Anthropic Messages API"]
```

**Responsibilities**

| Component | Responsibility | Does *not* do |
|---|---|---|
| `frontend/` | Render pages from in-repo mock data; client-side form validation; two client-side demo widgets | Call the API, hold a session, protect routes |
| `backend/` | Authentication, all domain logic, persistence, retrieval and authorization, audit logging | Run background jobs, parse PDFs/DOCX, call anything except the optional Anthropic API |
| Database | Single source of truth for the backend | — |
| Anthropic API (optional) | Generate a cited answer from retrieved passages | Participate in authorization (restricted queries never reach it) |

### 4.2 Backend layering and request lifecycle

```mermaid
flowchart TB
    req(["HTTP request"]) --> cors["CORSMiddleware"]
    cors --> router["Router in app/routers/<br/>Pydantic validates the body"]
    router --> dep["Depends get_current_user<br/>decode JWT, load user from DB"]
    router --> svc["Services in app/services/<br/>rag, vector_store, embeddings, chunking, llm"]
    router --> audit["core/audit.log_action"]
    dep --> models["SQLAlchemy models in app/models/"]
    svc --> models
    audit --> models
    models --> db[("SQLite or PostgreSQL")]
    svc -. optional .-> claude["Anthropic API"]
```

1. `CORSMiddleware` answers browser pre-flight requests and adds CORS headers for the configured origins.
2. A router function receives the request. FastAPI validates path/query/body against Pydantic schemas; failures become `422` responses.
3. Protected routes declare `Depends(get_current_user)`, which decodes the bearer token, loads the user row, and raises `401` on any failure.
4. Simple resources are handled directly in the router. Retrieval and chat are delegated to `app/services/`.
5. Each request gets its own SQLAlchemy session from `get_db` (`autoflush=False`, `autocommit=False`); routers commit explicitly and the session is closed afterwards.
6. Responses are serialized by the declared `response_model`, using camelCase aliases.

### 4.3 Authentication and authorization flow

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant A as FastAPI
    participant D as Database
    C->>A: POST /auth/login with email and password
    A->>D: SELECT user by email
    D-->>A: user row with password_hash and role
    A->>A: bcrypt.checkpw
    A-->>C: 200 with accessToken (HS256, exp 60 min) and user
    C->>A: GET /projects/... with Authorization Bearer token
    A->>A: jwt.decode checks signature and exp
    A->>D: load user by sub claim
    D-->>A: user with current role
    A->>A: endpoint logic (role matters only for retrieval)
    A-->>C: 200, or 401 / 404 / 422
```

- **Authentication** (who are you?) is a signed, expiring JWT. The token's `role` claim is informational; the **role used for decisions is always the one stored in the database**.
- **Authorization** (what may you do?) is implemented in exactly one place: the role-to-classification table in `app/models/enums.py` (`CLASSIFICATION_ACCESS`), applied during retrieval. No other endpoint checks roles, and no endpoint checks organization or project membership ([§9](#9-roles-and-permissions)).

### 4.4 Data flow

- **Ingestion:** file → UTF-8 text → paragraph chunks → one embedding per chunk → `document_chunks` rows (each carrying the document's classification) → document marked `Indexed`. See [§12.3](#123-knowledge-ingestion).
- **Retrieval/chat:** question → role → allowed classifications → (keyword guard) → SQL filter on project + classification → cosine ranking in Python → top 3 → optional Claude call → response and audit entry. See [§12.2](#122-retrieval-and-authorization) and [§12.4](#124-assistant-chat).
- **Everything else** is request → validation → single table read/write → response.

### 4.5 Error handling and logging

- Application errors use FastAPI's `HTTPException`, serialized as `{"detail": "<message>"}` (`400`, `401`, `404`, `409`). Validation errors are FastAPI's standard `422` body with a `detail` array.
- There are no custom exception handlers: an unhandled exception (for example a database integrity error or a `bcrypt` length error) returns a plain `500 Internal Server Error` and the traceback goes to the Uvicorn log.
- The Anthropic call catches only `httpx.HTTPError` and silently falls back to the offline reply; the `generatedBy` field is the only signal.
- The application configures no Python `logging`. The log output is Uvicorn's access log; the only application-level record is the `audit_log_entries` table ([§2.2.9](#229-audit-log)).
- Frontend: Next.js default error and 404 pages; no error boundaries.

### 4.6 Background jobs and real-time communication

None. Ingestion, workflow runs, and evaluation runs are synchronous request handlers. Redis is provisioned in `docker-compose.yml` but nothing uses it.

### 4.7 Deployment architecture (provided, not executed)

```mermaid
flowchart LR
    subgraph host["Docker host: docker compose up --build"]
        api["api<br/>built from backend/Dockerfile<br/>port 8000"]
        db[("db<br/>pgvector/pgvector:pg16<br/>port 5432, volume deployai-db-data")]
        redis[("redis<br/>redis:7-alpine<br/>port 6379, unused by api")]
    end
    client(["Browser or curl"]) -->|"8000"| api
    api -->|"DATABASE_URL to db:5432"| db
    api -. "REDIS_URL passed, never read" .-> redis
```

The `api` container runs `alembic upgrade head && python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port 8000` after the database health check passes. The frontend is not part of the Compose stack and has no Dockerfile. See [§17](#17-deployment-and-production) for what has and has not been verified.

---

## 5. Project Structure

```text
deployai-os/
├── README.md                          This document
├── frontend/                          Next.js 14 app (App Router) running on mock data
│   ├── app/
│   │   ├── layout.tsx                 Root layout: metadata, global CSS, system font stack
│   │   ├── globals.css                Tailwind directives
│   │   ├── page.tsx                   Redirects "/" to /login
│   │   ├── login/page.tsx             Login form (React Hook Form + Zod)
│   │   ├── register/page.tsx          Registration form
│   │   └── (app)/                     Route group that adds the app shell
│   │       ├── layout.tsx             Sidebar + topbar around all pages below
│   │       ├── dashboard/page.tsx
│   │       ├── organizations/page.tsx
│   │       ├── settings/page.tsx
│   │       └── projects/
│   │           ├── page.tsx           Project list
│   │           └── [projectId]/
│   │               ├── layout.tsx     Project header and the 14 tabs
│   │               ├── page.tsx       Redirects to overview
│   │               └── <module>/page.tsx   overview, discovery, requirements, architecture,
│   │                                       integrations, data-sources, knowledge, assistants,
│   │                                       workflows, deployments, monitoring, feedback,
│   │                                       evaluations, audit (one folder each)
│   ├── components/
│   │   ├── ui/                        button, card, badge, input, label, page-header, stat-card
│   │   ├── charts/                    simple-line-chart.tsx, simple-bar-chart.tsx (Recharts wrappers)
│   │   ├── sidebar.tsx, topbar.tsx, project-tabs.tsx
│   │   ├── knowledge-search-tester.tsx    Interactive retrieval demo (client-side rules)
│   │   └── assistant-chat-preview.tsx     Interactive chat demo (client-side rules)
│   ├── lib/
│   │   ├── mock-data.ts               The GulfBridge dataset every page renders
│   │   ├── types.ts                   TypeScript interfaces (the contract the backend mirrors)
│   │   └── utils.ts                   cn() class-name helper
│   ├── package.json, package-lock.json, next.config.js, tsconfig.json,
│   │   tailwind.config.ts, postcss.config.js, next-env.d.ts, .gitignore
│   └── README.md                      Frontend component README
└── backend/                           FastAPI service
    ├── app/
    │   ├── main.py                    App factory: CORS, router wiring, create_all on startup
    │   ├── config.py                  Settings from environment / .env
    │   ├── database.py                Engine, session factory, declarative Base, get_db
    │   ├── seed.py                    Idempotent demo-data loader (python -m app.seed)
    │   ├── core/
    │   │   ├── security.py            bcrypt hashing, JWT encode/decode
    │   │   ├── deps.py                get_current_user (used), require_role (defined, unused)
    │   │   └── audit.py               log_action() helper
    │   ├── models/                    One SQLAlchemy model file per entity, plus enums.py
    │   ├── schemas/                   Pydantic models; base.py defines the camelCase CamelModel
    │   ├── services/
    │   │   ├── embeddings.py          EmbeddingProvider + hashing implementation
    │   │   ├── vector_store.py        VectorStore interface, in-memory store, PgVectorStore sketch
    │   │   ├── chunking.py            Document text -> chunks
    │   │   ├── rag.py                 Authorization-aware retrieval
    │   │   └── llm.py                 Claude call with offline fallback
    │   └── routers/                   auth, organizations, projects, requirements, architecture,
    │                                  integrations, data_sources, knowledge, assistants,
    │                                  workflows, deployments, feedback, evaluations, audit
    ├── alembic/                       env.py, script.py.mako, versions/5eff5670ee55_initial_schema.py
    ├── alembic.ini
    ├── tests/                         conftest.py and four test modules (17 tests)
    ├── Dockerfile, docker-compose.yml
    ├── requirements.txt, requirements-dev.txt
    ├── .env.example, .gitignore
    └── README.md                      Backend component README
```

Generated or local-only files are intentionally omitted and are git-ignored: `node_modules/`, `.next/`, `*.tsbuildinfo`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `.coverage`, `*.db` (including the default `deployai.db`), and `.env`.

---

## 6. Getting Started

### 6.1 Prerequisites

| Requirement | Version | Needed for | Notes |
|---|---|---|---|
| Python 3 + `pip` | 3.10 or newer; **3.12.3 tested** | Backend | The code uses `X \| None` annotations that SQLAlchemy evaluates at runtime, so 3.9 and older are not supported. |
| Node.js + `npm` | ≥ 18.17 (Next.js 14 requirement); **22.22.2 tested** | Frontend | — |
| PostgreSQL | 16 (16.15 tested) | Optional | Only if you do not want SQLite. |
| Docker + Docker Compose | — | Optional | **Not verified** — no Docker daemon was available. |
| Anthropic API key | — | Optional | Enables live Claude replies; **never exercised** during verification. |

### 6.2 Get the code

```bash
git clone <repository-url> deployai-os    # placeholder: no remote repository is configured in this project
cd deployai-os
```

### 6.3 Run the backend (SQLite, zero configuration)

Run every command from `backend/` — the `.env` file and the default SQLite path (`./deployai.db`) are resolved **relative to the current working directory**.

```bash
cd backend
python3 -m venv .venv                  # isolated Python environment
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt    # runtime + test dependencies
python -m app.seed                     # create tables and load the demo dataset
uvicorn app.main:app --reload          # start the API with auto-reload
```

Expected output of the seed step (a second run prints `Already seeded (org-gulfbridge exists) — skipping.`):

```text
Seed complete: GulfBridge Professional Services demo dataset loaded.
Demo accounts (password for both: GulfBridge!Demo1):
  admin    demo.engineer@gulfbridge.example
  employee employee.demo@gulfbridge.example
```

**Verify it is running:**

```bash
curl http://localhost:8000/health      # -> {"status":"ok"}
```

Then open <http://localhost:8000/docs> for the interactive API documentation.

### 6.4 Run the frontend

```bash
cd frontend
npm install                            # `npm ci` gives a reproducible install from the lockfile
npm run dev                            # development server on http://localhost:3000
```

Open <http://localhost:3000>; it redirects to `/login` (a client-side redirect — you can also open <http://localhost:3000/login> directly). No environment variables are needed. For a production-mode run: `npm run build && npm run start`.

### 6.5 Optional: use PostgreSQL

**Native PostgreSQL 16 (verified).** Create a role and database, then point `DATABASE_URL` at it:

```bash
# as the postgres superuser (the verification used a superuser role to mirror the Docker image's default;
# a plain database owner should also suffice but was not tested)
psql -c "CREATE ROLE deployai LOGIN SUPERUSER PASSWORD 'deployai';" \
     -c "CREATE DATABASE deployai OWNER deployai;"

cd backend
export DATABASE_URL="postgresql+psycopg2://deployai:deployai@localhost:5432/deployai"
alembic upgrade head                   # create the schema from the migration
python -m app.seed
uvicorn app.main:app
```

The `deployai` / `deployai` credentials above are local demo values matching `docker-compose.yml`; never reuse them outside a throwaway environment.

**Docker Compose (not verified).**

```bash
cd backend
cp .env.example .env                   # optional; Compose reads ANTHROPIC_API_KEY from your shell or .env
docker compose up --build              # starts db (PostgreSQL+pgvector image), redis, and the api on :8000
```

### 6.6 Seed data and demo accounts

`python -m app.seed` (source: `backend/app/seed.py`) loads the same organization, project, and record IDs the frontend uses.

| Entity | Count | Notes |
|---|---|---|
| Organizations | 2 | `org-gulfbridge`, `org-northwind` |
| Users | 2 | `usr-demo-admin` (admin, "Demo Engineer"), `usr-demo-employee` (employee, "Sara Employee") |
| Projects | 1 | `proj-gulfbridge-knowledge-ops`, production, active, stage `iteration` |
| Requirements / ADRs | 6 / 3 | `REQ-101`…`REQ-106`, `ADR-001`…`ADR-003` |
| Integrations / data sources | 5 / 4 | One integration (`int-5`, WhatsApp) is in `error` state |
| Knowledge documents | 6 | Five `Indexed` with 2 chunks each (10 chunks); `doc-5` stays `Processing` with none; `doc-4` is `Restricted` |
| Assistant / workflows | 1 / 4 | `asst-1`; `wf-1`…`wf-4` (`wf-4` paused) |
| Deployments / feedback / evaluation runs / audit entries | 5 / 5 / 4 / 5 | Evaluations `v1.4`, `v1.5`, `v1.7`, `v1.9` |

**Demo credentials** (defined in `seed.py`; the password is public in this repository, so use them for local demos only and change or remove them before sharing any deployment):

| Role | Email | Password |
|---|---|---|
| admin | `demo.engineer@gulfbridge.example` | `GulfBridge!Demo1` |
| employee | `employee.demo@gulfbridge.example` | `GulfBridge!Demo1` |

To reset the SQLite demo data, stop the server, delete `backend/deployai.db`, and re-run `python -m app.seed`. For PostgreSQL see [§18](#18-troubleshooting-and-faq).

### 6.7 Optional: enable live Claude replies

Create an API key in your Anthropic account, put it in `backend/.env` as `ANTHROPIC_API_KEY=your_api_key_here`, and restart the server. A chat response with `"generatedBy": "claude"` indicates the live path ran; `"mock"` means the offline fallback was used. **This path has not been exercised during verification.**

---

## 7. Configuration

### 7.1 Backend environment variables

Defined in `backend/app/config.py` (`pydantic-settings`; names are case-insensitive; unknown variables are ignored). Values come from the process environment first, then from a `.env` file in the **current working directory**. A template is provided at `backend/.env.example`.

| Variable | Purpose | Required? | Default or example |
|---|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection URL | No | Default `sqlite:///./deployai.db`. PostgreSQL: `postgresql+psycopg2://user:password@host:5432/dbname` |
| `JWT_SECRET_KEY` | Key used to sign access tokens | No — but **must be replaced outside local development** | Default `dev-only-secret-change-me` (25 bytes; current PyJWT warns below 32 bytes for HS256) |
| `JWT_ALGORITHM` | JWT signing algorithm | No | `HS256` (the only algorithm exercised) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access-token lifetime | No | `60` (expiry enforcement verified) |
| `ANTHROPIC_API_KEY` | Enables live Claude replies | No | Unset → offline replies. Example: `your_api_key_here` |
| `CORS_ORIGINS` | Comma-separated browser origins allowed to call the API | No | `http://localhost:3000` |

Generate a strong signing key with:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 7.2 Docker Compose variables (`backend/docker-compose.yml`)

| Variable | Service | Purpose | Notes |
|---|---|---|---|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | `db` | Initial role and database | All set to `deployai` in the file |
| `DATABASE_URL` | `api` | Points the API at `db` | `postgresql+psycopg2://deployai:deployai@db:5432/deployai` |
| `JWT_SECRET_KEY` | `api` | Token signing | Set to the insecure development default in the file |
| `CORS_ORIGINS` | `api` | Allowed origins | `http://localhost:3000` |
| `ANTHROPIC_API_KEY` | `api` | Optional live replies | Interpolated from your shell or `.env` (`${ANTHROPIC_API_KEY:-}`) |
| `REDIS_URL` | `api` | — | **Passed to the container but not read by any code** |

### 7.3 Frontend

The frontend reads **no** environment variables (`process.env` is not referenced). If it is later connected to the API, an API base-URL variable (for example `NEXT_PUBLIC_API_URL`) would be a natural addition — that is a suggestion, not something that exists today.

> Never commit a real `.env` file or key. `.env` is git-ignored; only `.env.example` (with an empty `ANTHROPIC_API_KEY`) is tracked.

---

## 8. Using the Application

### 8.1 Frontend tour

1. Open <http://localhost:3000>. You are redirected to **/login** (client-side).
2. Click **Continue as Demo Engineer** (or submit the form with any well-formed values — nothing is sent anywhere). You land on **/dashboard**.
3. Use the sidebar: **Dashboard**, **Organizations** (two cards), **Projects**, **Settings**.
4. Open **Projects → Enterprise Knowledge & Operations AI**. The 14 tabs run from **Overview** (lifecycle stepper) to **Audit**.
5. On the **Knowledge** tab, use **Retrieval Tester**: *"How many annual leave days do I get?"* returns two leave-policy chunks; *"What is our travel reimbursement policy?"* returns two travel chunks; *"What are the executive compensation bands?"* shows **Access denied before retrieval**; anything else returns one generic demo chunk.
6. On the **Assistants** tab, send the same prompts in the chat preview; the refusal is tagged "Blocked by document-level authorization".
7. On **Deployments**, note that the **Rollback** buttons do nothing.

There is no sign-out control: the UI has no session.

### 8.2 Backend: interactive documentation

Open <http://localhost:8000/docs>, call `POST /auth/login` (or `POST /auth/demo`), copy the `accessToken`, use Swagger UI's **Authorize** button (HTTP Bearer), and try any endpoint. *(Standard Swagger UI behavior; not exercised in a browser during verification.)*

### 8.3 Backend: the "authorize before retrieval" walkthrough with cURL

All commands below were executed against a freshly seeded server; the responses shown are the real output (JWTs redacted, long values and lists trimmed with `…`; ids and timestamps vary).

First obtain a token for each seeded role:

```bash
API=http://localhost:8000
PID=proj-gulfbridge-knowledge-ops
ADMIN=$(curl -s -X POST $API/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"demo.engineer@gulfbridge.example","password":"GulfBridge!Demo1"}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["accessToken"])')
EMP=$(curl -s -X POST $API/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"employee.demo@gulfbridge.example","password":"GulfBridge!Demo1"}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["accessToken"])')
```

**1. An admin asks about executive compensation** — the Restricted document is returned, ranked first:

```bash
curl -s -X POST $API/projects/$PID/knowledge/search -H "Authorization: Bearer $ADMIN" \
  -H 'Content-Type: application/json' -d '{"query":"What are the executive compensation bands?"}'
```

Response — `200 OK`:

```json
{
  "restricted": false,
  "message": null,
  "chunks": [
    {
      "chunkId": "chk-7cde379228",
      "documentFilename": "Executive_Compensation_2026.xlsx",
      "classification": "Restricted",
      "content": "Executive Compensation Bands\n\nBase salary bands for the executive leadership team range from 850,000 to 1,650,000 AED an…",
      "score": 0.4438
    },
    "… 2 more"
  ]
}
```

**2. An employee asks the same question** — refused before any search runs; no chunks are loaded:

```bash
curl -s -X POST $API/projects/$PID/knowledge/search -H "Authorization: Bearer $EMP" \
  -H 'Content-Type: application/json' -d '{"query":"What are the executive compensation bands?"}'
```

Response — `200 OK`:

```json
{
  "restricted": true,
  "message": "This looks like it may touch Restricted-classification information (compensation, payroll, or executive matters). Your r…",
  "chunks": []
}
```

**3. An employee asks an ordinary question** — answered from Public/Internal documents:

```bash
curl -s -X POST $API/projects/$PID/knowledge/search -H "Authorization: Bearer $EMP" \
  -H 'Content-Type: application/json' -d '{"query":"How many annual leave days do I get?"}'
```

Response — `200 OK`:

```json
{
  "restricted": false,
  "message": null,
  "chunks": [
    {
      "chunkId": "chk-e339233507",
      "documentFilename": "Annual_Leave_Policy.pdf",
      "classification": "Internal",
      "content": "Up to five unused annual leave days may be carried over into the following calendar year. Any balance beyond five days i…",
      "score": 0.3356
    },
    "… 2 more"
  ]
}
```

**4. The assistant endpoint enforces the same rule.** Allowed question (offline reply, because no API key is set):

```bash
curl -s -X POST $API/projects/$PID/assistants/chat -H "Authorization: Bearer $EMP" \
  -H 'Content-Type: application/json' -d '{"message":"How do I reset my VPN access?"}'
```

Response — `200 OK`:

```json
{
  "reply": "Based on Support_FAQ_Master.pdf: Resetting Your VPN Access\n\nTo reset your company VPN credentials, open the IT Self-Serv…",
  "restricted": false,
  "sources": [
    {
      "chunkId": "chk-57e160f126",
      "documentFilename": "Support_FAQ_Master.pdf",
      "classification": "Public",
      "content": "Resetting Your VPN Access\n\nTo reset your company VPN credentials, open the IT Self-Service portal, select \"Reset VPN Acc…",
      "score": 0.3542
    },
    "… 2 more"
  ],
  "generatedBy": "mock"
}
```

Restricted question — the refusal text is returned and no sources are included:

```bash
curl -s -X POST $API/projects/$PID/assistants/chat -H "Authorization: Bearer $EMP" \
  -H 'Content-Type: application/json' -d '{"message":"Tell me the executive compensation bands"}'
```

Response — `200 OK`:

```json
{
  "reply": "This looks like it may touch Restricted-classification information (compensation, payroll, or executive matters). Your r…",
  "restricted": true,
  "sources": [],
  "generatedBy": "mock"
}
```

### 8.4 Role-specific workflows

| Role | How to obtain | What changes |
|---|---|---|
| **admin** | Seeded `demo.engineer@…`, or register under a **new** organization name | May retrieve all four classifications |
| **manager** | Not available through the API. Set in the database: `UPDATE users SET role = 'manager' WHERE email = '…';` (stored value is the enum member name; the change applies immediately because the role is read from the database on every request) | May retrieve Public, Internal, and Confidential |
| **employee** | Seeded `employee.demo@…`, or register under an **existing** organization name | May retrieve Public and Internal only |

Every role can use every non-retrieval endpoint identically ([§9](#9-roles-and-permissions)).

### 8.5 When something goes wrong

| Status | Meaning in this API | Typical cause |
|---|---|---|
| `400` | Upload is not UTF-8 text | A binary or PDF/DOCX file was uploaded |
| `401` | `Not authenticated` / `Invalid or expired token` / `Incorrect email or password` | Missing header, wrong token, token older than 60 minutes, bad credentials |
| `404` | `Project not found`, `Organization not found`, `Workflow not found`, `Deployment not found` | Unknown id (only some routes check) |
| `409` | `An account with that email already exists` | Re-registering an e-mail |
| `422` | FastAPI validation error with a `detail` array | Missing field or an enum value that is not allowed |
| `500` | Unhandled error | Password longer than 72 bytes at registration; writing to a nonexistent project on PostgreSQL; see [§18](#18-troubleshooting-and-faq) |

### 8.6 Ending a session

There is no logout endpoint and no token revocation. Clients simply discard the token; it stops working after `ACCESS_TOKEN_EXPIRE_MINUTES` (60 by default).

---

## 9. Roles and Permissions

### 9.1 Roles

| Role | Assigned when | Notes |
|---|---|---|
| `admin` | The user registers under an organization name that does not exist yet; or seeded | Highest clearance. **Anyone can become an admin by registering a new organization name.** |
| `manager` | Only by editing the database | Defined in the enum and the access table; no endpoint assigns it; not covered by automated tests |
| `employee` | The user registers under an existing organization name (case-insensitive); or seeded | Lowest clearance |

### 9.2 Retrieval clearance (the only role-dependent behavior)

Source: `CLASSIFICATION_ACCESS` in `backend/app/models/enums.py`. The checks below were run on SQLite and PostgreSQL.

| Document classification | admin | manager | employee |
|---|---|---|---|
| Public | Allowed | Allowed | Allowed |
| Internal | Allowed | Allowed | Allowed |
| Confidential | Allowed | Allowed | Denied |
| Restricted | Allowed | Denied | Denied |

### 9.3 Endpoint permissions

| Capability | admin | manager | employee | Notes |
|---|---|---|---|---|
| Register, log in, demo login, `GET /health` | Public | Public | Public | No token needed; `POST /auth/demo` returns an **admin** token |
| Read organizations, projects, and every per-project list (requirements, ADRs, integrations, data sources, documents, assistants, workflows, deployments, feedback, evaluations, audit) | Yes | Yes | Yes | Any authenticated user, **for any project, in any organization** |
| Create projects and per-project records; submit feedback | Yes | Yes | Yes | No role check |
| Upload documents (with any classification, including Restricted) | Yes | Yes | Yes | No role check |
| Run workflows, run evaluations, roll back deployments | Yes | Yes | Yes | No role check |
| Retrieve Public / Internal chunks (search and chat) | Yes | Yes | Yes | |
| Retrieve Confidential chunks | Yes | Yes | No | |
| Retrieve Restricted chunks | Yes | No | No | |
| Read the audit log | Yes | Yes | Yes | No role check |
| Assign or change roles | — | — | — | No endpoint exists |

### 9.4 Authentication versus authorization

Authentication (a valid, unexpired token for an existing user) is required by every route except the four public ones. Authorization beyond that is limited to the retrieval table above. `require_role(...)` is defined in `app/core/deps.py` but no route uses it, so no endpoint can return `403`. A user's `organization_id` is stored but never consulted when deciding access, which is why a user from one organization can read another's project data ([§15](#15-security-and-privacy)).

---

## 10. API Reference

The full, always-current contract is the OpenAPI document served at `/openapi.json` (rendered at `/docs` and `/redoc`). This section summarizes it and shows verified examples. The route inventory was derived from `app.openapi()`: **33 operations over 27 paths**.

### 10.1 Conventions

- **Base URL:** `http://localhost:8000` (the examples use `$API`).
- **Format:** JSON, except the upload endpoint (`multipart/form-data`). Keys are **camelCase** on the wire; request bodies also accept snake_case field names (verified with `customer_name`).
- **Authentication:** `Authorization: Bearer <accessToken>` on every route except `GET /health`, `POST /auth/register`, `POST /auth/login`, and `POST /auth/demo`.
- **Errors:** `{"detail": "<message>"}` for `400/401/404/409`; FastAPI's standard `detail` array for `422`; a plain-text `Internal Server Error` for unhandled `500`s.
- **Identifiers:** opaque strings with prefixes (`usr-`, `org-`, `proj-<slug>-`, `req-`, `adr-`, `int-`, `ds-`, `doc-`, `chk-`, `asst-`, `wf-`, `run-`, `dep-`, `fb-`, `eval-`, `aud-`).
- **Timestamps:** ISO 8601, stored in UTC. PostgreSQL returns a trailing `Z`; **SQLite returns no offset** (timezone information is not persisted).
- **Lists:** no pagination or filtering; every row is returned. Deployments, feedback, workflow runs, and the audit log are newest first; evaluations are oldest first; the other lists are in database order.
- **Project scoping:** nested routes take `project_id` from the path. It is **not validated** against the projects table (see [§19](#19-known-limitations-and-roadmap)).

### 10.2 Endpoint summary

#### System and authentication

| Method | Path | Auth | Purpose | Request body | Success | Errors |
|---|---|---|---|---|---|---|
| GET | `/health` | none | Liveness check | — | `200` `{"status":"ok"}` | — |
| POST | `/auth/register` | none | Create an account and organization/membership ([§2.2.1](#221-accounts-and-authentication)) | `{name, email, organization, password}` | `201` `TokenResponse` | `409`, `422`, `500` (password > 72 bytes) |
| POST | `/auth/login` | none | Exchange credentials for a token | `{email, password}` | `200` `TokenResponse` | `401`, `422` |
| POST | `/auth/demo` | none | Token for the seeded demo **admin** (no credentials) | — | `200` `TokenResponse` | — |
| GET | `/auth/me` | Bearer | Current user | — | `200` `UserOut` | `401` |

`UserOut` = `{id, name, email, role, organizationId}`; `TokenResponse` = `{accessToken, tokenType, user}`.

#### Organizations and projects

| Method | Path | Auth | Purpose | Request body | Success | Errors |
|---|---|---|---|---|---|---|
| GET | `/organizations` | Bearer | List organizations | — | `200` `OrganizationOut[]` | `401` |
| GET | `/organizations/{organization_id}` | Bearer | One organization | — | `200` | `401`, `404` |
| GET | `/projects` | Bearer | List all projects | — | `200` `ProjectOut[]` | `401` |
| POST | `/projects` | Bearer | Create a project in the caller's organization (audited) | `{name, customerName, environment?}` (default `development`) | `201` `ProjectOut` | `401`, `422` |
| GET | `/projects/{project_id}` | Bearer | One project | — | `200` | `401`, `404` |

`OrganizationOut` = `{id, name, industry, activeProjects}`; `ProjectOut` = `{id, name, organizationId, customerName, environment, status, currentStage}`.

#### Project records — `/projects/{project_id}/…`

| Method | Path | Request body (`POST`) | Item shape |
|---|---|---|---|
| GET, POST | `/requirements` | `{title, type, priority, stakeholder, status?}` (status default `Draft`) | `{id, title, type, priority, status, stakeholder}` |
| GET, POST | `/architecture` | `{title, context, decision, tradeoffs, status?}` (default `Proposed`) | `{id, title, context, decision, tradeoffs, status}` |
| GET, POST | `/integrations` | `{name, type, status?}` (default `disconnected`) | `{id, name, type, status, lastSync}` |
| GET, POST | `/data-sources` | `{name, kind, recordCount, status?}` (default `disconnected`) | `{id, name, kind, recordCount, status}` |
| GET, POST | `/feedback` | `{question, sentiment, reason?}` | `{id, question, sentiment, reason, createdAt}` |

All require a Bearer token (`401` otherwise); `GET` returns `200` with an array, `POST` returns `201` with the created item, and invalid bodies return `422`.

#### Knowledge and assistant — `/projects/{project_id}/…`

| Method | Path | Purpose | Request | Success | Errors |
|---|---|---|---|---|---|
| GET | `/knowledge` | List documents (not filtered by classification) | — | `200` `{id, filename, department, classification, status, chunks}[]` | `401` |
| POST | `/knowledge/upload` | Upload, chunk, embed, index ([§12.3](#123-knowledge-ingestion)) | multipart: `file`, `department`, `classification?` (default `Internal`) | `201` `{document, chunksCreated}` | `400` non-UTF-8, `422` |
| POST | `/knowledge/search` | Authorization-aware retrieval ([§12.2](#122-retrieval-and-authorization)) | `{query}` | `200` `{restricted, message, chunks:[{chunkId, documentFilename, classification, content, score}]}` | `401`, `422` |
| GET | `/assistants` | Stored assistant configuration | — | `200` `{id, name, model, temperature, knowledgeBase, citationMode}[]` | `401` |
| POST | `/assistants/chat` | Cited answer or refusal ([§12.4](#124-assistant-chat)) | `{message}` | `200` `{reply, restricted, sources[], generatedBy}` | `401`, `422` |

#### Operations — `/projects/{project_id}/…`

| Method | Path | Purpose | Success | Errors |
|---|---|---|---|---|
| GET | `/workflows` | List workflows | `200` `{id, name, status, lastRun, successRate}[]` | `401` |
| GET | `/workflows/{workflow_id}/runs` | Run history, newest first | `200` `{id, outcome, detail, ranAt}[]` (an unknown workflow yields `[]`) | `401` |
| POST | `/workflows/{workflow_id}/run` | Simulated run, audited ([§2.2.6](#226-workflow-runs-simulated)) | `201` run | `401`, `404` |
| GET | `/deployments` | Release history, newest first | `200` `{id, version, environment, status, deployedBy, deployedAt, commit}[]` | `401` |
| POST | `/deployments/{deployment_id}/rollback` | Append a rollback record, audited | `201` deployment | `401`, `404` |
| GET | `/evaluations` | Evaluation runs, oldest first | `200` `{id, version, date, correctness, faithfulness, citationAccuracy, avgLatency}[]` | `401` |
| POST | `/evaluations/run` | Simulated evaluation run | `201` evaluation run | `401` |
| GET | `/audit` | Audit log, newest first | `200` `{id, actor, action, resourceType, resourceId, ipAddress, timestamp}[]` | `401` |

### 10.3 Allowed values

| Field | Values |
|---|---|
| `role` | `admin`, `manager`, `employee` |
| `environment` | `development`, `staging`, `production` |
| project `status` | `active`, `paused`, `completed` |
| `currentStage` | `discovery`, `requirements`, `architecture`, `integrations`, `aiConfig`, `security`, `testing`, `deployment`, `monitoring`, `iteration` |
| requirement `type` | `Functional`, `Non-functional`, `Security`, `Integration`, `AI`, `Operational`, `Compliance` |
| requirement `priority` | `Low`, `Medium`, `High`, `Critical` |
| requirement `status` | `Draft`, `Validated`, `In Development`, `Testing`, `Accepted`, `Rejected` |
| ADR `status` | `Proposed`, `Accepted`, `Superseded` |
| integration `type` | `REST API`, `Webhook`, `Email`, `WhatsApp`, `File Upload`, `PostgreSQL` |
| integration `status` | `connected`, `disconnected`, `error` |
| data-source `status` | `connected`, `disconnected` |
| document `classification` | `Public`, `Internal`, `Confidential`, `Restricted` |
| document `status` | `Uploaded`, `Processing`, `Processed`, `Indexed`, `Failed` (only `Processing`, `Processed`, `Indexed` are ever set by code) |
| `citationMode` | `always`, `when-available` |
| workflow `status` | `active`, `paused`, `draft` |
| run `outcome` | `success`, `failed` |
| deployment `status` | `healthy`, `degraded`, `failed` |
| feedback `sentiment` | `positive`, `negative` |

### 10.4 Verified examples

Run the token snippet from [§8.3](#83-backend-the-authorize-before-retrieval-walkthrough-with-curl) first (it defines `$API`, `$PID`, `$ADMIN`, and `$EMP`). Retrieval and chat examples are in that section. Each response below is real output from a freshly seeded server; JWTs are redacted and long values or lists are trimmed with `…`.

<details>
<summary><strong>Authentication and errors</strong></summary>

**Health check — `GET /health`**

```bash
curl -s $API/health
```

Response — `200 OK`:

```json
{
  "status": "ok"
}
```

**Log in — `POST /auth/login`**

```bash
curl -s -X POST $API/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"demo.engineer@gulfbridge.example","password":"GulfBridge!Demo1"}'
```

Response — `200 OK`:

```json
{
  "accessToken": "<JWT>",
  "tokenType": "bearer",
  "user": {
    "id": "usr-demo-admin",
    "name": "Demo Engineer",
    "email": "demo.engineer@gulfbridge.example",
    "role": "admin",
    "organizationId": "org-gulfbridge"
  }
}
```

**Demo login, no credentials — `POST /auth/demo`** (returns an admin token; see [§15](#15-security-and-privacy))

```bash
curl -s -X POST $API/auth/demo
```

Response — `200 OK`:

```json
{
  "accessToken": "<JWT>",
  "tokenType": "bearer",
  "user": {
    "id": "usr-demo-admin",
    "name": "Demo Engineer",
    "email": "demo.engineer@gulfbridge.example",
    "role": "admin",
    "organizationId": "org-gulfbridge"
  }
}
```

**Current user — `GET /auth/me`**

```bash
curl -s $API/auth/me -H "Authorization: Bearer $ADMIN"
```

Response — `200 OK`:

```json
{
  "id": "usr-demo-admin",
  "name": "Demo Engineer",
  "email": "demo.engineer@gulfbridge.example",
  "role": "admin",
  "organizationId": "org-gulfbridge"
}
```

**Register under a new organization — `POST /auth/register`** (the new user is an `admin`)

```bash
curl -s -X POST $API/auth/register -H 'Content-Type: application/json' \
  -d '{"name":"Jane Doe","email":"jane.doe@example.com","organization":"Example Co","password":"correct-horse-battery"}'
```

Response — `201 Created`:

```json
{
  "accessToken": "<JWT>",
  "tokenType": "bearer",
  "user": {
    "id": "usr-cb3d367446c4",
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "role": "admin",
    "organizationId": "org-42e99ebb"
  }
}
```

**Errors**

Duplicate e-mail:

```bash
curl -s -X POST $API/auth/register -H 'Content-Type: application/json' \
  -d '{"name":"Jane Doe","email":"jane.doe@example.com","organization":"Example Co","password":"correct-horse-battery"}'
```

Response — `409 Conflict`:

```json
{
  "detail": "An account with that email already exists"
}
```

Missing fields (`422`, trimmed):

```bash
curl -s -X POST $API/auth/register -H 'Content-Type: application/json' \
  -d '{"name":"Only A Name"}'
```

Response — `422 Unprocessable Entity`:

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": [
        "body",
        "email"
      ],
      "msg": "Field required",
      "input": {
        "name": "Only A Name"
      }
    },
    "… 2 more"
  ]
}
```

No token:

```bash
curl -s $API/auth/me
```

Response — `401 Unauthorized`:

```json
{
  "detail": "Not authenticated"
}
```

Invalid token:

```bash
curl -s $API/auth/me -H "Authorization: Bearer not-a-real-token"
```

Response — `401 Unauthorized`:

```json
{
  "detail": "Invalid or expired token"
}
```

Wrong password:

```bash
curl -s -X POST $API/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"demo.engineer@gulfbridge.example","password":"wrong"}'
```

Response — `401 Unauthorized`:

```json
{
  "detail": "Incorrect email or password"
}
```

</details>

<details>
<summary><strong>Organizations and projects</strong></summary>

**List organizations**

```bash
curl -s $API/organizations -H "Authorization: Bearer $ADMIN"
```

Response — `200 OK`:

```json
[
  {
    "id": "org-gulfbridge",
    "name": "GulfBridge Professional Services",
    "industry": "Professional Services / Training / Consultancy",
    "activeProjects": 1
  },
  "… 1 more"
]
```

**List projects**

```bash
curl -s $API/projects -H "Authorization: Bearer $ADMIN"
```

Response — `200 OK`:

```json
[
  {
    "id": "proj-gulfbridge-knowledge-ops",
    "name": "Enterprise Knowledge & Operations AI",
    "organizationId": "org-gulfbridge",
    "customerName": "GulfBridge Professional Services",
    "environment": "production",
    "status": "active",
    "currentStage": "iteration"
  }
]
```

**Get one project**

```bash
curl -s $API/projects/$PID -H "Authorization: Bearer $ADMIN"
```

Response — `200 OK`:

```json
{
  "id": "proj-gulfbridge-knowledge-ops",
  "name": "Enterprise Knowledge & Operations AI",
  "organizationId": "org-gulfbridge",
  "customerName": "GulfBridge Professional Services",
  "environment": "production",
  "status": "active",
  "currentStage": "iteration"
}
```

**Unknown project**

```bash
curl -s $API/projects/does-not-exist -H "Authorization: Bearer $ADMIN"
```

Response — `404 Not Found`:

```json
{
  "detail": "Project not found"
}
```

**Create a project**

```bash
curl -s -X POST $API/projects -H "Authorization: Bearer $ADMIN" -H 'Content-Type: application/json' \
  -d '{"name":"Support Copilot","customerName":"Example Customer","environment":"development"}'
```

Response — `201 Created`:

```json
{
  "id": "proj-support-copilot-2dc909",
  "name": "Support Copilot",
  "organizationId": "org-gulfbridge",
  "customerName": "Example Customer",
  "environment": "development",
  "status": "active",
  "currentStage": "discovery"
}
```

</details>

<details>
<summary><strong>Project records (requirements, architecture, integrations, data sources, feedback)</strong></summary>

**List requirements**

```bash
curl -s $API/projects/$PID/requirements -H "Authorization: Bearer $ADMIN"
```

Response — `200 OK`:

```json
[
  {
    "id": "REQ-101",
    "title": "Employees can search internal documentation via chat",
    "type": "Functional",
    "priority": "Critical",
    "status": "Accepted",
    "stakeholder": "Ops Director"
  },
  "… 5 more"
]
```

**Create a requirement**

```bash
curl -s -X POST $API/projects/$PID/requirements -H "Authorization: Bearer $ADMIN" -H 'Content-Type: application/json' \
  -d '{"title":"Support agents can export chat transcripts","type":"Functional","priority":"Medium","stakeholder":"Support Lead"}'
```

Response — `201 Created`:

```json
{
  "id": "req-e97e2f34",
  "title": "Support agents can export chat transcripts",
  "type": "Functional",
  "priority": "Medium",
  "status": "Draft",
  "stakeholder": "Support Lead"
}
```

**Invalid enum value**

```bash
curl -s -X POST $API/projects/$PID/requirements -H "Authorization: Bearer $ADMIN" -H 'Content-Type: application/json' \
  -d '{"title":"x","type":"Nope","priority":"High","stakeholder":"x"}'
```

Response — `422 Unprocessable Entity`:

```json
{
  "detail": [
    {
      "type": "enum",
      "loc": [
        "body",
        "type"
      ],
      "msg": "Input should be 'Functional', 'Non-functional', 'Security', 'Integration', 'AI', 'Operational' or 'Compliance'",
      "input": "Nope",
      "ctx": {
        "expected": "'Functional', 'Non-functional', 'Security', 'Integration', 'AI', 'Operational' or 'Compliance'"
      }
    }
  ]
}
```

**List architecture decisions**

```bash
curl -s $API/projects/$PID/architecture -H "Authorization: Bearer $ADMIN"
```

Response — `200 OK`:

```json
[
  {
    "id": "ADR-001",
    "title": "Use PostgreSQL + pgvector for the MVP vector store",
    "context": "Customer wants a unified database and vector store with low operational overhead.",
    "decision": "Use pgvector for MVP; keep a VectorStoreInterface so Pinecone can be swapped in later.",
    "tradeoffs": "Less specialized vector infrastructure than a dedicated vector DB, but far simpler to operate.",
    "status": "Accepted"
  },
  "… 2 more"
]
```

**List integrations**

```bash
curl -s $API/projects/$PID/integrations -H "Authorization: Bearer $ADMIN"
```

Response — `200 OK`:

```json
[
  {
    "id": "int-1",
    "name": "Company Document Upload",
    "type": "File Upload",
    "status": "connected",
    "lastSync": "2026-10-11T18:16:51.678855"
  },
  "… 4 more"
]
```

**List data sources**

```bash
curl -s $API/projects/$PID/data-sources -H "Authorization: Bearer $ADMIN"
```

Response — `200 OK`:

```json
[
  {
    "id": "ds-1",
    "name": "Employee Handbook Repository",
    "kind": "Document store",
    "recordCount": "1,240 docs",
    "status": "connected"
  },
  "… 3 more"
]
```

**Submit feedback**

```bash
curl -s -X POST $API/projects/$PID/feedback -H "Authorization: Bearer $ADMIN" \
  -H 'Content-Type: application/json' -d '{"question":"Where do I find the VPN guide?","sentiment":"negative","reason":"Missing information"}'
```

Response — `201 Created`:

```json
{
  "id": "fb-8cb1c88b",
  "question": "Where do I find the VPN guide?",
  "sentiment": "negative",
  "reason": "Missing information",
  "createdAt": "2026-10-11T18:16:57.907596"
}
```

**List feedback**

```bash
curl -s $API/projects/$PID/feedback -H "Authorization: Bearer $ADMIN"
```

Response — `200 OK`:

```json
[
  {
    "id": "fb-8cb1c88b",
    "question": "Where do I find the VPN guide?",
    "sentiment": "negative",
    "reason": "Missing information",
    "createdAt": "2026-10-11T18:16:57.907596"
  },
  "… 5 more"
]
```

</details>

<details>
<summary><strong>Knowledge base and assistant configuration</strong></summary>

**List documents**

```bash
curl -s $API/projects/$PID/knowledge -H "Authorization: Bearer $ADMIN"
```

Response — `200 OK`:

```json
[
  {
    "id": "doc-1",
    "filename": "Employee_Handbook_v3.pdf",
    "department": "HR",
    "classification": "Internal",
    "status": "Indexed",
    "chunks": 2
  },
  "… 5 more"
]
```

**Upload a document**

```bash
printf 'Remote Work Policy\n\nEmployees may work remotely up to two days per week with manager approval.\n' > remote_work_policy.txt
curl -s -X POST $API/projects/$PID/knowledge/upload -H "Authorization: Bearer $ADMIN" \
  -F file=@remote_work_policy.txt -F department=HR -F classification=Internal
```

Response — `201 Created`:

```json
{
  "document": {
    "id": "doc-7e23a559",
    "filename": "remote_work_policy.txt",
    "department": "HR",
    "classification": "Internal",
    "status": "Indexed",
    "chunks": 1
  },
  "chunksCreated": 1
}
```

**Upload a non-text file**

```bash
printf '\377\376\000\001' > binary.dat
curl -s -X POST $API/projects/$PID/knowledge/upload -H "Authorization: Bearer $ADMIN" \
  -F file=@binary.dat -F department=Ops
```

Response — `400 Bad Request`:

```json
{
  "detail": "Only UTF-8 text files are supported in this reference implementation"
}
```

**Assistant configuration**

```bash
curl -s $API/projects/$PID/assistants -H "Authorization: Bearer $ADMIN"
```

Response — `200 OK`:

```json
[
  {
    "id": "asst-1",
    "name": "Company Knowledge Assistant",
    "model": "claude-sonnet-4-6",
    "temperature": 0.2,
    "knowledgeBase": "GulfBridge Company Knowledge Base",
    "citationMode": "always"
  }
]
```

</details>

<details>
<summary><strong>Workflows, deployments, evaluations, audit</strong></summary>

**List workflows**

```bash
curl -s $API/projects/$PID/workflows -H "Authorization: Bearer $ADMIN"
```

Response — `200 OK`:

```json
[
  {
    "id": "wf-1",
    "name": "Support Question Routing",
    "status": "active",
    "lastRun": "2026-10-11T18:16:51.687224",
    "successRate": 96.2
  },
  "… 3 more"
]
```

**Run a workflow** (outcome is random, weighted by the workflow's success rate)

```bash
curl -s -X POST $API/projects/$PID/workflows/wf-1/run -H "Authorization: Bearer $ADMIN"
```

Response — `201 Created`:

```json
{
  "id": "run-61c1d0399e",
  "outcome": "success",
  "detail": "Completed all steps successfully.",
  "ranAt": "2026-10-11T18:16:57.780409"
}
```

**Workflow run history**

```bash
curl -s $API/projects/$PID/workflows/wf-1/runs -H "Authorization: Bearer $ADMIN"
```

Response — `200 OK`:

```json
[
  {
    "id": "run-61c1d0399e",
    "outcome": "success",
    "detail": "Completed all steps successfully.",
    "ranAt": "2026-10-11T18:16:57.780409"
  }
]
```

**List deployments**

```bash
curl -s $API/projects/$PID/deployments -H "Authorization: Bearer $ADMIN"
```

Response — `200 OK`:

```json
[
  {
    "id": "dep-h1",
    "version": "v1.9.0",
    "environment": "production",
    "status": "healthy",
    "deployedBy": "A. Rahman",
    "deployedAt": "2026-09-26T09:12:00",
    "commit": "8f3c2a1"
  },
  "… 4 more"
]
```

**Roll back to an earlier deployment** (appends a new record)

```bash
curl -s -X POST $API/projects/$PID/deployments/dep-h3/rollback -H "Authorization: Bearer $ADMIN"
```

Response — `201 Created`:

```json
{
  "id": "dep-33cc4192",
  "version": "v1.8.1",
  "environment": "production",
  "status": "healthy",
  "deployedBy": "Demo Engineer",
  "deployedAt": "2026-10-11T18:16:57.885766",
  "commit": "1a7f6c9"
}
```

**List evaluation runs**

```bash
curl -s $API/projects/$PID/evaluations -H "Authorization: Bearer $ADMIN"
```

Response — `200 OK`:

```json
[
  {
    "id": "eval-1",
    "version": "v1.4",
    "date": "2026-08-02T00:00:00",
    "correctness": 86.0,
    "faithfulness": 89.0,
    "citationAccuracy": 82.0,
    "avgLatency": 3.4
  },
  "… 3 more"
]
```

**Run an evaluation** (simulated: metrics are nudged up from the latest run)

```bash
curl -s -X POST $API/projects/$PID/evaluations/run -H "Authorization: Bearer $ADMIN"
```

Response — `201 Created`:

```json
{
  "id": "eval-9b7530b0",
  "version": "v1.10",
  "date": "2026-10-11T18:16:57.944830",
  "correctness": 95.8,
  "faithfulness": 97.1,
  "citationAccuracy": 94.0,
  "avgLatency": 2.74
}
```

**Read the audit log** (note `ipAddress`: always `127.0.0.1`)

```bash
curl -s $API/projects/$PID/audit -H "Authorization: Bearer $ADMIN"
```

Response — `200 OK`:

```json
[
  {
    "id": "aud-4aa8fce635",
    "actor": "Demo Engineer",
    "action": "DEPLOYMENT_ROLLED_BACK",
    "resourceType": "deployment",
    "resourceId": "dep-33cc4192",
    "ipAddress": "127.0.0.1",
    "timestamp": "2026-10-11T18:16:57.890273"
  },
  "… 9 more"
]
```

</details>

---

## 11. Database Design and Data Model

### 11.1 Overview

The backend uses **SQLAlchemy 2.1.4** with typed 2.0-style models (`backend/app/models/`). The database is **SQLite by default** and **PostgreSQL 16** when `DATABASE_URL` says so; both were verified, including the migration. There are **16 tables** and 16 foreign keys.

Behavior that differs by engine:

| Topic | SQLite | PostgreSQL |
|---|---|---|
| Foreign keys | Declared but **not enforced** (`PRAGMA foreign_keys` is 0) — orphan rows are possible | Enforced (`ForeignKeyViolation` → unhandled `500`) |
| Enum columns | Strings | Native `ENUM` types (18 created by the migration) |
| Timestamps | Returned without a timezone offset | Returned in UTC with `Z` |

**Enum persistence.** SQLAlchemy stores the Python enum member **names** (for example `non_functional`, `ai_config`, `in_development`), while the API exposes the enum **values** (`Non-functional`, `aiConfig`, `In Development`). Keep this in mind when writing raw SQL (for example `UPDATE users SET role = 'manager' …`).

### 11.2 Entity-relationship diagram

The diagram below was **generated from the SQLAlchemy metadata** (primary keys, foreign keys, and the main fields; see the table in [§11.3](#113-tables-and-columns) for every column).

```mermaid
erDiagram
    organizations {
        string id PK
        string name
        string industry
    }
    projects {
        string id PK
        string name
        string organization_id FK
        enum environment
        enum status
        enum current_stage
    }
    users {
        string id PK
        string name
        string email
        enum role
        string organization_id FK
    }
    architecture_decisions {
        string id PK
        string project_id FK
        string title
        enum status
    }
    assistants {
        string id PK
        string project_id FK
        string name
        string model
        float temperature
    }
    audit_log_entries {
        string id PK
        string project_id FK
        string actor
        string action
        datetime timestamp
    }
    data_sources {
        string id PK
        string project_id FK
        string name
        string kind
        enum status
    }
    deployments {
        string id PK
        string project_id FK
        string version
        enum environment
        enum status
        string commit
    }
    evaluation_runs {
        string id PK
        string project_id FK
        string version
        float correctness
    }
    feedback_entries {
        string id PK
        string project_id FK
        enum sentiment
    }
    integrations {
        string id PK
        string project_id FK
        string name
        enum type
        enum status
    }
    knowledge_documents {
        string id PK
        string project_id FK
        string filename
        enum classification
        enum status
    }
    requirements {
        string id PK
        string project_id FK
        string title
        enum type
        enum priority
        enum status
    }
    workflows {
        string id PK
        string project_id FK
        string name
        enum status
        float success_rate
    }
    document_chunks {
        string id PK
        string document_id FK
        string project_id FK
        enum classification
        int position
        text content
        text embedding
    }
    workflow_runs {
        string id PK
        string workflow_id FK
        enum outcome
        datetime ran_at
    }
    organizations ||--o{ projects : "organization_id"
    organizations ||--o{ users : "organization_id"
    projects ||--o{ architecture_decisions : "project_id"
    projects ||--o{ assistants : "project_id"
    projects |o--o{ audit_log_entries : "project_id"
    projects ||--o{ data_sources : "project_id"
    projects ||--o{ deployments : "project_id"
    projects ||--o{ evaluation_runs : "project_id"
    projects ||--o{ feedback_entries : "project_id"
    projects ||--o{ integrations : "project_id"
    projects ||--o{ knowledge_documents : "project_id"
    projects ||--o{ requirements : "project_id"
    projects ||--o{ workflows : "project_id"
    knowledge_documents ||--o{ document_chunks : "document_id"
    projects ||--o{ document_chunks : "project_id"
    workflows ||--o{ workflow_runs : "workflow_id"
```

How the entities relate:

- An **organization** has many **users** and many **projects**.
- A **project** owns all the delivery records: requirements, architecture decisions, integrations, data sources, knowledge documents, assistants, workflows, deployments, feedback entries, and evaluation runs. Audit entries *optionally* reference a project (`project_id` is nullable, e.g. for cross-tenant events).
- A **knowledge document** has many **chunks**; each chunk repeats the document's `classification` and its `project_id` so retrieval can filter chunks directly.
- A **workflow** has many **workflow runs**.

### 11.3 Tables and columns

| Table | Columns (type; constraints) |
|---|---|
| `organizations` | `id` (string; PK)<br>`name` (string; required)<br>`industry` (string; required)<br>`created_at` (datetime; required) |
| `projects` | `id` (string; PK)<br>`name` (string; required)<br>`customer_name` (string; required)<br>`organization_id` (string; FK→organizations, required)<br>`environment` (enum; required)<br>`status` (enum; required)<br>`current_stage` (enum; required) |
| `users` | `id` (string; PK)<br>`name` (string; required)<br>`email` (string; unique, indexed, required)<br>`password_hash` (string; required)<br>`role` (enum; required)<br>`organization_id` (string; FK→organizations, required)<br>`created_at` (datetime; required) |
| `architecture_decisions` | `id` (string; PK)<br>`project_id` (string; FK→projects, indexed, required)<br>`title` (string; required)<br>`context` (text; required)<br>`decision` (text; required)<br>`tradeoffs` (text; required)<br>`status` (enum; required) |
| `assistants` | `id` (string; PK)<br>`project_id` (string; FK→projects, indexed, required)<br>`name` (string; required)<br>`model` (string; required)<br>`temperature` (float; required)<br>`knowledge_base` (string; required)<br>`citation_mode` (enum; required) |
| `audit_log_entries` | `id` (string; PK)<br>`project_id` (string; FK→projects, indexed, nullable)<br>`actor` (string; required)<br>`action` (string; required)<br>`resource_type` (string; required)<br>`resource_id` (string; required)<br>`ip_address` (string; required)<br>`timestamp` (datetime; required) |
| `data_sources` | `id` (string; PK)<br>`project_id` (string; FK→projects, indexed, required)<br>`name` (string; required)<br>`kind` (string; required)<br>`record_count` (string; required)<br>`status` (enum; required) |
| `deployments` | `id` (string; PK)<br>`project_id` (string; FK→projects, indexed, required)<br>`version` (string; required)<br>`environment` (enum; required)<br>`status` (enum; required)<br>`deployed_by` (string; required)<br>`deployed_at` (datetime; required)<br>`commit` (string; required) |
| `evaluation_runs` | `id` (string; PK)<br>`project_id` (string; FK→projects, indexed, required)<br>`version` (string; required)<br>`date` (datetime; required)<br>`correctness` (float; required)<br>`faithfulness` (float; required)<br>`citation_accuracy` (float; required)<br>`avg_latency` (float; required) |
| `feedback_entries` | `id` (string; PK)<br>`project_id` (string; FK→projects, indexed, required)<br>`question` (text; required)<br>`sentiment` (enum; required)<br>`reason` (string; nullable)<br>`created_at` (datetime; required) |
| `integrations` | `id` (string; PK)<br>`project_id` (string; FK→projects, indexed, required)<br>`name` (string; required)<br>`type` (enum; required)<br>`status` (enum; required)<br>`last_sync` (datetime; required) |
| `knowledge_documents` | `id` (string; PK)<br>`project_id` (string; FK→projects, indexed, required)<br>`filename` (string; required)<br>`department` (string; required)<br>`classification` (enum; required)<br>`status` (enum; required)<br>`created_at` (datetime; required) |
| `requirements` | `id` (string; PK)<br>`project_id` (string; FK→projects, indexed, required)<br>`title` (string; required)<br>`type` (enum; required)<br>`priority` (enum; required)<br>`status` (enum; required)<br>`stakeholder` (string; required) |
| `workflows` | `id` (string; PK)<br>`project_id` (string; FK→projects, indexed, required)<br>`name` (string; required)<br>`status` (enum; required)<br>`last_run` (datetime; nullable)<br>`success_rate` (float; required) |
| `document_chunks` | `id` (string; PK)<br>`document_id` (string; FK→knowledge_documents, indexed, required)<br>`project_id` (string; FK→projects, indexed, required)<br>`classification` (enum; required)<br>`position` (int; required)<br>`content` (text; required)<br>`embedding` (text; required) |
| `workflow_runs` | `id` (string; PK)<br>`workflow_id` (string; FK→workflows, indexed, required)<br>`outcome` (enum; required)<br>`detail` (string; required)<br>`ran_at` (datetime; required) |

### 11.4 Constraints, validation, and ORM behavior

- **Unique:** `users.email`. **Indexed:** `users.email` and every `project_id` / `document_id` / `workflow_id` foreign key.
- **Required fields:** `NOT NULL` except `workflows.last_run`, `feedback_entries.reason`, and `audit_log_entries.project_id`.
- **Validation lives in the API layer.** Pydantic enforces enum membership and required fields. E-mail format, password strength, string lengths, and numeric ranges are **not** validated. No database check constraints exist.
- **Embeddings** are stored as JSON-encoded lists of 256 floats in `document_chunks.embedding` (text), which is what makes the same schema work on SQLite and PostgreSQL.
- **Cascades:** `KnowledgeDocument.chunks` and `Workflow.runs` are configured `cascade="all, delete-orphan"`, but no delete endpoint exists.

### 11.5 Migrations

Alembic is configured (`backend/alembic.ini`, `backend/alembic/env.py`) to read `DATABASE_URL` from the app settings. One migration exists: `5eff5670ee55_initial_schema.py`. Verified on SQLite and PostgreSQL 16:

```bash
alembic upgrade head      # apply
alembic current           # show the applied revision
alembic check             # confirm the models and migration agree (reported no drift)
```

Caveats:

- The app also calls `Base.metadata.create_all()` at startup and the seed script does the same, so on a database where those ran first, `alembic upgrade head` fails because the tables already exist. Either start from an empty database or mark it as migrated with `alembic stamp head`.
- On **PostgreSQL**, `alembic downgrade` drops the tables but **leaves the 18 enum types behind**, so a subsequent `upgrade` fails with `type "environment" already exists` (observed). See [§18](#18-troubleshooting-and-faq) for the verified workaround.

### 11.6 Seeding

`python -m app.seed` creates tables if needed, then loads the dataset described in [§6.6](#66-seed-data-and-demo-accounts) in one transaction. It is idempotent (it exits early when `org-gulfbridge` exists) and verified on both engines. Password hashes for the two demo users are generated at seed time with `bcrypt`.

---

## 12. Core Business Logic and Workflows

### 12.1 Registration and token issuance

```mermaid
flowchart TD
    A["POST /auth/register"] --> B{"E-mail already used?"}
    B -- yes --> C["409 Conflict"]
    B -- no --> D{"Organization name matches an existing one? ILIKE, case-insensitive"}
    D -- no --> E["Create organization org-xxxxxxxx; role = admin"]
    D -- yes --> F["Join that organization; role = employee"]
    E --> G["bcrypt-hash the password"]
    F --> G
    G -- "password over 72 bytes with bcrypt 5.x" --> H["500 Internal Server Error"]
    G --> I["Insert user and commit"]
    I --> J["Issue JWT with sub, role, exp; return 201"]
```

Business rules: the organization lookup uses `ILIKE` without escaping, so `%` and `_` in the submitted name act as wildcards (verified: `Gulf%` joined GulfBridge as an employee). Login performs the e-mail lookup and `bcrypt.checkpw`; any mismatch returns the same `401` message.

### 12.2 Retrieval and authorization

```mermaid
flowchart TD
    Q["Question plus caller: user loaded from the JWT subject, role read from the database"] --> R["allowed = classifications whose permitted roles include the caller's role"]
    R --> K{"Query contains salary, compensation, executive, or payroll AND Restricted is not in allowed?"}
    K -- yes --> X["Return restricted = true with an explanatory message. No search runs. Audit: RETRIEVAL_BLOCKED_UNAUTHORIZED or ASSISTANT_CHAT_BLOCKED"]
    K -- no --> E["Embed the query: 256-dimension hashing vector"]
    E --> S["SQL: chunks WHERE project_id = the path project AND classification IN allowed"]
    S --> C["Cosine similarity in Python; sort descending"]
    C --> T["Keep the top 3 with score greater than 0"]
    T --> O["Return restricted = false with the chunks"]
```

| Step | Detail |
|---|---|
| Start | `POST …/knowledge/search` or `POST …/assistants/chat` by an authenticated user |
| Validation and permission checks | Token → user; role → allowed classifications; keyword guard; SQL classification filter |
| Logic | `app/services/rag.py::retrieve` → `vector_store.search` (default `InMemoryCosineVectorStore`) |
| Database operations | One `SELECT` on `document_chunks` filtered by project and allowed classifications; one `INSERT` on `audit_log_entries` when blocked (search) or always (chat) |
| Result | `restricted`, `message`, and up to 3 chunks with `score` (rounded to 4 decimals) |
| Failure conditions | No candidates or all scores ≤ 0 → empty `chunks`; unknown project → empty `chunks` (no `404`); non-ASCII-only text → zero vectors → empty `chunks` |

Both layers were checked manually on SQLite and PostgreSQL for all three roles, including a restricted-topic question phrased **without** trigger words (an employee received only Public/Internal chunks; an admin received the Restricted chunk). Only the keyword layer and the admin/employee outcomes have automated tests.

### 12.3 Knowledge ingestion

```mermaid
flowchart TD
    U["POST …/knowledge/upload with file, department, classification"] --> D{"File decodes as UTF-8?"}
    D -- no --> E4["400 Bad Request"]
    D -- yes --> P["Insert document with status Processing"]
    P --> C["Split on blank lines; group paragraphs up to 600 characters; word-wrap longer paragraphs"]
    C --> M["Embed each chunk; insert chunk rows carrying the document's classification"]
    M --> S{"Any chunks produced?"}
    S -- yes --> I["Status Indexed"]
    S -- no --> PR["Status Processed"]
    I --> A["Commit; audit DOCUMENT_UPLOADED; return 201"]
    PR --> A
```

Failure conditions: a non-UTF-8 file returns `400`; an invalid `classification` returns `422`; an empty file succeeds with `Processed` and zero chunks (verified).

### 12.4 Assistant chat

```mermaid
flowchart TD
    M["POST …/assistants/chat with message"] --> R["Retrieve as in section 12.2"]
    R --> X{"Restricted?"}
    X -- yes --> RF["reply = refusal text; sources empty; generatedBy = mock"]
    X -- no --> K{"ANTHROPIC_API_KEY set?"}
    K -- no --> MK["reply = Based on filename: top chunk text, or a not-found message; generatedBy = mock"]
    K -- yes --> API["POST to the Anthropic Messages API with the numbered passages as system prompt"]
    API -- "HTTP success" --> CL["reply = model text; generatedBy = claude"]
    API -- "httpx.HTTPError" --> MK
    RF --> AU["Audit ASSISTANT_CHAT_BLOCKED or ASSISTANT_CHAT; return 200"]
    MK --> AU
    CL --> AU
```

The system prompt tells the model to answer only from the numbered passages, cite them (for example `[1]`), and say it does not know otherwise. The request uses `max_tokens` 500 and a 20-second timeout. The live branch is **not verified**.

### 12.5 Workflow runs, rollbacks, and evaluation runs

| Operation | Rule (as implemented) |
|---|---|
| **Run a workflow** | `succeeded = random() * 100 <= successRate`. Append a run with a fixed message; set `lastRun = now`; `draft` → `active`; `successRate = round((rate × existingRuns + (100 or 0)) / (existingRuns + 1), 1)`. Seeded workflows have no stored runs, so the **first run sets the rate to 100.0 or 0.0**. |
| **Roll back a deployment** | Insert a `healthy` deployment copying the target's `version`, `environment`, and `commit`; `deployedBy` = caller's display name; `deployedAt` = now. Unknown or other-project id → `404`. |
| **Run an evaluation** | From the latest run by date: `metric = min(metric + U(0.1, 1.2), 99.5)` for correctness, faithfulness, and citation accuracy (1 decimal); `avgLatency = max(avgLatency − U(0, 0.15), 0.6)` (2 decimals); version suffix incremented (`v1.9` → `v1.10`). With no prior run: 85.0 / 88.0 / 90.0 / 2.4 s as `v1.0`. |

---

## 13. Development Commands

### 13.1 Backend (run from `backend/`)

| Command | What it does | Status |
|---|---|---|
| `pip install -r requirements-dev.txt` | Installs runtime and test dependencies (use a virtual environment) | Verified in a clean venv |
| `python -m app.seed` | Creates tables if needed and loads the demo dataset (idempotent) | Verified on SQLite and PostgreSQL |
| `uvicorn app.main:app --reload` | Development server with auto-reload on port 8000 | Verified |
| `uvicorn app.main:app --host 0.0.0.0 --port 8000` | Production-style start (the `Dockerfile` command) | Verified on other ports |
| `pytest` / `pytest -v` | Runs the 17 tests | Verified |
| `pytest --cov=app --cov-report=term` | Tests with line coverage | Verified (85%) |
| `alembic upgrade head` | Applies migrations | Verified on SQLite and PostgreSQL |
| `alembic current` / `alembic check` | Shows the applied revision / detects model-vs-migration drift | Verified |
| `alembic stamp head` | Marks a database whose tables already exist as migrated | Verified (SQLite) |
| `alembic revision --autogenerate -m "message"` | Generates a migration after a model change | Used to create the initial migration; not re-run during documentation |
| `alembic downgrade base` | Reverts the schema | Verified on PostgreSQL — **leaves enum types behind** ([§11.5](#115-migrations)) |
| `docker compose up --build` | Starts `db`, `redis`, `api` | **Not verified** (no Docker) |

There is no configured linter, formatter, or static type checker for the backend.

### 13.2 Frontend (run from `frontend/`)

| Command | What it does | Status |
|---|---|---|
| `npm install` / `npm ci` | Installs dependencies (`npm ci` is reproducible from `package-lock.json`) | `npm ci` verified |
| `npm run dev` | `next dev` on port 3000 | Verified (the `next dev` binary served `/login` and `/dashboard`) |
| `npm run build` | `next build`: compiles, type-checks, and prerenders; **linting is skipped** | Verified |
| `npm run start` | `next start`: serves the production build (add `-- -p <port>` to change the port) | Verified |
| `npm run typecheck` | `tsc --noEmit` | Verified (exit code 0) |

There are no `lint` or `test` scripts.

---

## 14. Testing and Quality Assurance

### 14.1 Strategy and setup

The backend has an automated, API-level test suite (`backend/tests/`) built on FastAPI's `TestClient`. `tests/conftest.py` creates an **in-memory SQLite** database per test (with `StaticPool` so every request shares one connection), overrides the `get_db` dependency, and offers a `register(...)` factory fixture that returns auth headers. Tests exercise real behavior end to end (real hashing, real embeddings, real retrieval); only the network is absent, so the offline LLM fallback is what runs. The frontend has **no** automated tests.

```bash
cd backend && pytest -v                       # 17 tests
cd backend && pytest --cov=app --cov-report=term
cd frontend && npm run typecheck && npm run build
```

### 14.2 Test inventory (17 tests)

| File | Tests | Covers |
|---|---|---|
| `tests/test_auth.py` | 7 | Registration makes the first user of a new organization `admin`; a second user joining the same organization is `employee`; duplicate e-mail → `409`; wrong password → `401`; `/auth/me` requires a token and returns the user; demo login works on an unseeded database |
| `tests/test_projects.py` | 3 | Create and list a project; unknown project → `404`; creation requires authentication |
| `tests/test_workflows.py` | 2 | A run is recorded and a `draft` workflow becomes `active`; unknown workflow → `404` (the random outcome is asserted only to be `success` or `failed`) |
| `tests/test_knowledge_access_control.py` | 5 | Employee refused on a restricted topic (keyword layer); admin retrieves the Restricted chunk; employee retrieves a Public chunk; chat enforces the same refusal; chat answers normally with `generatedBy == "mock"` |

### 14.3 Coverage

Measured with `pytest --cov=app` during verification: **85% of 1,249 statements** (183 missed). The services at the heart of retrieval (`rag.py`, `embeddings.py`) are at 100%. Modules with notable gaps:

| Module | Coverage | What is not exercised |
|---|---|---|
| `app/seed.py` | 0% | The seed script (run manually instead) |
| `app/routers/evaluations.py` | 45% | `POST …/evaluations/run` |
| `app/routers/deployments.py` | 60% | `POST …/rollback` |
| `app/services/llm.py` | 60% | The live Anthropic call and its error path |
| `app/services/chunking.py` | 60% | Word-wrapping of paragraphs longer than the chunk limit |
| `app/core/deps.py` | 69% | Invalid-token paths and the unused `require_role` |
| `app/routers/{requirements,architecture,integrations,data_sources,feedback}.py` | 67% each | The `POST` handlers |
| `app/services/vector_store.py` | 84% | `PgVectorStore` |

<details>
<summary><strong>Full per-module coverage table</strong></summary>

| Name                          |    Stmts |     Miss |   Cover |
|------------------------------ | -------: | -------: | ------: |
| app/config.py                 |       19 |        0 |    100% |
| app/core/audit.py             |        9 |        0 |    100% |
| app/core/deps.py              |       26 |        8 |     69% |
| app/core/security.py          |       21 |        2 |     90% |
| app/database.py               |       14 |        4 |     71% |
| app/main.py                   |       31 |        3 |     90% |
| app/models/\_\_init\_\_.py    |       15 |        0 |    100% |
| app/models/architecture.py    |       16 |        0 |    100% |
| app/models/assistant.py       |       16 |        0 |    100% |
| app/models/audit.py           |       16 |        0 |    100% |
| app/models/data\_source.py    |       15 |        0 |    100% |
| app/models/deployment.py      |       18 |        0 |    100% |
| app/models/enums.py           |       91 |        0 |    100% |
| app/models/evaluation.py      |       16 |        0 |    100% |
| app/models/feedback.py        |       16 |        0 |    100% |
| app/models/integration.py     |       16 |        0 |    100% |
| app/models/knowledge.py       |       31 |        0 |    100% |
| app/models/organization.py    |       12 |        0 |    100% |
| app/models/project.py         |       15 |        0 |    100% |
| app/models/requirement.py     |       16 |        0 |    100% |
| app/models/user.py            |       17 |        0 |    100% |
| app/models/workflow.py        |       25 |        0 |    100% |
| app/routers/architecture.py   |       18 |        6 |     67% |
| app/routers/assistants.py     |       22 |        1 |     95% |
| app/routers/audit.py          |       11 |        1 |     91% |
| app/routers/auth.py           |       54 |        1 |     98% |
| app/routers/data\_sources.py  |       18 |        6 |     67% |
| app/routers/deployments.py    |       25 |       10 |     60% |
| app/routers/evaluations.py    |       31 |       17 |     45% |
| app/routers/feedback.py       |       18 |        6 |     67% |
| app/routers/integrations.py   |       18 |        6 |     67% |
| app/routers/knowledge.py      |       46 |        4 |     91% |
| app/routers/organizations.py  |       22 |        7 |     68% |
| app/routers/projects.py       |       28 |        1 |     96% |
| app/routers/requirements.py   |       18 |        6 |     67% |
| app/routers/workflows.py      |       38 |        0 |    100% |
| app/schemas/architecture.py   |       15 |        0 |    100% |
| app/schemas/assistant.py      |       17 |        0 |    100% |
| app/schemas/audit.py          |       10 |        0 |    100% |
| app/schemas/auth.py           |       20 |        0 |    100% |
| app/schemas/base.py           |        4 |        0 |    100% |
| app/schemas/data\_source.py   |       13 |        0 |    100% |
| app/schemas/deployment.py     |       11 |        0 |    100% |
| app/schemas/evaluation.py     |       10 |        0 |    100% |
| app/schemas/feedback.py       |       13 |        0 |    100% |
| app/schemas/integration.py    |       13 |        0 |    100% |
| app/schemas/knowledge.py      |       29 |        0 |    100% |
| app/schemas/organization.py   |        6 |        0 |    100% |
| app/schemas/project.py        |       14 |        0 |    100% |
| app/schemas/requirement.py    |       15 |        0 |    100% |
| app/schemas/workflow.py       |       14 |        0 |    100% |
| app/seed.py                   |       65 |       65 |      0% |
| app/services/chunking.py      |       30 |       12 |     60% |
| app/services/embeddings.py    |       21 |        0 |    100% |
| app/services/llm.py           |       30 |       12 |     60% |
| app/services/rag.py           |       29 |        0 |    100% |
| app/services/vector\_store.py |       32 |        5 |     84% |
| **TOTAL**                     | **1249** |  **183** | **85%** |

</details>

### 14.4 Not covered by automated tests

- The **SQL-level classification filter** in isolation, and the **`manager` role** — both were checked manually on SQLite and PostgreSQL ([Appendix A](#appendix-a-verification-log)), but nothing would fail automatically if they regressed.
- Behavior on **PostgreSQL** — the suite runs only on in-memory SQLite (`conftest.py` hard-codes it); the PostgreSQL path was verified by replaying a probe by hand.
- The live **Claude** call, Docker/Compose, upload edge cases (large files, non-Latin text), CORS, and token expiry (checked manually).
- The entire **frontend**: no unit, component, or end-to-end tests; ESLint is not configured. The checks that exist are the type check, the production build, and a manual request of every route.

### 14.5 Known warnings in the test output

`StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead` (harmless), and — with a current PyJWT — `InsecureKeyLengthWarning` because the default development secret is 25 bytes (see [§7.1](#71-backend-environment-variables)).

---

## 15. Security and Privacy

> [!WARNING]
> The controls below are real but narrow. The gaps in [§15.2](#152-gaps-verified-or-evident-from-the-code) mean the classification model protects data only when identities are provisioned by a trusted party — which this project does not do. Treat the backend as a demo.

### 15.1 Implemented controls

| Control | Implementation | How it was checked |
|---|---|---|
| Password storage | `bcrypt` with a per-password salt (`app/core/security.py`); the hash is never returned by the API | Login tests; response schemas |
| Signed, expiring tokens | HS256 JWT with `sub`, `role`, `exp` (default 60 min) | Expired token returned `401` |
| Authentication on data routes | `Depends(get_current_user)`; 29 of 33 operations require a bearer token | OpenAPI inventory; `401` examples |
| Authorization before retrieval | Keyword guard plus a classification filter inside the retrieval query ([§12.2](#122-retrieval-and-authorization)) | Automated tests (keyword layer, admin/employee); manual checks (SQL layer, `manager`) on SQLite and PostgreSQL |
| Role read from the database | Role changes take effect without re-login | Promoted an employee to manager and reused the same token |
| Input validation | Pydantic schemas: required fields and enum membership → `422` | Examples in [§10.4](#104-verified-examples) |
| CORS allow-list | `CORSMiddleware` with `CORS_ORIGINS` | Preflight from the allowed origin echoed it; a disallowed origin got `400` without an allow-origin header |
| Injection resistance | Database access goes through the SQLAlchemy ORM with bound parameters; the only raw SQL (unused `PgVectorStore`) also binds parameters | Code review |
| Secret handling | Configuration only via environment/`.env`; `.env` is git-ignored; `.env.example` contains no secrets | File review |
| Output encoding (frontend) | React escapes rendered text; `dangerouslySetInnerHTML` is not used | Source search |
| Audit trail | Selected actions are recorded ([§2.2.9](#229-audit-log)) | Audit examples |
| Dependency scanning | `pip-audit -r requirements.txt` | No known vulnerabilities at verification time; `npm audit` findings are listed below |

### 15.2 Gaps (verified, or evident from the code)

Fixes are **suggestions**, not implemented behavior.

| ID | Gap | Evidence | Suggested fix |
|---|---|---|---|
| S-1 | **Open registration grants `admin`.** Registering under a new organization name creates that organization and makes you its admin. | Verified: a new-organization registration returned `role: admin` | Invite-only onboarding or e-mail verification; never derive roles from client input |
| S-2 | **No tenant isolation.** Authorization uses the role only; `organization_id` is never checked on any route. | Verified: an admin of a freshly self-registered organization retrieved GulfBridge's Restricted chunk and read its audit log | Scope every query by the caller's organization/project membership |
| S-3 | **`POST /auth/demo` is unauthenticated and returns an admin token.** | Verified | Remove it, or enable only when an explicit `DEMO_MODE` setting is on |
| S-4 | **No role checks on writes.** `require_role` is unused. | Verified: an employee created a project and uploaded a document classified Restricted | Apply `require_role` (or per-resource policies) to creation, upload, workflow, rollback, and evaluation routes |
| S-5 | **Weak default signing key**, also set in `docker-compose.yml`; no startup guard. | `config.py`; PyJWT warning | Require a ≥ 32-byte secret outside dev and fail fast otherwise |
| S-6 | **Weak credential handling at registration.** E-mail format and password policy are not validated; passwords over 72 bytes cause a `500` with bcrypt 5.x. | Verified (`not-an-email` accepted; `500` for 100 characters) | Use `EmailStr`; enforce length limits and a password policy |
| S-7 | **No rate limiting, lockout, refresh tokens, logout, or revocation.** | Code review | Add rate limiting; short-lived access tokens with refresh and a revocation list |
| S-8 | **Restricted document metadata is visible.** `GET …/knowledge` lists every document's filename and department to any authenticated user. | Verified | Filter the list by the caller's clearance |
| S-9 | **Audit log weaknesses.** `ipAddress` is a constant; the actor is a display name; coverage is partial; chat messages and blocked queries (first 120 characters) are stored and readable by any authenticated user; nothing makes entries tamper-evident. | Verified (IP), code review | Record request IP and user id; restrict reads by role; extend coverage; consider append-only storage |
| S-10 | **Uploads are unconstrained.** No size or type limit; the file is read fully into memory; any user chooses the classification. | Code review | Enforce limits, content sniffing, and a role-based rule for who may assign classifications |
| S-11 | **The keyword guard is coarse.** It over-blocks (an employee asking about the leave policy for *executive assistants* was refused). The SQL filter, not the guard, is the real control. | Verified | Keep the filter authoritative; replace the guard with policy-based decisions |
| S-12 | **Container and Compose hygiene.** No `.dockerignore` (so `.env`, local `*.db`, and `.venv` can be copied into the image); the image runs as root; Compose publishes PostgreSQL (5432) and Redis (6379) on the host with default credentials. | File review (not executed) | Add `.dockerignore`, a non-root `USER`, and stop publishing data-store ports |
| S-13 | **Frontend dependency advisories.** `npm audit` reports 10 findings (1 critical, 7 high, 2 moderate), chiefly `next@14.2.35` and the Tailwind/PostCSS toolchain; fixes require semver-major upgrades (Next 16, Tailwind 4). | Verified (`npm audit`) | Plan the Next.js 15/16 migration (async route `params`) and Tailwind upgrade |
| S-14 | **Wildcards in the organization lookup.** `ILIKE` is used without escaping, so `Gulf%` joined GulfBridge. | Verified | Use exact, normalized matching |
| S-15 | **The frontend enforces nothing.** Forms don't authenticate and `(app)` routes are not protected. | Source review | Add real authentication when connecting to the API |

### 15.3 Handling secrets

Keep `JWT_SECRET_KEY` and `ANTHROPIC_API_KEY` out of version control and out of images. Generate keys with a cryptographic source ([§7.1](#71-backend-environment-variables)). The demo password in `seed.py` is public by design and must not be used anywhere that holds real data.

### 15.4 Privacy

- **Data stored:** user name, e-mail, role, organization, and a bcrypt hash; uploaded document text and its embeddings; audit entries (including the first 120 characters of chat messages and blocked queries); feedback text. There is no retention policy and no delete endpoint.
- **Outbound data:** when `ANTHROPIC_API_KEY` is set, the user's question and the retrieved passages the caller is cleared for are sent to Anthropic's API. Without a key, nothing leaves the process.
- **Demo data** is fictional; do not load real personal or confidential data into this system.

---

## 16. Integrations and External Services

### 16.1 Anthropic Messages API (optional)

- **Purpose:** produce a grounded, cited answer from retrieved passages ([§12.4](#124-assistant-chat)).
- **Integration point:** `generate_reply()` in `backend/app/services/llm.py`.
- **Configuration:** `ANTHROPIC_API_KEY`. The model (`claude-sonnet-4-6`), `max_tokens` (500), timeout (20 s), and API version header (`2023-06-01`) are constants in the file; the stored assistant configuration is not consulted.
- **Request:** `POST https://api.anthropic.com/v1/messages` with headers `x-api-key`, `anthropic-version`, `content-type: application/json`; body `{model, max_tokens, system, messages:[{role:"user", content:<question>}]}`, where `system` holds the numbered passages and answering rules.
- **Output:** text blocks of the response are joined into `reply`; `generatedBy` becomes `"claude"`.
- **Errors:** `httpx.HTTPError` (network failure, timeout, non-2xx status) falls back to the offline reply with `generatedBy: "mock"`; nothing is logged. Other failures (for example a malformed body) are not caught.
- **Status:** **Not verified live** — no key was available.

### 16.2 PostgreSQL

Selected by `DATABASE_URL=postgresql+psycopg2://…` (driver `psycopg2-binary`). Migration, seed, and the full API probe were verified on PostgreSQL 16.15; the only behavioral difference found was foreign-key enforcement ([§11.1](#111-overview)).

### 16.3 pgvector

The Compose file uses the `pgvector/pgvector:pg16` image, but the application never creates the extension or a vector column; retrieval scores JSON-stored embeddings in Python. `PgVectorStore` in `app/services/vector_store.py` is an unused sketch of the production path, and **it does not run as written**. Executed against PostgreSQL 16.15 with pgvector 0.6.0:

| Attempt | Result |
|---|---|
| As written, default schema | `column "embedding_vector" does not exist` |
| As written, after adding the column (steps below) | `operator does not exist: vector <=> numeric[]` — the query vector is passed as an array instead of being cast to `vector` |

The class also compares the `classification` column against enum **values** (`Public`), whereas PostgreSQL stores the member **names** (`public`). An ad-hoc recipe that worked in testing (not part of the repository):

```sql
CREATE EXTENSION IF NOT EXISTS vector;
ALTER TABLE document_chunks ADD COLUMN IF NOT EXISTS embedding_vector vector(256);
UPDATE document_chunks SET embedding_vector = embedding::vector;

-- :q is the Python embedding list rendered as text, e.g. str(embedding); :cls holds enum NAMES
SELECT id, 1 - (embedding_vector <=> CAST(:q AS vector)) AS score
FROM document_chunks
WHERE project_id = :pid AND classification::text = ANY(:cls)
ORDER BY embedding_vector <=> CAST(:q AS vector)
LIMIT :k;
```

With this query the top three chunks and their scores matched the default in-memory store for the test question. Wiring it in would also need a migration, keeping `embedding_vector` in sync on upload, and a decision in `get_vector_store()`.

### 16.4 Redis

Provisioned by `docker-compose.yml` and announced to the API through `REDIS_URL`, but **no application code imports or reads it**. It can be removed from the Compose file or put to use (for example rate limiting or token revocation).

### 16.5 Frontend ↔ backend

Not integrated. The groundwork exists — CORS already allows `http://localhost:3000`, and the JSON contract mirrors `frontend/lib/types.ts` — but the UI would need a fetch layer, token storage, and route protection.

---

## 17. Deployment and Production

### 17.1 What exists and what was verified

| Item | Exists | Verified |
|---|---|---|
| Backend `Dockerfile` (`python:3.12-slim`, installs `libpq-dev` and `gcc`, installs requirements, copies the source, runs Uvicorn on 8000) | Yes | No (no Docker) |
| `docker-compose.yml` with `db` (`pgvector/pgvector:pg16`, health check `pg_isready`, named volume), `redis`, and `api` (waits for `db` to be healthy; runs migrate → seed → serve) | Yes | YAML parses; the migrate → seed → serve sequence was verified on native PostgreSQL 16; containers were **not** run |
| Frontend production build and server | Yes (`npm run build`, `npm run start`) | Yes |
| Frontend container, hosting configuration, reverse proxy / HTTPS, CI/CD, backups | **No** | — |
| Health endpoint | `GET /health` (no Compose health check is defined for `api`) | Yes |

### 17.2 Production checklist (recommendations, none implemented)

1. Resolve the security gaps in [§15.2](#152-gaps-verified-or-evident-from-the-code) — especially S-1 through S-5 — before exposing the API.
2. Inject a strong `JWT_SECRET_KEY` from a secrets manager; set `CORS_ORIGINS` to your real origins.
3. Terminate HTTPS at a reverse proxy or platform load balancer; do not publish PostgreSQL or Redis ports.
4. Run `alembic upgrade head` as a deliberate release step against an empty or `stamp`ed database, not by relying on `create_all`.
5. Add a `.dockerignore`, a non-root user, and pinned dependency versions (the requirements use `>=`).
6. Add structured logging, metrics, and alerting; the app currently emits only Uvicorn's access log.
7. Back up PostgreSQL and test restores; the "rollback" feature in this project only appends a record.
8. Upgrade the frontend's Next.js (and Tailwind) to supported major versions ([S-13](#152-gaps-verified-or-evident-from-the-code)) and add a build/test pipeline.

### 17.3 Frontend hosting

`npm run build && npm run start` runs the production server (verified locally). Any host that can run a Node.js process or supports Next.js 14 can serve it; no platform configuration is included. Because the frontend needs no environment variables today, nothing else is required until it is connected to the API.

---

## 18. Troubleshooting and FAQ

"Observed" means the symptom occurred while building or verifying this project; "General" means standard guidance not observed here.

| Symptom | Likely cause and diagnosis | Fix | Type |
|---|---|---|---|
| `ERROR: Cannot uninstall PyJWT … installed by debian` | Installing into the system Python where a distribution package owns PyJWT | Use a virtual environment ([§6.3](#63-run-the-backend-sqlite-zero-configuration)) | Observed |
| `error: externally-managed-environment` from `pip` | Recent Debian/Ubuntu protect the system Python (PEP 668) | Use a virtual environment | Observed |
| `source: not found` | The shell is `sh`/`dash`, which lacks `source` | Use `. .venv/bin/activate` or run in bash/zsh | Observed |
| `.env` values ignored, or an unexpected `deployai.db` appears | `.env` and `sqlite:///./deployai.db` resolve relative to the **current working directory** | Run commands from `backend/` | Observed |
| `InsecureKeyLengthWarning` | The default development secret is 25 bytes (< 32 recommended) | Set a ≥ 32-byte `JWT_SECRET_KEY` | Observed |
| `401 Invalid or expired token` | Token older than `ACCESS_TOKEN_EXPIRE_MINUTES`, or the server restarted with a different secret | Log in again | Observed |
| Browser CORS error; preflight returns `400` | The page's origin is not in `CORS_ORIGINS` | Add it (comma-separated) and restart | Observed |
| `500` on `POST /auth/register` | Password longer than 72 bytes with bcrypt 5.x (`ValueError` in the server log) | Use a shorter password (code fix suggested in [S-6](#152-gaps-verified-or-evident-from-the-code)) | Observed |
| `500` when creating a record under an unknown project (PostgreSQL) | `ForeignKeyViolation`; project ids are not validated (SQLite silently creates an orphan row) | Use a valid `project_id` | Observed |
| `alembic upgrade head` → `table organizations already exists` | The tables were created earlier by the seed script or app startup (`create_all`) | Start from an empty database, or run `alembic stamp head` | Observed |
| `alembic upgrade head` → `type "environment" already exists` (PostgreSQL) | `alembic downgrade` leaves the enum types behind | Reset the schema — **this deletes all data**: `DROP SCHEMA public CASCADE; CREATE SCHEMA public;` — then `alembic upgrade head` (verified) | Observed |
| An Arabic (or other non-Latin) document is `Indexed` but never retrieved | The tokenizer matches ASCII letters/digits only, so such text embeds to a zero vector | Use a real multilingual `EmbeddingProvider` | Observed |
| The top result doesn't answer the question | Hashing embeddings capture word overlap, not meaning | Swap in a real embedding model | Observed |
| `curl http://localhost:3000/` returns `307` but nothing is followed | The root page's redirect is delivered in the response body for the browser runtime; there is no `Location` header | Request `/login` directly in scripts and health checks | Observed |
| `StarletteDeprecationWarning` about `httpx` in test output | Starlette's test client prefers `httpx2` | Harmless; can be ignored | Observed |
| `npm audit` reports vulnerabilities | See [S-13](#152-gaps-verified-or-evident-from-the-code) | Plan major upgrades | Observed |
| `Connection refused` to PostgreSQL | The server is not running, or the URL/port is wrong | Start PostgreSQL; check `DATABASE_URL` | General |
| `Address already in use` | Port 8000 or 3000 is taken | `uvicorn … --port 8001`; `npm run dev -- -p 3001` | General |
| Docker Compose problems; a warning about the top-level `version` key | Compose was **not run** here; recent Compose versions ignore `version` and may warn | Remove the key if it warns | General |

### FAQ

**Is the frontend connected to the backend?** No. The frontend renders its own mock data; [§16.5](#165-frontend--backend) describes what connecting them would take.

**Why can an employee upload a Restricted document?** No endpoint checks roles ([S-4](#152-gaps-verified-or-evident-from-the-code)). Employees still cannot *retrieve* it.

**How do I get a `manager` user?** Edit the database: `UPDATE users SET role = 'manager' WHERE email = '…';` (see [§8.4](#84-role-specific-workflows)).

**Can I use real documents?** Not safely, and not in formats other than UTF-8 text; see [§15](#15-security-and-privacy) and [§19](#19-known-limitations-and-roadmap).

**How do I replace the hashing embeddings?** Implement `EmbeddingProvider` (`embed(text) -> list[float]`) and return it from `get_embedding_provider()` in `app/services/embeddings.py`. Existing stored vectors would have to be recomputed because their dimensions and meaning would differ.

**Can I run the tests against PostgreSQL?** Not as shipped: `tests/conftest.py` hard-codes in-memory SQLite.

**Why is there a Redis service?** It was provisioned for future use and is currently unused.

**How do I reset the demo data?** SQLite: delete `backend/deployai.db` and run `python -m app.seed`. PostgreSQL: reset the schema as above, `alembic upgrade head`, then seed.

**Why do the two halves show different leave-policy numbers?** They carry separately authored illustrative text ([§1.7](#17-about-the-fictional-customer-and-the-demo-data)).

---

## 19. Known Limitations and Roadmap

### 19.1 Known limitations

Security limitations are numbered **S-1…S-15** in [§15.2](#152-gaps-verified-or-evident-from-the-code). The rest:

| ID | Area | Limitation |
|---|---|---|
| L-1 | Integration | The frontend is not connected to the backend; its widgets simulate retrieval with hard-coded rules and fixed scores, and its demo content differs from the backend seed. |
| L-2 | Frontend | No authentication or session; the root redirect to `/login` is client-side (HTTP 307 without a `Location` header); `Rollback`, `Regenerate`, and `New Organization` buttons do nothing; any project id renders the same project; dashboard figures are static; English only (no i18n library); the UI was served and requested route by route but **not exercised in a browser**. |
| L-3 | Retrieval | Hashing embeddings (weak semantics); ASCII-only tokenization (Arabic is not retrievable); no relevance threshold; chunking splits on blank lines and a 600-character limit only. In the example run, the top chunk for "How many annual leave days do I get?" was the carry-over chunk, not the accrual chunk. |
| L-4 | Assistant | The live Claude path was never executed; stored assistant settings (model, temperature, citation mode) have no effect on chat. |
| L-5 | Simulation | Workflow and evaluation runs are simulated; the first workflow run overwrites the seeded success rate; paused workflows can be run. |
| L-6 | API surface | No update, delete, or pagination; nested routes do not validate `project_id` (orphans on SQLite, `500` on PostgreSQL); `GET …/workflows/{id}/runs` returns `[]` for unknown ids; no way to assign `manager`. |
| L-7 | Data | SQLite timestamps carry no timezone offset; SQLite does not enforce foreign keys. |
| L-8 | Migrations | PostgreSQL downgrade leaves enum types behind; `create_all` at startup overlaps with Alembic. |
| L-9 | Dead or broken code | `PgVectorStore` fails as written and is not wired in; `email-validator` and the `pgvector` Python package are unused; Redis is provisioned but unused; `require_role` is unused; `Uploaded`/`Failed` document statuses are never set. |
| L-10 | Operations | Docker/Compose never executed; no CI/CD, structured logging, metrics, or backups; ingestion is synchronous. |
| L-11 | Testing | Backend tests run only on in-memory SQLite; rollback, evaluation runs, record `POST`s, the SQL filter, and the `manager` role lack automated tests; no frontend tests or linting. |

### 19.2 Roadmap (suggestions, not commitments)

**Short term**
1. Close S-1 through S-6: remove or gate `/auth/demo`, stop granting `admin` on registration, enforce organization scoping and `require_role`, validate e-mail/password input, validate `project_id` (return `404`).
2. Add automated tests for the SQL classification filter, the `manager` role, rollback, and evaluation runs; run the suite on PostgreSQL in CI.
3. Fix or delete `PgVectorStore`; remove unused dependencies and the unused Redis service.
4. Add a `.dockerignore` and run the container as a non-root user.

**Medium term**
5. Connect the frontend to the API: a typed fetch layer, token handling, route protection, and shared contract tests.
6. Record real request IPs and user ids in the audit log; add update/delete and pagination where needed.
7. Add CI (tests, `tsc`, `next build`, `pip-audit`, `npm audit`) and screenshots/e2e tests for the UI.
8. Upgrade Next.js and Tailwind to supported majors ([S-13](#152-gaps-verified-or-evident-from-the-code)).

**Long term**
9. Replace hashing embeddings with a multilingual embedding model (including Arabic) and the pgvector path with a migration and tests.
10. Real document parsing (PDF/DOCX), asynchronous ingestion, a real workflow engine and evaluation harness, observability, and rate limiting.

---

## 20. Contributing

No `CONTRIBUTING` file, issue templates, code of conduct, or repository URL exist, so whether outside contributions are welcome is **To be confirmed** by the project owner. If you want to work on the project, this is a *suggested* workflow (not an existing policy):

1. Clone `<repository-url>` (placeholder) and create a branch: `git checkout -b feature/short-description`.
2. Backend changes: keep routers thin and logic in `app/services/`; use typed SQLAlchemy models and `CamelModel` schemas; add or update tests; run `pytest`. After model changes run `alembic revision --autogenerate -m "…"` and `alembic check`.
3. Frontend changes: run `npm run typecheck && npm run build`; keep `lib/types.ts` aligned with the backend schemas.
4. Update this README and the component READMEs when behavior changes, and keep every claim verifiable.
5. Open a pull request that says what changed and how you verified it. Report bugs or feature ideas through the issue tracker once one exists (**To be confirmed**).

---

## 21. License, Credits, and Contact

- **License:** none. The repository contains no `LICENSE` file, so no license is granted. Choosing one (for example MIT or Apache-2.0 for a portfolio project) is a decision for the owner — **To be confirmed**.
- **Maintainers / contact:** **To be confirmed.** No contact information is recorded in the project files.
- **Origin:** built from a product requirements document supplied by the project author; that document is not part of this repository.
- **Third-party software:** FastAPI, Starlette, Uvicorn, Pydantic, SQLAlchemy, Alembic, PyJWT, bcrypt, httpx, pytest (backend); Next.js, React, TypeScript, Tailwind CSS, Recharts, lucide-react, React Hook Form, and Zod (frontend). Each is governed by its own license.
- **Services:** the Anthropic Messages API is an optional external service used only when you provide a key.

---

## Appendix A. Verification Log

Environment: Linux (Ubuntu 24.04 packages), Python 3.12.3, Node.js 22.22.2, PostgreSQL 16.15 with pgvector 0.6.0 (native install), run in October 2026. **Not available:** Docker, a web browser, an Anthropic API key, other operating systems, other Python or Node versions.

| # | Check | Method | Result |
|---|---|---|---|
| 1 | Backend tests | `pytest` on the system Python and in a clean venv | 17 passed in both |
| 2 | Coverage | `pytest --cov=app` | 85% (1,249 statements) |
| 3 | Clean install | New venv, `pip install -r requirements-dev.txt` | Succeeded; versions in [§3](#3-technology-stack) |
| 4 | Dependency audit (Python) | `pip-audit -r requirements.txt` | No known vulnerabilities |
| 5 | Route inventory | `app.openapi()` | 33 operations, 27 paths; 4 public |
| 6 | Migration on SQLite | `alembic upgrade head`; `alembic check` | Applies; no drift |
| 7 | Migration on PostgreSQL | Same, plus `alembic downgrade base` | Applies; no drift; downgrade leaves 18 enum types and a later upgrade fails; schema-reset workaround verified |
| 8 | Seed idempotency | `python -m app.seed` twice | Second run skips (both engines) |
| 9 | Live API probe (SQLite) | Uvicorn plus about 70 requests across every route group | Behavior documented in §§2, 9, 10 |
| 10 | Same probe on PostgreSQL | Replayed unchanged | Identical status codes, except a `POST` to a nonexistent project (`201` on SQLite, `500` on PostgreSQL) |
| 11 | Access control by role | Admin, employee, and a database-promoted manager; Confidential document; restricted topic phrased without trigger words | Matches [§9.2](#92-retrieval-clearance-the-only-role-dependent-behavior) on both engines |
| 12 | Cross-organization access | A freshly self-registered organization's admin queried GulfBridge | Restricted chunk and audit log returned ([S-2](#152-gaps-verified-or-evident-from-the-code)) |
| 13 | Token expiry; `.env` resolution | `ACCESS_TOKEN_EXPIRE_MINUTES=-1`; running from two directories | `401` for an expired token; `.env` read from the working directory only |
| 14 | CORS | Preflight from allowed and disallowed origins | Allowed origin echoed; disallowed → `400` |
| 15 | `PgVectorStore` | Executed against pgvector 0.6.0 | Fails as written; corrected SQL matched the default store ([§16.3](#163-pgvector)) |
| 16 | Documented cURL examples | A script ran all 40 example blocks against a live server | Every expected status returned |
| 17 | Quick start | Clean venv: install, tests, seed, `uvicorn --reload`, `/health`, `/docs` | Worked |
| 18 | Frontend build | `npm ci`, `npm run typecheck`, `npm run build` | Succeeded; 23 routes including the automatic `_not-found` |
| 19 | Frontend production server | `next start`, request each route | 22 authored routes returned expected content; `/` and `/projects/<id>` respond `307` (the root redirect is carried in the response body, not a `Location` header — see [§2.1.1](#211-authentication-screens)); an unknown project id renders; an unknown path returns `404` |
| 20 | Frontend dev server | `next dev` | `/login` and `/dashboard` returned `200` |
| 21 | Frontend audit and static checks | `npm audit`; searches for env/network/token use and `dangerouslySetInnerHTML` | 10 advisories; none of the searched patterns present |
| 22 | This document | Script checks for internal links and anchors, referenced paths, code fences, table shape, and Mermaid syntax (the Mermaid parser) | Passed |

**Not verified:** Docker/Compose execution; the live Anthropic call; rendering and behavior in a browser; Windows/macOS; Python below 3.12 and Node versions other than 22; performance and load behavior; PostgreSQL with a non-superuser role.
