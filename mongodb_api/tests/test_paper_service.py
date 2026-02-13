"""Unit tests for PaperService using repository doubles."""

# Standard Library
from unittest.mock import MagicMock

# Third Party
import pytest

# Library
from mongodb_api.services.paper_service import (
    PaperAlreadyExistsError,
    PaperNotFoundError,
    PaperNotModifiedError,
    PaperService,
)


def test_create_paper_conflict():
    repository = MagicMock()
    repository.get_by_id.return_value = {"_id": "abc"}
    service = PaperService(repository)

    with pytest.raises(PaperAlreadyExistsError):
        service.create_paper({"_id": "abc"})


def test_find_paper_not_found():
    repository = MagicMock()
    repository.get_by_id.return_value = None
    service = PaperService(repository)

    with pytest.raises(PaperNotFoundError):
        service.find_paper("abc")


def test_update_not_modified():
    repository = MagicMock()
    repository.get_by_id.return_value = {"_id": "abc"}
    repository.update.return_value = 0
    service = PaperService(repository)

    with pytest.raises(PaperNotModifiedError):
        service.update_paper("abc", {"title": "new"})


def test_update_missing_paper():
    repository = MagicMock()
    repository.get_by_id.return_value = None
    service = PaperService(repository)

    with pytest.raises(PaperNotFoundError):
        service.update_paper("abc", {"title": "new"})
