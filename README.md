# DocApp

## Установка

## Установка:
```bash
git clone https://github.com/vldmirr/DocApp
cd DocApp
```

## ⚙️Конфигурация:
Для конфигурации проекта используется файл `.env` в проекте есть готовый файл в качестве примера `.env.example`:
```bash
# 1. Создаем .env из примера (вручную)
cp .env.example .env

# 2. Редактируем настройки
nano .env
```

Файл содержимое файла `.env` выглядит следующим образом, и содержит в себе параметры для настройки базы:
```.env
POSTGRES_DB=test_db
POSTGRES_USER=test_postgres
POSTGRES_PASSWORD=test_password
POSTGRES_HOST=test_db
POSTGRES_PORT=5432

DEBUG=True
LOG_LEVEL=INFO

DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
```

### 1. поднимаем все необходимые контейнеры
```bash
docker-compose up -d
```
Сервисы:
   - `web`: FastAPI приложение

   - `db`: PostgreSQL база данных

## Инициализия миграции 

```bash

docker-compose run --rm web alembic revision --autogenerate -m "db2026-07-05"
```
## ⚡Запуску:
### Применяем миграции
```bash
docker-compose run --rm web alembic upgrade head 

#Предварительная проверка созданных таблиц
docker-compose exec db psql -U postgres -d quizapp_db -c "\dt"
```

## 📡 API конечные точки
Swagger UI: http://localhost:/docs

**POST** `/api/v1/documents` - создание запроса
**DELETE** `/api/v1/documents/{doc_id}` - удаление запроса

## Формат передаваемых данных:

```json
{
    "text": "some text",
    "rubrics": ["rubric1", "rubric2"]  
}
```