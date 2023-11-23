# %%

# test_routes.py

# Standard Library
# Importing necessary libraries and modules
import os
import sys
from unittest.mock import MagicMock

# Third Party
from fastapi.testclient import TestClient

# Library
from mongodb_api.main import app  # Import your FastAPI app
from mongodb_api.models import Paper, PaperUpdate
from mongodb_api.utils import custom_serialize, load_paper_json

# Setting the current path for loading test data
current_path = os.path.join(os.path.dirname(__file__), "..")

# Loading test data for entry and update tests
entry_paper_test = Paper(
    **load_paper_json(os.path.join(current_path, "example_entry.json"))
)
paper_data = custom_serialize(entry_paper_test)

update_paper_test = PaperUpdate(
    **load_paper_json(os.path.join(current_path, "example_update.json"))
)
update_data = custom_serialize(update_paper_test)

# Setting up mock MongoDB client
app.mongodb_client = MagicMock()
app.database = {"papers": MagicMock()}

# Initializing TestClient with the FastAPI app
client = TestClient(app)

def test_app_is_running():
    """
    Test to verify if the FastAPI application is running and accessible.
    """
    response = client.get("/paper")
    assert response.status_code == 200  # Expecting a successful response

def test_create_paper():
    """
    Test to verify the creation of a paper in the database.
    """
    app.database["papers"].find_one.return_value = custom_serialize(
        entry_paper_test
    )
    response = client.post("/paper/", json=paper_data)
    assert response.status_code == 201  # Expecting a successful creation response
    assert response.json() == paper_data  # Verifying the response data

def test_read_paper():
    """
    Test to verify reading a specific paper from the database.
    """
    response = client.get("/paper/" + str(entry_paper_test.entry_id))
    assert response.status_code != 500  # Expecting no server error
    assert response.json() == paper_data  # Verifying the response data

def test_read_inexisting_paper():
    """
    Test to verify the behavior when trying to read a non-existing paper.
    """
    non_existing_id = "1234"
    app.database["papers"].find_one.return_value = None  # Mocking non-existence
    response = client.get(f"paper/{non_existing_id}")
    assert response.status_code == 404  # Expecting a 'not found' response
    assert response.json()["detail"] == f"Paper with ID {non_existing_id} not found"

def test_update_paper():
    """
    Test to verify updating an existing paper.
    """
    existing_id = str(entry_paper_test.entry_id)
    update_data_with_id = {**update_data, "entry_id": existing_id}  # Including 'entry_id'
    update_result_mock = MagicMock()
    update_result_mock.modified_count = 1
    app.database["papers"].find_one.side_effect = [paper_data, update_data_with_id]  # Mocking before and after update
    app.database["papers"].update_one.return_value = update_result_mock

    response = client.put(f"/paper/{existing_id}", json=update_data)
    assert response.status_code == 200  # Expecting a successful update response
    assert response.json() == update_data_with_id  # Verifying the updated data

def test_update_inexisting_paper():
    """
    Test to verify the behavior when trying to update a non-existing paper.
    """
    non_existing_id = "1234"
    app.database["papers"].find_one.return_value = None  # Mocking non-existence
    response = client.put(f"/paper/{non_existing_id}", json=update_data)
    assert response.status_code == 404  # Expecting a 'not found' response
    assert response.json()["detail"] == f"Paper with ID {non_existing_id} not found"

def test_nothing_to_update():
    """
    Test to verify the behavior when there is nothing to update on an existing paper.
    """
    existing_id = str(entry_paper_test.entry_id)
    app.database["papers"].find_one.return_value = paper_data  # Mocking existing paper
    response = client.put(f"/paper/{existing_id}", json={})
    assert response.status_code == 304  # Expecting a 'not modified

def test_delete_paper():
    response = client.delete("/paper/" + str(entry_paper_test.entry_id))
    assert response.status_code == 204
