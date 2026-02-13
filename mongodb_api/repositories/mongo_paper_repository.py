"""MongoDB-backed paper repository implementation."""

# Library
from .paper_repository import PaperRepository


class MongoPaperRepository(PaperRepository):
    """Concrete repository using a Mongo collection."""

    def __init__(self, papers_collection):
        self._papers_collection = papers_collection

    def create(self, paper_data):
        result = self._papers_collection.insert_one(paper_data)
        return self.get_by_id(result.inserted_id)

    def get_by_id(self, paper_id):
        return self._papers_collection.find_one({"_id": paper_id})

    def list(self, limit=100):
        return list(self._papers_collection.find(limit=limit))

    def update(self, paper_id, update_data):
        update_result = self._papers_collection.update_one(
            {"_id": paper_id}, {"$set": update_data}
        )
        return update_result.modified_count

    def delete(self, paper_id):
        delete_result = self._papers_collection.delete_one({"_id": paper_id})
        return delete_result.deleted_count
