"""
Модуль содержит описание кнопок меню-клавиатуру для всех типов чартов.
"""

from aiogram.types import KeyboardButtonPollType, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Начать работу с ботом'),
            KeyboardButton(text='Как работать с ботом'),

        ],
        {
            KeyboardButton(text='Создать новое обращение'),
            KeyboardButton(text='Статус предыдущих обращений')
        }
    ],
    resize_keyboard=True,
    input_field_placeholder='Жалуся, обо всем доложим куда надо!'
)
