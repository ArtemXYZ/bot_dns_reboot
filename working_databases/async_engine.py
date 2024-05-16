"""
Модуль содержит функции создания подключения к базам данных.


!!! Обязательно в конфиге CONFIG_JAR_DRIVERNAME=postgresql+asyncpg.
!!!! Обязательна установка библиотеки asyncpg.

"""
# check_telegram_id
# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------- Импорт стандартных библиотек Пайтона
import os

# ---------------------------------- Импорт сторонних библиотек
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.engine.url import URL

# -------------------------------- Локальные модули
# from working_databases.configs import *


# ----------------------------------------------------------------------------------------------------------------------
# 0/ Асинхронное подключение к базе данных : !- работает
async def get_async_engine(ANY_CONFIG: dict | URL | str) -> object:
    """Функция создает АСИНХРОННОЕ подключение к базе данных. На вход принимает файл конфигурации.
    !!! Обязательно в конфиге CONFIG_JAR_DRIVERNAME=postgresql+asyncpg,
    Несмотря на то, что используется Алхимия, необходима установка библиотеки asyncpg!!!!
    """

    # Проверка типа входной конфигурации подключения:
    # Если на вход конфигурация в словаре:
    if isinstance(ANY_CONFIG, dict) == True:
        url_string = URL.create(**ANY_CONFIG)  # 1. Формируем URL-строку соединения с БД.
        #  Эквивалент: url_string = (f'{drivername}://{username}:{password}@{host}:{port}/{database}')

    # Если на вход url_string:
    elif isinstance(ANY_CONFIG, str) == True:
        url_string = ANY_CONFIG
    else:
        url_string = None

    # 2. Создаем переменную асинхронного подключения к БД.
    async_engine = create_async_engine(url_string)
    # , echo=True - работает,  poolclass=AsyncAdaptedQueuePool, future=True - ?
    # connection = async_engine.connect()
    return async_engine
    # return create_async_engine(url_string)

# Асинхронная сессия:
async def get_async_sessionmaker(ANY_CONFIG: dict | URL | str):
    session_maker = async_sessionmaker(bind=get_async_engine(ANY_CONFIG),
                                             class_=AsyncSession, expire_on_commit=False) # await ?
    return session_maker


#

# ---------------------- Тесты:
# async def get():
#     aws = await async_select(CONFIG_JAR_ASYNCPG, 'inlet.staff_for_bot', 'tg',
#                           'tg', 1034809823)
#     # return aws
#     print(aws)
#
# asyncio.run(get())

# async_sessionmaker = get_async_sessionmaker(config)
# async def get_telegram_id(session: AsyncSession, tg_id: int):
#     query = select(staff_for_bot).where(staff_for_bot.tg == tg_id)
#
#     result = await session.execute(query)
#     return result.scalar()

# ----------------------------------------------------- разобрать потом

# # --------------------- Работает только в этом модуле в других недоступен объект сессии
# Проверяем есть ли зарегистрированный телеграм id на удаленной базе:
# async_get_telegram_id
# async def async_select(ANY_CONFIG: dict | URL | str, tb_name: str, columns_search: str, where_columns_name: str,
#                        where_columns_value: any):  # , results_aal_or: str
#
#     # SQL Сырой запрос на выборку данных (+ условие фильтрации выборки):
#     # Это работает.
#     SQL = text(
#         f"SELECT {tb_name}.{columns_search} FROM {tb_name} "
#         f"WHERE {tb_name}.{where_columns_name} = '{where_columns_value}'")
#     # {schema_and_table} WHERE {where_columns_name} = {where_columns_value} # - Работает
#
#     # Ключ подключения:
#     engine_obj = get_async_engine(ANY_CONFIG)
#
#     async with engine_obj.begin() as async_connection: # todo здесь может быть проблема с connect()
#         # connection
#         result_temp = await async_connection.execute(SQL)
#
#         # async_connection.close() - не нужно
#         # await async_connection.dispose()
#         # async_connection.commit()
#         # async_connection = async_engine.connect() - можно так (вроде то же самое, но без ролбека транзакций)
#         # connect() в этом методе явно надо прописывать комит, а в аналогичной begin - есть автокомит.
#
#     # Выдает в текстовом формате (не точно)
#     result = result_temp.scalar()
#
#     # для исключения ошибки с преобразованием типов:
#     if result is not None:
#         fin = int(result)
#     else:
#         fin = result
#
#     return fin
# ---------------------




