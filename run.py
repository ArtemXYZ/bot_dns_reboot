"""
Чат бот телеграмм

1. Приветственные сообщения (сразу без лишней воды:
Tasks bot OAiT SV
OAiTSVManagerBot !
problem helper -
helper_bot
DNS_helper_bot
DNS_help_manager_bot
help_manager_DNS_bot
helpManagerDNSBot

retail_helper_bot
retail_help_bot

DNSHelpManager
helpDNSManager
helpManagerDNS !

DNSHelper -

@HelperDNSBot !
@tasksOAiTSVBot (https://t.me/tasksOAiTSVBot)
"""

# -------------------------------- Стандартные модули
import os

# -------------------------------- Сторонние библиотеки
import asyncio

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command  # Фильтр только для старта
from aiogram.client.default import DefaultBotProperties  # Обработка текста HTML разметкой

# -------------------------------- Локальные модули
from dotenv import find_dotenv, load_dotenv  # Для переменных окружения
load_dotenv(find_dotenv())  # Загружаем переменную окружения

from handlers.admin_session import admin_router
from handlers.general_session import general_router
from handlers.supervisor_session import supervisor_router
from handlers.retail_session import retail_router
from handlers.private_session import private_router



from menu.cmds_list_menu import default_menu  # Кнопки меню для всех типов чартов


# --------------------------------


# ----------------------------------------------------------------------------------------------------------------------

bot = Bot(token=os.getenv('API_TOKEN'), default=DefaultBotProperties(parse_mode='HTML'))  # Для переменных окружения

# --------------------------------------------- Инициализация диспетчера событий
# Принимает все события и отвечает за порядок их обработки в асинхронном режиме.
dp = Dispatcher()

# Назначаем роутеры:
# dp.include_routers(admin_router, general_router, supervisor_router, retail_router, private_router) #
#

dp.include_router(retail_router)
dp.include_router(general_router)


# user_group_router.message.filter(ChatTypeFilter(['group', 'supergroup']))
# user_group_router.edited_message.filter(ChatTypeFilter(['group', 'supergroup']))
# --------------------------------------------- Тело бота:


# пусто


# ---------------------------------------------------- Зацикливание работы бота
# Отслеживание событий на сервере тг бота:
async def run_bot():
    await bot.delete_webhook(drop_pending_updates=True)  # Сброс отправленных сообщений, за время, что бот был офлайн.
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats()) # если надо удалить  команды из меню.

    await bot.set_my_commands(commands=default_menu, scope=types.BotCommandScopeDefault())  # Список команд в меню.
    # BotCommandScopeAllPrivateChats - для приват чартов  # todo здесь разобраться!
    # BotCommandScopeDefault - для всех чартов

    await dp.start_polling(bot, interval=1, allowed_updates=['message', 'edited_message', 'callback_query'])
    # todo allowed_updates=ALLOWED_UPDATES, - Блокирует мне кодсейчас!!! - передаем туда список разрешенных
    #  событий для бота с сервера
    # , interval=2 интервал запросов на обновление.


# Запуск асинхронной функции run_bot:
if __name__ == "__main__":
    asyncio.run(run_bot())

#


# --------------------------------------------- Огрызки
# def get_keyboard_directions():
#     """Генерация клавиатуры"""
#     # Инициализация кнопок
#     buttons = [
#         InlineKeyboardButton(text='Аналитика', callback_data='Аналитика_клик'),
#         InlineKeyboardButton(text='Форматы', callback_data='Форматы_клик'),
#         InlineKeyboardButton(text='Товарооборот', callback_data='Товарооборот_клик')
#     ]  # число кнопок
#
#     keyboard = types.InlineKeyboardMarkup(row_width=1)
#     keyboard.add(*buttons)
#     return keyboard
#
# @dp.message(Command('test'))
# async def test(message: types.Message):
#     # Отправляем пользователю сообщение с кнопками
#     await message.answer('Выбери:', reply_markup=get_keyboard_directions())
#
#     # # in_kb = types.InlineKeyboardMarkup()  # Создаем экземпляр класса инлайн клавиатуры
#     # in_kb.add(types.InlineKeyboardButton(text='Аналитика', callback_data="Аналитика_клик"))  # добавляем кнопку
#
# # Отработка события при нажатии кнопки
# @dp.callback_query(filters.Text(['Аналитика_клик', 'Форматы_клик', 'Товарооборот_клик']))
# async def send_random_value(call: types.CallbackQuery):
#     await call.message.answer('Отлично')
#     await call.answer()  # сервер Telegram ждёт от нас подтверждения о доставке колбэка, иначе в течение 30 секунд будет показывать специальную иконку.


# f' *  <em>/дашборды</em> - обращение по <b>дашбордам</b>.\n'
# f' *  <em>/инструмент_ценники</em> - Вопросы (проблемы) с <b>ценниками</b>.\n'  #- Вопросы (проблемы) с
# f' *  <em>/боты</em> - Вопросы (проблемы) с <b>Telegram-ботами</b>.\n'
# f' *  <em>/аналитика</em> - Вопросы (проблемы) с <b>ценниками</b>.\n'


# ,  reply_markup=in_kb

# -------------------------------------------

# \u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002 18

# \u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002 17


# В этой переменной содержатся все типы обновлений на сервере которые мы пропускаем (не фильтруем) на бота
# остальные мимо
# ALLOWED_UPDATES = ['message', 'edited_message', 'callback_query']  # !!! Добавить типы фильтров