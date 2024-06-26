"""
Модуль обработки событий для обычных пользователей (розница)
"""

# ----------------------------------------------------------------------------------------------------------------------
# import io
import asyncio
# --------------------------------

from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, StateFilter, or_f

# from aiogram.utils.formatting import as_list, as_marked_section, Bold, Italic

from menu import keyboard_menu  # Кнопки меню - клавиатура внизу
from menu import inline_menu  # Кнопки встроенного меню - для сообщений

from handlers.text_message import *

from filters.chats_filters import ChatTypeFilter

# Назначаем роутер для чата под розницу:
private_router = Router()

# Фильтруем события на этом роутере:
private_router.message.filter(ChatTypeFilter(['private']))
private_router.edited_message.filter(ChatTypeFilter(['private']))

# ------------------------------------------------- Тело модуля




# инлайн кнопка выбрать обращение
# копка клавиатура внизу создать обращение



# ------------------------------------- огрызки кода старых версий прозапас
# # пробелы не трогать внутри текста (настроено методом подбора)! Иначе, собъется выравнивание (ТЛГ сжимает пробелы)
#     await message.answer(f'Выбери тему обращения (категорию вопроса / проблемы):\n'
#
#                          f'\n'
#                          # ---------------------- Отпрвить к Аналитикам:
#                          f'<b><u>I. АНАЛИТИКА</u></b>\n'  # Жирный, подчеркнутый
#                          f'Вопросы (проблемы) с:\n'
#                          f' *  <b>Дашбордами:</b>                            <em>/dashboards</em>.\n'  # 17
#                          f' *  <b>Ценниками:</b>                                <em>/price_tags_tool</em>\n'
#                          f' *  <b>Telegram-ботами:</b>                     <em>/bots</em>\n'  # 14
#                          f' *  <b>Ценниками:</b>                                <em>/analytics</em>\n'  # 18
#
#                          f'\n'
#                          # ---------------------- Отпрвить к Форматам:
#                          f'<b><u>II. ФОРМАТЫ</u></b>\n'
#                          f'Вопросы (проблемы) по:\n'
#                          f' *  <b>АР (везет товар):</b>                       <em>/prod_coming</em>.\n'
#                          f' *  <b>АР (не везет товар):</b>                 <em>/not_prod_coming</em>\n'
#                          f' *  <b>СЕ:</b>                                                   <em>/ce</em>\n'
#                          f' *  <b>Границам категорий:</b>             <em>/borders</em>\n'
#                          f' *  <b>Лежакам:</b>                                     <em>/unsold</em>\n'
#
#                          f'\n'
#                          # ---------------------- Отпрвить товарообору:
#                          f'<b><u>III. ТОВАРООБОРОТ</u></b>\n'
#                          f'Вопросы (проблемы) по:\n'
#                          f' *  <b>МП:</b>                                                 <em>/sales</em>.\n'
#                          f' *  <b>Мерчам (не везет товар):</b>      <em>/merch</em>\n'
#                          f' *  <b>Ценам на товар:</b>                        <em>/price</em>\n'
#                          f' *  <b>Закупке товара:</b>                        <em>/purchase</em>\n'
#                          f' *  <b>ВЕ:</b>                                                  <em>/be</em>\n'
#                          f' *  <b>СТМ:</b>                                               <em>/stm</em>\n'
#                          f' *  <b>Уценке:</b>                                         <em>/discount</em>\n'
#                          # f'или напиши мне прямо в чарт '
#                          f'\n'
#                          f'и я направлю твою <b>"БОЛЬ"</b> нужным людям!',
#                          reply_markup=keyboard_menu.menu_kb)


# # @user_private_router.message((F.text.lower().contains('обращен'))
# #                              | (F.text.lower().contains('заяв'))
# #                              | (F.text.lower() == 'Создать новое обращение'))


# @user_private_router.message(F.text.lower() == "варианты оплаты")
# @user_private_router.message(Command("payment"))
# async def payment_cmd(message: types.Message):
#     text = as_marked_section(
#         Bold("Варианты оплаты:"),
#         "Картой в боте",
#         "При получении карта/кеш",
#         "В заведении",
#         marker="✅ ",
#     )
#     await message.answer(text.as_html())

