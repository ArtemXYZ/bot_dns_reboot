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


# chats_filters
class ChatTypeFilter(Filter):

    # Сюда пердаем список имен чартов
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    # Здесь вытает сответствие типу чата в котором было сообщение (тру если соответствет названию) или нет
    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types



# Кастомный фильтр для типов пользователей (ветки хендлеров: админ, супервайзер итд)
class IsAdmin(Filter):
    def __init__(self) -> None:
        pass

    # Добавляем объект Бот
    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        return message.from_user.id in bot.my_admins_list
        # my_admins_list - наполняем адишниками админов переменную.