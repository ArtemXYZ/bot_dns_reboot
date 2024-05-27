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


from aiogram import types, Bot

from sqlalchemy.ext.asyncio import async_sessionmaker

from working_databases.local_db_mockup import *


# session_users_list:str = None
from aiogram.filters import Filter


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
            data['session'] = session  #    Передаем в словарь переменную, которая будет доступна в хендлерах.
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


#   тесты      ---------------------------

class TypeSessionMiddleware(BaseMiddleware):

    """
    Универсальный слой-определитель пользователей.
    На основе from_user.id выдает текстовый тип сессии (session_types = ['admin', 'retail', 'oait', '', '', '', ''])
    Далее эти значения пердаются на роутер и там сравниваются в кастомных фильтрах.
    Таким образом, достигается фильтрация пользователей по сессииям (разграничение прав).

    # todo - добавить проверку (досмтуп к этой функци после проверки на регистрацию.
    """



    def __init__(self, session_pool: async_sessionmaker) -> Any:
        self.session_pool = session_pool
        self.session_type_str = None

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
            # bot: Bot - # todo надо в базовый класс передать объект бота/ окрутка фйограмм


    ) -> Any:

        # self.data = data
        bot: Bot = data.get('bot')

        # Проверка принадлежности сообщения:
        if isinstance(event, Message):  # message: types.Message
            get_id_tg = event.from_user.id  # + работает
            # print(get_id_tg)
            query = select(Users.session_type).where(Users.id_tg == get_id_tg)
            # print(query)

            async with self.session_pool() as session:
                get_session_types = await session.execute(query)
                self.session_type_str = get_session_types.scalar_one_or_none()   # + работает
                # print(session_type_str)
                await session.commit()

                # Передаем в словарик данных наш тип сесии:
                # data['session_type'] = self.session_type_str  # + работает (data["session_type"] = self.session_pool.get_session_type(event))
                # print(f'Передаем в словарик данных наш тип сесcии: {data["session_type"]}')
            # Если тип сессии из базы (разрешенный) совпадает со значением в фильтре:
            # return await handler(event, data)

            # session_users_list:str = self.session_type_str
            # print(f'Передаем в переменную наш тип сесcии: {session_users_list}')
            # return await session_users_list

            bot.retail_session_users_list = self.session_type_str

            print(f'Наш тип сесcии: {bot.retail_session_users_list}')
            return bot.retail_session_users_list




    # async def get_type_session(self) -> Any:  #, data: Dict[str, Any]
    #     return self.session_type_str


# class GetDataEvent(Filter):
#
#     def __init__(self) -> None:
#         pass
#
#     async def __call__(self, bot: Bot) -> bool:
#         return bot.retail_session_users_list
#
# class GetDataEvent(TypeSessionMiddleware):
#     def __init__(self) -> None:
#         pass



    # async def get_type_session(self) -> Any:  #, data: Dict[str, Any]
    #     return await data["session_type"]

#   тесты      ---------------------------





# class TypeSessionMiddleware(BaseMiddleware):
#
#     """
#     Работаее частично. здесь отрабатывает но не передаются данные словаря в роутеры.
#
#     Универсальный слой-определитель пользователей.
#     На основе from_user.id выдает текстовый тип сессии (session_types = ['admin', 'retail', 'oait', '', '', '', ''])
#     Далее эти значения пердаются на роутер и там сравниваются в кастомных фильтрах.
#     Таким образом, достигается фильтрация пользователей по сессииям (разграничение прав).
#
#     # todo - добавить проверку (досмтуп к этой функци после проверки на регистрацию.
#     """
#     def __init__(self, session_pool: async_sessionmaker) -> None:
#         self.session_pool = session_pool
#
#     async def __call__(
#             self,
#             handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
#             event: Message,  #   TelegramObject
#             data: Dict[str, Any],
#     ) -> Any:
#
#
#         # Проверка принадлежности сообщения:
#         if isinstance(event, Message):  # message: types.Message
#
#             get_id_tg = event.from_user.id  # + работает
#             # print(get_id_tg)
#             query = select(Users.session_type).where(Users.id_tg==get_id_tg)
#             # print(query)
#             async with self.session_pool() as session:
#                 get_session_types = await session.execute(query)
#                 session_type_str = get_session_types.scalar_one_or_none()   # + работает
#                 # print(session_type_str)
#                 await session.commit()
#
#                 # Передаем в словарик данных наш тип сесии:
#                 data['session_type'] = session_type_str  # + работает
#
#                 print(f'Передаем в словарик данных наш тип сесcии: {data["session_type"]}')
#
#             # Если тип сессии из базы (разрешенный) совпадает со значением в фильтре:
#             return await handler(event, data)

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


