# %%

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
from mongodb_api.models import Paper, PaperUpdate
# Local imports
from mongodb_api.utils import custom_serialize, load_paper_json

current_path = os.path.join(os.path.dirname(__file__), "..")

entry_paper_test = Paper(
    **load_paper_json(os.path.join(current_path, "example_entry.json"))
)

paper_data = custom_serialize(entry_paper_test)

update_paper_test = PaperUpdate(
    **load_paper_json(os.path.join(current_path, "example_update.json"))
)

update_data = custom_serialize(update_paper_test)

app.mongodb_client = MagicMock()
app.database = {"papers": MagicMock()}
app.database["papers"].find_one.return_value = custom_serialize(
    entry_paper_test
)  # .model_dump()


# return app.database["papers"]
client = TestClient(app)

# %%
# def setup_mongodb_mock():


def test_app_is_running():
    response = client.get("/paper")
    assert (
        response.status_code == 200
    )  # Replace with the actual expected status code


def test_create_paper():
    # Convert to dict for JSON serialization, handling special types
    response = client.post("/paper/", json=paper_data)
    assert response.status_code == 201, response.text
    assert response.json() == paper_data


def test_read_paper():
    # db_mock = app.database["papers"]
    # db_mock.find_one.return_value = entry_paper_test.model_dump()

    response = client.get("/paper/" + str(entry_paper_test.entry_id))
    assert response.status_code != 500
    assert response.json() == paper_data


def test_update_paper():
    # Mock the `update_one` method to return an object
    # with a `modified_count` attribute
    update_result_mock = MagicMock()
    update_result_mock.modified_count = 1
    app.database["papers"].update_one.return_value = update_result_mock

    response = client.put(
        "/paper/" + str(entry_paper_test.entry_id), json=update_data
    )
    assert response.status_code == 200


def test_delete_paper():
    response = client.delete("/paper/" + str(entry_paper_test.entry_id))
    assert response.status_code == 204


# Additional tests for error scenarios, edge cases, and validation failures
