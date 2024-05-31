"""
Функции для включения и выключения бота.
Что бы поместить асинхронные функции в тело async def run_bot():
(а это нужно для того что бы один раз использовать асинх сейшенмейкер (исключить нагрузку и ошибки))
пришлось вынести в отдельный модуль
"""

# -------------------------------- Стандартные модули
# -------------------------------- Сторонние библиотеки
# import asyncio
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
# -------------------------------- Локальные модули
from working_databases.configs import *

# from dotenv import find_dotenv, load_dotenv  # Для переменных окружения
# load_dotenv(find_dotenv())  # Загружаем переменную окружения

from sql.get_user_data_sql import *

from working_databases.async_engine import *  # +

from working_databases.init_db import *

from working_databases.orm_query_builder import *
from working_databases.query_builder import *


# ----------------------------------------------------------------------------------------------------------------------

#  Вложенная функция в startup_on (сравнение данных в локальной и удаленной базах данных:
async def updating_local_db(session_pool: AsyncSession):
    """
    логика: как только запускаем сравниваем в локальной бд айди с внешней бд
    Делаем выборку из локал бд (выдаст либо список, либо пустой список):
    - если нет ничего, то просто наполняем бд, если есть то сравниваем и потом наполняем.

    """

    # Делаем выборку id_tg из локал бд (выдаст либо список, либо пустой список):
    raw_data_local_db = await get_id_tg_in_users(session_pool)  # +


    # Преобразуем выходные данные (список кортежей) в список, тк это единственное, что понимает нумпи.
    get_id_tg_list_local_db = []
    for row in raw_data_local_db:
        if row is None: # todo Потом переделать, обработать нули и пустоты
            print(row)
        else:
            get_id_tg_list_local_db.append(int(row))
    # print(f' Делаем выборку всех id_tg из Локал БД: {get_id_tg_list_local_db}')  # +


    # Если список пуст:
    if not get_id_tg_list_local_db:
        print('Таблица пользователей в базе данных пустая.')

        # ------------------ Раздел наполнения локал БД (+ фильтрация данных):
        # Извлекаем все данные с удаленного сервера о пользователях через сырой запрос:
        # в выборку попадут данные только зарегистрированных пользователей и не удаленных (уволенных).
        data = await get_data_in_jarvis(
            engine_obj=await get_async_engine(CONFIG_JAR_ASYNCPG),
            sql=user_data_sql_text
        )

        # Наполнение внутренней БД проекта данными пользователей через ОРМ:
        # Предварительно, отсеиваются строки с пустыми значениями в хотя бы 1 колонке и разделяются на 2 составляющие ( \
        # баги и норм данные.
        # !! Открывается 2 сессии еще одна в мидел вери
        bugs = await insert_data(data, session_pool)
        # Есть принты о результатах в функции 👆

    else:
        print('Таблица пользователей в базе данных не пустая.')
        # Делаем выборку всех id_tg из Джарвиса (запрос к таблице бота регистрации на удаленном хосте):
        raw_data_jarvis = await get_data_in_jarvis(
            engine_obj=await get_async_engine(CONFIG_JAR_ASYNCPG),
            sql=table_for_reg_bot
        )
        # print(f'Сырая выборка всех id_tg из Джарвиса: {raw_data_jarvis}')
        # Преобразуем выходные данные в список, тк это единственное, что понимает нумпи.
        get_id_tg_list_in_jarvis = []
        for row in raw_data_jarvis:
            if row is None:# todo Потом переделать, обработать нули и пустоты
                print(row)
            else:
                get_id_tg_list_in_jarvis.append(int(row[0]))  # +
        # print(f' Делаем выборку всех id_tg из Джарвиса (запрос к таблице бота регистрации на удаленном хосте):'
        #       f' {get_id_tg_list_in_jarvis}')

        # ------------------------------------------------ NumPy
        # Преобразуем списки в массивы (объекты нумпи):
        local_db_array = np.array(get_id_tg_list_local_db)  # Работает и просто со списками, но раз уж написал пуцсть
        jarvis_db_array = np.array(get_id_tg_list_in_jarvis) # остаются.

        # print(local_db_array)
        # print(jarvis_db_array)

        # Чистим списки (чтобы исключить в последующем добавление к старым объектам в списке - новых):
        get_id_tg_list_local_db.clear()
        get_id_tg_list_in_jarvis.clear()

        # Проверяем, равны ли массивы поэлементно (сравниваем выборки из 2-х баз):
        arrays_equal: bool = np.array_equal(local_db_array, jarvis_db_array)  # +
        #  Функция np.array_equal проверяет, равны ли два массива.
        #  Она вернет True, если массивы одинаковы по форме и содержимому, и False в противном случае.

        # print(f'Проверяем, равны ли массивы поэлементно (сравниваем выборки из 2-х баз): {arrays_equal}, '
        #       f'local_db_array: {len(local_db_array)}, jarvis_db_array: {len(jarvis_db_array)}')

        #  если массивы одинаковы по форме и содержимому
        if arrays_equal is True:
            print(f'Информация в локальной базе данных актуальна и не требует обновления.')

        else:
            # 1. Найдем удаленных пользователей на удаленном хосте:
            # Найдем значения в (local_db_array), которые отсутствуют во втором массиве (jarvis_db_array):
            not_values_in_jarvis_db = np.setdiff1d(local_db_array, jarvis_db_array)
            if len(not_values_in_jarvis_db) == 0:
                # print(f'Анализ локальной базы данных: уволенные сотрудники (удаленные из бд.) - отсутствуют.')
                ...
            else:
                print(f'Анализ удаленной базы данных: имеются неактуальные сотрудники (удаленные из бд.). '
                      f'Проставляем пометку в локальной базе об их удалении:\n{not_values_in_jarvis_db}')

            # 2. Найдем добавленных пользователей на удаленном хосте (вновь зарегистрированных ботом регистрации):
            not_values_in_local_db = np.setdiff1d(jarvis_db_array , local_db_array)
            if len(not_values_in_local_db) == 0:
                # print(f'Анализ локальной базы данных: новых зарегистрированных пользователей на удаленном серевере'
                #       f' не обнаружено, данные совпадают.')
                ...
            else:
                print(f'Анализ локальной базы данных: отсутствуют новые зарегистрированные пользователи. '
                      f'Добавим их базу:\n{not_values_in_local_db}')











# -------------------- При старте и при выключении бота:
async def startup_on(session_pool: AsyncSession):
    """Общая функция при запуске бота выполняет ряд программ для обеспечения  нормальной работы бота"""

    # 0. Создание Локал БД.
    await create_db()  # +

    # --------------- tests

    await updating_local_db(session_pool)  # todo

    # --------------- tests

    # включить проверку (при включении и периодически) если база есть
    # то проверить отличия,
    # если нет то ничего

    # ------------------

    print('Бот запущен, все норм!')


# -------------------- При выключении
async def shutdown_on():
    print('Бот лег!')


# # get_id_tg_list_in_jarvis = [{'id_tg': row[0]} for row in raw_data_jarvis ] - нумпи не понимает словари и тупл