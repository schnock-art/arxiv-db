# Architecture

This document describes the current architecture of `arxiv-db`, its runtime flow, and key design decisions.

## 1. System overview

`arxiv-db` is organized around layered API access with explicit persistence boundaries:

1. **Ingestion (optional/demo)** via `arxiv_crawler/main.py`
2. **API route layer** via FastAPI (`mongodb_api/main.py` + `mongodb_api/routes.py`)
3. **Service layer** via `mongodb_api/services/paper_service.py`
4. **Repository layer** via `mongodb_api/repositories/*`
5. **Persistence layer** via MongoDB (`papers` collection)

At runtime, API clients interact with route handlers, handlers delegate business behavior to the service, and the service delegates data access to repository implementations.

---

## 2. High-level component diagram

```text
                 +-----------------------+
                 |   arXiv API service   |
                 +-----------+-----------+
                             |
                             | (via arxiv python package)
                             v
+------------------+   +---------------------------+   +--------------------------+
| API Clients      +-->+ FastAPI Routes            +-->+ PaperService             |
| curl/UI/services |   | mongodb_api/routes.py     |   | mongodb_api/services/*   |
+------------------+   +-------------+-------------+   +------------+-------------+
                                    |                              |
                                    | request.app.paper_service    | repository contract
                                    v                              v
                              +-----+-------------------------------+------+
                              | MongoPaperRepository (Mongo adapter)       |
                              | mongodb_api/repositories/*                 |
                              +--------------------+------------------------+
                                                   |
                                                   v
                                           +-------+--------+
                                           | MongoDB papers |
                                           +----------------+
```

---

## 3. Module responsibilities

## `mongodb_api/main.py`
- Creates FastAPI app instance.
- Configures logging from `mongodb_api/logging.conf`.
- Loads MongoDB connection settings from `~/creds/mongodb.env`.
- Uses a FastAPI lifespan context manager to initialize and close MongoDB client.
- Wires runtime dependencies on app state:
  - `paper_repository` (`MongoPaperRepository`)
  - `paper_service` (`PaperService`)
- Registers paper routes under `/paper`.

## `mongodb_api/routes.py`
- Defines CRUD handlers on an `APIRouter`.
- Uses `request.app.paper_service` only (no direct collection calls).
- Maps service/domain errors to HTTP exceptions.
- Converts URL path IDs using `urllib.parse.unquote`.
- Returns `Paper` models (or lists of them) for response validation/serialization.

## `mongodb_api/services/paper_service.py`
- Owns CRUD business logic independent of FastAPI and Mongo APIs.
- Defines domain-level errors:
  - `PaperAlreadyExistsError`
  - `PaperNotFoundError`
  - `PaperNotModifiedError`
- Interacts only through `PaperRepository` contract.

## `mongodb_api/repositories/paper_repository.py`
- Defines persistence interface (`PaperRepository`) for create/get/list/update/delete semantics.

## `mongodb_api/repositories/mongo_paper_repository.py`
- Concrete Mongo implementation of `PaperRepository`.
- Encapsulates collection operations (`insert_one/find_one/find/update_one/delete_one`).

## `mongodb_api/models/models.py`
- Defines canonical data contracts:
  - `Paper`: full record schema, `_id` alias mapping to `entry_id`.
  - `PaperUpdate`: partial update schema.
- Loads example payloads from JSON files for OpenAPI examples.
- Exposes `model_dump_serialized(...)` wrappers that call shared serializer logic.

## `mongodb_api/utils.py`
- `load_paper_json`: reads ordered JSON and parses datetime fields.
- `custom_serialize`: normalizes datetime and URL fields for outbound payload/database use.

## `mongodb_api/tests/test_routes.py`
- Uses `fastapi.testclient.TestClient`.
- Mocks collection handles and injects service/repository wiring into app state.
- Verifies route behavior through HTTP-level tests.

