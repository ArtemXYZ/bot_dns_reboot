"""
Режим сессии для замов отдела
"""

# -------------------------------- Стандартные модули

# -------------------------------- Сторонние библиотеки
from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, StateFilter, or_f
from aiogram.client.default import DefaultBotProperties  # Обработка текста HTML разметкой

# -------------------------------- Локальные модули
from filters.chats_filters import ChatTypeFilter

# from aiogram.utils.formatting import as_list, as_marked_section, Bold, Italic

# from menu import keyboard_menu  # Кнопки меню - клавиатура внизу
# from menu import inline_menu  # Кнопки встроенного меню - для сообщений


# Назначаем роутер для чата под розницу:
supervisor_router = Router()

# Фильтруем события на этом роутере:
# supervisor_router.message.filter(ChatTypeFilter(['supervisor']))
# supervisor_router.edited_message.filter(ChatTypeFilter(['supervisor']))