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


async def add_request_message(session: AsyncSession, data: dict):  # , get_tg_id: int , message: types.Message, - упразднено.
    """
    Запрос в БД на добавление обращения:
    session=await get_async_sessionmaker(CONFIG_LOCAL_DB)
    """

    #  Формируем набор данных для вставки:
    # id_tg: int = message.from_user.id - упразднено.
    # request_data_set = Requests(request_message=data['request_message'], tg_id=id_tg) - упразднено.

    request_data_set = Requests(**data)


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


# ----------------------------------------------- Поиск косяков в данных
async def null_filter(row_data):
    """
    Поиск косяков в данных
    # Проверка на пустоту, для исключения ошибок (конфликт nullable=False)
    # условие: если хотя бы в 1 поле есть пустота (неразрешенная) - отлавливаем и переходим к след. строке
    # отлавливание: запись в список словарей и пердача их в бд в дальнейшем
    # Перебираем по строчно данные  выгрузки из удаленной базы :
    # # Словарь: !! важно понимать: в data - нет имен колонок, по этому по индексу.

    :Цель: Проверяет каждую строку данных на наличие None.
    Логика: Если хотя бы одно значение в строке равно None, вся строка добавляется в bug_tuple,
    а row_data устанавливается в None.
    Возврат: Возвращает либо строку данных (если нет ошибок), либо кортеж ошибок.
    """

    # insert_row_tuple = []
    bug_tuple = []

    # Перебираем строки данных по элементам кортежа:
    for next_column_row in row_data:
        # Перебираем строку по элементам:
        if next_column_row is None:
            # print(f'Эта строка с косяком: {row_data}')
            bug_tuple.append(row_data)
            row_data = None
            break  # завершение цикла, переход к следующему.

        # insert_row_tuple.append(row_data)
    print(f'Здесь только чистые строки: {row_data}')
    # print(bug_tuple)
    return row_data, bug_tuple


async def insert_data(data, session_pool: AsyncSession): # todo - не доделано - пересмотреть Все.

    """ Вставка данных о пользователях в локальную бд.

    Вложенная функция для insert_data. Осуществляет проверку данных перед вставкой
    на пустоту.
    Цель: Вставляет данные в базу данных после проверки на ошибки.
    Логика: Для каждой строки данных вызывается null_filter, и если строка корректна, она добавляется в базу данных.
    Если строка содержит ошибки, она добавляется в bugs_tuple.
    Коммит: Сохраняет данные в базе данных после всех проверок.
    """

    # Открываем контекстный менеджер для сохранения данных.
    async with session_pool() as pool:

        bugs_tuple = []  # Словарь строк с кривыми исходными данными.
        # insert_row_tuple = []

        # Перебираем данные по строчно:
        for row_data in data:

            # на выходе 2 картежа с багами и отфильтрованный от NULL
            # todo  bug_row - что с ними ? - делать продумать позже
            insert_row_tuple, bug_row = await null_filter(row_data)

            if insert_row_tuple is None:
                bugs_tuple.append(bug_row) # Копим косяки в кортеж.!!
            else:
                # Жесткая типизация данных:
                insert_obj = Users(
                        id_tg=int(insert_row_tuple[0]),
                        code=str(insert_row_tuple[1]),
                        session_type=str(insert_row_tuple[2]),
                        full_name=str(insert_row_tuple[3]),
                        post_id=int(insert_row_tuple[4]),
                        post_name=str(insert_row_tuple[5]),
                        branch_id=int(insert_row_tuple[6]),
                        branch_name=str(insert_row_tuple[7]),
                        rrs_name=str(insert_row_tuple[8]),
                        division_name=str(insert_row_tuple[9]),
                        user_mail=str(insert_row_tuple[10]),
                        is_deleted=bool(insert_row_tuple[11]),
                        employee_status=bool(insert_row_tuple[12]),
                        holiday_status = bool(insert_row_tuple[13]),
                        admin_status =bool(insert_row_tuple[14])
                    )
                pool.add(insert_obj)

        await pool.commit()
    print('Данные удачно мигрировали в локальную базу данных!')
    print(f'Косяки в данных для этих строк: {bugs_tuple}')

    return bugs_tuple
# -------------------------------------------------
