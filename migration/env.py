import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db import Base
from app.db import ASYNC_DATABASE_URL

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = ASYNC_DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Включаем сравнение типов
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    """Выполнение миграций с синхронным подключением"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # Включаем сравнение типов для автоматического обнаружения изменений
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
        # Добавляем функцию для фильтрации таблиц
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()

def include_object(object, name, type_, reflected, compare_to):
    """Фильтр для включения только нужных объектов"""
    # Игнорируем системные таблицы
    if type_ == "table" and name.startswith("alembic"):
        return False
    return True

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async engine."""
    try:
        connectable = create_async_engine(
            ASYNC_DATABASE_URL,
            poolclass=pool.NullPool,
            echo=True,
            pool_pre_ping=True,
        )

        print(f"Подключение к БД: {ASYNC_DATABASE_URL}")
        
        async with connectable.connect() as connection:
            print("Подключение установлено успешно")
            await connection.run_sync(do_run_migrations)
            print("Миграции выполнены успешно")

        await connectable.dispose()
        
    except Exception as e:
        print(f"Ошибка при выполнении миграций: {e}")
        raise

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())