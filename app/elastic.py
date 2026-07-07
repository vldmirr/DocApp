from elasticsearch import AsyncElasticsearch
import os

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")

# Создаем клиент 
es_client = AsyncElasticsearch(
    [ELASTICSEARCH_URL],
    request_timeout=30,
    max_retries=3,
    retry_on_timeout=True
)

async def init_elastic():
    """Создание индекса если не существует"""
    try:
        # Проверяем существование индекса
        exists = await es_client.indices.exists(index="documents")
        
        if exists:
            # Если индекс существуе
            await es_client.indices.delete(index="documents")
            print("Старый индекс удален")
        
        # Создаем новый индекс с правильным маппингом
        index_settings = {
            "settings": {
                "analysis": {
                    "analyzer": {
                        "russian_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "russian_stop",
                                "russian_stemmer"
                            ]
                        }
                    },
                    "filter": {
                        "russian_stop": {
                            "type": "stop",
                            "stopwords": "_russian_"
                        },
                        "russian_stemmer": {
                            "type": "stemmer",
                            "language": "russian"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "id": {"type": "integer"},
                    "text": {
                        "type": "text",
                        "analyzer": "russian_analyzer",
                        "fields": {
                            "keyword": {"type": "keyword", "ignore_above": 256}
                        }
                    }
                }
            }
        }
        
        await es_client.indices.create(index="documents", body=index_settings)
        print("Индекс 'documents' успешно создан")
        
    except Exception as e:
        print(f"Ошибка при инициализации Elasticsearch: {e}")
        raise

async def index_document(doc_id: int, text: str):
    """Индексация документа в Elasticsearch"""
    try:
        await es_client.index(
            index="documents",
            id=doc_id,
            document={"id": doc_id, "text": text}
        )
    except Exception as e:
        print(f"Ошибка индексации документа {doc_id}: {e}")

async def delete_from_elastic(doc_id: int):
    """Удаление документа из Elasticsearch"""
    try:
        await es_client.delete(index="documents", id=doc_id)
    except Exception as e:
        print(f"Ошибка удаления документа {doc_id} из Elasticsearch: {e}")

async def search_elastic(query: str, size: int = 20):
    """Поиск документов в Elasticsearch"""
    if not query or query.strip() == "":
        return []
    
    try:
        response = await es_client.search(
            index="documents",
            body={
                "query": {
                    "match": {
                        "text": {
                            "query": query,
                            "operator": "or",
                            "fuzziness": "AUTO"
                        }
                    }
                },
                "size": size,
                "_source": ["id"]
            }
        )
        
        # Извлекаем ID документов
        doc_ids = [int(hit["_id"]) for hit in response["hits"]["hits"]]
        return doc_ids
        
    except Exception as e:
        print(f"Ошибка поиска в Elasticsearch: {e}")
        return []

async def delete_index():
    """Удаление индекса (для тестов)"""
    try:
        await es_client.indices.delete(index="documents")
        print("Индекс 'documents' удален")
    except Exception as e:
        print(f"Ошибка удаления индекса: {e}")

async def close_elastic():
    """Закрытие соединения с Elasticsearch"""
    await es_client.close()