# tests/test_elastic.py
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.elastic import (
    init_elastic,
    index_document,
    delete_from_elastic,
    search_elastic,
    delete_index,
    close_elastic,
)

# Фикстуры для тестов
@pytest.fixture
def mock_es_client():
    """Создает мок клиента Elasticsearch"""
    with patch('app.elastic.es_client') as mock:
        # Создаем все необходимые моки
        mock.indices = MagicMock()
        mock.indices.exists = AsyncMock()
        mock.indices.delete = AsyncMock()
        mock.indices.create = AsyncMock()
        mock.index = AsyncMock()
        mock.delete = AsyncMock()
        mock.search = AsyncMock()
        mock.close = AsyncMock()
        yield mock

@pytest_asyncio.fixture
async def test_data():
    """Тестовые данные"""
    return {
        "doc_id": 1,
        "text": "Это тестовый документ для проверки поиска"
    }

# Тесты для init_elastic
@pytest.mark.asyncio
async def test_init_elastic_creates_new_index(mock_es_client):
    """Тест создания нового индекса, если он не существует"""
   
    mock_es_client.indices.exists.return_value = False
    
    await init_elastic()
    
   
    mock_es_client.indices.exists.assert_called_once_with(index="documents")
    mock_es_client.indices.delete.assert_not_called()
    mock_es_client.indices.create.assert_called_once()
    
   
    call_args = mock_es_client.indices.create.call_args
    assert call_args.kwargs["index"] == "documents"
    assert "mappings" in call_args.kwargs["body"]
    assert "settings" in call_args.kwargs["body"]

@pytest.mark.asyncio
async def test_init_elastic_recreates_existing_index(mock_es_client):
    """Тест пересоздания индекса, если он уже существует"""
    # Настраиваем мок: индекс существует
    mock_es_client.indices.exists.return_value = True
    
    await init_elastic()
    
    # Проверяем, что индекс был удален и создан заново
    mock_es_client.indices.exists.assert_called_once_with(index="documents")
    mock_es_client.indices.delete.assert_called_once_with(index="documents")
    mock_es_client.indices.create.assert_called_once()

@pytest.mark.asyncio
async def test_init_elastic_handles_error(mock_es_client):
    """Тест обработки ошибок при инициализации"""
    mock_es_client.indices.exists.side_effect = Exception("Connection error")
    
    with pytest.raises(Exception, match="Connection error"):
        await init_elastic()

@pytest.mark.asyncio
async def test_index_document_success(mock_es_client, test_data):
    """Тест успешной индексации документа"""
    doc_id = test_data["doc_id"]
    text = test_data["text"]
    
    await index_document(doc_id, text)
    
    mock_es_client.index.assert_called_once_with(
        index="documents",
        id=doc_id,
        document={"id": doc_id, "text": text}
    )

@pytest.mark.asyncio
async def test_index_document_handles_error(mock_es_client, test_data, capsys):
    """Тест обработки ошибки при индексации"""
    mock_es_client.index.side_effect = Exception("Index error")
    doc_id = test_data["doc_id"]
    text = test_data["text"]
    
    await index_document(doc_id, text)
    
    captured = capsys.readouterr()
    assert f"Ошибка индексации документа {doc_id}" in captured.out

@pytest.mark.asyncio
async def test_delete_from_elastic_success(mock_es_client):
    """Тест успешного удаления документа"""
    doc_id = 1
    
    await delete_from_elastic(doc_id)
    
    mock_es_client.delete.assert_called_once_with(
        index="documents",
        id=doc_id
    )

@pytest.mark.asyncio
async def test_delete_from_elastic_handles_error(mock_es_client, capsys):
    """Тест обработки ошибки при удалении"""
    mock_es_client.delete.side_effect = Exception("Delete error")
    doc_id = 1
    
    await delete_from_elastic(doc_id)
    
    captured = capsys.readouterr()
    assert f"Ошибка удаления документа {doc_id} из Elasticsearch" in captured.out

@pytest.mark.asyncio
async def test_search_elastic_success(mock_es_client):
    """Тест успешного поиска документов"""
    # Настраиваем ответ Elasticsearch
    mock_response = {
        "hits": {
            "hits": [
                {"_id": "1", "_source": {"id": 1}},
                {"_id": "2", "_source": {"id": 2}}
            ]
        }
    }
    mock_es_client.search.return_value = mock_response
    
    result = await search_elastic("тестовый запрос", size=20)
    
    assert result == [1, 2]
    
    mock_es_client.search.assert_called_once()
    call_args = mock_es_client.search.call_args

    assert call_args.kwargs["index"] == "documents"
    assert call_args.kwargs["body"]["size"] == 20
    assert "query" in call_args.kwargs["body"]
    assert "match" in call_args.kwargs["body"]["query"]
    assert "text" in call_args.kwargs["body"]["query"]["match"]
    assert call_args.kwargs["body"]["query"]["match"]["text"]["query"] == "тестовый запрос"
    assert call_args.kwargs["body"]["query"]["match"]["text"]["operator"] == "or"
    assert call_args.kwargs["body"]["query"]["match"]["text"]["fuzziness"] == "AUTO"
    assert call_args.kwargs["body"]["_source"] == ["id"]

