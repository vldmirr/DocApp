from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional


# Question Schemas
class DocumentBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=800)

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: int
    created_at: datetime
    rubrics: List[str]

    model_config = ConfigDict(from_attributes=True)