"""Прослушка событий в базе данных. (триггеры).

mapper: Автоматически передаётся SQLAlchemy.
Это объект, который управляет соответствием между моделью и таблицей базы данных.
connection: Автоматически передаётся SQLAlchemy.
Это объект соединения с базой данных, который использовался для выполнения операции.
target: Автоматически передаётся SQLAlchemy. Это экземпляр модели MyModel, который был вставлен в базу данных.

# ------------------------------------
# SQLAlchemy, на самом деле, предоставляет возможность прослушивать события, однако,
непосредственно в рамках SQLAlchemy не существует механизма триггеров, как в SQL. SQLAlchemy позволяет создавать
обработчики событий, которые могут реагировать на различные события, такие как вставка, обновление или удаление
записей в базе данных.

# Эти обработчики событий можно использовать для реализации подобного функционала, хотя это будет работать на уровне
ORM SQLAlchemy, а не непосредственно на уровне базы данных. То есть, они будут реагировать на операции, совершаемые
через SQLAlchemy, а не напрямую в базе данных.

# Если вам действительно необходимы триггеры, работающие на уровне базы данных, вам может
потребоваться реализовывать их непосредственно с помощью SQL, используя средства, предоставленные вашей базой данных
(например, PostgreSQL, MySQL и т. д.). В этом случае, вам придется писать SQL-запросы для создания и управления
триггерами, а SQLAlchemy будет использоваться для выполнения этих запросов через свой интерфейс.
# ------------------------------------
"""

# -------------------------------- Стандартные модули
# import asyncio
# -------------------------------- Сторонние библиотеки
import asyncio
from sqlalchemy import event
# -------------------------------- Локальные модули
from working_databases.local_db_mockup import *
from handlers.oait_session import *
from sqlalchemy.ext.asyncio import AsyncSession

# Создаем глобальную асинхронную очередь
event_queue = asyncio.Queue()
# ----------------------------------------------------------------------------------------------------------------------
# Обработчик событий на добавление записей в бд для requests:
@event.listens_for(Requests, 'after_insert')
# Здесь `target` - это объект модели `Obs`, который был вставлен
def after_insert_requests(mapper, connection: AsyncSession, target:Requests):
    """
        # requests_history.request_message
        # await send_message(target.request_message)
        """
    # Добавляем задачу в асинхронную очередь
    asyncio.get_event_loop().call_soon_threadsafe(event_queue.put_nowait, target)

    # Асинхронный обработчик для выполнения задач из очереди
async def process_event_queue():
    while True:
        target = await event_queue.get()
        await handle_after_insert(target)



    # target - это экземпляр модели MyModel, который был добавлен в базу данных
    # ссылка на экземпляр объекта, который был только что вставлен в базу
    return await target # скорее всего целиком всю строку будет передавать.





# # Обработчик событий на добавление записей в бд для requests:
# @event.listens_for(Requests, 'after_insert')
# # Здесь `target` - это объект модели `Obs`, который был вставлен
# async def after_insert_requests(mapper, connection: AsyncSession, target:Requests):
#
#     """
#     # requests_history.request_message
#     # await send_message(target.request_message)
#     """
#
#     # target - это экземпляр модели MyModel, который был добавлен в базу данных
#     # ссылка на экземпляр объекта, который был только что вставлен в базу
#     return await target # скорее всего целиком всю строку будет передавать.



# -------------------- хлам
# async def get_target_requests()-> Requests:
#     target =
#     return await after_insert_requests()
