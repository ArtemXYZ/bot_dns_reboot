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


# ----------------------------------------------- Поиск косяков в данных
async def null_filter(row_data):
    """
    Поиск косяков в данных
    # Проверка на пустоту, для исключения ошибок (конфликт nullable=False)
    # условие: если хотя бы в 1 поле есть пустота (неразрешенная) - отлавливаем и переходим к след. строке
    # отлавливание: запись в список словарей и пердача их в бд в дальнейшем
    # Перебираем по строчно данные  выгрузки из удаленной базы :
    # # Словарь: !! важно понимать: в data - нет имен колонок, по этому по индексу.

    :param data:
    :param num_columns:
    :return:
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

    Логика:
    формируем словарь, проверяем его на пустоты. если есть хотя бы в 1 - отбрасываем и запоминаем.
    такой словарь можно потом без труда записать в базу в отличии от сырой строки row - в ней нет имен колонок.
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


# async def get_user_data(session_remote: AsyncSession, any_sql_path: str | bytes, **values: tuple[int, str, float]):
# Сохраняем данные в таблицу Пользователи (локал бд):
# async def insert_data_old(insert_data, session_pool: AsyncSession):  # , columns, - упразднено.
#     """ Вставка данных о пользователях в локальную бд.
#     """

    # async with session_pool() as pool:
    #     for row in insert_data:
            # Преобразование полей в соответствующие типы данных  - не поддерживает прямое присваивание элементу.
            # print(f"Row data: {row}")


            # insert_obj = Users(
            # # id_tg = r[0],
            # # code = r[1],
            # # session_type = r[2],
            # # full_name = r[3],
            # # post_id = r[4],
            # # post_name = r[5],
            # # branch_id = r[6],
            # # branch_name = r[7],
            # # rrs_name = r[8],
            # # division_name = r[9],
            # # user_mail = r[10],
            # # is_deleted= r[11],
            # # employee_status = r[12],
            # # holiday_status = r[13],
            # # admin_status = r[14]
            # )
        #     pool.add(insert_obj)
        # await pool.commit()
        # В цикле это уместно, если вы хотите добавлять и фиксировать каждую запись отдельно.
        # Однако это может быть неэффективным, так как каждое добавление и фиксация выполняются отдельно.
        # Лучше добавлять объекты в сессию в цикле, а затем выполнять commit один раз вне цикла.

        # print('Данные удачно мигрировали в локальную базу данных!')

        # Фильтр нулевых значяений для отсеивания ошибок:

        # Преобразование полей в соответствующие типы данных  - не поддерживает прямое присваивание элементу.
        # print(f"Row data: {row}")
        # new_insert = Users(
        #     id_tg=int(row[0]),
        #     code=str(row[1]),
        #     session_type=str(row[2]),
        #     full_name=str(row[3]),
        #     post_id=int(row[4]),
        #     post_name=str(row[5]),
        #     branch_id=int(row[6]),
        #     branch_name=str(row[7]),
        #     rrs_name=str(row[8]),
        #     division_name=str(row[9]),
        #     user_mail=str(row[10]),
        #     is_deleted=bool(row[11]),
        #     employee_status=bool(row[12])
        #     # holiday_status
        #     # admin_status

        # )

        # Создаем экземпляр ORM модели и добавляем его в сессию
        # new_insert = Users(**dict(zip(columns, row)))

        # pool.add(new_insert)

        #  добавлять и фиксировать каждую запись
        # await session.commit()

        #     await pool.commit()
        #     # В цикле это уместно, если вы хотите добавлять и фиксировать каждую запись отдельно.
        #     # Однако это может быть неэффективным, так как каждое добавление и фиксация выполняются отдельно.
        #     # Лучше добавлять объекты в сессию в цикле, а затем выполнять commit один раз вне цикла.
        #
        # print('Данные удачно мигрировали в локальную базу данных!')

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

#  # Перебираем по строчно данные  выгрузки из удаленной базы :
#         for row in data:
#
#             # Проверка на пустоту, для исключения ошибок (конфликт nullable=False)
#             # условие: если хотя бы в 1 поле есть пустота (неразрешенная) - отлавливаем и переходим к след. строке
#             if row[0] is None:
#                 continue #  завершение итерации, перход к следующей.
#             elif row[1] is None:
#                 continue
#             elif row[2] is None:
#                 continue
#             elif row[3] is None:
#                 continue
#             elif row[4] is None:
#                 continue
#             elif row[5] is None:
#                 continue
#             elif row[6] is None:
#                 continue
#             elif row[7] is None:
#                 continue
#             elif row[8] is None:
#                 continue
#             elif row[9] is None:
#                 continue
#             elif row[10] is None:
#                 continue
#             elif row[11] is None:
#                 continue
#             # elif row[12] is None:  # employee_status - nullable=True,
#             #     continue
#             elif row[13] is None:
#                 continue
#             elif row[14] is None:
#                 continue
#             else:
#                 pass



