"""
Модуль содержит функции асинхронных SQL запросов к базам данных.
В основном с помощью ОРМ.
"""
# check_telegram_id
# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------- Импорт стандартных библиотек Пайтона
# ---------------------------------- Импорт сторонних библиотек
import asyncio
from sqlalchemy import select, String, Table, update, delete, text
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession


# -------------------------------- Локальные модули
from working_databases.async_engine import *


# ----------------------------------------------------------------------------------------------------------------------

# Проверяем есть ли зарегистрированный телеграм id на удаленной базе: # async_get_telegram_id
#
# # Ключ подключения:
async def async_select( tb_name: str, columns_search: str,
                       where_columns_name: str, where_columns_value: any, engine_obj:AsyncEngine):  # , results_aal_or: str
    """
    engine_obj = get_async_engine(CONFIG_JAR_ASYNCPG)
    SQL - можно вынести в параметр и будет более универсальная функция.
    """

    # SQL Сырой запрос на выборку данных (+ условие фильтрации выборки):
    # Это работает.
    SQL = text(
        f"SELECT {tb_name}.{columns_search} FROM {tb_name} "
        f"WHERE {tb_name}.{where_columns_name} = '{where_columns_value}'")
    # {schema_and_table} WHERE {where_columns_name} = {where_columns_value} # - Работает


    async with engine_obj.connect() as async_connection: # todo здесь может быть проблема с connect()
        # connection
        result_temp = await async_connection.execute(SQL)

        # async_connection.close() - не нужно
        # await async_connection.dispose()
        # async_connection.commit()
        # async_connection = async_engine.connect() - можно так (вроде то же самое, но без ролбека транзакций)
        # connect() в этом методе явно надо прописывать комит, а в аналогичной begin - есть автокомит.

    # Выдает в текстовом формате (не точно)
    result = result_temp.scalar()

    # для исключения ошибки с преобразованием типов:
    if result is not None:
        fin = int(result)
    else:
        fin = result

    return fin

















# Check Type User
# async def orm_async_select(ANY_CONFIG: dict | URL | str, session_maker, tb_name):
#     session_maker = await ? get_async_sessionmaker(ANY_CONFIG)