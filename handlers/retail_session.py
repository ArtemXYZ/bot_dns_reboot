"""
Режим сессии для розницы

Основная ветка по работе с обращениями
"""

# -------------------------------- Стандартные модули
import asyncio
# -------------------------------- Сторонние библиотеки
from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, StateFilter, or_f
from aiogram.client.default import DefaultBotProperties  # Обработка текста HTML разметкой

# -------------------------------- Локальные модули
from handlers.text_message import * # Список ругательств:
from filters.chats_filters import ChatTypeFilter

# from aiogram.utils.formatting import as_list, as_marked_section, Bold, Italic

from menu import keyboard_menu  # Кнопки меню - клавиатура внизу
from menu import inline_menu  # Кнопки встроенного меню - для сообщений



# Назначаем роутер для чата под розницу:
retail_router = Router()

# Фильтруем события на этом роутере:
# retail_router.message.filter(ChatTypeFilter(['retail']))
# retail_router.edited_message.filter(ChatTypeFilter(['retail']))

# ----------------------------------------------------------------------------------------------------------------------

# Обработка событий на команду /start
@retail_router.message(CommandStart())
async def start_cmd(message: types.Message):
    user = message.from_user.first_name  # Имя пользователя

    # Краткое описание возможностей бота, зачем нужен:
    await message.answer((hello_users_retail.format(user)), parse_mode='HTML')   # .as_html()


    await asyncio.sleep(1)  # Добавляем задержку для второго сообщения.

    #
    await message.answer(f'Давай попробуем решить твой вопрос! 💆‍♂️',
                         reply_markup=keyboard_menu.menu_kb)

    await asyncio.sleep(1)

    # здесь вызвать кнопки контекстные: создать обращение, вызвать справку. +
    # Инлайн кнопка:
    await message.answer(f'Создать новое обращение ✍️ ?',
                         reply_markup=inline_menu.get_callback_btns(btns={
                             'Создать': 'new',
                             'Позже': 'none'
                         }))  # create
                        # сделать друг на друга кнопки#



# Реакция на нажатие кнопки Новая заявка: (or_f(Command("menu"), (F.text.lower() == "меню")))
@retail_router.callback_query(F.data.startswith('new'))
async def callback_new(callback: types.CallbackQuery): # для бд -   , session: AsyncSession
    # product_id = callback.data.split("_")[-1]
    # await orm_delete_product(session, int(product_id))

    #  0. Окно выбора категории обращения +
    await callback.answer()  # для сервера ответ
    await callback.message.answer(category_problem, parse_mode='HTML') #.as_html() - похоже не работает с f строкой




# @retail_router.message(CommandStart())
# async def start_cmd(message: types.Message):
#     await message.answer("Привет, я виртуальный помощник")


