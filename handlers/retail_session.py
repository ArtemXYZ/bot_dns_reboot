"""
Режим сессии для розницы

Основная ветка по работе с обращениями
"""

# -------------------------------- Стандартные модули
import asyncio
# -------------------------------- Сторонние библиотеки
from typing import Dict
from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, StateFilter, or_f
from aiogram.client.default import DefaultBotProperties  # Обработка текста HTML разметкой

# from aiogram.fsm.state import State, StatesGroup
# from aiogram.fsm.context import FSMContext
# -------------------------------- Локальные модули
from handlers.text_message import *  # Список ругательств:
from filters.chats_filters import *

# from aiogram.utils.formatting import as_list, as_marked_section, Bold, Italic

from menu import keyboard_menu  # Кнопки меню - клавиатура внизу
from menu.inline_menu import *  # Кнопки встроенного меню - для сообщений

from menu.button_generator import get_keyboard

from working_databases.orm_query_builder import *
from handlers.data_preparation import *

from handlers.all_states import *
# ----------------------------------------------------------------------------------------------------------------------
# Назначаем роутер для чата под розницу:
retail_router = Router()

# Фильтруем события на этом роутере:
# 1-й фильтр: чат может быть “приватным”, ”групповым“, ”супер групповым“ или "каналом” - > \
#  ( “private”, “group”, “supergroup”, “channel”)
# 2-й фильтр: по типу юзеров (тип сессии).

retail_router.message.filter(ChatTypeFilter(['private']), TypeSessionFilter(allowed_types=['oait', 'boss']))  # retail oait
retail_router.edited_message.filter(ChatTypeFilter(['private']), TypeSessionFilter(allowed_types=['oait', 'boss']))
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------- 0. Первичное приветствие всех пользователей при старте.
# После аутентификации нажимает кнопку продолжить...
# @retail_router.message(StateFilter(StartUser.check_next), F.data.startswith('go_repeat') | F.data.startswith('go_next'))
@retail_router.callback_query(StateFilter(StartUser.check_next), F.data.startswith('go_next')) # StartUser.check_next
# Переделать в заменяемый текст
async def hello_after_on_next(callback: types.CallbackQuery, state: FSMContext):

    await asyncio.sleep(2)

    user = callback.message.from_user.first_name  # Имя пользователя
    await callback.message.edit_text((hello_users_retail.format(user)), parse_mode='HTML')

    # await message.delete()  # Удаляет введенное сообщение пользователя (для чистоты чата) +
    await asyncio.sleep(8)

    # .message.edit_text
    await callback.message.edit_text(f'Если хочешь, я кратко расскажу, как со мной работать, '
                         f'а после уже помогу в решении твоих вопросов, ну или '
                         f'можешь приступать самостоятельно!',
                         parse_mode='HTML',
                         reply_markup=get_callback_btns(
                             btns={'▶️ КРАТКИЙ ИНСТРУКТАЖ': 'instruction',
                                   '⏩ ПРИСТУПИТЬ К РАБОТЕ': 'go_work'
                                   },
                             sizes=(1, 1)
                         ))
    # Чистим состояние:
    await state.clear()

    # Встает в ожидании нажатия кнопки
    await state.set_state(Instructor.instruct_or_gowork)


# Фильтруем все, кроме события нажатия 2-х кнопок (Если что-то напишет левое в чат, то удалим)
@retail_router.message(StateFilter(Instructor.instruct_or_gowork))
async def filter_unresolved_ext(message: types.Message, state: FSMContext):
    # удалит сообщение (блокирует все сообщения)
    # if not message.text in {'Создать заявку', 'Изменить заявку',
    #                          'Удалить заявку', 'Запросить статус заявки', 'Перейти в чат с исполнителем'}:
    await message.delete()


# ----------------------------- Конец 0.

