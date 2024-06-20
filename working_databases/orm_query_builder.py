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
    result = result_tmp.scalar_one_or_none()  # получение одного результата или None

    return result


async def check_id_tg_in_users(id: int, session: AsyncSession) -> bool:
    """
    Проверяем данные о пользователе в локал БД.
    Ищем по telegram айдишнику из сообщения в локальной базе данных пользователя и выводим его статус
    """

    # Создаем выражение CASE:
    # (Если есть в базе (тогда удален или не удален) и если нет то None)
    is_deleted_case = case(
        (Users.is_deleted == True, True),
        (or_(Users.is_deleted == False, Users.is_deleted == 0), False)
    ).label('is_deleted')

    query = select(is_deleted_case).where(Users.id_tg == id)
    result_tmp = await session.execute(query)
    result = result_tmp.scalar_one_or_none()  # .scalar_one_or_none() .scalar()
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


async def add_request_message(session: AsyncSession,
                              data: dict):  # , get_tg_id: int , message: types.Message, - упразднено. +
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

    # Обновляем объект, чтобы получить все значения, включая автоинкременты и прочее- работает(изменил логику, не наджо)
    await session.refresh(request_data_set)
    request_message_id = request_data_set.id
    # print(f'request_message_id = {request_message_id}')  # ссылаемся на колонку, вся строка не вызовется

    # Возвращаем обновленный объект - работает
    return request_message_id


# работало, но изменилась логика, измененно - РАБОТАЕТ.
# async def update_notification_id(search_request_id: int, update_notification_id: int, session_pool: AsyncSession):
#     """
#     На вход 2 начения (где обновить - айди обращения, значение для обновления.
#     """
#     query = update(Requests).where(Requests.id == search_request_id).values(
#                 notification_id=update_notification_id)
#     await session_pool.execute(query)
#     # results = result_tmp.scalars()  #  # выдаст либо список либо пусой список. results_list_int
#     await session_pool.commit()
#     return print(f'id уведоления о поступившей задаче - записано в базу : {update_notification_id}')
#

# Если сообщение не отправлено (заблокировали бота, удалились) +
async def add_row_sending_error(
        add_notification_employees_id_error: int, add_reques_id: int, session_pool: AsyncSession):
    """
    Если сообщение не отправлено (заблокировали бота, удалились), то апдейтим таблитцу HistoryDistributionRequests
    по колонке  sending_error (bool)
    """

    data_set = HistoryDistributionRequests(
        notification_employees_id=add_notification_employees_id_error,
        notification_id=0,
        reques_id=add_reques_id,
        sending_error=True
    )
    session_pool.add(data_set)
    await session_pool.commit()


# измененная функция update_notification_id  - работает +
async def add_row_in_history_distribution(add_notification_employees_id: int, add_notification_id: int,
                                          add_request_id: int, session_pool: AsyncSession):
    """
    На вход 3 начения (где обновить - айди обращения, значение для обновления. tg_id обратившегося пользователя)
    notification_employees_id: телеграмм id работника, которому направлено уведомление
    notification_id: id уведомления (рассылка поступившей задачи) сотруднику (id сообщения)
    reques_id: id обращения в таблице Requests
    """

    data_set = HistoryDistributionRequests(
        notification_employees_id=add_notification_employees_id,
        notification_id=add_notification_id,
        request_id=add_request_id
        # , sending_error = False  server_default
    )
    session_pool.add(data_set)
    await session_pool.commit()
    # return print(f'notification_id - аписан в базу : {update_notification_id}')


# В oait_router, после доставки оповчещения, работник нажимает на кнопку ЗАБРАТЬ ЗАЯВКУ
async def check_notification_id_in_history_distribution(get_notification_id: int, session_pool: AsyncSession):
    """
    Сравниваем в базе значение  notification_id при нажатии кнопкми (идентифицируеми кто нажал)
    """

    query = select(HistoryDistributionRequests.request_id).where(
        HistoryDistributionRequests.notification_id == get_notification_id)
    result_tmp = await session_pool.execute(query)
    result = result_tmp.scalar_one_or_none()  # один результат или ничего.
    # .scalar_one_or_none() .scalar()

    return result



