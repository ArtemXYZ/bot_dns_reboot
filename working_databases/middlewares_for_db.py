"""
Модуль "ПРОМЕЖУТОЧНЫХ СЛОЕВ" содержит пользовательские классы необходимых в дальнейшем
для работы с базами данных (SQL запросов).
В основном с помощью ОРМ.
"""

# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------- Импорт стандартных библиотек Пайтона
# ---------------------------------- Импорт сторонних библиотек
from typing import Any, Awaitable, Callable, Dict
from sqlalchemy import select, update, delete
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from sqlalchemy.ext.asyncio import async_sessionmaker

from working_databases.local_db_mockup import *
# ----------------------------------------------------------------------------------------------------------------------
class DataBaseSession(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data['session'] = session
            return await handler(event, data)

# -------------------------------------------- Фильтры из id БД ------------
# class UsersRetailSession(BaseMiddleware):
#     """Для фильтрации розницы"""
#
#     def __init__(self, session_pool: sessionmaker) -> None:
#         super().__init__()
#         self.session_pool = session_pool
#         self.admin_ids = set()
#
#     async def get_retail_list(self) -> set:
#         """Получает список id_tg всей розницы из базы данных."""
#
#         async with self.session_pool() as session:
#             result = await session.execute(select(Users.id_tg))
#             admin_ids = {row for row in result.scalars().all()}
#         self.admin_ids = admin_ids
#
#         async def on_pre_process_update(self, update: types.Update, data: dict):
#             """Загружает список админов перед обработкой обновления."""
#             await self.get_admins_list()
#             data['admin_ids'] = self.admin_ids


    #         ---------------------------
class TypeSessionMiddleware(BaseMiddleware):

    """
    Универсальный слой-определитель пользователей.
    На основе from_user.id выдает текстовый тип сессии (session_types = ['admin', 'retail', 'oait', '', '', '', ''])
    Далее эти значения пердаются на роутер и там сравниваются в кастомных фильтрах.
    Таким образом, достигается фильтрация пользователей по сессииям (разграничение прав).

    # todo - добавить проверку (досмтуп к этой функци после проверки на регистрацию.
    """
    def __init__(self, session_pool: async_sessionmaker) -> None:
        self.session_pool = session_pool

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:

        # Проверка принадлежности сообщения:
        # if isinstance(event, Message):  # message: types.Message

        get_id_tg = event.from_user.id # + работает
        # print(get_id_tg)
        query = select(Users.session_type).where(Users.id_tg==get_id_tg)
        # print(query)
        async with self.session_pool() as session:
            get_session_types = await session.execute(query)
            session_type_str = get_session_types.scalar_one_or_none()   #. .one() one_or_none() # + работает
            # print(session_type_str)
            await session.commit()

            # Передаем в словарик данных наш тип сесии:
            data["session_type"] = session_type_str # + работает
            print(data["session_type"])
        # Если тип сессии из базы (разрешенный) совпадает со значением в фильтре:
        return await handler(event, data)

# --------------------------------------------------
# class TypeSessionMiddleware(BaseMiddleware):
#
#     """
#
#     Универсальный слой-определитель пользователей.
#     На основе from_user.id выдает текстовый тип сессии (session_types = ['admin', 'retail', 'oait', '', '', '', ''])
#     Далее эти значения пердаются на роутер и там сравниваются в кастомных фильтрах.
#     Таким образом, достигается фильтрация пользователей по сессииям (разграничение прав).
#     """
#     def __init__(self, session_types: list[str], session_pool: sessionmaker) -> None:
#         self.session_types = session_types
#         self.session_pool = session_pool
#
#     async def __call__(self, message: types.Message) -> bool:
#
#         for next_type in self.session_types:
#
#             get_id_tg = message.from_user.id
#             query = select(Users.session_type).where(Users.id_tg == get_id_tg)
#
#             async with self.session_pool() as session:
#
#                 get_session_types = await session.execute(query)
#                 get_session_types.scalar()   #. .one() one_or_none()
#                 await session.commit()
#
#             # Если тип сессии из базы (разрешенный) совпадает со значением в фильтре:
#             return get_session_types == next_type


