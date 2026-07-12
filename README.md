# DocApp

## Установка

```bash
git clone https://github.com/vldmirr/DocApp
cd DocApp
```

### Первый способ: ручная установка

```bash
python -m venv venv
#Для Windows: 
venv\Scripts\activate
# Для macOS / Linux: 
source venv/bin/activate

pip install -r requirements.txt
```

### Второй способ: поднимаем все необходимые контейнеры
```bash
docker-compose up -d
```

## ⚙️Конфигурация:

Файл содержимое файла `.env` выглядит следующим образом, и содержит в себе параметры для настройки базы:
```.env
POSTGRES_DB=test_db
POSTGRES_USER=test_postgres
POSTGRES_PASSWORD=test_password
POSTGRES_HOST=db 
POSTGRES_PORT=5432

DEBUG=True
LOG_LEVEL=INFO


DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
```

Сервисы:
   - `web-1`: FastAPI приложение

   - `db-1`: PostgreSQL база данных

   - `elastic-1`: сам движек 

## Инициализия миграции и применение миграции

```bash

docker-compose run --rm web alembic revision --autogenerate -m "init"
```
## ⚡Запуску:
### Применяем миграции
```bash
docker-compose run --rm web alembic upgrade head 

#Предварительная проверка созданных таблиц
docker-compose exec db psql -U test_postgres -d test_db -c "\dt"
```

## 📡 API конечные точки
Swagger UI: http://localhost:8080/docs

- **GET** `/search` - непосредственно сам поиск
- **POST** `/documents` - создание запроса
- **DELETE** `/documents/{doc_id}` - удаление запроса

## Формат передаваемых данных:

```json
{
    "text": "some text",
    "rubrics": ["rubric1", "rubric2"]  
}
```
