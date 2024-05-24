"""
Режим сессии для замов отдела
"""

# -------------------------------- Стандартные модули

# -------------------------------- Сторонние библиотеки
from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, StateFilter, or_f
from aiogram.client.default import DefaultBotProperties  # Обработка текста HTML разметкой

# -------------------------------- Локальные модули
from filters.chats_filters import *

# from aiogram.utils.formatting import as_list, as_marked_section, Bold, Italic

# from menu import keyboard_menu  # Кнопки меню - клавиатура внизу
# from menu import inline_menu  # Кнопки встроенного меню - для сообщений


# Назначаем роутер для чата под розницу:
oait_manager_router = Router()

# фильтрует (пропускает) только личные сообщения и только определенных пользователей:
oait_manager_router.edited_message.filter(ChatTypeFilter(['private']), TypeSessionFilter(allowed_types=['oait']))
oait_manager_router.edited_message.filter(ChatTypeFilter(['private']), TypeSessionFilter(allowed_types=['oait']))

