"""
Модуль обработки событий для обычных пользователей (филиалы)
"""


from aiogram import types, Router
from aiogram.filters import CommandStart, Command

user_private_router = Router()

# -------------------------------------------------  Тело модуля