"""
Модуль фильтрации роутеров.
Фильтрует события, в зависимости от того в каком чате было написано сообщение.

Кастомный класс наследуется из класса Filter.
"""


from aiogram.filters import Filter
from aiogram import types


# chats_filters
class ChatTypeFilter(Filter):

    # Сюда пердаем список имен чартов
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    # Здесь вытает сответствие типу чата в котором было сообщение (тру если соответствет названию) или нет
    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types