async def check_notification_for_tg_id(request_id: int, session_pool: AsyncSession):
    """
     Ищем id оповещения для автора обращения (отправлялось ли уведомление заявителю?))
    """

    query = select(Requests.id_notification_for_tg_id).where(Requests.id == request_id)
    result_tmp = await session_pool.execute(query)
    result = result_tmp.scalar_one_or_none()  # один результат или ничего.

    return result


async def check_personal_status_for_tg_id(tg_id: int, request_id, session_pool: AsyncSession):
    """
     Ищем personal_status ==  in_work по tg_id в таблице  HistoryDistributionRequests
    """

    query = select(HistoryDistributionRequests.notification_employees_id).where(
        HistoryDistributionRequests.notification_employees_id == tg_id,
        HistoryDistributionRequests.request_id == request_id,
        HistoryDistributionRequests.personal_status == 'in_work'
    )
    result_tmp = await session_pool.execute(query)
    result = result_tmp.scalar_one_or_none()  # один результат или ничего.

    return result

async def get_tg_id_in_requests_history(request_id: int, session_pool: AsyncSession):
    """
     Ищем втора обращения (в базе значение tg_id по request_id в requests_history)
    """

    query = select(Requests.tg_id).where(Requests.id == request_id)
    result_tmp = await session_pool.execute(query)
    result = result_tmp.scalar_one_or_none()  # один результат или ничего.

    return result


async def get_all_personal_status_in_working(search_request_id: int, session_pool: AsyncSession):
    """
    Есть ли еще кто то со статусом в работе?
    Логика: Есть кто то еще, кто взял в работу эту задачу!
    Нам необходимо узнать есть ли еще кто то по этой задаче, кто взял ее в работу.
    Вытаскиваем всех кто имеет статус в работе и ? может добавить тех кто уже завершил по конкретному обращению.
    используем только количество.

    Вернет всех кто взял задачу или завершил ее.
    """

    query = select(HistoryDistributionRequests.notification_employees_id).where(
        HistoryDistributionRequests.request_id == search_request_id,
        HistoryDistributionRequests.personal_status == 'in_work')  # != 'not_working'
    result_tmp = await session_pool.execute(query)
    result = result_tmp.all()  # возвращает список кортежей [(1,), (2,), (3,)] или []

    return result


async def update_personal_status(
        search_request_id: int, search_notification_employees_id: int, session_pool: AsyncSession):
    """
    На вход 2 начения (обновляем статус конкретного работника, кто взял в работу задачу).
    """
    query = update(HistoryDistributionRequests).where(
        HistoryDistributionRequests.request_id == search_request_id,
        HistoryDistributionRequests.notification_employees_id == search_notification_employees_id
    ).values(personal_status='in_work')
    await session_pool.execute(query)
    # results = result_tmp.scalars()  #  # выдаст либо список либо пусой список. results_list_int
    await session_pool.commit()
    # return print(
    #     f' Ответственный {search_notification_employees_id} по задаче №_{search_request_id} записан в Requests.')

async def update_requests_status(
        search_request_id: int, search_notification_employees_id: int, session_pool: AsyncSession):
    """
    На вход 2 начения (обновляем статус конкретного работника, кто взял в работу задачу).
    """
    query = update(HistoryDistributionRequests).where(
        HistoryDistributionRequests.request_id == search_request_id,
        HistoryDistributionRequests.notification_employees_id == search_notification_employees_id
    ).values(personal_status='in_work')
    await session_pool.execute(query)
    # results = result_tmp.scalars()  #  # выдаст либо список либо пусой список. results_list_int
    await session_pool.commit()





async def get_notification_id_and_employees_id_tuples(search_request_id: int, session_pool: AsyncSession):
    """
    Выборка данных по колонке notification_id на основе входящего search_request_id
    """

    query = select(HistoryDistributionRequests.notification_employees_id,
                   HistoryDistributionRequests.notification_id).where(
        HistoryDistributionRequests.request_id == search_request_id)
    result_tmp = await session_pool.execute(query)
    result_tuples = result_tmp.all()  # возвращает список кортежей
    # .scalar_one_or_none()  # один результат или ничего. .scalar()

    return result_tuples


