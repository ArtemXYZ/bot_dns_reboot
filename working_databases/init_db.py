"""
Модуль создания и удаления бд
"""
# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------- Импорт стандартных библиотек Пайтона
# ---------------------------------- Импорт сторонних библиотек
from sqlalchemy.ext.asyncio import AsyncSession
# -------------------------------- Локальные модули
# ----------------------------------------------------------------------------------------------------------------------
#  Через общий пул сесии:
async def create_db(session_pool:AsyncSession):
    """Функция создания базы данных и всех таблиц если они еще не созданы."""
    async with session_pool:
        await session_pool.run_sync(Base.metadata.create_all)

async def drop_db(session_pool:AsyncSession):
    """Функция сброса (удаления) базы данных и всех таблиц."""

    async with session_pool:
        await session_pool.run_sync(Base.metadata.drop_all)

# -------------------------------------------------------
# Создается отдельное подключение: (работают, но не нужны)
# async def create_db_(engine_obj:AsyncEngine):
#     """Функция создания базы данных и всех таблиц если они еще не созданы."""
#     async with engine_obj.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#
# async def drop_db_(engine_obj:AsyncEngine):
#     """Функция сброса (удаления) базы данных и всех таблиц."""
#     async with engine_obj.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)

