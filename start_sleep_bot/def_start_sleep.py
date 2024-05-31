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
    Делаем выборку из локал бд (выдаст либо список либо пусой список):
    - если нет тничего, то просто наполняем бд, если есть то сравниваем и потом наполняем.

    """

    # Делаем выборку id_tg из локал бд (выдаст либо список либо пусой список):
    get_id_tg_list_local_db = await get_id_tg_in_users(session_pool)

    # Если список пуст:
    if not get_id_tg_list_local_db:
        print('Таблица пользователей в базе данных пустая.')

        # ------------------ Раздел наполнеия локал БД (+ фильтрация данных):
        # Извлекаем все данные с удаленного сервера о пользователях через сырой запрос:
        # в выборку попадут данные только зарегистрированных пользователей и не удаленных (уволенных).
        data = await get_data_in_jarvis(
            engine_obj=await get_async_engine(CONFIG_JAR_ASYNCPG),
            sql=user_data_sql_text
        )

        # Наполнение внутренней БД проекта данными пользователей через ОРМ:
        # Предварительно, отсеиваются строки с пустыми значениями в хотябы 1 колонке и разделяются на 2 составляющие ( \
        # баги и норм данные.
        # !! Открывается 2 сесии еще одна в мидел вери
        bugs = await insert_data(data, session_pool)
        # Есть принты о результатах в функции 👆

    else:
        print('Таблица пользователей в базе данных не пустая.')
        # Делаем выборку всех id_tg из Джарвиса (запрос к таблице бота регистрации на удаленном хосте):
        get_id_tg_list_in_jarvis = await get_data_in_jarvis(
            engine_obj=await get_async_engine(CONFIG_JAR_ASYNCPG),
            sql=table_for_reg_bot)

        # Проверяем, равны ли массивы поэлементно (сравниваем выборки из 2-х баз):
        arrays_equal: bool = np.array_equal(get_id_tg_list_local_db, get_id_tg_list_in_jarvis)
        #  Функция np.array_equal проверяет, равны ли два массива.
        #  Она вернет True, если массивы одинаковы по форме и содержимому, и False в противном случае.

        #  если массивы одинаковы по форме и содержимому
        if arrays_equal is True:
            print(f'Инфоромация в локальной базе данных актуальна и не требует обновления.')

        else:
            # Найдем индексы, где элементы различаются
            # different_indices = np.where(array1 != array2)[0]

            # # Найдем значения в первом массиве (в локальной бд), которые отличаются от значений второго массива (jarvis)
            # different_values_local_db = get_id_tg_list_local_db[get_id_tg_list_local_db != get_id_tg_list_in_jarvis]

            # НАйдем удаленных пользователей:
            # Найдем значения в первом массиве, которые отсутствуют во втором массиве:
            not_values_in_local_db = np.setdiff1d(get_id_tg_list_local_db, get_id_tg_list_in_jarvis)
            print(f'В локальной базе для записей {not_values_in_local_db} будет выставлена пометка удалены.')


# -------------------- При старте и при выключении бота:
async def startup_on(session_pool: AsyncSession):
    """Общая функция при запуске бота выполняет ряд программ для обеспечения  нормальной работы бота"""

    # 0. Создание Локал БД.
    await create_db()  # +

    # --------------- tests

    await updating_local_db(session_pool)  # todo

    # --------------- tests

    # включить проверку (при включении и переодически) если база есть
    # то проверить отличия,
    # если нет то ничего

    # ------------------

    print('Бот запущен, все норм!')


# -------------------- При выключении
async def shutdown_on():
    print('Бот лег!')
