# arxiv-db

A Python project for collecting arXiv metadata and serving it from a MongoDB-backed REST API built with FastAPI.

## What this repository does

This repository has two main pieces:

1. **`mongodb_api/`**: A FastAPI service that exposes CRUD endpoints for research paper documents stored in MongoDB.
2. **`arxiv_crawler/`**: A small script-oriented module that demonstrates fetching results from arXiv and shaping them into the API's `Paper` schema.

The API uses Pydantic models to validate payloads, serializes URLs/datetimes into MongoDB-friendly formats, and stores papers in a `papers` collection.

---

## Features

- FastAPI application with OpenAPI docs at `/docs`.
- MongoDB Atlas/local MongoDB connectivity via environment file.
- `Paper` and `PaperUpdate` models with field validation.
- CRUD endpoints:
  - `POST /paper/` create a paper
  - `GET /paper/` list papers (limit 100)
  - `GET /paper/{id}` fetch one paper by URL-encoded ID
  - `PUT /paper/{id}` update one paper
  - `DELETE /paper/{id}` delete one paper
- Basic route tests using `fastapi.testclient` and mocked DB handles.

---

## Repository layout

```text
arxiv-db/
├── arxiv_crawler/           # arXiv fetch/demo script
├── mongodb_api/
│   ├── main.py              # FastAPI app + MongoDB lifespan
│   ├── routes.py            # API routes
│   ├── utils.py             # Serialization and JSON helpers
│   ├── models/
│   │   ├── models.py        # Pydantic schemas (Paper, PaperUpdate)
│   │   ├── example_entry.json
│   │   └── example_update.json
│   └── tests/
├── requirements.txt
├── environment.yml
└── Makefile
```

---

## Prerequisites

- Python 3.10+ (3.12 is used in the checked-in cache artifacts)
- A MongoDB instance (Atlas or local)
- pip (or conda if you want to use `environment.yml`)

---

## Configuration

The API expects MongoDB settings from a dotenv file located at:

```text
~/creds/mongodb.env
```

Required keys:

```dotenv
ATLAS_URI=mongodb+srv://<user>:<password>@<cluster>/<db>?retryWrites=true&w=majority
DB_NAME=arxiv
```

> Note: `mongodb_api/main.py` reads this exact path using `dotenv_values`; if the file is missing, app startup will fail when trying to create the Mongo client.

---

## Installation

### Option A: pip

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Option B: conda

```bash
conda env create -f environment.yml
conda activate <env-name>
```

---

## Running the API

From the repo root:

```bash
python -m uvicorn mongodb_api.main:app --reload
```

Then open:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

The paper endpoints are under `/paper`.

---

## Example API usage

### Create a paper

```bash
curl -X POST "http://localhost:8000/paper/" \
  -H "Content-Type: application/json" \
  -d '{
    "_id": "http://arxiv.org/abs/2210.06998v2",
    "title": "Example title",
    "summary": "Example abstract",
    "published": "2022-10-13T13:08:54Z",
    "updated": "2023-01-09T16:33:43Z",
    "pdf_url": "http://arxiv.org/pdf/2210.06998v2",
    "download_path": "/tmp/2210.06998v2.pdf",
    "doi": null,
    "comment": ""
  }'
```

### List papers

```bash
curl "http://localhost:8000/paper/"
```

### Get one paper by ID

Because the ID is itself a URL, URL-encode it in the path:

```bash
curl "http://localhost:8000/paper/http%3A%2F%2Farxiv.org%2Fabs%2F2210.06998v2"
```

### Update a paper

```bash
curl -X PUT "http://localhost:8000/paper/http%3A%2F%2Farxiv.org%2Fabs%2F2210.06998v2" \
  -H "Content-Type: application/json" \
  -d '{"comment": "Updated via API"}'
```

### Delete a paper

```bash
curl -X DELETE "http://localhost:8000/paper/http%3A%2F%2Farxiv.org%2Fabs%2F2210.06998v2"
```

---

## Running tests

```bash
pytest mongodb_api/tests -q
```

Tests mock the app's MongoDB handles and primarily validate route behavior and response status expectations.

---

## Development notes

- `Paper.entry_id` is stored as MongoDB `_id` (via Pydantic aliasing).
- `custom_serialize` converts `datetime` to ISO8601 strings and `AnyUrl` to plain strings before DB operations.
- There are utility make targets for environment export and maintenance tasks, but some commands are Windows-oriented (`.bat` paths).

---

## Known limitations / caveats

- `arxiv_crawler/main.py` is a demonstration script and not integrated as a production ingestion pipeline.
- The API currently exposes only minimal pagination/filtering (simple list with `limit=100`).
- Error handling and status code semantics can be further hardened (for example delete/update edge cases).

---

## License

No explicit license file is currently included. Add one before external distribution.