#   # работает, но нужен тупл.
#         insert_row_tuple = tuple(
#             row[0],  # 'id_tg'
#             row[1],  # 'code':
#             row[2],  # 'session_type':
#             row[3],  # 'full_name':
#             row[4],  # 'post_id':
#             row[5],  # 'post_name':
#             row[6],  # 'branch_id':
#             row[7],  # 'branch_name':
#             row[8],  # 'rrs_name':
#             row[9],  # 'division_name':
#             row[10],  # 'user_mail':
#             row[11],  # 'is_deleted':
#             row[12],  # 'employee_status':
#             row[13],  # 'holiday_status':
#             row[14],  # 'admin_status':
#         )
#         # print(insert_row_tuple)


# for row in data:
#             print(row)
#             # Словарь: !! важно понимать: в data - нет имен колонок, по этому по индексу.
#
#             if row[0] is None:
#                 bugs_list.append(row)
#                 continue  # завершение итерации, переход к следующей.
#             elif row[1] is None:
#                 bugs_list.append(row)
#                 continue
#             elif row[2] is None:
#                 bugs_list.append(row)
#                 continue
#             elif row[3] is None:
#                 bugs_list.append(row)
#                 continue
#             elif row[4] is None:
#                 bugs_list.append(row)
#                 continue
#             elif row[5] is None:
#                 bugs_list.append(row)
#                 continue
#             elif row[6] is None:
#                 bugs_list.append(row)
#                 continue
#             elif row[7] is None:
#                 bugs_list.append(row)
#                 continue
#             elif row[8] is None:
#                 bugs_list.append(row)
#                 continue
#             elif row[9] is None:
#                 bugs_list.append(row)
#                 continue
#             elif row[10] is None:
#                 bugs_list.append(row)
#                 continue
#             elif row[11] is None:
#                 bugs_list.append(row)
#                 continue
#             elif row[12] is None:
#                 bugs_list.append(row)
#                 continue
#             elif row[13] is None:
#                 bugs_list.append(row)
#                 continue
#             elif row[14] is None:
#                 bugs_list.append(row)
#                 continue
#             else:
#                 pass


#     # # Жесткая типизация данных:
#     # insert_row_dict_fin = {
#     #     'id_tg': int(insert_row_dict['id_tg']),
#     #     'code': str(insert_row_dict['code']),
#     #     'session_type': str(insert_row_dict['session_type']),
#     #     'full_name': str(insert_row_dict['full_name']),
#     #     'post_id': int(insert_row_dict['post_id']),
#     #     'post_name': str(insert_row_dict['post_name']),
#     #     'branch_id': int(insert_row_dict['branch_id']),
#     #     'branch_name': str(insert_row_dict['branch_name']),
#     #     'rrs_name': str(insert_row_dict['rrs_name']),
#     #     'division_name': str(insert_row_dict['division_name']),
#     #     'user_mail': str(insert_row_dict['user_mail']),
#     #     'is_deleted': bool(insert_row_dict['is_deleted']),
#     #     'employee_status': bool(insert_row_dict['employee_status']),
#     #     'holiday_status': bool(insert_row_dict['holiday_status']),
#     #     'admin_status': bool(insert_row_dict['admin_status']),
#     # }

