"""
Функции для включения и выключения бота.
Что бы поместить асинхронные функции в тело async def run_bot():
(а это нужно для того что бы один раз использовать асинх сейшенмейкер (исключить нагрузку и ошибки))
пришлось вынести в отдельный модуль
"""

# -------------------------------- Стандартные модули
# -------------------------------- Сторонние библиотеки

# -------------------------------- Локальные модули
from working_databases.configs import *

# from dotenv import find_dotenv, load_dotenv  # Для переменных окружения
# load_dotenv(find_dotenv())  # Загружаем переменную окружения


from working_databases.async_engine import *

from working_databases.init_db import *

from working_databases.orm_query_builder import *
from working_databases.query_builder import *








# -------------------- При старте и при выключении бота:
async def on_startup(bot, session: AsyncSession):
    """Общая функция при запуске бота выполняет ряд программ для обеспечения  нормальной работы бота"""

    # 0. Создание Локал БД.
    await create_db(session_pool=session)

    # ------------------ Раздел наполнеия и обновления локал БД:
    # Извлекаем все данные с удаленного сервера о пользователях через сырой запрос:
    data, columns = await get_user_data(engine_obj=await get_async_engine(CONFIG_JAR_ASYNCPG))

    # Наполнение внутренней БД проекта данными пользователей через ОРМ:
    # !! Открывается 2 сесии еще одна в мидел вери
    await insert_data(data, columns, session_pool=session)
    # insert_data =

    # включить проверку (при включении и переодически) если база есть
    # то проверить отличия,
    # если нет то ничего

    # ------------------

    print('Бот запущен, все норм!')







# -------------------- При выключении
async def on_shutdown(bot):
    print('Бот лег!')