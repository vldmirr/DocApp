from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class DocumentBase(BaseModel):
    text: str
    rubrics: List[str] = []

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    text: Optional[str] = None
    rubrics: Optional[List[str]] = None

class DocumentDelete(BaseModel):
    id: int

class DocumentResponse(BaseModel):
    id: int
    rubrics: List[str]
    text: str
    created_date: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SearchQuery(BaseModel):
    text: Optional[str] = None
    rubrics: Optional[List[str]] = None
    limit: Optional[int] = 10
    offset: Optional[int] = 0


class SearchResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int