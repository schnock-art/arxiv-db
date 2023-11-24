"""
This module contains the API routes for the MongoDB API.

The API routes are implemented using FastAPI, a modern Python web framework
for building APIs with minimal code.
"""

# Standard Library
import datetime
import logging
from typing import List
#from fastapi.encoders import jsonable_encoder
from urllib.parse import unquote

# Third Party
from fastapi import APIRouter, Body, HTTPException, Request, Response, status
from pydantic import AnyUrl

from .models.models import Paper, PaperUpdate

# the __name__ resolve to "uicheckapp.services"
logger = logging.getLogger(__name__)
# This will load the uicheckapp logger

router = APIRouter()


@router.post(
    "/",
    response_description="Create a new Paper",
    status_code=status.HTTP_201_CREATED,
    response_model=Paper,
)
def create_paper(request: Request, paper: Paper = Body(...)):
    """
    Create a new paper in the database.

    Parameters:
    - request (Request): The request object.
    - paper (Paper): The paper data to be created.

    Returns:
    The created paper as a dictionary.
    """
    try:
        logger.info(f"Creating paper with id {paper.entry_id}")
        logger.info(paper)
        paper_data = paper.model_dump_serialized(json_dump=False)
        logger.info(paper_data)
        paper = request.app.database["papers"].find_one({"_id": paper_data["_id"]})
        logger.info(paper)
        if paper:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Paper with ID {id} already exists",
            )



        result = request.app.database["papers"].insert_one(paper_data)
        paper_id = result.inserted_id

        # Retrieve the newly created paper
        created_paper = request.app.database["papers"].find_one({"_id": paper_id})
    except Exception as e:
        logger.error(f"Error creating paper: {e}")
        raise e

    if not created_paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Created paper not found"
        )

    logger.info(f"Created paper with id {paper_id}")
    return Paper(**created_paper)


@router.get(
    "/", response_description="List all papers", response_model=List[Paper]
)
def list_papers(request: Request):
    """
    Retrieve a list of papers from the database.

    Parameters:
    - request (Request): The request object.

    Returns:
    A list of papers, each as a dictionary.
    """
    try:
        papers = list(request.app.database["papers"].find(limit=100))
    except Exception as e:
        logger.error(f"Error listing papers: {e}")
        raise e

    logger.info(f"Found {len(papers)} papers")
    logger.info(papers)
    return papers


@router.get(
    "/{id:path}",
    response_description="Get a single paper by id",
    response_model=Paper,
)
def find_paper(id: str, request: Request):
    """
    Retrieve a single paper by its ID.

    Parameters:
    - id (str): The ID of the paper to retrieve.
    - request (Request): The request object.

    Returns:
    The requested paper as a dictionary, or raises an HTTP 404 error if not
    found.
    """
    try:
        id = unquote(id)
        logger.info(f"Finding paper with id {id}")
        paper = request.app.database["papers"].find_one({"_id": id})
        logger.info(paper)
    except Exception as e:
        logger.error(f"Error finding paper with id {id}: {e}")
        raise e

    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with ID {id} not found"
        )
    logger.info(f"Found paper with ID {id}")
    return paper


@router.put(
    "/{id:path}", response_description="Update a paper", response_model=Paper
)
def update_paper(id: str, request: Request, paper: PaperUpdate = Body(...)):
    """
    Update an existing paper's details.

    Parameters:
    - id (str): The ID of the paper to update.
    - request (Request): The request object.
    - paper (PaperUpdate): The updated paper data.

    Returns:
    The updated paper as a dictionary, or raises an HTTP 404 error if not
    found or not updated.
    """
    id = unquote(id)
    logger.info(f"Updating paper with id {id}")
    #update_data = paper.model_dump_serialized(json_dump=False)

    update_data = paper.model_dump_serialized(json_dump=False, ignore_none=True)
    logger.info(update_data)
    try:
        existing_paper = request.app.database["papers"].find_one({"_id": id})
    except Exception as e:
        logger.error(f"Error finding paper with id {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with ID {id} not found"
        )


    update_result = request.app.database["papers"].update_one(
        {"_id": id}, {"$set": update_data}
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail=f"Paper with ID {id} not modified",
        )

    updated_paper = request.app.database["papers"].find_one({"_id": id})

    if not updated_paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with ID {id} not found",
        )

    logger.info(f"Updated paper with id {id}")
    return updated_paper

@router.delete("/{id:path}", response_description="Delete a paper")
def delete_paper(id: str, request: Request, response: Response):
    """
    Delete a paper from the database.

    Parameters:
    - id (str): The ID of the paper to delete.
    - request (Request): The request object.
    - response (Response): The response object.

    Returns:
    An HTTP 204 response on successful deletion, or raises an HTTP 404 error
    if not found.
    """
    try:
        id = unquote(id)
        logger.info(f"Deleting paper with id {id}")
        delete_result = request.app.database["papers"].delete_one(
            {"_id": id}
        )
        response.status_code = status.HTTP_200_OK
        return response

    except Exception as e:
        logger.error(f"Error deleting paper with id {id}: {e}")
        raise e


