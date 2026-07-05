import logging
import time
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.db import engine
from app.models.models import Base
from app.api import doc_router

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создание таблиц при запуске
    logger.info("started")
    yield
    logger.info("shutdown")
    

app = FastAPI(
    title="SearchApp API",
    description="API сервис для просмотра и поиска нужных документов",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {process_time:.2f}ms"
    )
    
    return response

# Подключение роутеров
app.include_router(doc_router.router, prefix="/api/v1")
