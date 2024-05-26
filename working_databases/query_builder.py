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
from aiogram import types

# -------------------------------- Локальные модули
from sql.get_user_data_sql import *
from working_databases.configs import *
# from working_databases.async_engine import *
# from working_databases.local_db_mockup import *
from working_databases.async_engine import *
# ----------------------------------------------------------------------------------------------------------------------

# Проверяем есть ли зарегистрированный телеграм id на удаленной базе: # async_get_telegram_id
#
# # Ключ подключения:
async def async_select(tb_name: str, columns_search: str,
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
# ---------------------------------------
async def get_user_data(engine_obj:AsyncEngine, *args_format: tuple[int, str, float]):

    """ Возвращает все данные с удаленного сервера о пользователях через сырой запрос
    НА выходе:  # Список всех данных:
                data = select_data.fetchall()
                # Имена колонок:
                columns = select_data.keys()
    Далее, все эти дапнные пердадуться в другую функцию для записи через ОРМ во внутреннюю таблицу проекта.
    """
    try:
        if args_format is None:
            args_format = None
        else:
            args_format

            if args_format:  # is not None
                # Форматируем SQL запрос, если есть аргументы для форматирования
                formatted_query = user_data_sql_text.format(*args_format) # todo sql - заменить после дагов!!!
                # user_data_sql_text_old, user_data_sql_text
            else:
                formatted_query = user_data_sql_text # todo sql

            # Забираем данные:
            async with engine_obj.connect() as conn:
                # Извлекаем данные:
                select_data = await conn.execute(text(formatted_query))

                # Список всех данных:
                data = select_data.fetchall()
                # Имена колонок:
                # columns = select_data.keys() - не нукжны!

            await engine_obj.dispose()  # Закрытие соединения вручную. Важно! Если не закрыть соединение, будут ошибки!

        # for r in data:
        #     print(f'{r}')

        return data  #, columns tuple(

    #  Если наступит ошибка в значениях:
    except (ValueError, TypeError):
        print(f'Не удалось выполнить sql запрос. Проверьте входные данные для: {args_format}')

    #  Другие любые ошибки (скорее всего будут относиться к синтаксису):
    except Exception as error:
        print(f'Ошибка: {type(error).__name__}, сообщение: {str(error)}!')
        # Ошибка извлечения данных.







# Check Type User
# async def orm_async_select(ANY_CONFIG: dict | URL | str, session_maker, tb_name):
#     session_maker = await ? get_async_sessionmaker(ANY_CONFIG)