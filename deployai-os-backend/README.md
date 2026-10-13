# DeployAI OS — Backend

Reference FastAPI backend for **DeployAI OS**, the enterprise AI deployment
platform portfolio project. This is the backend half of the same project as
[`deployai-os-frontend`](../deployai-os-frontend) — same customer
(GulfBridge Professional Services), same record IDs, same PRD.

Where the frontend phase shipped a full UI over mock data, this phase ships
a real, running API: real auth, a real (if lightweight) RAG pipeline, and a
genuine, tested implementation of the platform's core safety property —
**a user can never retrieve a document they aren't cleared for, because the
authorization check runs before the search, not after** (ADR-003).

## Quick start (zero config)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python -m app.seed              # loads the GulfBridge demo dataset
uvicorn app.main:app --reload   # http://localhost:8000/docs
```

That's it — no database server, no API keys. `DATABASE_URL` defaults to a
local SQLite file, and the assistant/retrieval endpoints fall back to
deterministic mock responses with no `ANTHROPIC_API_KEY` set.

**Demo accounts** (seeded by `app.seed`, password for both:
`GulfBridge!Demo1`):

| Role     | Email                                  |
|----------|-----------------------------------------|
| admin    | `demo.engineer@gulfbridge.example`      |
| employee | `employee.demo@gulfbridge.example`      |

Or skip credentials entirely: `POST /auth/demo` mirrors the frontend's
"Continue as Demo Engineer" button and hands back a token directly.

## Going to production: Docker Compose

```bash
cp .env.example .env   # optionally add a real ANTHROPIC_API_KEY
docker compose up --build
```

This provisions real Postgres (via the `pgvector/pgvector` image, so the
extension is present), Redis, and the API — running Alembic migrations and
the seed script automatically before serving.

## Architecture highlights

- **Auth**: JWT bearer tokens, `bcrypt` password hashing. First user to
  register under a new organization name becomes its `admin`; anyone
  registering under an existing one joins as `employee`.
- **Authorize-before-retrieval (ADR-003)**, for real: `app/services/rag.py`
  checks the querying user's role against each document's classification
  *before* any similarity search runs — enforced twice, deliberately
  redundantly: a keyword check on the query short-circuits the obvious
  cases, and the vector store's own SQL query filters by allowed
  classifications regardless, so a chunk above the user's clearance is
  never loaded, let alone scored or returned. See
  `tests/test_knowledge_access_control.py` for the tests that hold this to
  account against the real pipeline (upload → embed → authorize →
  retrieve), not a mocked stand-in.
- **Swap-able vector storage (ADR-001)**: `app/services/vector_store.py`
  defines a `VectorStore` interface. The default `InMemoryCosineVectorStore`
  scores candidates in Python and works identically on SQLite or Postgres —
  it's what the tests and default setup use. `PgVectorStore` is a complete,
  correct reference implementation of the production path (pushing ANN
  search into Postgres via pgvector's `<->` operator), included but not
  live-tested here — see "Known simplifications" below.
- **Embeddings without external calls**: `app/services/embeddings.py` uses
  feature hashing (the "hashing trick") — a real, deterministic,
  dependency-free technique — rather than a trained model. It's enough to
  power genuine retrieval for a demo-sized dataset; swap in Voyage AI,
  OpenAI, or similar behind the same `EmbeddingProvider` interface for
  production-grade semantic search.
- **Assistant replies**: `app/services/llm.py` calls the real Anthropic
  Messages API when `ANTHROPIC_API_KEY` is set (grounded in retrieved
  chunks, instructed to cite them or say it doesn't know), and falls back
  to a deterministic mock otherwise. Restricted queries never reach the
  model at all.
- **Audit logging**: every document upload, retrieval block, chat turn,
  workflow run, and deployment rollback writes an `AuditLogEntry` via
  `app/core/audit.py`.

## API

Full interactive docs at `/docs` once running. Routes follow the same
resource nesting as the frontend's URLs — `/projects/{project_id}/knowledge`,
`/projects/{project_id}/workflows`, etc. JSON keys are camelCase on the wire
(`projectId`, `successRate`) via a shared Pydantic base
(`app/schemas/base.py`), matching the interfaces in the frontend's
`lib/types.ts` with no translation layer needed on either side.

## Testing

```bash
pytest -v
```

17 tests, all exercising real behavior against an isolated in-memory SQLite
database (no mocking of the RAG or access-control logic) — auth and role
assignment, project CRUD, workflow run simulation, and the full
upload-to-retrieval access-control path for both an authorized admin and a
blocked employee, through both the retrieval-tester and assistant-chat
endpoints.

## Known simplifications

Documented deliberately, the same way the frontend's README flags its own
sandbox-driven deviations:

- **Embeddings are hashing-based, not a trained model** (see above) — real
  semantic understanding needs a real embedding provider.
- **`PgVectorStore` is a reference implementation, not exercised by the test
  suite** — it targets a native `vector` column that the default schema
  doesn't create. Provisioning it: add a migration with
  `op.execute("CREATE EXTENSION IF NOT EXISTS vector")` plus a
  `document_chunks.embedding_vector vector(256)` column, backfill it from
  the existing JSON column, and switch `get_vector_store()` to return
  `PgVectorStore()` when `settings.is_postgres`.
- **No strict multi-tenant read isolation** — any authenticated user can
  list any organization or project. This matches the platform's own
  framing (an internal tool for the team *deploying* AI to customers, not a
  customer-facing self-service portal), but a real multi-tenant product
  would scope reads by organization too.
- **CRUD depth varies by resource** — the entities with real, differentiated
  behavior (knowledge, assistants, workflows, deployments) got the most
  attention; simpler reference data (requirements, architecture decisions,
  integrations, data sources) support list + create, following the same
  pattern PATCH/DELETE would extend if needed.
- **Workflow runs and evaluation runs are simulated**, not backed by a real
  execution or eval harness — `POST .../workflows/{id}/run` and
  `POST .../evaluations/run` produce a plausible outcome (weighted by
  trailing success rate, or nudged metrics) rather than doing real work.
  Same phase-boundary as the frontend's own "next steps" list.
- **Document ingestion accepts UTF-8 text only** — real PDF/DOCX extraction
  is a drop-in addition ahead of the decode step in
  `routers/knowledge.py::upload_document`; nothing downstream changes.

## Project structure

```
app/
  main.py            FastAPI app, CORS, router wiring, table creation on startup
  config.py          Settings (env-driven, all defaults work with zero config)
  database.py        SQLAlchemy engine/session
  seed.py            Loads the GulfBridge demo dataset (idempotent)
  models/            SQLAlchemy models — one file per entity, enums.py shared
  schemas/           Pydantic request/response models (camelCase on the wire)
  core/
    security.py      Password hashing, JWT encode/decode
    deps.py           get_current_user, require_role
    audit.py           log_action helper
  services/
    embeddings.py     EmbeddingProvider + hashing-trick default
    vector_store.py   VectorStore interface + in-memory and pgvector implementations
    chunking.py       Document -> chunk splitting
    rag.py             Authorize-before-retrieval retrieval pipeline
    llm.py             Real Claude call + mock fallback for assistant replies
  routers/            One file per resource, thin — logic lives in services/
alembic/              Migrations (initial schema already generated)
tests/                pytest suite (see above)
docker-compose.yml     Postgres+pgvector, Redis, api
```

## Next steps

Per the same phased roadmap the frontend's README follows: real document
extraction (PDF/DOCX), a real embedding provider, the pgvector production
path switched on, a real workflow execution engine, and wiring the frontend
itself over to these endpoints in place of `lib/mock-data.ts`.
