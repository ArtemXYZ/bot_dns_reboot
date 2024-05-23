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

async def check_id_tg_in_users(session: AsyncSession, id: int):
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
async def insert_data(data, session_pool: AsyncSession):  # , columns, - упразднено.
    """ Вставка данных о пользователях в локальную бд.
    """

    async with session_pool() as pool:
        # Перебираем по строчно данные  выгрузки из базы удаленной:
        for row in data:
            # Преобразование полей в соответствующие типы данных  - не поддерживает прямое присваивание элементу.

            # print(f"Row data: {row}")

            new_insert = Users(
                id_tg=int(row[0]),
                code=str(row[1]),
                session_type=str(row[2]),
                full_name=str(row[3]),
                post_id=int(row[4]),
                post_name=str(row[5]),
                branch_id=int(row[6]),
                branch_name=str(row[7]),
                rrs_name=str(row[8]),
                division_name=str(row[9]),
                user_mail=str(row[10]),
                is_deleted=bool(row[11]),
                employee_status=bool(row[12])
            )


        # Создаем экземпляр ORM модели и добавляем его в сессию
        # new_insert = Users(**dict(zip(columns, row)))

            pool.add(new_insert)

            #  добавлять и фиксировать каждую запись
            # await session.commit()

            await pool.commit()
            # В цикле это уместно, если вы хотите добавлять и фиксировать каждую запись отдельно.
            # Однако это может быть неэффективным, так как каждое добавление и фиксация выполняются отдельно.
            # Лучше добавлять объекты в сессию в цикле, а затем выполнять commit один раз вне цикла.

        print('Данные удачно мигрировали в локальную базу данных!')

            # new_insert = Users(**dict(zip(
            #                 id_tg=int(data['id_tg']),
            #                 code=data['code'],
            #                 session_type=data['session_type'],
            #                 full_name=data['full_name'],
            #                 post_id=int(data['post_id']),
            #                 post_name=data['post_name'],
            #                 branch_id=int(data['branch_id']),
            #                 branch_name=data['branch_name'],
            #                 rrs_name=data['rrs_name'],
            #                 division_name=data['division_name'],
            #                 user_mail=data['user_mail'],
            #                 is_deleted=data['is_deleted'],
            #                 employee_status=data['employee_status'],
            #                 ), row))

            #     new_insert = Users(**dict(zip(
            #                 id_tg=astyp(data[0]),
            #                 code=data[1],
            #                 session_type=data[2],
            #                 full_name=data[3],
            #                 post_id=int(data[4]),
            #                 post_name=data[5],
            #                 branch_id=int(data[6]),
            #                 branch_name=data[7],
            #                 rrs_name=data[8],
            #                 division_name=data[9],
            #                 user_mail=data[10],
            #                 is_deleted=data[11],
            #                 employee_status=data[12],
            #                ), row))

# new_insert = Users(
#                 id_tg=int(data['id_tg']),
#                 code=data['code'],
#                 session_type=data['session_type'],
#                 full_name=data['full_name'],
#                 post_id=int(data['post_id']),
#                 post_name=data['post_name'],
#                 branch_id=int(data['branch_id']),
#                 branch_name=data['branch_name'],
#                 rrs_name=data['rrs_name'],
#                 division_name=data['division_name'],
#                 user_mail=data['user_mail'],
#                 is_deleted=data['is_deleted'],
#                 employee_status=data['employee_status']
#                 )
# new_insert = Users(
#                 id_tg={columns['id_tg']:row[0]},
#                 code={columns['code']:row[1]},
#                 session_type={columns['session_type']:row[2]},
#                 full_name={columns['full_name']:row[3]},
#                 post_id={columns['post_id']:row[4]},
#                 post_name={columns['post_name']:row[5]},
#                 branch_id={columns['branch_id']:row[6]},
#                 branch_name={columns['branch_name']:row[7]},
#                 rrs_name={columns['rrs_name']:row[8]},
#                 division_name={columns['division_name']:row[9]},
#                 user_mail={columns['user_mail']:row[10]},
#                 is_deleted={columns['is_deleted']:row[11]},
#                 employee_status={columns['employee_status']:row[12]})