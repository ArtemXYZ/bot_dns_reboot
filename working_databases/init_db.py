"""
Модуль создания бд
"""
# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------- Импорт стандартных библиотек Пайтона
# ---------------------------------- Импорт сторонних библиотек
import asyncio
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from sqlalchemy.ext.asyncio import AsyncSession
from working_databases.local_db_mockup import Base
# -------------------------------- Локальные модули
from working_databases.async_engine import *

# ----------------------------------------------------------------------------------------------------------------------
async def create_db(engine_obj:AsyncEngine):
    """Функция создания базы данных и всех таблиц если они еще не созданы."""
    async with engine_obj.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db(engine_obj:AsyncEngine):
    """Функция сброса (удаления) базы данных и всех таблиц."""
    async with engine_obj.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)