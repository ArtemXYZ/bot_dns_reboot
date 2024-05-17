"""
Модуль фильтрации роутеров.
Фильтрует события, в зависимости от того в каком чате было написано сообщение.

Кастомный класс наследуется из класса Filter.

Важно:
Тип чата может быть “приватным”, ”групповым“, ”супергрупповым“ или "каналом” - >
( “private”, “group”, “supergroup”, “channel”)
см.: https://core.telegram.org/bots/api#chat

Справочно:

    Чем отличие группы от супергруппы в Telegram?

Максимальное количество участников в группе составляет 200 человек.
Управлять группой может только ее владелец. Нет поиска по участникам.
Обычная группа имеет ограниченные функционал и боты в ней работают плохо или не работают вообще.

Супергруппа - это открытая группа с более чем 200 человек участников.
Функционал у таких групп намного шире. Есть поиск по участникам.
Можно назначать права администратора другим участникам.
"""

from aiogram.filters import Filter
from aiogram import types, Bot
from sqlalchemy.orm import DeclarativeBase

from working_databases.local_db_mockup import *

admins_list = []
# импортировать ссесию.


# ----------------------------------------------------------------------------------------------------------------------
# chats_filters
class ChatTypeFilter(Filter):
    """Для фильтрации ипа приватности (групповой чат или приватный или супер приватный"""

    # Сюда передаем список имен чартов:
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    # Здесь выдает соответствие типу чата в котором было сообщение (тру если соответствует названию) или нет
    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types

# -------------------------- Кастомные фильтры для разграничения доступа различным типам пользователей #6
class UsersRetailSession(Filter):
    """Для фильтрации розницы"""
    def __init__(self) -> None:
        pass

    # Проверяем входной id с id в retail_session_users_list = []
    # лист наполняется из базы данных по типу разрешенной сессии для пользователя.:
    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        return message.from_user.id in bot.retail_session_users_list

class UsersOAiTSession(Filter):
    """Для фильтрации сотрудников OAiT"""
    def __init__(self) -> None:
        pass

    # Проверяем входной id с id в retail_session_users_list = []
    # лист наполняется из базы данных по типу разрешенной сессии для пользователя.:
    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        return message.from_user.id in bot.oait_session_users_list

class UsersOAiTManagerSession(Filter):
    """Для фильтрации сообщений заместителей начальника и начальников OAiT"""
    def __init__(self) -> None:
        pass

    # Проверяем входной id с id в retail_session_users_list = []
    # лист наполняется из базы данных по типу разрешенной сессии для пользователя.:
    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        return message.from_user.id in bot.oait_manager_session_users_list

class UsersAdminSession(Filter):
    """Для фильтрации админов"""
    def __init__(self) -> None:
        pass

    # Проверяем входной id с id в retail_session_users_list = []
    # лист наполняется из базы данных по типу разрешенной сессии для пользователя.:
    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        return message.from_user.id in bot.admin_session_users_list















# ------------------------------------------------ Архив
#  typical session users  IsTypeUserSession
# class IsTypeUser(Filter):
#
#     # Сюда передаем список имен сессий (админ, розница и тд.) (параметры класса):
#     def __init__(self, session_types: list[str], mockup_class) -> None:  # , BotBase:Class
#         self.chat_types = session_types
#         self.mockup_class = mockup_class
#
#     # Проверяем входной id с id в базе данных на соответствие типу:
#     async def __call__(self, message: types.Message, mockup_class, session_types) -> bool: # , BotBase
#         """type_user_id"""
#
#         # id пользователя написавшего:
#         user_id = message.from_user.id
#
#         # запрос в базу данных: вернет тип пользователя по id
#         # type_user_id = BotBase.Select.type_user.were(users_id=user_id)
#         # Использование ORM для запроса в базу данных:
#         session = Session()  # Создание сессии, убедитесь, что вы правильно настроили вашу сессию
#
#         # Запрос к базе данных на соответствие типа пользователя.
#         user = session.query(Users).filter(User.user_id == user_id).first()
#         if user and user.user_type in session_types:
#             return True
#         else:
#             return False
#
#         # импортировать из асинк ссесии
#
#
#         # Запрос в локал бд по типу сессии достаем id !!
#         # или из базы накидываем в лист все айди соответствующие флагу !!
#
#         # При запуске бота добавить проверку в бд актуальных данных по сотруднику.?????
#         # делать это потом по времени.
#         # или продумать.
#
#         return type_user_id in session_types