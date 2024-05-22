"""
Модуль создания и удаления бд
"""
# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------- Импорт стандартных библиотек Пайтона
# ---------------------------------- Импорт сторонних библиотек
from sqlalchemy.ext.asyncio import AsyncEngine
from working_databases.local_db_mockup import Base
# -------------------------------- Локальные модули
from working_databases.async_engine import *
# ----------------------------------------------------------------------------------------------------------------------


# -------------------------------------------------------
# Создается отдельное подключение:
async def create_db(): # engine_obj:AsyncEngine
    """Функция создания базы данных и всех таблиц если они еще не созданы."""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_db(): # engine_obj:AsyncEngine
    """Функция сброса (удаления) базы данных и всех таблиц."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ------------------ огрызки
#     async with session_pool:
#         await session_pool.run_sync(Base.metadata.drop_all)

#  Через общий пул сесии:
# async def create_db(session_pool:AsyncSession):
#     """Функция создания базы данных и всех таблиц если они еще не созданы."""
#     async with session_pool.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#
# async def drop_db(session_pool:AsyncSession):
#     """Функция сброса (удаления) базы данных и всех таблиц."""
#
#     async with session_pool.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#
#     # async with session_pool:
#     #     await session_pool.run_sync(Base.metadata.drop_all)