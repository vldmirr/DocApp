import pytest
from fastapi.testclient import TestClient
from ..app.main import app

client = TestClient(app)

class TestSearchAPI:
    def test_search_success(self):
        response = client.get("/search?query=test")
        assert response.status_code == 200
        
    def test_search_empty_query(self):
        response = client.get("/search?query=")
        assert response.status_code == 422
        
    def test_create_document(self):
        data = {"id": 1, "text": "test content"}
        response = client.post("/documents", json=data)
        assert response.status_code == 200
        
    def test_delete_document(self):
        response = client.delete("/documents/1")
        assert response.status_code == 200
        
    def test_delete_not_found(self):
        response = client.delete("/documents/9999")
        assert response.status_code == 404