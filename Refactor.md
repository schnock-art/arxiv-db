# Refactor Plan: API + Data Platform Evolution

## Purpose

This document defines the **outcomes** and **roadmap** for refactoring the current project into a robust, extensible platform that can evolve from a paper metadata API into a **knowledge graph platform** accessible by AI agents and automation scripts.

---

## Vision (Target State)

Build a platform that:

1. Ingests and curates arXiv paper metadata (and later additional sources).
2. Stores high-quality canonical entities and relationships.
3. Exposes an API for:
   - human users,
   - internal services,
   - AI agents/tools.
4. Supports retrieval patterns useful for agentic systems:
   - structured lookup,
   - relationship traversal,
   - semantic/hybrid search.

---

## Desired Outcomes

## O1. Better maintainability
- Decouple API routes from persistence details.
- Introduce clear boundaries: API layer, domain/service layer, repository/data layer.
- Reduce hidden runtime coupling and improve testability.

## O2. Stronger data integrity
- Move core operational storage to **PostgreSQL + SQLAlchemy/SQLModel**.
- Enforce constraints (PK/unique/indexes/foreign keys) and controlled migrations.
- Preserve stable API contracts while improving internal consistency.

## O3. Knowledge graph readiness
- Introduce a graph-capable data model for entities and relationships (papers, authors, topics, citations, institutions, venues).
- Enable query patterns beyond CRUD: neighborhood exploration, path discovery, relevance ranking.
- Keep graph model interoperable with API and analytics layers.

## O4. AI-agent accessibility
- Provide agent-friendly APIs:
  - predictable schemas,
  - filterable endpoints,
  - pagination + cursors,
  - provenance metadata,
  - optional tool-friendly query endpoint(s).
- Add auth/rate limiting/observability suitable for non-human clients.

## O5. Reliability and delivery velocity
- Add CI gates for linting/tests/type checks.
- Add migration and deployment discipline.
- Improve telemetry and error handling.

---

## Non-Goals (for initial refactor)

- Building a full autonomous multi-agent orchestration system in v1.
- Rewriting every module from scratch.
- Shipping advanced graph ML features before core data quality is stable.

---

## Architecture Direction

## Data stores (recommended staged approach)

### Stage 1 (Primary store modernization)
- **PostgreSQL** as source of truth for transactional API operations.
- SQLAlchemy/SQLModel for ORM + schema management.
- Alembic for migrations.

### Stage 2 (Knowledge graph support)
Choose one path depending on complexity/performance needs:

1. **Postgres-first graph model** (tables for nodes/edges + recursive CTEs)
   - Fastest to implement, fewer moving parts.
2. **Dual-store model** (Postgres + graph DB such as Neo4j)
   - Better native graph traversals; added operational complexity.

Recommendation: start with Postgres-first graph primitives, then introduce a dedicated graph DB only when traversals/scale justify it.

---

## Target Domain Model (incremental)

Core entities:
- Paper
- Author
- Topic
- Category
- Institution
- Venue/Journal

Core relationships:
- `AUTHORED_BY` (Paper -> Author)
- `CITES` (Paper -> Paper)
- `HAS_TOPIC` (Paper -> Topic)
- `BELONGS_TO_CATEGORY` (Paper -> Category)
- `AFFILIATED_WITH` (Author -> Institution)

Include provenance fields for trust/replay:
- `source_system`
- `source_id`
- `ingested_at`
- `last_observed_at`
- optional confidence/quality score

---

## Refactor Roadmap

## Phase 0 — Alignment & contracts (1 sprint)

**Goals**
- Freeze external API contract where possible.
- Define architecture boundaries and coding conventions.

**Deliverables**
- Repository interface definitions (`PaperRepository`, later graph-oriented repositories).
- ADR(s) documenting storage decisions.
- Refined API contract doc with compatibility guarantees.

**Exit criteria**
- Team agrees on migration sequence and backward compatibility strategy.

---

## Phase 1 — Persistence abstraction (1 sprint)

**Goals**
- Remove direct DB access from route handlers.

**Deliverables**
- Service + repository layer introduced.
- Routes call services only.
- Existing behavior covered by tests.

**Exit criteria**
- Swapping repositories does not require route changes.

---

## Phase 2 — PostgreSQL adoption (1–2 sprints)

**Goals**
- Move operational CRUD storage from MongoDB to PostgreSQL.

**Deliverables**
- SQLModel/SQLAlchemy models.
- Alembic migrations.
- Postgres-backed repository implementation.
- Data migration/backfill script from Mongo-compatible documents.

**Exit criteria**
- CRUD endpoints pass parity tests.
- Production-ready migrations and rollback plan exist.

---

## Phase 3 — Knowledge graph baseline (1–2 sprints)

**Goals**
- Introduce graph relationships and traversal-friendly APIs.