# Асинхронное подключение к базе данных (sessionmaker): !- работает
# async def get_async_sessionmaker(ANY_CONFIG: dict | URL | str):
#     """Функция создает АСИНХРОННОЕ подключение к базе данных. На вход принимает файл конфигурации.
#     !!! Обязательно в конфиге CONFIG_JAR_DRIVERNAME=postgresql+asyncpg,
#     Несмотря на то, что используется Алхимия, необходима установка библиотеки asyncpg!!!!
#     """
#
#     try:  # Блок исключений ошибок при осуществлении подключения:
#         # any_config # 1.Проверка на отсутствие файла концигурации подкючения: если нет данных на вход: !!
#
#         # Проверка типа входной конфигурации подключения:
#         # Если на вход конфигурация в словаре:
#         if isinstance(ANY_CONFIG, dict) == True:
#             url_string = URL.create(**ANY_CONFIG)  # 1. Формируем URL-строку соединения с БД.
#             #  Эквивалент: url_string = (f'{drivername}://{username}:{password}@{host}:{port}/{database}')
#
#         # Если на вход url_string:
#         elif isinstance(ANY_CONFIG, str) == True:
#             url_string = ANY_CONFIG
#         else:
#             url_string = None
#
#         # 2. Создаем переменную асинхронного подключения к БД.
#         async_engine = create_async_engine(url_string, poolclass=AsyncAdaptedQueuePool, future=True,
#                                            echo=True)  # , echo=True - работает,  poolclass=AsyncAdaptedQueuePool, future=True - ?
#
#         async_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)
#         # , class_=AsyncSession, expire_on_commit=False
#         # ! параметр expire_on_commit=False - сразу не закрывается ссесия после коммита для повторного использования.
#
#         # async_connection = async_engine.connect() - можно так (вроде то же самое, но без ролбека транзакций)
#         # connect() в этом методе явно надо прописывать комит, а в аналогичной begin - есть автокомит.
#
#         return async_session
#
#     #  Если наступит ошибка в значениях:
#     except (ValueError, TypeError):
#         print(f'Ошибка создания ссесии подключения к базе данных! Проверьте входные данные {ANY_CONFIG} \n'
#               f'и зависимые переменные: формирование url_string: {url_string}, async_engine: {async_engine}')
#
#     #  Другие любые ошибки (скорее всего будут относиться к синтаксису):
#     except Exception as error:
#         print(f'Ошибка: {type(error).__name__}, сообщение: {str(error)}!')

# Проверяем есть ли зарегистрированныйц телеграм id на удаленной базе:
# async def get_telegram_id(ANY_CONFIG, tb_name: str, columns_search: str, where_columns_name: str,
#                           where_columns_value: any): # , results_aal_or: str
#     """
#         Функция выбирает данные по идентификатору (id) через сырой запрос.
#         # tuple[int, str, float]
#
#         :param tb_name: Имя таблицы где ищем. (inlet.staff_for_bot)
#         :type tb_name: str
#
#         :param columns_search: Имя колонки где ищем. (* - колонка)
#         :type columns_search: str
#
#         :param where_columns_name: Фильтруем по колонке (* - колонка)
#         :type where_columns_name: str
#
#         :param where_columns_value: Значение для  фильтрации (* - колонка)
#         :type where_columns_value: any
#
#         :param results_aal_or: Показать все строки или варианты: #  all() - показать все записи, first - первая строка,
#          one - одна, # one_or_none - одна или ноль (если больше -будет ошибка)
#         :type results_aal_or: any
#
#         :rtype: pd.DataFrame
#         :return: DataFrame
#
#         :notes: Функция частично универсально. Есть возможность использовать различнгые методы выдачи результатов
#         (выше описано). Однако возможности функции ограничены -  только для одной калонки. Можно переделать под множество
#         через кваргсы.
#         """
#
#     async with get_async_sessionmaker(ANY_CONFIG) as async_session:
#
#         # SQL Сырой запрос на выборку данных (+ условие фильтрации выборки):
#         SQL = text(f"SELECT {columns_search} FROM {tb_name} WHERE {where_columns_name} = {where_columns_value}") # - Работает
#
#         result_temp = await async_session.execute(SQL)  # Извлечь данные из запроса
#
#         # # Варианты выдачи выборки:
#         # if results_aal_or == 'all':
#         #     result = result_temp.all()
#         #
#         # elif results_aal_or == 'first':
#         #     result = result_temp.first()
#         #
#         # elif results_aal_or == 'one':
#         #     result = result_temp.one()
#         #
#         # elif results_aal_or == 'one_or_none':
#         #     result = result_temp.one_or_none()
#
#     return result_temp


# _______________________ пробы
# # return result.scalar()  # Выдать скалярные (очищенные) величины
# def g(ANY_CONFIG, tb_name: str, columns_search: str, where_columns_name: str,
#                           where_columns_value: any):
#     SQL = text(f"SELECT {columns_search} FROM {tb_name} WHERE {where_columns_name} = {where_columns_value}")
#     return SQL
#
#     SQL = g(CONFIG_JAR, 'inlet.staff_for_bot','tg', 'tg', 49295383)
#     async with get_async_sessionmaker(CONFIG_JAR) as async_session:
#         result_temp = async_session.execute(SQL)
#
#     return print(result_temp.scalar())
# print(get())


# async def get():
#     # f = get_telegram_id(CONFIG_JAR, 'inlet.staff_for_bot',
#     #                     'tg', 'tg', '49295383') #, 'one'
#     # f = get_async_sessionmaker(CONFIG_JAR)
#     f = get_telegram_id(CONFIG_JAR, 'inlet.staff_for_bot',
#                         'tg', 'tg', '49295383')
#     print(f)

# if isinstance(ANY_CONFIG, dict) == True:
