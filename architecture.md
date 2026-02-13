# Architecture

This document describes the current architecture of `arxiv-db`, its runtime flow, and key design decisions.

## 1. System overview

`arxiv-db` is organized around a service-oriented data flow:

1. **Ingestion (optional/demo)** via `arxiv_crawler/main.py`
2. **API layer** via FastAPI (`mongodb_api/main.py` + `mongodb_api/routes.py`)
3. **Persistence layer** via MongoDB (`papers` collection)

At runtime, clients interact only with the API. The crawler currently acts as an external producer/demo script rather than an internal background worker.

---

## 2. High-level component diagram

```text
                 +-----------------------+
                 |   arXiv API service   |
                 +-----------+-----------+
                             |
                             | (via arxiv python package)
                             v
+------------------+   +-----+----------------------+   +------------------+
| API Clients      +-->+ FastAPI app (mongodb_api) +-->+ MongoDB database |
| curl/UI/services |   | - validation (Pydantic)   |   | papers collection|
+------------------+   | - route handlers          |   +------------------+
                       | - serialization utilities |
                       +---------------------------+
```

---

## 3. Module responsibilities

## `mongodb_api/main.py`
- Creates FastAPI app instance.
- Configures logging from `mongodb_api/logging.conf`.
- Loads MongoDB connection settings from `~/creds/mongodb.env`.
- Uses a FastAPI lifespan context manager to initialize and close MongoDB client.
- Registers paper routes under `/paper`.

## `mongodb_api/routes.py`
- Defines CRUD handlers on an `APIRouter`.
- Uses `Request`-scoped app state (`request.app.database`) for DB access.
- Converts URL path IDs using `urllib.parse.unquote` before DB lookup.
- Returns `Paper` models (or lists of them) for response validation/serialization.

## `mongodb_api/models/models.py`
- Defines the canonical data contracts:
  - `Paper`: full record schema, with `_id` alias mapping to `entry_id`.
  - `PaperUpdate`: partial update schema.
- Loads example payloads from JSON files for OpenAPI examples.
- Exposes `model_dump_serialized(...)` wrappers that call shared serializer logic.

## `mongodb_api/utils.py`
- `load_paper_json`: reads ordered JSON and parses datetime fields.
- `custom_serialize`: normalizes datetime and URL fields for outbound payload/database use.

## `mongodb_api/tests/test_routes.py`
- Uses `fastapi.testclient.TestClient`.
- Mocks database handles on the app object.
- Performs route-level behavior checks.

## `arxiv_crawler/main.py`
- Prototype script to query arXiv and map result fields into `Paper`.
- Demonstrates serializing and POSTing records (script-style notebook snippets).

---

## 4. Request lifecycle

For a typical API call (for example `POST /paper/`):

1. FastAPI receives HTTP request.
2. Pydantic validates incoming JSON against `Paper`.
3. Route serializes model with `model_dump_serialized(...)` to ensure `_id`, datetime, and URL compatibility.
4. Route checks/inserts document in `papers` collection.
5. Response is returned and validated against `Paper` response model.

For read/update/delete routes, the path `id` is URL-decoded before querying MongoDB.

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

This lets MongoDB documents remain straightforward JSON-like records while preserving strict API contracts.

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

Current tests are route-centric and use mocked DB objects rather than a real Mongo instance.

Strengths:
- Fast feedback.
- No external DB dependency for most checks.

Gaps/opportunities:
- Add integration tests against ephemeral MongoDB (e.g., Testcontainers/mongomock-backed abstractions).
- Improve negative-path assertions and response body checks.
- Expand contract tests for serialization edge cases.

---

## 8. Architectural constraints and trade-offs

1. **Simplicity over abstraction**
   - DB access is done directly inside route handlers for straightforward CRUD logic.
2. **Schema-first API**
   - Pydantic models provide a strong contract boundary.
3. **Single collection design**
   - Fits current scope (paper metadata store) but may need indexing/query extension as data volume grows.
4. **Crawler as script**
   - Fast for experimentation; not yet productionized into jobs/queues/workers.

---

## 9. Potential evolution roadmap

- Introduce service/repository layers to decouple route logic from persistence.
- Add query filters (categories/date ranges/text search) and pagination metadata.
- Add robust duplicate handling and idempotent upsert workflow.
- Formalize ingestion into scheduled/background tasks.
- Add observability (structured logs, metrics, traces).
- Add CI workflow for lint/test/type-check on pull requests.
