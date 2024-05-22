"""
Модуль содержит функции асинхронных SQL запросов к базам данных c помощью ОРМ.
"""

# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------- Импорт стандартных библиотек Пайтона
# ---------------------------------- Импорт сторонних библиотек
import asyncio
from sqlalchemy import select, String, Table, update, delete, text
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types

# -------------------------------- Локальные модули
from working_databases.async_engine import *
from working_databases.local_db_mockup import *
from working_databases.configs import *

from sql.get_user_data_sql import *

# ----------------------------------------------------------------------------------------------------------------------

async def check_id_tg_in_users(session: AsyncSession, id:int):
    # + добавить логику (обработчик ошибок), если такого нет в базе
    """Сравниваем айдишник из сообщения в локальной базе данных"""
    query = select(Users).where(Users.id_tg == id)
    result = await session.execute(query)
    return result.scalar()



async def add_request_message(message: types.Message, session: AsyncSession, data: dict):  # , get_tg_id: int
    """
    Запрос в БД на добавление обращения:
    session=await get_async_sessionmaker(CONFIG_LOCAL_DB)
    """
    #  Формируем набор данных для вставки:
    id_tg: int = message.from_user.id
    request_data_set = Requests(request_message=data['request_message'], tg_id=id_tg)
    session.add(request_data_set)
    await session.commit()
    # check_id = check_id_tg_in_users(session, id_tg)

    # # 1. select in db id_tg (проверка есть ли такой или нет):
    # if check_id is not None:
    #
    #     # 2. ---- если есть, то добавляем в базу
    #     #  Формируем запрос:
    #     session.add(request_data_set)
    #     # Сохраняем и закрываем соединение:
    #     await session.commit()
    # else:
    #     pass
    #     # отправить обновить базу данных
# -----------------------------------------------

# ----------------------------------------------- тестово
# async def get_user_data(session_remote: AsyncSession, any_sql_path: str | bytes, **values: tuple[int, str, float]):
# Сохраняем данные в таблицу Пользователи (локал бд):
async def insert_data(data, columns, session_pool:AsyncSession):

    """ Вставка данных о пользователях в локальную бд.
    """

    async with session_pool() as pool:

        # Перебираем по строчно данные  выгрузки из базы удаленной:
        for row in data:
            # Создаем экземпляр ORM модели и добавляем его в сессию
            new_insert = Users(**dict(zip(columns, row)))
            pool.add(new_insert)

            #  добавлять и фиксировать каждую запись
            # await session.commit()

        await pool.commit()
        # В цикле это уместно, если вы хотите добавлять и фиксировать каждую запись отдельно.
        # Однако это может быть неэффективным, так как каждое добавление и фиксация выполняются отдельно.
        # Лучше добавлять объекты в сессию в цикле, а затем выполнять commit один раз вне цикла.

    print('Данные удачно мигрировали в локальную базу данных!')

