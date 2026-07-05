from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from app.models.schemas import (
    DocumentResponse, 
    DocumentCreate, 
)
from app.db import get_db  # нужно изменить на асинхронную версию
from app.models import models

router = APIRouter()

# 1. СОЗДАНИЕ ДОКУМЕНТА
@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    doc_data: DocumentCreate, 
    db: AsyncSession = Depends(get_db)  # меняем Session на AsyncSession
):
    """
    Создать новый документ в PostgreSQL (асинхронно)
    """
    try:
        db_doc = models.Document(
            text=doc_data.text,
            rubrics=doc_data.rubrics,
        )
        db.add(db_doc)
        await db.commit()  # добавляем await
        await db.refresh(db_doc)  # добавляем await
        
        return DocumentResponse(
            id=db_doc.id,
            rubrics=db_doc.rubrics,
            text=db_doc.text,
            created_at=db_doc.created_at
        )
    except Exception as e:
        await db.rollback()  # добавляем await
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating document: {str(e)}"
        )

# 2. ВЫДАЧА ДОКУМЕНТА ПО ID
@router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: int, 
    db: AsyncSession = Depends(get_db)  # меняем Session на AsyncSession
):
    """
    Получить документ по ID из PostgreSQL (асинхронно)
    """
    try:
        # Используем асинхронный запрос
        result = await db.execute(
            select(models.Document).where(models.Document.id == doc_id)
        )
        db_doc = result.scalar_one_or_none()
        
        if not db_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {doc_id} not found"
            )
        
        return DocumentResponse(
            id=db_doc.id,
            rubrics=db_doc.rubrics,
            text=db_doc.text,
            created_at=db_doc.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving document: {str(e)}"
        )

# 3. УДАЛЕНИЕ ДОКУМЕНТА ПО ID
@router.delete("/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db)  # меняем Session на AsyncSession
):
    """
    Удалить документ по ID из PostgreSQL (асинхронно)
    """
    try:
        # Проверяем существование документа
        result = await db.execute(
            select(models.Document).where(models.Document.id == doc_id)
        )
        db_doc = result.scalar_one_or_none()
        
        if not db_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with id {doc_id} not found"
            )
        
        # Удаляем документ
        await db.delete(db_doc)  # добавляем await
        await db.commit()  # добавляем await
        
        # Возвращаем 204 No Content (без тела ответа)
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()  # добавляем await
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}"
        )