@pytest.mark.asyncio
async def test_search_elastic_with_different_size(mock_es_client):
    """Тест поиска с разным размером результата"""
    mock_response = {
        "hits": {
            "hits": [
                {"_id": str(i), "_source": {"id": i}} for i in range(5)
            ]
        }
    }
    mock_es_client.search.return_value = mock_response
    
    result = await search_elastic("запрос", size=5)
    
    assert len(result) == 5
    mock_es_client.search.assert_called_once()
    call_args = mock_es_client.search.call_args
    assert call_args.kwargs["body"]["size"] == 5

@pytest.mark.asyncio
async def test_search_elastic_empty_query(mock_es_client):
    """Тест поиска с пустым запросом"""
    result = await search_elastic("")
    assert result == []
    mock_es_client.search.assert_not_called()

@pytest.mark.asyncio
async def test_search_elastic_whitespace_query(mock_es_client):
    """Тест поиска с запросом из пробелов"""
    result = await search_elastic("   ")
    assert result == []
    mock_es_client.search.assert_not_called()

@pytest.mark.asyncio
async def test_search_elastic_empty_response(mock_es_client):
    """Тест поиска без результатов"""
    mock_response = {"hits": {"hits": []}}
    mock_es_client.search.return_value = mock_response
    
    result = await search_elastic("несуществующий запрос")
    assert result == []

@pytest.mark.asyncio
async def test_search_elastic_handles_error(mock_es_client, capsys):
    """Тест обработки ошибки при поиске"""
    mock_es_client.search.side_effect = Exception("Search error")
    
    result = await search_elastic("тестовый запрос")
    
    assert result == []
    captured = capsys.readouterr()
    assert "Ошибка поиска в Elasticsearch" in captured.out

@pytest.mark.asyncio
async def test_search_elastic_returns_only_ids(mock_es_client):
    """Тест, что search возвращает только ID документов"""
    mock_response = {
        "hits": {
            "hits": [
                {"_id": "10", "_source": {"id": 10, "extra": "field"}},
                {"_id": "20", "_source": {"id": 20, "extra": "field"}},
                {"_id": "30", "_source": {"id": 30, "extra": "field"}}
            ]
        }
    }
    mock_es_client.search.return_value = mock_response
    
    result = await search_elastic("запрос")
    
    assert result == [10, 20, 30]

@pytest.mark.asyncio
async def test_delete_index_success(mock_es_client):
    """Тест успешного удаления индекса"""
    await delete_index()
    
    mock_es_client.indices.delete.assert_called_once_with(index="documents")

@pytest.mark.asyncio
async def test_delete_index_handles_error(mock_es_client, capsys):
    """Тест обработки ошибки при удалении индекса"""
    mock_es_client.indices.delete.side_effect = Exception("Delete index error")
    
    await delete_index()
    
    captured = capsys.readouterr()
    assert "Ошибка удаления индекса" in captured.out

@pytest.mark.asyncio
async def test_close_elastic(mock_es_client):
    """Тест закрытия соединения"""
    await close_elastic()
    mock_es_client.close.assert_called_once()

# # Интеграционные тесты (требуют запущенного Elasticsearch)
# @pytest.mark.integration
# @pytest.mark.asyncio
# async def test_integration_full_flow():
#     """Интеграционный тест полного цикла работы с Elasticsearch"""
#     # Проверяем, что Elasticsearch доступен
#     try:
#         await es_client.info()
#     except Exception as e:
#         pytest.skip(f"Elasticsearch not available: {e}")
    
#     try:
#         # Инициализируем индекс
#         await init_elastic()
        
#         # Индексируем документы
#         test_docs = [
#             (1, "Первый тестовый документ"),
#             (2, "Второй тестовый документ для поиска")
#         ]
#         for doc_id, text in test_docs:
#             await index_document(doc_id, text)
        
#         #Search
#         results = await search_elastic("тестовый", size=10)
#         assert len(results) > 0
#         assert 1 in results or 2 in results
        
#         #Delete
#         await delete_from_elastic(1)
        
#         # Check
#         results_after_delete = await search_elastic("тестовый", size=10)
#         assert 1 not in results_after_delete
        
#         #Clear
#         await delete_index()
        
#     finally:
#         await close_elastic()

# @pytest.mark.integration
# @pytest.mark.asyncio
# async def test_integration_bulk_indexing():
#     """Интеграционный тест массовой индексации"""
#     try:
#         await es_client.info()
#     except Exception as e:
#         pytest.skip(f"Elasticsearch not available: {e}")
    
#     try:
#         await init_elastic()
        
#         # Индексируем много документов
#         documents = [(i, f"Документ номер {i}") for i in range(1, 101)]
#         for doc_id, text in documents:
#             await index_document(doc_id, text)
        
#         # Search
#         results = await search_elastic("документ", size=20)
#         assert len(results) == 20
        
#         # chek ID
#         expected_ids = list(range(1, 101))
#         assert sorted(results) == expected_ids
        
#         # Очистка
#         await delete_index()
        
#     finally:
#         await close_elastic()
