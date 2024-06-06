"""
Режим сессии для ОАИТ
"""

# -------------------------------- Стандартные модули
import asyncio
# -------------------------------- Сторонние библиотеки
from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, StateFilter, or_f
from aiogram.client.default import DefaultBotProperties  # Обработка текста HTML разметкой
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
# -------------------------------- Локальные модули
from handlers.text_message import *  # Список ругательств:
from filters.chats_filters import *

# from aiogram.utils.formatting import as_list, as_marked_section, Bold, Italic

# from menu import keyboard_menu  # Кнопки меню - клавиатура внизу
from menu import inline_menu  # Кнопки встроенного меню - для сообщений

from menu.button_generator import get_keyboard

from working_databases.query_builder import *
from working_databases.events import *
from handlers.all_states import *

# ----------------------------------------------------------------------------------------------------------------------
# Назначаем роутер для всех типов чартов:
oait_router = Router()

# фильтрует (пропускает) только личные сообщения и только определенных пользователей:
# oait_router.message.filter(ChatTypeFilter(['private']), TypeSessionFilter(allowed_types=['oait']))
# oait_router.edited_message.filter(ChatTypeFilter(['private']), TypeSessionFilter(allowed_types=['oait']))


# ----------------------------------------------------------------------------------------------------------------------
# Приветствие для ОАИТ
# @oait_router.message(StateFilter(None), F.text == 'next')
# async def hello_after_on_next(message: types.Message):
#     user = message.from_user.first_name  # Имя пользователя
#     await message.answer((hello_users_oait.format(user)),
#                          parse_mode='HTML')

@oait_router.callback_query(StateFilter(StartUser.check_next), F.data.startswith('go_next'))
async def send_request_text_for_users(callback_query: types.CallbackQuery, state: FSMContext, session):
    bot = callback_query.bot
    await bot.send_message(chat_id=1034809823, text='Новая запись в Requests:')




#
# async def get_event():
#
#     event = await after_insert_requests()
#     message_text = f'Новая запись в Requests: {event}'
#
#     await message.answer(message_text)