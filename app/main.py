from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from app.db import init_db, get_db
from app.elastic import init_elastic, close_elastic
from app.api.search_router import SearchService
from app.models.schemas import SearchResponse, DocumentCreate, DocumentResponse
from app.api.doc_router import create_document
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск
    try:
        logger.info("Инициализация базы данных...")
        await init_db()
        logger.info("База данных инициализирована")
        
        logger.info("Инициализация Elasticsearch...")
        await init_elastic()
        logger.info("Elasticsearch инициализирован")
    except Exception as e:
        logger.error(f"Ошибка при инициализации: {e}")
        raise
    
    yield
    
    # Остановка
    try:
        await close_elastic()
        logger.info("Elasticsearch закрыт")
    except Exception as e:
        logger.error(f"Ошибка при закрытии Elasticsearch: {e}")

app = FastAPI(
    title="Search Service",
    description="Поисковый сервис для документов",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/search", response_model=SearchResponse)
async def search_documents(
    query: str = Query(..., description="Поисковый запрос"),
    limit: int = Query(20, description="Количество результатов"),
    db: AsyncSession = Depends(get_db)
):
    """Поиск документов по тексту"""
    service = SearchService(db)
    return await service.search(query, limit)

@app.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление документа по ID"""
    service = SearchService(db)
    deleted = await service.delete(doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": f"Document {doc_id} deleted"}

@app.post("/documents", response_model=DocumentResponse)
async def create_document(
    doc: DocumentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создание нового документа (для тестирования)"""
    service = SearchService(db)
    return await service.add_document(doc)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)