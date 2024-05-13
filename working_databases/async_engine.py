"""
Модуль содержит функции асинхронного подключения к базам данных.
"""

# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------- Импорт стандартных библиотек Пайтона
import os

# ---------------------------------- Импорт сторонних библиотек
import asyncio
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sqlalchemy.engine.url import URL
from sqlalchemy.exc import OperationalError
from sqlalchemy import text  # , insert

from working_databases.configs import *



# ----------------------------------------------------------------------------------------------------------------------
# Асинхронное подключение к базе данных (sessionmaker):
def get_async_sessionmaker(ANY_CONFIG: dict | URL | str):
    """Функция создает АСИНХРОННОЕ подключение к базе данных. На вход принимает файл конфигурации."""

    try:  # Блок исключений ошибок при осуществлении подключения:
        # any_config # 1.Проверка на отсутствие файла концигурации подкючения: если нет данных на вход: !!

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

        # 2. Создаем переменную  асинхронного подключения к БД.
        async_engine = create_async_engine(url_string, echo=True)  # , echo=True - работает

        async_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)
        # ! параметр expire_on_commit=False - сразу не закрывается ссесия после коммита для повторного использования.

        ## async_connection = async_engine.connect() - можно так (вроде то же самое, но без ролбека транзакций)

        return async_session

    #  Если наступит ошибка в значениях:
    except (ValueError, TypeError):
        print(f'Ошибка создания ссесии подключения к базе данных! Проверьте входные данные {ANY_CONFIG} \n'
              f'и зависимые переменные: формирование url_string: {url_string}, async_engine: {async_engine}')

    #  Другие любые ошибки (скорее всего будут относиться к синтаксису):
    except Exception as error:
        print(f'Ошибка: {type(error).__name__}, сообщение: {str(error)}!')


# check_telegram_id:
async def get_telegram_id(ANY_CONFIG, tb_name: str, columns_search: str, where_columns_name: str,
                          where_columns_value: any, results_aal_or: str):
    """
        Функция выбирает данные по идентификатору (id) через сырой запрос.
        # tuple[int, str, float]

        :param tb_name: Имя таблицы где ищем. (branch_coefficients_data)
        :type tb_name: str

        :param columns_search: Имя колонки где ищем. (closed - колонка)
        :type columns_search: str

        :param where_columns_name: Фильтруем по колонке (branch_1c_id - колонка)
        :type where_columns_name: str

        :param where_columns_value: Значение для  фильтрации (branch_1c_id - колонка)
        :type where_columns_value: any

        :param results_aal_or: Показать все строки или варианты: #  all() - показать все записи, first - первая строка,
         one - одна, # one_or_none - одна или ноль (если больше -будет ошибка)
        :type results_aal_or: any

        :rtype: pd.DataFrame
        :return: DataFrame

        :notes: Функция частично универсально. Есть возможность использовать различнгые методы выдачи результатов
        (выше описано). Однако возможности функции ограничены -  только для одной калонки. Можно переделать под множество
        через кваргсы.
        """

    async with get_async_sessionmaker(ANY_CONFIG) as async_session:

        # SQL Сырой запрос на выборку данных (+ условие фильтрации выборки):
        SQL = text(f"SELECT {columns_search} FROM {tb_name} WHERE {where_columns_name} = {where_columns_value}")

        result_temp: list[Row] = []  # Объявить переменную

        result_temp.extend(await async_session.execute(SQL))  # Извлечь данные из запроса

        # Варианты выдачи выборки:
        if results_aal_or == 'all':
            result = [row.scalar() for row in result_temp]

        elif results_aal_or == 'first':
            result = result_temp[0].scalar() if result_temp else None

        elif results_aal_or == 'one':
            result = result_temp[0].scalar()

        elif results_aal_or == 'one_or_none':
            result = result_temp[0].scalar() if result_temp else None

    return result

    # return result.scalar()  # Выдать скалярные (очищенные) величины


async def get_():
    f = get_telegram_id(CONFIG_JAR, 'inlet.staff_for_bot',
                        'tg', 'tg', 49295383, 'one')

    print(f)

asyncio.run(get_())
# async_sessionmaker = get_async_sessionmaker(config)
# async def get_telegram_id(session: AsyncSession, tg_id: int):
#     query = select(staff_for_bot).where(staff_for_bot.tg == tg_id)
#
#     result = await session.execute(query)
#     return result.scalar()
