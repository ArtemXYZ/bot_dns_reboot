"""
Модуль обработки событий для дмина
"""

# -------------------------------- Стандартные модули

# -------------------------------- Сторонние библиотеки
from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, StateFilter, or_f
from aiogram.client.default import DefaultBotProperties  # Обработка текста HTML разметкой

# -------------------------------- Локальные модули
from filters.chats_filters import ChatTypeFilter

admin_router = Router()

# -------------------------------------------------  Тело модуля