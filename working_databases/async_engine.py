"""
Модуль содержит функции асинхронного подключения к базам данных.
"""

# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------- Импорт стандартных библиотек Пайтона
import os

# ---------------------------------- Импорт сторонних библиотек
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sqlalchemy.engine.url import URL
from sqlalchemy.exc import OperationalError


# os.getenv('DB_URL')
# ----------------------------------------------------------------------------------------------------------------------
# Фсинхронное подключение к базе данных (sessionmaker):
def get_async_sessionmaker(any_config: dict | URL | str):
    """Функция создает АСИНХРОННОЕ подключение к базе данных. На вход принимает файл конфигурации."""

    try:  # Блок исключений ошибок при осуществлении подключения:
        # any_config # 1.Проверка на отсутствие файла концигурации подкючения: если нет данных на вход: !!

        # Проверка типа входной конфигурации подключения:
        # Если на вход конфигурация в словаре:
        if isinstance(any_config, dict) == True:
            url_string = URL.create(**any_config)  # 1. Формируем URL-строку соединения с БД.
            #  Эквивалент: url_string = (f'{drivername}://{username}:{password}@{host}:{port}/{database}')

        # Если на вход url_string:
        elif isinstance(any_config, str) == True:
            url_string = any_config
        else:
            url_string = None

        # 2. Создаем переменную  асинхронного подключения к БД.
        async_engine = create_async_engine(url_string)  # , echo=True

        async_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)
        # ! параметр expire_on_commit=False - сразу не закрывается ссесия после коммита для повторного использования.

        ## async_connection = async_engine.connect() - можно так (вроде то же самое, но без ролбека транзакций)

        return async_session

    #  Если наступит ошибка в значениях:
    except (ValueError, TypeError):
        print(f'Ошибка создания ссесии подключения к базе данных! Проверьте входные данные {any_config} \n'
              f'и зависимые переменные: формирование url_string: {url_string}, async_engine: {async_engine}')

    #  Другие любые ошибки (скорее всего будут относиться к синтаксису):
    except Exception as error:
        print(f'Ошибка: {type(error).__name__}, сообщение: {str(error)}!')


# check_telegram_id
# async def get_telegram_id(session: AsyncSession, tg_id: int):
#     query = select(staff_for_bot).where(staff_for_bot.tg == tg_id)
#
#     result = await session.execute(query)
#     return result.scalar()
