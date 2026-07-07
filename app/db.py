from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime, timezone
from sqlalchemy.exc import OperationalError
import os
import asyncio

def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


# Используем переменную из окружения или значение по умолчанию
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://test_postgres:test_password@db:5432/test_db")

engine = create_async_engine(DATABASE_URL, echo=os.getenv("DEBUG", "False").lower() == "true")
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    rubrics = Column(JSON, nullable=False)
    text = Column(String, nullable=False)
    created_date = Column(DateTime, nullable=False, default=utc_now())

async def init_db(max_retries=5, delay=3):
    """Инициализация БД с повторными попытками"""
    for attempt in range(max_retries):
        try:
            print(f"Попытка подключения к БД {attempt + 1}/{max_retries}...")
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print("База инициализирована!")
            return
        except OperationalError as e:
            print(f"Ошибка подключения к БД (попытка {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise
            print(f"Повтор через {delay} секунд...")
            await asyncio.sleep(delay)

async def get_db():
    async with async_session() as session:
        yield session