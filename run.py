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
# --------------------------------
import os
# --------------------------------
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command  # Фильтор только для старта
from aiogram.client.default import DefaultBotProperties # Обработка текста HTML разметкой
# --------------------------------
from config_bot import *
# -------------------------------- Для переменных окружения (после выгрузки)
# from dotenv import find_dotenv, load_dotenv
# load_dotenv(find_dotenv())  # Загружаем переменную окружения
# from handlers.user_private import user_private_router




# ----------------------------------------------------------------------------------------------------------------------


# bot = Bot(token=os.getenv('TOKEN'))  # Для переменных окружения
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode='HTML')) # Обработка текста HTML разметкой
# --------------------------------------------- Инициализация диспетчера событий
# (принимает все собыфтия и отвечает за порядок их обработки в асинхронном режиме)
dp = Dispatcher()
# dp.include_router(user_private_router)
# --------------------------------------------- Тело бота:
# Обработка событий на команду /start
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    user = message.from_user.first_name  # Имя пользователя
    await message.answer(f'<b>Привет</b>, {user}!  На связи <b>"Tasks bot meneger".</b>\n'
                         f'Я помогаю в решении вопросов и проблем, возникающих в ходе повседневной деятельности '
                         f'филиалов по дивизиону "Средняя Волга".\n'
                         f'Создаю заявки и распределяю их на исполнителей в соответствии с их компетенцией, '
                         f'исходя из категории обращения. '
                         f'Направляю уведомления по завершении обработки заявки заказчику, и много другое...')

    await asyncio.sleep(1)  # Добавляем задержку для второго сообщения.

    # Краткое описание возможностей бота, зачем нужен:
    await message.answer(f'Давай попробуем решить твой вопрос!')

    # здесь вызвать кнопки контекстные: создать обращение, вызвать справку.











# /new
@dp.message(Command('new'))
async def new_cmd(message: types.Message):

    #  0. Окно выбора категории обращения +
    # пробелы не трогать внутри текста (настроено методом подбора)! Иначе, собъется выравнивание (ТЛГ сжимает пробелы)
    await message.answer(f'Выбери тему обращения (категорию вопроса / проблемы):\n'     
                                                                   
                         f'\n'     
                         # ---------------------- Отпрвить к Аналитикам:                   
                         f'<b><u>I. АНАЛИТИКА</u></b>\n' # Жирный, подчеркнутый
                         f'Вопросы (проблемы) с:\n' 
                         f' *  <b>Дашбордами:</b>                            <em>/dashboards</em>.\n' # 17
                         f' *  <b>Ценниками:</b>                                <em>/price_tags_tool</em>\n'
                         f' *  <b>Telegram-ботами:</b>                     <em>/bots</em>\n'   # 14
                         f' *  <b>Ценниками:</b>                                <em>/analytics</em>\n'  # 18
                                                  
                         f'\n' 
                         # ---------------------- Отпрвить к Форматам:
                         f'<b><u>II. ФОРМАТЫ</u></b>\n'
                         f'Вопросы (проблемы) по:\n' 
                         f' *  <b>АР (везет товар):</b>                       <em>/prod_coming</em>.\n' 
                         f' *  <b>АР (не везет товар):</b>                 <em>/not_prod_coming</em>\n'
                         f' *  <b>СЕ:</b>                                                   <em>/ce</em>\n'
                         f' *  <b>Границам категорий:</b>             <em>/borders</em>\n'
                         f' *  <b>Лежакам:</b>                                     <em>/unsold</em>\n'

                         f'\n'
                         # ---------------------- Отпрвить товарообору:
                         f'<b><u>III. ТОВАРООБОРОТ</u></b>\n' 
                         f'Вопросы (проблемы) по:\n'                                     
                         f' *  <b>МП:</b>                                                 <em>/sales</em>.\n' 
                         f' *  <b>Мерчам (не везет товар):</b>      <em>/merch</em>\n'
                         f' *  <b>Ценам на товар:</b>                        <em>/price</em>\n'
                         f' *  <b>Закупке товара:</b>                        <em>/purchase</em>\n'                         
                         f' *  <b>ВЕ:</b>                                                  <em>/be</em>\n'
                         f' *  <b>СТМ:</b>                                               <em>/stm</em>\n'
                         f' *  <b>Уценке:</b>                                         <em>/discount</em>\n'
                         # f'или напиши мне прямо в чарт '
                         f'\n'
                         f'и я направлю твою <b>"БОЛЬ"</b> нужным людям!')




# Кнопка создать обращение.


# инлайн кнопка выбрать обращение
# копка клавиатура внизу создать обращение



# Ответ на вариации входящих сообщений:
# Только жесткое совпадение по словам, нужно доделать разделитель слов в сообщении потозже!
@dp.message()
async def echo(message: types.Message):
    text = message.text

    if text in ['Привет', 'привет', 'hi', 'hello']:
        await message.answer('И тебе привет!')
    elif text in ['Пока', 'пока', 'До свидания']:
        await message.answer('И тебе пока!')
    else:
        await message.answer(message.text)






# ------------------------ Зацикливание работы бота
# Отслеживание событий на сервере тг бота:
async def run_bot():
    await bot.delete_webhook(drop_pending_updates=True)  # Сброс отправленных сообщений, за время, что бот был офлайн.
    await dp.start_polling(bot, interval=1)  # , interval=2 интервал запросов на обновление.


# Запуск асинхронной функции run_bot:
if __name__ == "__main__":
    asyncio.run(run_bot())

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