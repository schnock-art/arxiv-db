# test_routes.py
# Standard Library
import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)

# Standard Library
from unittest.mock import MagicMock

# Third Party
from fastapi.testclient import TestClient

# Library
from mongodb_api.main import app  # Import your FastAPI app

client = TestClient(app)


def setup_mongodb_mock():
    app.mongodb_client = MagicMock()
    app.database = {"papers": MagicMock()}
    return app.database["papers"]


def test_app_is_running():
    response = client.get("/paper")
    assert (
        response.status_code != 404
    )  # Replace with the actual expected status code


def test_create_paper():
    db_mock = setup_mongodb_mock()
    db_mock.insert_one.return_value.inserted_id = "123"

    response = client.post(
        "/paper", json={"title": "New Paper", "content": "Content"}
    )
    assert response.status_code == 201
    assert response.json() == {"_id": "123"}


def test_read_paper():
    db_mock = setup_mongodb_mock()
    db_mock.find_one.return_value = {"_id": "123", "title": "Existing Paper"}

    response = client.get("/paper/123")
    assert (
        response.status_code != 500
    )  # Replace with the actual expected status code
    assert response.json() == {"_id": "123", "title": "Existing Paper"}


def test_update_paper():
    db_mock = setup_mongodb_mock()
    db_mock.update_one.return_value.modified_count = 1

    response = client.put("/paper/123", json={"title": "Updated Title"})
    assert response.status_code == 200


def test_delete_paper():
    db_mock = setup_mongodb_mock()
    db_mock.delete_one.return_value.deleted_count = 1

    response = client.delete("/paper/123")
    assert response.status_code == 204


# Additional tests for error scenarios, edge cases, and validation failures
