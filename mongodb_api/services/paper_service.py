"""Service layer for paper operations."""

# Library
from mongodb_api.repositories.paper_repository import PaperRepository


class PaperAlreadyExistsError(Exception):
    """Raised when attempting to create a paper that already exists."""


class PaperNotFoundError(Exception):
    """Raised when requested paper does not exist."""


class PaperNotModifiedError(Exception):
    """Raised when update operation does not modify a paper."""


class PaperService:
    """Business logic for paper CRUD, independent from route details."""

    def __init__(self, repository: PaperRepository):
        self._repository = repository

    def create_paper(self, paper_data):
        existing = self._repository.get_by_id(paper_data["_id"])
        if existing:
            raise PaperAlreadyExistsError

        created = self._repository.create(paper_data)
        if not created:
            raise PaperNotFoundError
        return created

    def list_papers(self):
        return self._repository.list(limit=100)

    def find_paper(self, paper_id):
        paper = self._repository.get_by_id(paper_id)
        if not paper:
            raise PaperNotFoundError
        return paper

    def update_paper(self, paper_id, update_data):
        existing = self._repository.get_by_id(paper_id)
        if not existing:
            raise PaperNotFoundError

        modified_count = self._repository.update(paper_id, update_data)
        if modified_count == 0:
            raise PaperNotModifiedError

        updated = self._repository.get_by_id(paper_id)
        if not updated:
            raise PaperNotFoundError
        return updated

    def delete_paper(self, paper_id):
        return self._repository.delete(paper_id)