# --------------------------------------- old
async def check_insert_data_for_null_old(data):
    """
    Вложенная функция для insert_data. Осуществляет проверку данных перед вставкой
    на пустоту.

    Логика:
    формируем словарь, проверяем его на пустоты. если есть хотя бы в 1 - отбрасываем и запоминаем.
    такой словарь можно потом без труда записать в базу в отличии от сырой строки row - в ней нет имен колонок.
    """
    bugs_dict = []  # Словарь строк с кривыми исходными данными.
    result_insert_list = []

    # Перебираем по строчно данные  выгрузки из удаленной базы :
    for row in data:

        # Словарь: !! важно понимать: в data - нет имен колонок, по этому по индексу.

        # работает, но нужен тупл.
        insert_row_dict = {
            'id_tg': row[0],
            'code': row[1],
            'session_type': row[2],
            'full_name': row[3],
            'post_id': row[4],
            'post_name': row[5],
            'branch_id': row[6],
            'branch_name': row[7],
            'rrs_name': row[8],
            'division_name': row[9],
            'user_mail': row[10],
            'is_deleted': row[11],
            'employee_status': row[12],
            'holiday_status': row[13],
            'admin_status': row[14],
        }
        # print(insert_row_dict)

        # Проверка на пустоту, для исключения ошибок (конфликт nullable=False)
        # условие: если хотя бы в 1 поле есть пустота (неразрешенная) - отлавливаем и переходим к след. строке
        # отлавливание: запись в список словарей и пердача их в бд в дальнейшем

        # работает, но нужен тупл.
        if insert_row_dict['id_tg'] is None:
            bugs_dict.append(insert_row_dict)
            continue  # завершение итерации, переход к следующей.
        elif insert_row_dict['code'] is None:
            bugs_dict.append(insert_row_dict)
            continue
        elif insert_row_dict['session_type'] is None:
            bugs_dict.append(insert_row_dict)
            continue
        elif insert_row_dict['full_name'] is None:
            bugs_dict.append(insert_row_dict)
            continue
        elif insert_row_dict['post_id'] is None:
            bugs_dict.append(insert_row_dict)
            continue
        elif insert_row_dict['post_name'] is None:
            bugs_dict.append(insert_row_dict)
            continue
        elif insert_row_dict['branch_id'] is None:
            bugs_dict.append(insert_row_dict)
            continue
        elif insert_row_dict['branch_name'] is None:
            bugs_dict.append(insert_row_dict)
            continue
        elif insert_row_dict['rrs_name'] is None:
            bugs_dict.append(insert_row_dict)
            continue
        elif insert_row_dict['division_name'] is None:
            bugs_dict.append(insert_row_dict)
            continue
        elif insert_row_dict['user_mail'] is None:
            bugs_dict.append(insert_row_dict)
            continue
        elif insert_row_dict['is_deleted'] is None:
            bugs_dict.append(insert_row_dict)
            continue
        elif insert_row_dict['employee_status'] is None:
            bugs_dict.append(insert_row_dict)
            continue
        elif insert_row_dict['holiday_status'] is None:
            bugs_dict.append(insert_row_dict)
            continue
        elif insert_row_dict['admin_status'] is None:
            bugs_dict.append(insert_row_dict)
            continue
        else:
            pass

        # Жесткая типизация данных:

        # работает, но нужен тупл.
        insert_row_dict_fin = {
            'id_tg': int(insert_row_dict['id_tg']),
            'code': str(insert_row_dict['code']),
            'session_type': str(insert_row_dict['session_type']),
            'full_name': str(insert_row_dict['full_name']),
            'post_id': int(insert_row_dict['post_id']),
            'post_name': str(insert_row_dict['post_name']),
            'branch_id': int(insert_row_dict['branch_id']),
            'branch_name': str(insert_row_dict['branch_name']),
            'rrs_name': str(insert_row_dict['rrs_name']),
            'division_name': str(insert_row_dict['division_name']),
            'user_mail': str(insert_row_dict['user_mail']),
            'is_deleted': bool(insert_row_dict['is_deleted']),
            'employee_status': bool(insert_row_dict['employee_status']),
            'holiday_status': bool(insert_row_dict['holiday_status']),
            'admin_status': bool(insert_row_dict['admin_status']),
        }

        # print(insert_row_dict_fin)
        result_insert_list.append(insert_row_dict_fin)
    print(f'Косяки в данных для этих строк: {bugs_dict}')
    print(result_insert_list)
    return result_insert_list, bugs_dict



#  elif next_column_row is None:
#             bug_tuple.append(row_data)
#             continue
#         elif next_column_row is None:
#             bug_tuple.append(row_data)
#             continue
#         elif next_column_row is None:
#             bug_tuple.append(row_data)
#             continue
#         elif next_column_row is None:
#             bug_tuple.append(row_data)
#             continue
#         elif next_column_row[5] is None:
#             bug_tuple.append(row_data)
#             continue
#         elif next_column_row[6] is None:
#             bug_tuple.append(row_data)
#             continue
#         elif next_column_row[7] is None:
#             bug_tuple.append(rrow_dataow)
#             continue
#         elif next_column_row[8] is None:
#             bug_tuple.append(row_data)
#             continue
#         elif next_column_row[9] is None:
#             print(f'Здесь ноль: {next_column_row}')
#             bug_tuple.append(row_data)
#             continue
#         elif next_column_row[10] is None:
#             bug_tuple.append(row_data)
#             continue
#         elif next_column_row[11] is None:
#             bug_tuple.append(row_data)
#             continue
#         elif next_column_row[12] is None:
#             bug_tuple.append(row_data)
#             continue
#         elif next_column_row[13]is None:
#             bug_tuple.append(row_data)
#             continue
#         elif next_column_row[14] is None:
#             bug_tuple.append(row_data)
#             continue
#         else:
#             pass

# # Проверка на пустоту в каждом столбце строки  - шляпа!!!
        # if any(value is None for value in next_column_row):
        #     bug_tuple.append(row_data)
        #     continue # завершение итерации, переход к следующей.