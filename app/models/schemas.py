from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DocumentBase(BaseModel):
    text: str
    rubrics: List[str] = []


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    rubrics: Optional[List[str]] = None
    text: Optional[str] = None

class DocumentDelete(BaseModel):
    id: int

class DocumentResponse(BaseModel):
    id: int
    rubrics: List[str]
    text: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class SearchQuery(BaseModel):
    text: Optional[str] = None
    rubrics: Optional[List[str]] = None
    limit: Optional[int] = 10
    offset: Optional[int] = 0


class SearchResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int