import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest
from ..app.main import app
from ..app.db import init_db
from httpx import AsyncClient, ASGITransport
import asyncio

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Инициализирует БД перед тестами"""

    asyncio.run(init_db())

@pytest.mark.asyncio
async def test_search_success():
    async with AsyncClient(transport=ASGITransport(app=app),
                            base_url="http://test") as ac: 
        response = await ac.get("/search", params={"query":"text","limit":20}) 
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_document():
    async with AsyncClient(transport=ASGITransport(app=app),
                            base_url="http://test") as ac:  
        data = {"text":"test_text","rubrics":["6","7"]}
        response = await ac.post("/documents", json=data)
        assert response.status_code == 200
   
@pytest.mark.asyncio  
async def test_delete_document():
    async with AsyncClient(transport=ASGITransport(app=app),
                            base_url="http://test") as ac: 
        response = await ac.delete("/documents/1")
        assert response.status_code == 200
    
@pytest.mark.asyncio  
async def test_delete_not_found():
    async with AsyncClient(transport=ASGITransport(app=app),
                            base_url="http://test") as ac: 
        response = await ac.delete("/documents/9999")
        assert response.status_code == 404