async def update_message_id_applicant(search_request_id: int, message_id_applicant: int, session_pool: AsyncSession):

    """
    Апдейтим айди отправленного сообщения в таблицу обращений Requests (поле: id_notification_for_tg_id)/
    Для того, что бы в последующем можно было изменять его.
    """
    query = update(Requests).where(Requests.id == search_request_id).values(
        id_notification_for_tg_id=message_id_applicant)
    await session_pool.execute(query)
    # results = result_tmp.scalars()  #  # выдаст либо список либо пусой список. results_list_int
    await session_pool.commit()



async def get_full_name_employee(get_tg_id: int, session_pool: AsyncSession):
    """
    Сравниваем в базе значение  notification_id при нажатии кнопкми (идентифицируеми кто нажал)
    """

    query = select(Users.full_name).where(Users.id_tg == get_tg_id)
    result_tmp = await session_pool.execute(query)
    result = result_tmp.scalar_one_or_none()  # один результат или ничего.
    # .scalar_one_or_none() .scalar()

    return result



async def get_employees_names(have_personal_status_in_working, session_pool: AsyncSession, exception=None):
    """
    exception - исключаем из списка сотруднка (нужно для вариаций сообщений пользователям об ответственных по задаче).

    На выходе: employees_names_str,
    содержит имена сотрудников, разделенные ", ", или None, если have_personal_status_in_working пусто.
    На вход: [(1,), (2,), (3,)] или []
    """
    # exception = None

    employees_names = []

    if exception is None:

        # Если список не пустой (есть ответственные по задаче)
        if have_personal_status_in_working:

            # Вытаскиваем имена всех (по айди) остальных ответственных со статусом в работе:
            for i in have_personal_status_in_working:
                # каждая итерация цикла будет предоставлять вам один кортеж из списка.
                employee_id = i[0]  # По этому, Извлекаем конкретное значение ( каждый кортеж содержит только одно значение)
                # -> число без кавычек.
                # print(f'employee_id = {employee_id} !!!')
                employee_name_row = await get_full_name_employee(int(employee_id), session_pool)  # -> "Иванов Иван"
                # print(f'employee_name_row = {employee_name_row} !!!')
                employees_names.append(employee_name_row)
                # Преобразование списка имен в строку с разделителем ", "

                employees_names_str = ", ".join(employees_names)
                # Очистка списка
                # employees_names.clear()  #может быть излишним,
                # так как переменная employees_names объявлена внутри функции и будет очищена при каждом вызове).

        else:
            employees_names_str = None

        return employees_names_str

    else:
        # Если список не пустой (есть ответственные по задаче)
        if have_personal_status_in_working:

            # Вытаскиваем имена всех (по айди) остальных ответственных со статусом в работе:
            for i in have_personal_status_in_working:

                # каждая итерация цикла будет предоставлять вам один кортеж из списка.
                employee_id = i[0]  # По этому, Извлекаем конкретное значение

                if exception != int(employee_id):
                    employee_name_row = await get_full_name_employee(int(employee_id), session_pool)  # -> "Иванов Иван"
                    # print(f'employee_name_row = {employee_name_row} !!!')
                    employees_names.append(employee_name_row)
                    # Преобразование списка имен в строку с разделителем ", "

                    employees_names_str = ", ".join(employees_names)
                    # Очистка списка
                    # employees_names.clear()  # может быть излишним,
                    # так как переменная employees_names объявлена внутри функции и будет очищена при каждом вызове).
        else:
            employees_names_str = None

        return employees_names_str




# -------------------------
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
            bug_list.append(row_data)  # Сохраняем строкис косяками в отдельный список.
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
                bugs_tuple.append(
                    bug_row)  # Копим косяки в кортеж.!! # todo  bug_row - что с ними ? - делать продумать позже
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
                    holiday_status=bool(insert_row_tuple[13]),
                    admin_status=bool(insert_row_tuple[14])
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
