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
import pandas as pd
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

async def get_user_data_df(*args_format: tuple[int, str, float]) -> pd.DataFrame:
    """
    Функция для извлечения данных из любого запроса sql в DataFrame. Важно! *args_format - только int!!!

    :param any_sql_path: любой путь по типу: r'\\src\\sql\\in.sql' , defaults to None
    :type any_sql_path: str or bytes
    # только байтовые, либо только строковые объекты

    :param root_dir: путь корневого каталога (импортируется)
    :type root_dir: :str or bytes

    :param any_config: путь сохранения файла (указать)
    :type any_config: dict

    :param args_format: путь сохранения файла (указать)
    :type args_format: tuple[int, str, float]

    :rtype: pd.DataFrame
    :return: DataFrame

    :notes:

    #  todo: строка  с путем может конфликтовать (выдавать ошибки) из за "сырой строки" = r'\\*'. Именно по этому
    #  todo: переменную с путем необходимо сразу писать в параметры функции без использования промежуточных переменных
    #  todo: (из-за этого были ошибки ранее).
    # Аргумент any_sql_path должен быть абсолютный путь до файла, в том числе имя файла и расширение.
    """
    try:

        # todo: Позже переписать, добавить исключения, проверку на наличия файла, правильности пути.
        if args_format is None:
            args_format = None
        else:
            # args_format

            connection: AsyncSession = await get_async_sessionmaker(CONFIG_JAR_ASYNCPG)

            if args_format:  # is not None
                # Форматируем SQL запрос, если есть аргументы для форматирования
                formatted_query = user_data_sql_text.format(*args_format)
            else:
                formatted_query = user_data_sql_text

            # Извлекаем данные:
            extract_data = pd.read_sql(formatted_query, con=connection)  # Сохраняем данные в дата-фрейм без

            # Вставляем данные:
            with connection:
                extract_data.to_sql(name_table, con=connection, if_exists=if_non_nul, index=False, schema=None)
                insert_data = await session_remote.insert(select_data)



            connection.close()  # Закрытие соединения вручную. Важно! Если не закрыть соединение, будут ошибки!





            # return extract

    #  Если наступит ошибка в значениях:
    except (ValueError, TypeError):
        print(f'Не удалось выполнить sql запрос. Проверьте входные данные для {any_sql_path}: {args_format}')

    #  Другие любые ошибки (скорее всего будут относиться к синтаксису):
    except Exception as error:
        print(f'Ошибка: {type(error).__name__}, сообщение: {str(error)}!')
        # Ошибка извлечения данных





# df_branch_coefficients_data = get_from_sql(r'\src\sql\get_branch_coefficients_data.sql',
#                                                root_dir, config_local_host)



# Check Type User
# async def orm_async_select(ANY_CONFIG: dict | URL | str, session_maker, tb_name):
#     session_maker = await ? get_async_sessionmaker(ANY_CONFIG)