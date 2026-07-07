from app.db import get_db
from app.elastic import search_elastic, delete_from_elastic, index_document
from app.api.doc_router import get_documents_by_ids, delete_document, create_document
from app.models.schemas import DocumentCreate, DocumentResponse, SearchResponse
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

class SearchService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def search(self, query: str, limit: int = 20) -> SearchResponse:
        """Поиск документов"""
        # Поиск ID в Elasticsearch
        doc_ids = await search_elastic(query, limit)
        
        # Получение полных данных из БД
        documents = await get_documents_by_ids(self.db, doc_ids)
        
        # Преобразование в ответ
        response_docs = [
            DocumentResponse(
                id=doc.id,
                rubrics=doc.rubrics,
                text=doc.text,
                created_date=doc.created_date
            ) for doc in documents
        ]
        
        return SearchResponse(
            documents=response_docs,
            total=len(response_docs)
        )
    
    async def delete(self, doc_id: int) -> bool:
        """Удаление документа"""
        await delete_from_elastic(doc_id)
        
        # Удаление из БД
        return await delete_document(self.db, doc_id)
    
    async def add_document(self, doc_data: DocumentCreate) -> DocumentResponse:
        """Добавление документа (для тестов)"""
        doc = await create_document(self.db, doc_data)
        
        # Индексация в Elasticsearch
        await index_document(doc.id, doc.text)
        
        return DocumentResponse(
            id=doc.id,
            rubrics=doc.rubrics,
            text=doc.text,
            created_date=doc.created_date
        )