# @user_private_router.message(
#     (F.text.lower().contains("доставк")) | (F.text.lower() == "варианты доставки"))
# @user_private_router.message(Command("shipping"))
# async def shipping_cmd(message: types.Message):
#     text = as_list(
#         as_marked_section(
#             Bold("Варианты доставки/заказа:"),
#             "Курьер",
#             "Самовынос (сейчас прибегу заберу)",
#             "Покушаю у Вас (сейчас прибегу)",
#             marker="✅ ",
#         ),
#         as_marked_section(
#             Bold("Нельзя:"),
#             "Почта",
#             "Голуби",
#             marker="❌ "
#         ),
#         sep="\n----------------------\n",
#     )
#     await message.answer(text.as_html())


# @user_private_router.message(F.text.lower() == 'Создать новое обращение')  #

# # Реагирование на обычную команду (точное совпадение) # /new
# @user_private_router.message(or_f(Command('new'), (F.text.lower() == 'Создать новое обращение'))
# async def new_cmd(message: types.Message):
#     #  0. Окно выбора категории обращения +
#     # пробелы не трогать внутри текста (настроено методом подбора)! Иначе, собъется выравнивание (ТЛГ сжимает пробелы)
#     await message.answer(f'Выбери тему обращения (категорию вопроса / проблемы):\n'
#
#                          f'\n'
#                          # ---------------------- Отпрвить к Аналитикам:
#                          f'<b><u>I. АНАЛИТИКА</u></b>\n'  # Жирный, подчеркнутый
#                          f'Вопросы (проблемы) с:\n'
#                          f' *  <b>Дашбордами:</b> <em>/dashboards</em>.\n'  # 17
#                          f' *  <b>Ценниками:</b> <em>/price_tags_tool</em>\n'
#                          f' *  <b>Telegram-ботами:</b> <em>/bots</em>\n'  # 14
#                          f' *  <b>Ценниками:</b> <em>/analytics</em>\n'  # 18
#
#                          f'\n'
#                          # ---------------------- Отпрвить к Форматам:
#                          f'<b><u>II. ФОРМАТЫ</u></b>\n'
#                          f'Вопросы (проблемы) по:\n'
#                          f' *  <b>АР (везет товар):</b> <em>/coming</em>.\n'  # prod_coming
#                          f' *  <b>АР (не везет товар):</b> <em>/no_coming</em>\n'  # not_prod_coming
#                          f' *  <b>СЕ:</b> <em>/ce</em>\n'
#                          f' *  <b>Границам категорий:</b> <em>/borders</em>\n'
#                          f' *  <b>Лежакам:</b> <em>/unsold</em>\n'
#
#                          f'\n'
#                          # ---------------------- Отпрвить товарообору:
#                          f'<b><u>III. ТОВАРООБОРОТ</u></b>\n'
#                          f'Вопросы (проблемы) по:\n'
#                          f' *  <b>МП:</b> <em>/sales</em>.\n'
#                          f' *  <b>Мерчам:</b> <em>/merch</em>\n'
#                          f' *  <b>Ценам на товар:</b> <em>/price</em>\n'
#                          f' *  <b>Закупке товара:</b> <em>/purchase</em>\n'
#                          f' *  <b>ВЕ:</b> <em>/be</em>\n'
#                          f' *  <b>СТМ:</b> <em>/stm</em>\n'
#                          f' *  <b>Уценке:</b> <em>/discount</em>\n'
#                          # f'или напиши мне прямо в чарт '
#                          f'\n'
#                          f'и я направлю твою <b>"БОЛЬ"</b> нужным людям!')

# f'     <b>Привет</b>, {user} 🖖 !\n'
#                          f'--------------------------------------------------------------------------------------------'
#                          f'---------\n'
#                          f'     На связи <b>"Tasks bot meneger". 🦾</b>\n'  # <strong> </strong>
#                          f'--------------------------------------------------------------------------------------------'
#                          f'---------\n'
#                          f'\n'
#                          f'  *  🤝   Я помогаю в решении вопросов и проблем розничных подразделений'
#                          f', возникающих в ходе повседневной деятельности.\n'
#                          f'\n'
#                          f'   * 🤙   Создаю заявки по обращениям и распределяю их на исполнителей в отделе ОАиТ СВ '
#                          f'в соответствии с их профилем деятельности, исходя из категории обращения.\n'
#                          f'\n'
#                          f'   *  👍  Направляю уведомления по завершении обработки заявки заказчику, и много другое...'