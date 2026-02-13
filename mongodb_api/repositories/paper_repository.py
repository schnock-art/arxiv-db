"""Repository interfaces for paper persistence."""

# Standard Library
from abc import ABC, abstractmethod
from typing import Any


class PaperRepository(ABC):
    """Persistence contract for paper CRUD operations."""

    @abstractmethod
    def create(self, paper_data: dict[str, Any]) -> dict[str, Any]:
        """Create and return a persisted paper."""

    @abstractmethod
    def get_by_id(self, paper_id: str) -> dict[str, Any] | None:
        """Get one paper by id."""

    @abstractmethod
    def list(self, limit: int = 100) -> list[dict[str, Any]]:
        """List papers."""

    @abstractmethod
    def update(self, paper_id: str, update_data: dict[str, Any]) -> int:
        """Update a paper and return modified count."""

    @abstractmethod
    def delete(self, paper_id: str) -> int:
        """Delete a paper and return deleted count."""
