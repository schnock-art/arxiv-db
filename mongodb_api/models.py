"""
This module contains the models for representing research papers
and their updates.

The models defined in this module are:
- Paper: Represents a research paper with details
    including title, summary, URLs, and metadata.
- PaperUpdate: Model for updating the details of a research paper.
    Each field is optional.
"""

# Standard Library
import datetime
import logging
from typing import Optional

# Third Party
from pydantic import AnyUrl, BaseModel, Field

# the __name__ resolve to "uicheckapp.services"
logger = logging.getLogger(__name__)
# This will load the uicheckapp logger


class Paper(BaseModel):
    """
    Represents a research paper with details including title, summary, URLs,
    and metadata.

    Attributes:
    - entry_id (AnyUrl): Unique identifier URL for the paper.
    - title (str): Title of the paper.
    - summary (str): Summary or abstract of the paper.
    - published (datetime.datetime): Date and time when the paper was
      published, in UTC.
    - updated (datetime.datetime): Date and time when the paper was last
      updated, in UTC.
    - pdf_url (AnyUrl): URL to access the PDF version of the paper.
    - download_path (Optional[str]): Local filesystem path where the PDF is
      downloaded.
    - doi (Optional[str]): Digital Object Identifier for the paper.
    - comment (Optional[str]): Additional comments or notes about the paper.

    The model supports automatic population by field names and allows
    arbitrary types.
    """

    entry_id: AnyUrl = Field(
        ..., alias="_id", description="Unique identifier URL for the paper"
    )
    title: str = Field(..., description="Title of the paper")
    summary: str = Field(..., description="Summary of the paper")
    published: datetime.datetime = Field(
        ..., description="Publication date and time in UTC"
    )
    updated: datetime.datetime = Field(
        ..., description="Last updated date and time in UTC"
    )
    pdf_url: AnyUrl = Field(
        ..., description="URL to the PDF version of the paper"
    )
    download_path: Optional[str] = Field(
        None, description="Local path where the PDF is downloaded"
    )
    doi: Optional[str] = Field(
        None,
        pattern=r"^10.\d{4,9}/[-._;()/:A-Z0-9]+$",
        description="Digital Object Identifier",
    )
    comment: Optional[str] = Field(None, description="Additional comments")

    class Config:
        """
        Configuration for the model.
        """

        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "entry_id": "http://arxiv.org/abs/2210.06998v2",
                "title": "Test Title insert",
                # "author": "Miguel de Cervantes",
                "summary": "Test Summary insert",
                "published": datetime.datetime(
                    2022, 10, 13, 13, 8, 54, tzinfo=datetime.timezone.utc
                ),
                "updated": datetime.datetime(
                    2023, 1, 9, 16, 33, 43, tzinfo=datetime.timezone.utc
                ),
                "pdf_url": "http://arxiv.org/pdf/2210.06998v2",
                "download_path": "\\arxiv\\cs.CR\\testfile.pdf",
                "doi": None,
                "comment": "",
                # "primary_category": "cs.CR",
            }
        }


class PaperUpdate(BaseModel):
    """
    Model for updating the details of a research paper. Each field is optional.

    This model is typically used for PATCH requests in APIs, allowing partial
    updates to a paper's details.

    Attributes:
    - title (Optional[str]): New title of the paper.
    - summary (Optional[str]): New summary or abstract of the paper.
    - published (Optional[datetime.datetime]): New publication date and time,
      in UTC.
    - updated (Optional[datetime.datetime]): New last updated date and time,
      in UTC.
    - pdf_url (Optional[AnyUrl]): New URL for the PDF version of the paper.
    - download_path (Optional[str]): New download path for the paper's PDF.
    - doi (Optional[str]): New Digital Object Identifier for the paper.
    - comment (Optional[str]): New additional comments or notes about the
      paper.
    """

    title: Optional[str] = None
    summary: Optional[str] = None
    published: Optional[datetime.datetime] = None
    updated: Optional[datetime.datetime] = None
    pdf_url: Optional[AnyUrl] = None
    download_path: Optional[str] = None
    doi: Optional[str] = None
    comment: Optional[str] = None

    class Config:
        """
        Configuration for the model.
        """

        json_schema_extra = {
            "example": {
                "title": "Test Title",
                # "author": "Miguel de Cervantes",
                "summary": "Test Summary",
            }
        }
