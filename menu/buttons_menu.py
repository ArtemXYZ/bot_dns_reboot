"""
Модуль содержит описание кнопок меню для всех типов чартов.
"""

from aiogram.types import BotCommand

default_buttons = [
    BotCommand(command='start', description='Начать работу с ботом'),
    BotCommand(command='help', description='Как работать с ботом'),
    BotCommand(command='new', description='Создать новое обращение'),
    BotCommand(command='status', description='Статус предыдущих обращений')
]

# private
# /list:		Просмотреть список задач