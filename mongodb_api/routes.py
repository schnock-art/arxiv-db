from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
from urllib.parse import unquote
from models import Paper, PaperUpdate
import logging
router = APIRouter()


@router.post("/", 
             response_description="Create a new Paper", 
             status_code=status.HTTP_201_CREATED, 
             response_model=Paper)
def create_book(request: Request, paper: Paper = Body(...)):
    paper = jsonable_encoder(paper)
    new_paper = request.app.database["papers"].insert_one(paper)
    created_paper = request.app.database["papers"].find_one(
        {"_id": new_paper.inserted_id}
    )

    return created_paper

@router.get("/", 
            response_description="List all papers", 
            response_model=List[Paper])
def list_papers(request: Request):
    papers = list(request.app.database["papers"].find(limit=100))
    return papers


@router.get("/{id:path}", 
            response_description="Get a single book by id", 
            response_model=Paper)
def find_paper(id: str, request: Request):
    logging.info(id)
    if (paper := request.app.database["papers"].find_one({"_id": id})) is not None:
        return paper
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                        detail=f"Paper with ID {id} not found")


@router.put("/{id:path}", response_description="Update a paper", response_model=Paper)
def update_paper(id: str, request: Request, paper: PaperUpdate = Body(...)):
    paper = {k: v for k, v in paper.model_dump().items() if v is not None}
    if len(paper) >= 1:
        update_result = request.app.database["papers"].update_one(
            {"_id": id}, {"$set": paper}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"Paper with ID {id} not found")

    if (
        existing_paper := request.app.database["papers"].find_one({"_id": id})
    ) is not None:
        return existing_paper

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                        detail=f"Paper with ID {id} not found")


@router.delete("/{id:path}", response_description="Delete a paper")
def delete_paper(id: str, request: Request, response: Response):
    delete_result = request.app.database["papers"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                        detail=f"Paper with ID {id} not found")