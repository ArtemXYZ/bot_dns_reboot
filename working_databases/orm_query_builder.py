"""
Модуль содержит функции асинхронных SQL запросов к базам данных c помощью ОРМ.
"""

# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------- Импорт стандартных библиотек Пайтона
# ---------------------------------- Импорт сторонних библиотек
import asyncio
from sqlalchemy import select, String, Table, update, delete, text, or_

from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import types

# -------------------------------- Локальные модули
from working_databases.async_engine import *
from working_databases.local_db_mockup import *
from working_databases.configs import *

from sql.get_user_data_sql import *


# ----------------------------------------------------------------------------------------------------------------------
async def update_chat_id_local_db(search_id_tg: int, update_chat_id: int, session_pool: AsyncSession):

    """
    На вход 1 строка. Функция для обновления записей в колонке chat_id во внутренней БД.

    """

    # Открываем контекстный менеджер для сохранения данных.
    async with session_pool() as pool:

        query = update(Users).where(Users.id_tg == search_id_tg).values(chat_id=update_chat_id)
        # В SQLAlchemy условие выборки должно быть записано без использования Python-оператора not.

        await pool.execute(query)
        # results = result_tmp.scalars()  #  # выдаст либо список либо пусой список. results_list_int

    return print(f'Данные пользователя: id_tg: {search_id_tg}, chat_id  {update_chat_id} - обновлены!')



async def get_id_tg_in_users(id: int, session: AsyncSession) -> bool:

    """
    Проверяем данные о пользователе в локал БД.
    Ищем по telegram айдишнику из сообщения в локальной базе данных пользователя и сравниваем
    Если есть то на выход айди, нет то None
    """

    query = select(Users.id_tg).where(Users.id_tg == id)
    result_tmp = await session.execute(query)
    result = result_tmp.scalar_one_or_none() # получение одного результата или None

    return result


async def check_id_tg_in_users(id: int, session: AsyncSession) -> bool:

    """
    Проверяем данные о пользователе в локал БД.
    Ищем по telegram айдишнику из сообщения в локальной базе данных пользователя и выводим его статус
    """

    # Создаем выражение CASE:
    # (Если есть в базе (тогда удален или не удален) и если нет то None)
    is_deleted_case  = case(
        (Users.is_deleted == True, True),
        (or_(Users.is_deleted == False, Users.is_deleted == 0), False)
    ).label('is_deleted')

    query = select(is_deleted_case).where(Users.id_tg == id)
    result_tmp = await session.execute(query)
    result = result_tmp.scalar_one_or_none() # .scalar_one_or_none() .scalar()
    # print(result)

    return result


async def get_id_tg_in_users(session_pool: AsyncSession) -> list:

    """
    Забираем выборку id_tg из локал БД. Только действующие сотрудники.
    Далее сравниваем с id_tg с выборкой из внешней базы данных.
    """

    # Открываем контекстный менеджер для сохранения данных.
    async with session_pool() as pool:

        # Только действующие сотрудники:
        # Либо ноль либо фелсе:
        query = select(Users.id_tg).where(or_(Users.is_deleted == False, Users.is_deleted == 0))
        # В SQLAlchemy условие выборки должно быть записано без использования Python-оператора not.

        result_tmp = await pool.execute(query)
        results = result_tmp.scalars().all()  #

    # Преобразование всех значений в целые числа:
    results_list_int = [int(result) for result in results]

    # выдаст либо список либо пусой список.
    return results_list_int









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

    # Обновляем объект, чтобы получить все значения, включая автоинкременты и прочее.
    new = await session.refresh(request_data_set)

    # Возвращаем обновленный объект
    return new

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
    bug_list = []

    # Перебираем строки данных по элементам кортежа:
    for next_column_row in row_data:
        # Перебираем строку по элементам (Если значение в колонке для строки равно None):
        if next_column_row is None:
            # print(f'Эта строка с косяком: {row_data}')
            bug_list.append(row_data) # Сохраняем строкис косяками в отдельный список.
            row_data = None  # Устанавливаем для строки значение None (далее для фильтрации)
            break  # завершение цикла, переход к следующему.

        # insert_row_tuple.append(row_data)  # Сохраняем строки без пропусков в отдельный список. не надо (для 1 строки)
        # print(f'Только строки без пропусков: {row_data}')
    # print(f'Результат работы фильтра значений для строки: {row_data}') # перенос на уровень выше для правильной работы
    return row_data, bug_list


async def insert_data(data, session_pool: AsyncSession):

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
            # на вход строка, на выходе 2 картежа с багами и отфильтрованный (NULL - для багов, и нормальное)
            insert_row_tuple, bug_row = await null_filter(row_data)
            print(f'Результат работы фильтра значений для строки: {insert_row_tuple}')

            if insert_row_tuple is None:
                bugs_tuple.append(bug_row) # Копим косяки в кортеж.!! # todo  bug_row - что с ними ? - делать продумать позже
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
    #
        await pool.commit()
    print('Данные удачно мигрировали в локальную базу данных!')
    print(f'Эти строки содержат пропуски и по этому не были допущены к записи в базу данных: {bugs_tuple}')
    #
    return bugs_tuple
# -------------------------------------------------

async def update_delet_local_db(search_id_tg, session_pool: AsyncSession):

    """
    На вход 1 строка. Функция для обновления записей в колонке удаленные во внутренней БД.
    # where_columns_name: str, where_columns_value: any, columns_search: str,
    """

    # Открываем контекстный менеджер для сохранения данных.
    async with session_pool() as pool:

        query = update(Users).where(Users.id_tg == search_id_tg).values(is_deleted=True)
        # В SQLAlchemy условие выборки должно быть записано без использования Python-оператора not.

        await pool.execute(query)
        # results = result_tmp.scalars()  #  # выдаст либо список либо пусой список. results_list_int

    return print(f'Строка c id_tg: {search_id_tg} - обновлена! озиция значится удаленной.')