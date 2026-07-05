from sqlalchemy import String, DateTime, Text, ARRAY, Index
from datetime import datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from typing import List

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rubrics: Mapped[List[str]] = mapped_column(ARRAY(String), default=list) 
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    __table_args__ = (
        # Index('idx_documents_created_date', created_at.desc()),
        
        # Index('idx_documents_rubrics', rubrics.desc),
        
        Index('idx_documents_search',text),
    )