## `mongodb_api/tests/test_paper_service.py`
- Unit tests for service behavior with mocked repository doubles.
- Verifies domain error handling independent of FastAPI route code.

## `arxiv_crawler/main.py`
- Prototype script to query arXiv and map result fields into `Paper`.
- Demonstrates serializing and POSTing records.

---

## 4. Request lifecycle

For a typical API call (for example `POST /paper/`):

1. FastAPI receives HTTP request.
2. Pydantic validates incoming JSON against `Paper`.
3. Route serializes model with `model_dump_serialized(...)`.
4. Route calls `request.app.paper_service.create_paper(...)`.
5. Service enforces business rule checks (e.g., duplicate prevention).
6. Service delegates persistence operation to repository.
7. Repository performs Mongo operation and returns data.
8. Route maps domain errors to HTTP status codes and returns response.

For read/update/delete routes, path `id` is URL-decoded before service invocation.

---

## 5. Data model and storage mapping

## Canonical paper record
Core fields include:
- `_id` (arXiv entry URL)
- `title`, `summary`
- `published`, `updated` (ISO timestamps)
- `pdf_url`
- optional `download_path`, `doi`, `comment`

## Mapping behavior
- API field `entry_id` is aliased to Mongo `_id` for persistence.
- `AnyUrl` fields are serialized as strings before insert/update.
- Datetimes are emitted in ISO format (UTC `Z` suffix normalization).

---

## 6. Configuration and runtime dependencies

## External systems
- MongoDB server (Atlas/local)
- Optional arXiv upstream API (crawler only)

## Python/runtime dependencies
- FastAPI + Uvicorn
- Pydantic v2
- PyMongo
- python-dotenv
- arxiv package (crawler)

## Logging
- Configured via `logging.conf` using console handlers.
- Module loggers write operational events for CRUD operations and startup/shutdown.

---

## 7. Testing strategy

Current tests now combine:
- Route-level behavior tests (`test_routes.py`) with mocked storage handles.
- Service-level unit tests (`test_paper_service.py`) validating business behavior and error conditions.

Strengths:
- Faster unit feedback for business logic.
- Better isolation between transport (HTTP) and domain rules.

Gaps/opportunities:
- Add integration tests against ephemeral MongoDB.
- Expand parity tests for future alternate repository implementations.
- Add contract tests for API response schemas and error taxonomy.

---

## 8. Architectural constraints and trade-offs

1. **Layered separation added (Phase 1)**
   - Routes are now persistence-agnostic through service/repository abstraction.
2. **Schema-first API**
   - Pydantic models remain the external contract boundary.
3. **Single collection design**
   - Still suitable for current scope; schema/index strategy will evolve for Postgres migration.
4. **Crawler as script**
   - Still demo-style and not yet formalized into scheduled jobs/workers.

---

## 9. Refactor progress tracking (from `Refactor.md`)

## Phase 0 — Alignment & contracts
- [x] Initial roadmap and refactor phases documented (`Refactor.md`).
- [ ] Repository ADRs and explicit API compatibility contract not yet added.

## Phase 1 — Persistence abstraction
- [x] Service layer introduced (`PaperService`).
- [x] Repository interface introduced (`PaperRepository`).
- [x] Mongo repository implementation added (`MongoPaperRepository`).
- [x] Routes call services instead of direct DB collection methods.
- [x] Service behavior covered by unit tests (`test_paper_service.py`).
- [ ] Full route/contract test suite green in all environments.

## Phase 2+ (planned)
- [ ] PostgreSQL + migrations not started.
- [ ] Graph entities/relations not started.
- [ ] Agent-facing hardening (auth/rate limits/pagination consistency) not started.

---

## 10. Potential evolution roadmap

- Add Postgres repository implementation behind same `PaperRepository` contract.
- Introduce migration/parity tests to validate behavior across repository backends.
- Add query filters and deterministic pagination semantics.
- Add observability (structured logs, metrics, traces).
- Add CI workflow for lint/test/type-check on pull requests.
