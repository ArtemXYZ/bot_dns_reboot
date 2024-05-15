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


admins_list = []
# импортировать ссесию.


# ----------------------------------------------------------------------------------------------------------------------
# chats_filters
class ChatTypeFilter(Filter):

    # Сюда передаем список имен чартов:
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    # Здесь выдает соответствие типу чата в котором было сообщение (тру если соответствует названию) или нет
    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types




# --------------------------------
# access rights права доступа admin_list
# Кастомный фильтр для типов пользователей  #6
# (ветки хендлеров: админ, супервайзер итд)  - устарело
class IsTypeUser(Filter):

    # Сюда передаем список имен сессий (админ, розница и тд.) (параметры класса):
    def __init__(self, session_types: list[str]) -> None:  # , BotBase:Class
        self.chat_types = session_types
        # self.BotBase = BotBase

    # Проверяем входной id с id в базе данных на соответствие типу:
    async def type_user_id(self, message: types.Message, bot: Bot, session_types) -> bool: # , BotBase

        # id пользователя написавшего:
        user_id = message.from_user.id

        # запрос в базу данных: вернет тип пользователя по id
        # type_user_id = BotBase.Select.type_user.were(users_id=user_id)
        # Использование ORM для запроса в базу данных:
        session = Session()  # Создание сессии, убедитесь, что вы правильно настроили вашу сессию

        # Запрос к базе данных на соответствие типа пользователя.
        user = session.query(User).filter(User.user_id == user_id).first()
        if user and user.user_type in session_types:
            return True
        else:
            return False

        # импортировать из асинк ссесии



        return type_user_id in session_types
