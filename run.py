"""
Чат бот телеграмм

ЗадаЧа:

1. Приветственные сообщения (сразу без лишней воды:
Tasks bot OAiT SV
OAiTSVManagerBot !
problem helper -
helper_bot
DNS_helper_bot
DNS_help_manager_bot
help_manager_DNS_bot
helpManagerDNSBot

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
load_dotenv(find_dotenv()) # Загружаем переменную окружения

from handlers.user_private import user_private_router
from menu.links_menu import default_menu # Кнопки меню для всех типов чартов
# --------------------------------
ALLOWED_UPDATES = ['message, edited_message'] # !!! Добавить типы фильтров

# ----------------------------------------------------------------------------------------------------------------------

bot = Bot(token=os.getenv('API_TOKEN'), default=DefaultBotProperties(parse_mode='HTML'))  # Для переменных окружения

# --------------------------------------------- Инициализация диспетчера событий
# Принимает все события и отвечает за порядок их обработки в асинхронном режиме.
dp = Dispatcher()
dp.include_routers(user_private_router) # admin_private_router,

# --------------------------------------------- Тело бота:





#






# ---------------------------------------------------- Зацикливание работы бота
# Отслеживание событий на сервере тг бота:
async def run_bot():
    await bot.delete_webhook(drop_pending_updates=True)  # Сброс отправленных сообщений, за время, что бот был офлайн.
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats()) # если надо удалить  команды из меню.
    await bot.set_my_commands(commands=default_menu, scope=types.BotCommandScopeDefault()) # Список команд в меню.
    # BotCommandScopeAllPrivateChats - для приват чартов
    # BotCommandScopeDefault - для всех чартов
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES, interval=1)
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
#     await message.answer(f'Выбери тему обращения (категорию вопроса / проблемы):\n'
#
#                          f'\n'
#                          # ---------------------- Отпрвить к Аналитикам:
#                          f'<b><u>I. АНАЛИТИКА</u></b>\n' # Жирный, подчеркнутый
#                          f'Вопросы (проблемы) с:\n'
#                          f' *  <b>Дашбордами:</b> <em>/дашборды</em>.\n'
#                          f' *  <b>Ценниками:</b> <em>/инструмент_ценники</em>\n'
#                          f' *  <b>Telegram-ботами:</b> <em>/боты</em>\n'
#                          f' *  <b>Ценниками:</b> <em>/аналитика</em>\n'
#
#                          f'\n'
#                          # ---------------------- Отпрвить к Форматам:
#                          f'<b><u>II. ФОРМАТЫ</u></b>\n'
#                          f'Вопросы (проблемы) по:\n'
#                          f' *  <b>АР (везет товар):</b> <em>/ap_товар_едет</em>.\n'
#                          f' *  <b>АР (не везет товар):</b> <em>/ap_товар_не_едет</em>\n'
#                          f' *  <b>СЕ:</b> <em>/се</em>\n'
#                          f' *  <b>Границам категорий:</b> <em>/границы</em>\n'
#                          f' *  <b>Лежакам:</b> <em>/лежаки</em>\n'
#
#                          f'\n'
#                          # ---------------------- Отпрвить товарообору:
#                          f'<b><u>III. ТОВАРООБОРОТ</u></b>\n'
#                          f'Вопросы (проблемы) по:\n'
#                          f' *  <b>МП:</b> <em>/продажи</em>.\n'
#                          f' *  <b>Мерчам (не везет товар):</b> <em>/мерч</em>\n'
#                          f' *  <b>Ценам на товар:</b> <em>/цена</em>\n'
#                          f' *  <b>Закупке товара:</b> <em>/закуп</em>\n'
#                          f' *  <b>ВЕ:</b> <em>/ве</em>\n'
#                          f' *  <b>СТМ:</b> <em>/стм</em>\n'
#                          f' *  <b>Уценке:</b> <em>/уценка</em>\n'
#                          # f'или напиши мне прямо в чарт '
#                          f'и я направлю твою <b>"БОЛЬ"</b> нужным людям!')
# \u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002 18

# \u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002\u2002 17