**Deliverables**
- Node/edge schema (Postgres-first).
- Relationship ingestion pipeline (authors/topics/citations).
- Endpoints for neighborhood and relation queries.

**Exit criteria**
- Can answer: “show related papers by topic/citations/authors.”

---

## Phase 4 — Agent-facing API hardening (1 sprint)

**Goals**
- Make API safe/reliable for automated clients and AI agents.

**Deliverables**
- Auth (API keys/OAuth2, depending on deployment model).
- Rate limits and request quotas.
- Cursor pagination and consistent filter/sort semantics.
- Error taxonomy and idempotency guidance.

**Exit criteria**
- Agent integrations can run unattended with predictable behavior.

---

## Phase 5 — Search and relevance (optional, iterative)

**Goals**
- Improve discovery quality for humans and agents.

**Deliverables**
- Full-text + metadata search (Postgres + optional search index).
- Optional embeddings + hybrid retrieval.
- Ranking heuristics (recency/citation/topic similarity).

**Exit criteria**
- Retrieval quality supports downstream agent tasks.

---

## Test-Driven Development (TDD) Execution Model

We will execute the refactor using a strict **test-first** workflow to guarantee behavior stability during architectural and storage changes.

### TDD principles for this refactor
- **Red → Green → Refactor** on each change slice (endpoint/service/repository).
- Write tests for expected behavior **before** implementation changes.
- Preserve public API compatibility unless explicitly versioned and documented.
- Treat test suite pass state as a release gate for each phase.

### Test pyramid for this project

1. **Contract/API tests** (highest priority first)
   - Validate request/response schema, status codes, and error payloads for `/paper` and future `/v1/*` endpoints.
   - Lock current external behavior before persistence migration.

2. **Service/Repository unit tests**
   - Define repository semantics (create/get/list/update/delete) independent of concrete storage backend.
   - Reuse the same test matrix for Mongo-compatible implementation and Postgres implementation.

3. **Database integration tests**
   - Run against ephemeral Postgres with migrations applied.
   - Validate constraints, indexes, and transaction behavior.

4. **Migration/parity tests**
   - Assert parity between legacy and new repositories for core CRUD use-cases.
   - Add backfill checks (counts, field parity, sampling validations).

### Phase-aligned TDD gates

- **Phase 0**
  - Add baseline contract tests that describe current behavior.

- **Phase 1**
  - Add repository interface tests first; only then implement service + repository abstraction.

- **Phase 2**
  - Implement Postgres repository only after parity tests are green for the abstraction layer.
  - Add integration tests for migrations and data constraints.

- **Phase 3+**
  - Add graph traversal tests first (neighbors/path queries), then implement graph APIs.
  - Introduce agent-oriented non-functional tests (pagination determinism, rate-limit behavior, idempotency where applicable).

### CI quality gates
- Lint + type checks.
- Unit + contract tests on every PR.
- Integration tests (including migrations) on protected branches/nightly as needed.
- No merge when parity tests fail during migration window.

## API Strategy for AI Agents and Scripts

Design principles:
- Stable versioned endpoints (`/v1/...`).
- Explicit machine-oriented schemas and examples.
- Deterministic pagination/sorting.
- Strong observability headers (request IDs, latency hints where possible).

Suggested endpoint families:
- `/papers`
- `/authors`
- `/topics`
- `/relations`
- `/graph/neighbors`
- `/graph/path`
- `/search`

Agent utility features:
- Bulk fetch endpoints for context hydration.
- “since timestamp” incremental sync endpoints.
- Provenance and confidence in response payloads.

---

## Migration & Risk Management

Key risks:
- Behavioral drift during persistence swap.
- Data quality inconsistencies between legacy and new models.
- Operational overhead from adding graph capabilities too early.

Mitigations:
- Contract/parity test suite before and after migration.
- One-way backfill + validation scripts + checksums.
- Feature flags for gradual endpoint rollout.
- Start graph capabilities with simple read use-cases first.

---

## Definition of Done (Refactor Program)

A refactor is complete when:

1. API routes are persistence-agnostic.
2. PostgreSQL is primary store with migration discipline.
3. Core graph relationships are queryable over API.
4. Agent-oriented API guarantees are documented and enforced.
5. CI/CD enforces tests, linting, typing, and migration checks.
6. Documentation includes onboarding, architecture, and operations runbooks.

---

## Suggested Immediate Next Steps (Next 2 Weeks)

1. Implement repository/service abstraction for current paper CRUD.
2. Add SQLModel schema equivalent for `Paper` + migration scaffolding.
3. Add parity tests to compare old/new repository behavior.
4. Define first graph entities (`Paper`, `Author`, `Topic`) and edge schema.
5. Add a minimal `/v1/graph/neighbors` endpoint contract draft.

This sequence keeps momentum while minimizing rewrite risk and preserves your long-term knowledge-graph vision.
