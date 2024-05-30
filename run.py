"""
Чат бот телеграмм

1. Приветственные сообщения (сразу без лишней воды:
Tasks bot OAiT SV -
OAiTSVManagerBot !
problem helper -
helper_bot

DNS_helper_bot  !
DNSHelperBot

DNSrequestsHandlerBot

DNSrequestSHandlerBot

DNSrequestShandlerBot

DNS_help_manager_bot
help_manager_DNS_bot
helpManagerDNSBot

retail_helper_bot
retail_help_bot

DNSHelpManager +++

DNS

 problem DNShandlerBot

DNShandlerBot

helpDNSManager
helpManagerDNS !

DNSHelper -

@HelperDNSBot !
@tasksOAiTSVBot (https://t.me/tasksOAiTSVBot)

DNS request handler
DNS request Helper BotManager
DNS Request Help Manager
DNS requests Helper ++++
DNS Help requests Bot
DNS Help requests handler
DNS requests handler Bot

requests Helper Bot manager
"""
from typing import List

# -------------------------------- Стандартные модули
# import logging
# logging.basicConfig(level=logging.INFO)
# -------------------------------- Сторонние библиотеки
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties  # Обработка текста HTML разметкой
# from aiogram.utils import executor
# -------------------------------- Локальные модули
from working_databases.configs import *

from dotenv import find_dotenv, load_dotenv  # Для переменных окружения

load_dotenv(find_dotenv())  # Загружаем переменную окружения

from working_databases.init_db import *
from working_databases.middlewares_for_db import *

from working_databases.async_engine import *
from working_databases.orm_query_builder import *
from working_databases.query_builder import *

from handlers.general_session import general_router
from handlers.oait_session import oait_router
from handlers.oait_manager_session import oait_manager_router
from handlers.retail_session import retail_router
from handlers.admin_session import admin_router

from menu.cmds_list_menu import default_menu  # Кнопки меню для всех типов чартов

from start_sleep_bot.def_start_sleep import *

# --------------------------------
# phone_number_id = message.сontact.phone_number # достать номер телефона

# ----------------------------------------------------------------------------------------------------------------------
bot: Bot = Bot(token=os.getenv('API_TOKEN'),
               default=DefaultBotProperties(parse_mode='HTML'))  # Для переменных окружения

# --------------------------------------------- Инициализация диспетчера событий
# Принимает все события и отвечает за порядок их обработки в асинхронном режиме.
dp = Dispatcher()

# Будет работать до фильтров !!! На все типы обновлений (событий).
dp.message.outer_middleware(TypeSessionMiddleware(session_pool=session_pool_LOCAL_DB))

# Назначаем роутеры:
# dp.include_routers(general_router, admin_router, oait_manager_router, oait_router, retail_router) #

#  Распределение роутеров - порядок записи имеет значение. не трогать! (3й урок)
# dp.include_router(admin_router)
dp.include_router(retail_router)
# dp.include_router(general_router)



# dp.include_router(oait_router)
# dp.include_router(oait_manager_router)

# -------------------------------------------------- Тело бота:

# type_session: GetDataEvent = GetDataEvent() тесты!
# print(type_session.get_type_session())


# ---------------------------------------------------- Зацикливание работы бота
# Отслеживание событий на сервере тг бота:
async def run_bot():
    # ---------------------
    async def on_startup(bot):
        # Удаление Webhook и всех ожидающих обновлений
        await bot.delete_webhook(drop_pending_updates=True)
        print("Webhook удален и ожидающие обновления сброшены.")

        await startup_on(session=session_pool_LOCAL_DB)

    async def on_shutdown(bot):
        await shutdown_on()

    # ---------------------
    dp.startup.register(on_startup)  # действия при старте бота +
    dp.shutdown.register(on_shutdown)  # действия при остановке бота +

    # -------------------------------------------------------------------------------
    # Установка промежуточного слоя (сразу для диспетчера, не для роутеров):
    dp.update.middleware(DataBaseSession(session_pool=session_pool_LOCAL_DB))

    await bot.delete_webhook(drop_pending_updates=True)  # Сброс отправленных сообщений, за время, что бот был офлайн.
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats()) # если надо удалить  команды из меню.

    # todo здесь переделать (не для всех!)
    await bot.set_my_commands(commands=default_menu, scope=types.BotCommandScopeDefault())  # Список команд в меню.
    # BotCommandScopeAllPrivateChats - для приват чартов  # todo здесь переделать разобраться!
    # BotCommandScopeDefault - для всех чартов

    await dp.start_polling(bot, skip_updates=True,
                           allowed_updates=['message', 'edited_message', 'callback_query'])  # , interval=1
    # todo allowed_updates=ALLOWED_UPDATES, - передаем туда список разрешенных
    #  событий для бота с сервера
    # , interval=2 интервал запросов на обновление.


# Запуск асинхронной функции run_bot:
if __name__ == "__main__":
    asyncio.run(run_bot())

# todo типы message
# todo message_reaction()
# todo channel_post() .edited_channel_post() - надо запретить постить все
# .chat_boost() Поддержка чата
# .errors()


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


# my_admins_list =[] # наполняем адишниками админов переменную.

# Для того, что бы передавать сессию в другие функции
# * вызов асиинхронки без функции невозможен, по этому приходится лепить еще одну функцию в модуле для вызова
# можно передать изначальную функцию сессии прямо в целевую функцию так:
# session_pool=await get_async_sessionmaker(CONFIG_LOCAL_DB)), но повторный вызов уже существующей сессии
# будет невозможен. По этому, здесь эта вспомог. функция.


#
#  К экземпляру бота добавляем свойства (списки с users_id под каждый тип сессии:
# Обязательно присвоить значение, чтоб зарегестрировать переменную в экземпляре бота.
# bot.retail_session_users_list: list[int] = None  # [1034809823, 141407179]
# bot.retail_session_users_list: list[int] = [1034809823, 141407179]
# bot.oait_session_users_list = [1034809823, 141407179]
# bot.oait_manager_session_users_list = [1034809823]
# bot.admin_session_users_list = [1034809823]  #! надо в int , 1372644288
