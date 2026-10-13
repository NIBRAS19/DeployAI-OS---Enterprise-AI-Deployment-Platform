# DeployAI OS — Frontend (Phase 1 + Flagship Modules)

Reference implementation based on a simulated enterprise AI deployment engagement. This is the frontend for **DeployAI OS**, built with Next.js 14 (App Router), TypeScript, and Tailwind CSS, following the PRD's recommended stack.

## What's here

- Full authentication UI (login/register) using React Hook Form + Zod
- App shell: sidebar navigation, topbar, and a 14-tab project sub-navigation matching the PRD's module list
- Dashboard with platform-wide stats and a request-volume chart
- A project workspace for the fictional customer **GulfBridge Professional Services**, including:
  - **Overview** — deployment lifecycle stepper + architecture diagram
  - **Discovery** — business goal, pain points, constraints, success metrics, timeline
  - **Requirements** — requirements table
  - **Architecture** — Architecture Decision Records (ADRs)
  - **Integrations** & **Data Sources** — connection status cards/tables
  - **Knowledge Base** — document table + a working retrieval tester (ask about "annual leave" or "travel reimbursement" for ranked, cited chunks; ask about "executive compensation" to see an authorize-before-retrieval refusal)
  - **Assistants** — assistant configuration + a working chat preview implementing the PRD's demo scenario (cited answers, refusal on restricted topics)
  - **Workflows** — visual workflow canvas (static) + execution table
  - **Deployments** — environment health cards + deployment history with rollback UI
  - **Monitoring** — latency, error rate, and AI cost charts
  - **Feedback** — feedback stats + top-issues chart
  - **Evaluations** — evaluation run history showing score improvement across versions
  - **Audit Log** — audit event table

All data is mocked in `lib/mock-data.ts` — there is no backend yet. Swap that file's exports for real API calls (e.g. via TanStack Query against the FastAPI service from the PRD) once the backend exists.

Two deliberate deviations from the PRD's exact stack, both for sandbox reasons rather than design ones: UI primitives (`components/ui/*`) are hand-rolled shadcn-style equivalents instead of the shadcn CLI (no registry access in this environment — swap in real shadcn/ui anytime), and fonts use the system stack instead of `next/font/google` (no Google Fonts access here).

**Dependency note:** Next.js is pinned to `14.2.35`, the latest patch on the 14.x line, to pick up security fixes released after `14.2.5`. `npm audit` will still flag advisories that are only fully resolved on Next.js 15/16 — those majors change route `params` from a plain object to a `Promise` (among other breaking changes), which every page and layout here would need to be rewritten around. Worth doing before any real deployment; left as-is here so the phased build could stay in scope.

## Running it

\`\`\`bash
npm install
npm run dev
\`\`\`

Open http://localhost:3000 — it redirects to `/login`. Use "Continue as Demo Engineer" to skip straight to the dashboard.

## What's next (per the PRD's phased roadmap)

This covers the frontend slice of Phase 1 (Foundation) plus flagship pieces of Phases 3/4/6/7/8 — UI only, no backend:

1. **FastAPI backend** — auth, multi-tenant Postgres models, RBAC middleware, the REST API in PRD §49
2. **Real RAG pipeline** — upload → parse → chunk → embed → pgvector, wired to the Knowledge Base and Assistant pages
3. **Real integrations** — WhatsApp Cloud API, email ingestion, webhooks
4. **Workflow execution engine** — make the canvas editable and backed by real runs
5. **Deployment engine** — real environment promotion + rollback, backed by CI/CD
6. **Wire TanStack Query** to replace the static mock-data imports once the API exists

The component structure (`components/ui/*`, `lib/types.ts`) is set up so new modules reuse the same primitives — tell me which phase to build next.