# ----------------------------- 0.1. Если нажали кнопку "Инструктаж" - ответ на кнопку:
@retail_router.callback_query(StateFilter(Instructor.instruct_or_gowork), F.data.startswith('instruction'))
# Если у пользователя нет активного состояния (StateFilter(None) + он ввел команду "instruction")
async def get_instruction(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()  # Для сервера ответ о нажатии кнопки (кнопка не будет переливаться в ожидании).

    await callback.message.edit_text(
        f'Я включил специальное инлайновое меню.\n'
        f'С помощью него ты сможешь взаимодействовать с моим функционалом.'
        f'Для того, чтобы обратиться в ОАиТ за помощью в решении проблем '
        f'и прочих рабочих моментов, необходимо нажать кнопку в меню:\n'
        f'<b> * Создать заявку *</b>.'
        f'Далее, необходимо будет выбрать: <b> * Категория заявки *</b> \n'
        f', чтобы я точно понял, кому из сотрудников направить твою <b>боль</b>,\n'
        f'В дальнейшем, я всегда буду подсказывать по ходу твоих действий, так что не запутаешься!\n'
        f'Но если вдруг у тебя возникнут какие то проблемы или вопросы по работе со мной, '
        f'всегда можно обратиться за помощью, нажав кнопку "Помощь" или в "Меню", '
        f'далее команду <i>help</i>\n'
        f'Надеюсь, теперь ты разобрался и можем приступать к работе!',
        reply_markup=get_callback_btns(
            btns={'СОЗДАТЬ ЗАЯВКУ': 'go_create_request',
                  'ПЕРЕЙТИ В ЧАТ': 'go_chat_user',
                  'ИЗМЕНИТЬ ЗАЯВКУ': 'go_chenge_request',
                  'УДАЛИТЬ ЗАЯВКУ': 'go_delete_request',
                  'ЗАПРОСИТЬ СТАТУС ЗАЯВКИ': 'go_status_request'
                  },
            sizes=(2, 2, 1)))

    # Очистка состояния пользователя:
    await state.clear()


# 0.2. Если нажали кнопку "ПРИСТУПИТЬ К РАБОТЕ" - ответ на кнопку:
@retail_router.callback_query(StateFilter(Instructor.instruct_or_gowork), F.data.startswith('go_work'))
async def get_instruction(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()  # Для сервера ответ о нажатии кнопки (кнопка не будет переливаться в ожидании).
    await callback.message.edit_text(f'Вот тебе рабочий инструмент 👇, думаю разберешься 😉.',
                                     reply_markup=get_callback_btns(
                                         btns={'СОЗДАТЬ ЗАЯВКУ': 'go_create_request',
                                               'ПЕРЕЙТИ В ЧАТ': 'go_chat_user',
                                               'ИЗМЕНИТЬ ЗАЯВКУ': 'go_chenge_request',
                                               'УДАЛИТЬ ЗАЯВКУ': 'go_delete_request',
                                               'ЗАПРОСИТЬ СТАТУС ЗАЯВКИ': 'go_status_request'
                                               },
                                         sizes=(2, 2, 1)))
    # Очистка состояния пользователя:
    await state.clear()
    # await asyncio.sleep(5)
    # await callback.message.delete() - удалит кнопки


# ----------------------------- Конец 0.1/2

#
#

# ----------------------------- 1.0. Работа с нижней клавиатурой меню.
# -------------- 1.1. Ветка при создании заявки:
@retail_router.callback_query(StateFilter(None),
                              F.data.startswith('go_create_request'))  # (StateFilter(None), F.text == 'Создать заявку')
async def get_request_problem(callback: types.CallbackQuery, state: FSMContext):
    # Заменяет старое меню на новое
    # ---------------------------------------- Инлайновое меню (уровень 0):
    btn_main_retail_inline = get_callback_btns(
        btns={'📈 АНАЛИТИКА': 'problem_analytics',
              '🏬 ФОРМАТЫ': 'problem_formats',
              '🛞 ТОВАРООБОРОТ': 'problem_trade_turnover',
              '⏹ ОТМЕНА': 'problem_cancel'},
        sizes=(1, 1, 1, 1)
    )

    # Вывод инлайнового меню (категории обращений), реакция при создании заявки
    await callback.message.edit_text(
        f'Выберите категорию обращения 🚨', parse_mode='HTML', reply_markup=btn_main_retail_inline)
    # Встает в ожидании нажатия кнопки
    await state.set_state(SetCategory.main_category)
    #  CetCategory.sab_category


#
#
#

# # # # 1.1.0 Родитель (Ветка при создании заявки) -> Реакции на нажатие кнопок инлайнового меню на категории обращений:
# ----------------------- callback на cancel
@retail_router.callback_query(
    StateFilter(SetCategory.main_category, SetCategory.sab_category,
                AddRequests.request_message), F.data.startswith('problem_cancel'))
# Если у пользователя нет активного состояния (StateFilter(None) + он ввел команду "cancel")
async def get_cancel(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    # await callback.message.delete()  # удалит кнопки

    await callback.message.edit_text(f'Терминал:',
                                     reply_markup=get_callback_btns(
                                         btns={'СОЗДАТЬ ЗАЯВКУ': 'go_create_request',
                                               'ПЕРЕЙТИ В ЧАТ': 'go_chat_user',
                                               'ИЗМЕНИТЬ ЗАЯВКУ': 'go_chenge_request',
                                               'УДАЛИТЬ ЗАЯВКУ': 'go_delete_request',
                                               'ЗАПРОСИТЬ СТАТУС ЗАЯВКИ': 'go_status_request'
                                               },
                                         sizes=(2, 2, 1)))

    # Очистка состояния пользователя:
    await state.clear()


# ----------------------- callback на АНАЛИТИКА
@retail_router.callback_query(StateFilter(SetCategory.main_category), F.data.startswith('problem_analytics'))
# Если у пользователя нет активного состояния (StateFilter(None) + он ввел команду "analytics")
async def get_problem_analytics_state(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    btn_problem_analytics = get_callback_btns(
        btns={'📊 ДАШБОРДЫ': 'problem_dashboards',
              '🔖 ЦЕННИКИ': 'problem_tags',
              '🤖 TELEGRAM-БОТЫ': 'problem_bot',
              '⬅️ НАЗАД': 'problem_inline_back',
              '⏹ ОТМЕНА': 'problem_cancel'},
        sizes=(1, 1, 1, 2))

    await callback.message.edit_text(f'Выберите подкатегорию обращения в разделе АНАЛИТИКА:',
                                     parse_mode='HTML',
                                     reply_markup=btn_problem_analytics)
    await state.clear()
    # Встает в ожидании нажатия кнопки и переходит к меню отправки сообщения:
    await state.set_state(SetCategory.sab_category)


# ----------------------- callback на ФОРМАТЫ
@retail_router.callback_query(StateFilter(SetCategory.main_category), F.data.startswith('problem_formats'))
# Если у пользователя нет активного состояния (StateFilter(None) + он ввел команду "analytics")
async def get_problem_formats_state(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    btn_problem_formats = get_callback_btns(btns={'АР (ВЕЗЕТ ТОВАР)': 'problem_coming',
                                                  'АР (НЕ ВЕЗЕТ ТОВАР) ': 'problem_no_coming',
                                                  'СЕ': 'problem_ce',
                                                  'ГРАНИЦЫ КАТЕГОРИЙ': 'problem_borders',
                                                  'ЛЕЖАКИ': 'problem_unsold',
                                                  '⬅️ НАЗАД': 'problem_inline_back',
                                                  '⏹ ОТМЕНА': 'problem_cancel'},
                                            sizes=(1, 1, 1, 1, 1, 2))

    await callback.message.edit_text(f'Выберите подкатегорию обращения в разделе ФОРМАТЫ:',
                                     parse_mode='HTML',
                                     reply_markup=btn_problem_formats)
    await state.clear()
    # Встает в ожидании нажатия кнопки и переходит к меню отправки сообщения:
    await state.set_state(SetCategory.sab_category)


# ----------------------- callback на ТОВАРООБОРОТ
@retail_router.callback_query(StateFilter(SetCategory.main_category), F.data.startswith('problem_trade_turnover'))
# Если у пользователя нет активного состояния (StateFilter(None) + он ввел команду "analytics")
async def get_problem_trade_turnover_state(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    btn_problem_trade_turnover = get_callback_btns(
        btns={'МП': 'problem_sales',
              'МЕРЧИ': 'problem_merch',
              'ЦЕНА НА ТОВАР': 'problem_price',
              'ЗАКУПКА ТОВАРА': 'problem_purchase',
              'ВЕ': 'problem_ve',
              'СТМ': 'problem_stm',
              'УЦЕНКА': 'problem_discount',
              '⬅️ НАЗАД': 'problem_inline_back',
              '⏹ ОТМЕНА': 'problem_cancel'},
        sizes=(1, 1, 1, 1, 1, 1, 1, 2))

    await callback.message.edit_text(f'Выберите подкатегорию обращения в разделе ТОВАРООБОРОТ:',
                                     parse_mode='HTML',
                                     reply_markup=btn_problem_trade_turnover)
    await state.clear()
    # Встает в ожидании нажатия кнопки и переходит к меню отправки сообщения:
    await state.set_state(SetCategory.sab_category)


# ----------------------- callback на problem_inline_back
@retail_router.callback_query(
    StateFilter(SetCategory.sab_category, AddRequests.request_message), F.data.startswith('problem_inline_back'))
# Если у пользователя нет активного состояния (StateFilter(None) + он ввел команду "cancel")
async def get_problem_inline_back_state(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text(f'Выберите категорию обращения 🚨',
                                     parse_mode='HTML',
                                     reply_markup=get_callback_btns(
                                         btns={'📈 АНАЛИТИКА': 'problem_analytics',
                                               '🏬 ФОРМАТЫ': 'problem_formats',
                                               '🛞 ТОВАРООБОРОТ': 'problem_trade_turnover',
                                               '⏹ ОТМЕНА': 'problem_cancel'},
                                         sizes=(1, 1, 1, 1)))
    await state.clear()
    # Встает в ожидании нажатия кнопки и переходит к меню отправки сообщения:
    await state.set_state(SetCategory.main_category)


# ----------------------- callback на все возможные варианты
@retail_router.callback_query(
    StateFilter(SetCategory.sab_category),
    F.data.startswith('problem_') & (~F.data.startswith('problem_cancel') | ~F.data.startswith('problem_inline_back')))
async def get_problem_trade_turnover_state(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    # Узнаем какая кнопка была нажата:
    selected_subcategory = callback.data
    # print(selected_subcategory)

    # Интерпретация келбек ключей,  генерации данных для БД:
    write_to_base = generator_category_data(selected_subcategory)

    # Вытаскиваем данные:
    # get_category = await state.get_data()

    # print(f'get_category_data = {get_category_data}')

    # Заменяем клаву:
    await callback.message.edit_text(f'Введите текст обращения ', reply_markup=get_callback_btns(  # todo: по \
        # todo:  {get_category} - доработать , так , что бы выволдило категорию обращения.

        btns={'⬅️ НАЗАД': 'problem_inline_back',
              '⏹ ОТМЕНА': 'problem_cancel'},
        sizes=(2,)))

    # Вытаскиваем идентификеатор сообщения (до того, как обнулим состояние):
    chat_id = callback.message.chat.id   # chat_id_before_entering_text
    message_id = callback.message.message_id  # message_id_before_entering_text

    await state.clear()
    await state.set_state(AddRequests.request_message)

    # Перекидываем в стейт дату наши подготовленные данные для отправки сообщения
    await state.update_data(write_to_base)
    await state.update_data(chat_id = chat_id, message_id = message_id)

# ----------------------- callback на ввод сообщения: # await callback.message.delete()  # удалит кнопки
# Становимся в состояние ожидания ввода
# Пользователь ввел текст

@retail_router.message(StateFilter(AddRequests.request_message), F.text)  #from aiogram import Bot
# Если ввел текст обращения (AddRequests.request_message, F.text):
async def get_request_message_users(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):

    # ---------------------------- удаляем инлайновые кнопки (при вводе сообщения):
    # Формируем полученные данные из другого стейта (chat_id, message_id):
    data = await state.get_data()
    chat_id = data['chat_id']
    message_id = data['message_id']

    # Удаляем конкретное сообщение. +- (может быть ошибка, если до этого ботт был выключен и история не очищена \
    # (протестить еще раз))
    await bot.delete_message(chat_id=chat_id, message_id=message_id)

    await message.delete() # Удаляет введенное сообщение пользователя (для чистоты чата) +

    # Передам словарь с данными (ключ = request_message, к нему присваиваем данные message.text), после апдейтим +
    await state.update_data(request_message=message.text, tg_id=message.from_user.id)

    # Забираем обновленные данные:
    new_data = await state.get_data()
    # print(f' До удаления:  {new_data}')

    # Удаляем ключи и их значения из словаря (они больше не нужны):
    del new_data['chat_id']  # temp_data  +
    del new_data['message_id'] # temp_data  +

    print(f' После удаления:  {new_data}')  # - Работает +

    # Запрос в БД на добавление обращения:
    await add_request_message(session, new_data)

    # Очистка состояния пользователя:
    await state.clear()

    sent_message = await message.answer(f'<b>Обращение зарегистрировано, ожидайте ответа!</b> \n'
                         f'Как только обращение будет взято в работу, я направлю уведомление.'
                         f'\n'
                         f'<em><b>Ваше обращение:</b> {new_data.get("request_message")}</em>'
                         )
    # del new_data

    # -------------------------- Удаляем введенное сообщение выше 👆:
    # Очищаем данные, тк, на прямую удалить сообщение выше не получится - выходит ошибка
    # (скорее всего из-за удаления сообщения выше)

    await asyncio.sleep(5)

    # await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    # Через 2 секунды возвращаем исходное главное меню.

    await sent_message.edit_text(f'Терминал:',
                                     reply_markup=get_callback_btns(
                                         btns={'СОЗДАТЬ ЗАЯВКУ': 'go_create_request',
                                               'ПЕРЕЙТИ В ЧАТ': 'go_chat_user',
                                               'ИЗМЕНИТЬ ЗАЯВКУ': 'go_chenge_request',
                                               'УДАЛИТЬ ЗАЯВКУ': 'go_delete_request',
                                               'ЗАПРОСИТЬ СТАТУС ЗАЯВКИ': 'go_status_request'
                                               },
                                         sizes=(2, 2, 1)))


    # await message.edit_text(f'Терминал:',
    #                                  reply_markup=get_callback_btns(
    #                                      btns={'СОЗДАТЬ ЗАЯВКУ': 'go_create_request',
    #                                            'ПЕРЕЙТИ В ЧАТ': 'go_chat_user',
    #                                            'ИЗМЕНИТЬ ЗАЯВКУ': 'go_chenge_request',
    #                                            'УДАЛИТЬ ЗАЯВКУ': 'go_delete_request',
    #                                            'ЗАПРОСИТЬ СТАТУС ЗАЯВКИ': 'go_status_request'
    #                                            },
    #                                      sizes=(2, 2, 1)))




    # await bot.edit_message_text(chat_id=message.chat.id,
    #                             message_id=message.message_id,
    #                             text=f'Терминал:',
    #                                  reply_markup=get_callback_btns(
    #                                      btns={'СОЗДАТЬ ЗАЯВКУ': 'go_create_request',
    #                                            'ПЕРЕЙТИ В ЧАТ': 'go_chat_user',
    #                                            'ИЗМЕНИТЬ ЗАЯВКУ': 'go_chenge_request',
    #                                            'УДАЛИТЬ ЗАЯВКУ': 'go_delete_request',
    #                                            'ЗАПРОСИТЬ СТАТУС ЗАЯВКИ': 'go_status_request'
    #                                            },
    #                                      sizes=(2, 2, 1)))






# -- Если понадобятся кнопки, то делаем через новый обработчик:
# @retail_router.message(StateFilter(AddRequests.request_message), F.text)
# async def change_request_message_users(message: types.Message, state: FSMContext):




# -------------- 1.2. Ветка при отмене заявки:
# back_step
# @retail_router.message(StateFilter(AddRequests.request_message), F.text == 'Отменить заявку')
# async def get_back_request(message: types.Message):
#     await state.clear()
#     await message.delete()
#     # Заменяет старое меню на новое
#     await message.answer(f'Ок!', reply_markup=RETAIL_KEYB_MAIN)
# 'Отменить заявку',
# 'Показать категори',

# -------------- 1.3. Ветка при изменеии заявки:
@retail_router.message(StateFilter(None), F.text == 'Изменить заявку')
async def get_change_request(message: types.Message):
    await message.delete()
    #
    await message.answer(f'Эта функция еще в разработке! \n'
                         f'Что будет? Запрос в локал бд - найти заяки по айди пользователя'
                         f'Выдать список заявок и тд. -> (продумать логику) ')


# -------------- 1.4. Ветка при удалении заявки:
@retail_router.message(StateFilter(None), F.text == 'Удалить заявку')
async def get_change_request(message: types.Message):
    await message.delete()
    #
    await message.answer(f'Эта функция еще в разработке! \n'
                         f'Что будет? Запрос в локал бд - найти заяки по айди пользователя'
                         f'Выдать список заявок и тд. -> (продумать логику) ')


# -------------- 1.5. Ветка при удалении заявки:
@retail_router.message(StateFilter(None), F.text == 'Запросить статус заявки')
async def get_status_request(message: types.Message):
    await message.delete()
    #
    await message.answer(f'Эта функция еще в разработке! \n'
                         f'Что будет? Запрос в локал бд - найти заяки по айди пользователя'
                         f'Выдать список заявок и тд. -> (продумать логику) ')


# -------------- 1.6. Ветка при удалении заявки:
@retail_router.message(StateFilter(None), F.text == 'Перейти в чат с исполнителем')
async def get_chat_with_worker(message: types.Message):
    await message.delete()
    #
    await message.answer(f'Эта функция еще в разработке! \n'
                         f'Что будет? Запрос в локал бд - найти активные заяки по айди пользователя'
                         f'Выдать список заявок и тд. -> (продумать логику) ')
    await message.answer(category_problem, parse_mode='HTML')  # !!

# ----------------------------- Конец 1.0. Работа с нижней клавиатурой меню.


# ----------------------------------------------------------------------------------------------------------------------
# @retail_router.message(F.text == 'Показать справку по категориям')
# async def get_info_category(message: types.Message):
#     await message.delete()
#
#     await message.answer(category_problem, parse_mode='HTML')

# ---------------------------- Нижняя сопутствующая клавиатура кнопке "Создать заявку" конец:


# await message.answer(f'Введите суть обращения', reply_markup=REQUEST_PROBLEM)

# , reply_markup=types.ReplyKeyboardRemove() - удаляет клаву # Удалить старое меню

# f'А если вдруг тебе понадобится '
#     await asyncio.sleep(1)

# todo Добавить приветственную картинку и отредактить текст.

# Такое же меню меню можно вызвать с помощью кнопок внизу экрана
# Обработка событий на команду /start
# @retail_router.message(CommandStart())
# async def start_cmd(message: types.Message):
#     user = message.from_user.first_name  # Имя пользователя
#
#     # Краткое описание возможностей бота, зачем нужен:
#     await message.answer((hello_users_retail.format(user)), parse_mode='HTML')   # .as_html()
#
#
#     await asyncio.sleep(1)  # Добавляем задержку для второго сообщения.

# #
# await message.answer(f'Давай попробуем решить твой вопрос! 💆‍♂️',
#                      reply_markup=keyboard_menu.menu_kb)

# await asyncio.sleep(1)

# здесь вызвать кнопки контекстные: создать обращение, вызвать справку. +
# Инлайн кнопка:
# await message.answer(f'Создать новое обращение ✍️ ?',
#                      reply_markup=inline_menu.get_callback_btns(btns={
#                          'Создать': 'new',
#                          'Позже': 'none'
#                      }))  # create
#                     # сделать друг на друга кнопки#

# Реакция на нажатие кнопки Новая заявка: (or_f(Command("menu"), (F.text.lower() == "меню")))
# @retail_router.callback_query(F.data.startswith('new'))
# async def callback_new(callback: types.CallbackQuery): # для бд -   , session: AsyncSession
#     # product_id = callback.data.split("_")[-1]
#     # await orm_delete_product(session, int(product_id))
#
#     #  0. Окно выбора категории обращения +
#     await callback.answer()  # для сервера ответ
#     await callback.message.answer(category_problem, parse_mode='HTML') #.as_html() - похоже не работает с f строкой

# @retail_router.message(CommandStart())
# async def start_cmd(message: types.Message):
#     await message.answer("Привет, я виртуальный помощник")

# , parse_mode='HTML', reply_markup=inline_menu.get_callback_btns(btns={async def add_product(message: types.Message):
#                                      'Пройти атентификацию': 'get_type_users'}))   # , parse_mode='HTML'    await message.answer("Привет розница! Что хочешь сделать?", reply_markup=RETAIL_KEYB)

#
# f'\u00A0\u00A0💆‍♂️\u00A0\u00A0Давай попробуем решить твой вопрос!\n'
#                          f'\n'
#                          f'Для начала необходимо выбрать категорию обращения, чтобы я точно понял,'
#                          f' кому из сотрудников направить твою боль, а дальше я уже подскажу.\n'
#                          f'\n'

# f'Для того, чтобы <b>создать новую заявку</b> \n'
#                          f'<i>(обратиться в ОАиТ за помощью в решении проблем и прочих рабочих моментов)</i>'
#                          f', необходимо выбрать <b>категорию обращения</b>,'
#                          f' чтобы я точно понял, кому из сотрудников направить твою <b>боль</b>,'
#                          f' а дальше и так интуитивно понятно. \n'
#                          f'К тому же я всегда буду подсказывать по ходу твоих действий.')


#     data_main_category = callback_query.data
#     if data == 'problem_analytics':
#         await bot.send_message(callback_query.from_user.id, 'Выберите отчет:', reply_markup=analytics_menu_keyboard())
#         await state.set_state(CetCategory.analytics)
#     elif data == 'problem_formats':

# # await asyncio.sleep(1)
#     # await callback.message.answer(f'Для того, чтобы обратиться в ОАиТ за помощью в решении проблем '
#     #                               f'и прочих рабочих моментов, необходимо нажать кнопку в меню:\n'
#     #                               f'<b> * Создать заявку *</b>.',
#     #                               reply_markup=RETAIL_KEYB_MAIN)
#     #
#     # await asyncio.sleep(2)
#     # await callback.message.answer(f'Далее, необходимо будет выбрать: <b> * Категория заявки *</b> \n'
#     #                               f', чтобы я точно понял, кому из сотрудников направить твою <b>боль</b>,\n')
#     #
#     # await asyncio.sleep(2)
#     # await callback.message.answer(
#     #     f'В дальнейшем, я всегда буду подсказывать по ходу твоих действий, так что не запутаешься!')
#     #
#     # await asyncio.sleep(1)
#     # await callback.message.answer(f'Но если вдруг у тебя возникнут какие то проблемы или вопросы по работе со мной, '
#     #                               f'всегда можно обратиться за помощью, нажав кнопку "Меню", '
#     #                               f'далее команду <i>help</i>')
#     #
#     # await asyncio.sleep(2)
#     # await callback.message.answer(f'Надеюсь, теперь ты разобрался и можем приступать к работе!')
#     #
#     # await asyncio.sleep(3)
#     # await callback.message.answer(f'Если что, - я готов! Жалуйся ✍️ !')


# # Кнопки меню внизу (первый старт)
# RETAIL_KEYB_MAIN = get_keyboard(
#     'Создать заявку',
#     'Изменить заявку',
#     'Удалить заявку',
#     'Запросить статус заявки',
#     'Перейти в чат с исполнителем',
#     placeholder='Выберите действие',
#     sizes=(2, 1, 1)  # кнопок в ряду, по порядку 1й ряд и тд.
# )
#
# REQUEST_PROBLEM = get_keyboard(
#     # 'Изменить категорию',
#     'Отменить заявку',
#     'Показать категори',
#     placeholder='Выберите действие',
#     sizes=(2,)  # кнопок в ряду, по порядку 1й ряд и тд. 2, 1
# )
