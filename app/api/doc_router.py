from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db import Document
from app.models.schemas import DocumentCreate
from datetime import datetime, timezone

def utc_now():
    """Возвращает текущее время в UTC без часового пояса"""
    return datetime.now(timezone.utc).replace(tzinfo=None)

async def create_document(db: AsyncSession, doc: DocumentCreate):
    """Создание документа в БД"""
    db_doc = Document(
        rubrics=doc.rubrics,
        text=doc.text,
        created_date=utc_now()  # Явно устанавливаем дату
    )
    db.add(db_doc)
    await db.commit()
    await db.refresh(db_doc)
    return db_doc

async def get_documents_by_ids(db: AsyncSession, ids: list[int]):
    """Получение документов по ID с сортировкой по дате"""
    if not ids:
        return []
    
    query = select(Document).where(Document.id.in_(ids)).order_by(desc(Document.created_date))
    result = await db.execute(query)
    return result.scalars().all()

async def delete_document(db: AsyncSession, doc_id: int):
    """Удаление документа из БД"""
    doc = await db.get(Document, doc_id)
    if doc:
        await db.delete(doc)
        await db.commit()
        return True
    return False