
import uuid
from typing import Optional
from pydantic import BaseModel, Field, validator
import datetime


class Paper(BaseModel):
    entry_id: str = Field(alias="_id")
    title: str = Field(...)
    summary: str = Field(...)
    #author: str = Field(...)
    published: datetime.datetime = Field(...)
    updated: datetime.datetime = Field(...)
    pdf_url: str = Field(...)
    download_path: str = Field(...)
    doi: Optional[str] = Field(...)
    comment: Optional[str] = Field(...)
    #primary_category: str = Field(...)   

    class Config:
        populate_by_name = True
        arbitrary_types_allowed=True
        json_schema_extra = {
            "example": {
                "entry_id": "http://arxiv.org/abs/2210.06998v2",
                "title": "Test Title insert",
                #"author": "Miguel de Cervantes",
                "summary": "Test Summary insert",
                "published": datetime.datetime(2022, 10, 13, 13, 8, 54, tzinfo=datetime.timezone.utc),
                "updated": datetime.datetime(2023, 1, 9, 16, 33, 43, tzinfo=datetime.timezone.utc),
                "pdf_url": 'http://arxiv.org/pdf/2210.06998v2',
                "download_path": '\\arxiv\\cs.CR\\DE-FAKE:_Detection_and_Attribution_of_Fake_Images_Generated_by_Text-to-Image_Generation_Models.pdf',
                "doi": "",
                "comment": "",
                #"primary_category": "cs.CR",
            }
        }

class PaperUpdate(BaseModel):
    title: Optional[str]
    #author: Optional[str]
    summary: Optional[str]
    published: Optional[datetime.datetime]
    updated: Optional[datetime.datetime]
    pdf_url: Optional[str]
    download_path: Optional[str]
    doi: Optional[str]
    comment: Optional[str]

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Test Title",
                #"author": "Miguel de Cervantes",
                "summary": "Test Summary",
            }
        }