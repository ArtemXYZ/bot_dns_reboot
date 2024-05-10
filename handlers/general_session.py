"""
Общий режим сессии для всех типов чартов

1. Выполняет чистку сообщений от брани.
2. Отвечает за логирование пользователей при старте.
"""

# -------------------------------- Стандартные модули
from string import punctuation
import asyncio
# -------------------------------- Сторонние библиотеки
from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, StateFilter, or_f
from aiogram.client.default import DefaultBotProperties  # Обработка текста HTML разметкой

# -------------------------------- Локальные модули
from handlers.text_message import swearing_list  # Список ругательств:
from filters.chats_filters import ChatTypeFilter

# from aiogram.utils.formatting import as_list, as_marked_section, Bold, Italic

# from menu import keyboard_menu  # Кнопки меню - клавиатура внизу
# from menu import inline_menu  # Кнопки встроенного меню - для сообщений

# Назначаем роутер для всех типов чартов:
general_router = Router()

# ----------------------------------------------------------------------------------------------------------------------

# ставить логирование!!


#

# 1. -------------------------- Очистка сообщений от ругательств для всех типов чартов:
# Отлавливает символы в ругательствах (замаскированные ругательства):
def clean_text(text: str):
    return text.translate(str.maketrans('', '', punctuation))


# Ловим все сообщения, ищем в них ругательства:
@general_router.edited_message()  # даже если сообщение редактируется
@general_router.message()  # все входящие
async def cleaner(message: types.Message):
    if swearing_list.intersection(clean_text(message.text.lower()).split()):
        await message.answer(f'<b>Сообщение удалено!</b>\n'
                             f'<b>{message.from_user.first_name}</b>, попрошу конструктивно и без брани!')
                                # , parse_mode='HTML'
                                # Подобные сообщения, будут удалены!
        await message.delete()  # Удаляем непристойные сообщения.
        # await message.chat.ban(message.from_user.id)  # Если нужно, то в бан!


# ------------------------------------------------------------------------------