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
from aiogram.types import ContentType

from aiogram.exceptions import TelegramBadRequest # except

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

retail_router.message.filter(ChatTypeFilter(['private']),
                             TypeSessionFilter(allowed_types=['oait', 'boss']))  # retail oait
retail_router.edited_message.filter(ChatTypeFilter(['private']), TypeSessionFilter(allowed_types=['oait', 'boss']))


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------- 0. Первичное приветствие всех пользователей при старте.
# После аутентификации нажимает кнопку продолжить...
# @retail_router.message(StateFilter(StartUser.check_next), F.data.startswith('go_repeat') | F.data.startswith('go_next'))
@retail_router.callback_query(StateFilter(StartUser.check_next), F.data.startswith('go_next'))  # StartUser.check_next
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

    # Интерпретация келбек ключей, генерации данных для БД:
    write_to_base = generator_category_data(selected_subcategory)

    # Заменяем клаву: message_menu =
    message_menu = await callback.message.edit_text(f'Введите текст обращения ',
                                                    reply_markup=get_callback_btns(

                                                        btns={'⬅️ НАЗАД': 'problem_inline_back',
                                                              '⏹ ОТМЕНА': 'problem_cancel'},
                                                        sizes=(2,)))

    # Для того, что бы после ввода пользователем текста ссобщения можно было изменить кнопки:
    edit_chat_id = message_menu.chat.id
    edit_message_id = message_menu.message_id

    # Очищаем состояние, встаем в ожидание ввода текста пользователем:
    await state.clear()
    await state.set_state(AddRequests.request_message)

    # Перекидываем в стейт-дату наши подготовленные данные для дальнейшего редактирования сообщения:
    await state.update_data(write_to_base, edit_chat_id=edit_chat_id, edit_message_id=edit_message_id)


# ----------------------- callback на ввод сообщения: # await callback.message.delete()  # удалит кнопки
# Становимся в состояние ожидания ввода
# Если ввел текст обращения (AddRequests.request_message, F.text):
@retail_router.message(StateFilter(AddRequests.request_message), F.text)
async def get_request_message_users(message: types.Message,
                                    state: FSMContext, session: AsyncSession, bot: Bot):
    # , bot: Bot callback: types.CallbackQuery,

    await message.delete()  # Удаляет введенное сообщение пользователя (для чистоты чата) +

    # Получаем данные из предыдущего стейта:
    data_write_to_base = await state.get_data()
    # print(f'data_write_to_base    -   {data_write_to_base} !!!')

    # Получаем идентификаторы сообщения, для редактирования:
    edit_chat_id_new = data_write_to_base.get('edit_chat_id')
    edit_message_id_new = data_write_to_base.get('edit_message_id')
    # Передам словарь с данными (ключ = request_message, к нему присваиваем данные message.text), после апдейтим +
    await state.update_data(request_message=message.text, tg_id=message.from_user.id)

    # ответить прикрепите документы attach_doc_menu message_menu
    await bot.edit_message_text(chat_id=edit_chat_id_new,
                                message_id=edit_message_id_new,
                                text=f'<b>Ваше обращение:</b>\n'
                                     f'<em>{message.text}</em>\n'
                                     f'<b>Категория:</b>\n'
                                     f'<em>{data_write_to_base['name_category']}</em>\n'
                                     f'<b>Подкатегория:</b>\n'
                                     f'<em>{data_write_to_base['name_subcategory']}</em>',
                                reply_markup=get_callback_btns(
                                    btns={'📨 ОТПРАВИТЬ ЗАЯВКУ': 'skip_and_send',
                                          '📂 ПРИКРЕПИТЬ ФАЙЛЫ': 'attach_doc'},
                                    sizes=(1, 1))
                                )
    # todo: по  todo:  {get_category} - доработать , так , что бы выволдило категорию обращения +- .

    # Получаем обновленные данные:
    data_request_message = await state.get_data()
    # Очищаем состояние, встаем в ожидание ввода текста пользователем:
    await state.clear()
    await state.set_state(AddRequests.send_message_or_add_doc)
    # Передаем данные в следующее состояние по сценарию:
    await state.update_data(data_request_message)


# Пользователь нажимает ОТПРАВИТЬ ЗАЯВКУ. #  ------------------------- работает +
@retail_router.callback_query(StateFilter(AddRequests.send_message_or_add_doc), F.data.startswith('skip_and_send'))
async def skip_and_send_message_users(callback: types.CallbackQuery,
                                      state: FSMContext, session: AsyncSession, bot: Bot):  # message: types.Message,

    # Получаем данные из предыдущего стейта:
    back_data_tmp = await state.get_data()
    #
    #     # Передадим на изменение в следущее сообщение:
    edit_chat_id_final = back_data_tmp['edit_chat_id']
    edit_message_id_final = back_data_tmp['edit_message_id']

    # удаляем их для корректной передачи на запись в бд.
    del back_data_tmp['edit_chat_id']
    # edit_chat_id_new = data_write_to_base.get('edit_chat_id')
    del back_data_tmp['edit_message_id']

    await state.clear()

    # обновляем изменения
    await state.update_data(back_data_tmp)
    # Значение для колонки в обращениях, что нет документов (data_request_message['doc_status'] = False)
    await state.update_data(doc_status=False)

    # Запрос в БД на добавление обращения:
    data_request_message_to_send = await state.get_data()

    # Вытаскиваем данные из базы после записи (обновленные всю строку полностью) и отправляем ее в другие стейты:
    # Забираю только айди что бы идентифицировать задачу:
    refresh_request_message_id = await add_request_message(session, data_request_message_to_send)  #
    print(f'Айди обращения = {refresh_request_message_id}')

    # ---------------------------------- рассылка поступившей задачи
    # Получаем tg_id написавшего юзера:
    # notification_employees_id = data_request_message_to_send['tg_id']

    bot = callback.bot

    # Получаем список id работников на рассылку:
    # mailing_list = generator_mailing_list(data_request_message_to_send)
    # mailing_list = [141407179, 143453792,  163904370,  1206297168, 1372644288]
    mailing_list = [500520383, 1372644288]

    for send in mailing_list:
        # Если пользователь удалил бота, мы не можем ему отправить уведомление о задаче, \
        # пропускаем ошибку, цикл продолжается:

        notification_employees_id = send
        try:
            notification_id = await bot.send_message(
                chat_id=send,
                text=f'Поступило новое обращение: {data_request_message_to_send['request_message']}'
                , reply_markup=get_callback_btns(
                    btns={'📨 ЗАБРАТЬ ЗАЯВКУ': 'pick_up_request',
                          '📂 ДЕЛЕГИРОВАТЬ ЗАЯВКУ': 'delegate_request'},  # передать часть работы.
                    sizes=(1, 1))
            )

            # Получаем ID отправленного сообщения
            id_notification = notification_id.message_id
            print(f'ID отправленного сообщения: {id_notification}')

            # Инсертим данные в таблицу HistoryDistributionRequests:
            await add_row_in_history_distribution(
                notification_employees_id, id_notification, refresh_request_message_id, session)


        # Пропускаем текущую итерацию и продолжаем со следующей
        except TelegramBadRequest as e:
            print(f"Ошибка при отправке сообщения для chat_id {send}: {e}")

            # сохрантять чат айди, кому не отправили
            await add_row_sending_error(notification_employees_id, refresh_request_message_id, session)

            # Отправляем админу айди и другие (возможно полные) данные по юзеру, которому не доставлено оповещение.
            # get_admin = asdfg # todo сделать выборку админов (в чат или группу? в группу проще, \
            # # todo если не в группу, то сделать цикл
            #
            # await bot.send_message(chat_id=get_admin,
            #     text=f'Уведомление по обращению №_{refresh_request_message_id},'
            #          f' tg_id: {data_request_message_to_send['tg_id']}, '
            #          f'не было доставлено работнику: {notification_employees_id}')










    # ------------ работало, не нужно в связи с выявленными особенностями убрали
    # Апдейтим id в базу данных:
    # await update_notification_id(refresh_request_message_id, id_notification, session)
    # ------------ работало, не нужно в связи с выявленными особенностями

    # ------------------------- рассылка поступившей задачи

    # Очистка состояния пользователя:
    await state.clear()  #

    # копируем данные в сотсояние
    # await state.set_state(AddRequests.transit_request_message_id)
    # # Передаем данные в следующее состояние по сценарию:
    # await state.update_data(refresh_data)

    message_final = await bot.edit_message_text(
        chat_id=edit_chat_id_final,
        message_id=edit_message_id_final,
        text=f'<b>Обращение зарегистрировано, ожидайте ответа!</b> \n'
             f'Как только обращение будет взято в работу, я направлю уведомление.'
             f'\n'
        # f'<em><b>Ваше обращение:</b> {new_data.get("request_message")}</em>'
    )

    # -------------------------- Удаляем введенное сообщение выше 👆:
    # Очищаем данные, тк, на прямую удалить сообщение выше не получится - выходит ошибка
    # (скорее всего из-за удаления сообщения выше)

    await asyncio.sleep(2)

    # await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    # Через 2 секунды возвращаем исходное главное меню.

    await message_final.edit_text(f'Терминал:',
                                  reply_markup=get_callback_btns(
                                      btns={'СОЗДАТЬ ЗАЯВКУ': 'go_create_request',
                                            'ПЕРЕЙТИ В ЧАТ': 'go_chat_user',
                                            'ИЗМЕНИТЬ ЗАЯВКУ': 'go_chenge_request',
                                            'УДАЛИТЬ ЗАЯВКУ': 'go_delete_request',
                                            'ЗАПРОСИТЬ СТАТУС ЗАЯВКИ': 'go_status_request'
                                            },
                                      sizes=(2, 2, 1)))


#  ------------------------- работает +


# ----------------------------------- тестовый вариант  - не работал

# # Пользователь нажимает ОТПРАВИТЬ ЗАЯВКУ. #  ------------------------- тест
# @retail_router.callback_query(StateFilter(AddRequests.send_message_or_add_doc), F.data.startswith('skip_and_send'))
# async def skip_and_send_message_users_(callback: types.CallbackQuery,
#                                       state: FSMContext, session: AsyncSession): # , bot: Bot
#     # await callback.answer()
#
#     # Получаем данные из предыдущего стейта:
#     # back_data_tmp = await state.get_data()
#
#
#     message_final =  await callback.message.edit_text(
#                                     text=f'<b>Обращение зарегистрировано, ожидайте ответа!</b> \n'
#                                      f'Как только обращение будет взято в работу, я направлю уведомление.'
#                                      f'\n'
#                                      # f'<em><b>Ваше обращение:</b> {new_data.get("request_message")}</em>'
#                                      )
#
#
#     # Очистка состояния пользователя:
#     # await state.clear()
#     await state.set_state(None)
#
#
#
#     await asyncio.sleep(3)
#     await message_final.edit_text(f'Терминал:',
#                                      reply_markup=get_callback_btns(
#                                          btns={'СОЗДАТЬ ЗАЯВКУ': 'go_create_request',
#                                                'ПЕРЕЙТИ В ЧАТ': 'go_chat_user',
#                                                'ИЗМЕНИТЬ ЗАЯВКУ': 'go_chenge_request',
#                                                'УДАЛИТЬ ЗАЯВКУ': 'go_delete_request',
#                                                'ЗАПРОСИТЬ СТАТУС ЗАЯВКИ': 'go_status_request'
#                                                },
#                                          sizes=(2, 2, 1)))
#
# ----------------------------------- тестовый вариант  - не работал


# Если пользователь отправил любой (условно) тип документа:
# @dp.message_handler(StateFilter(AddRequests.documents),
#                     content_types=[ContentType.DOCUMENT,
#                                    ContentType.PHOTO,
#                                    ContentType.VIDEO,
#                                    ContentType.AUDIO,
#                                    ContentType.VOICE,
#                                    ContentType.VIDEO_NOTE,
#                                    ContentType.MEDIA_GROUP
#                                    ])
# async def get_request_all_doc_users(message: types.Message, state: FSMContext, session: AsyncSession):  # , bot: Bot

# """
# Принимаем все виды документов от пользователя (сохраняем каждый под собственным айди в отделной таблице
# (под документы есть 2 таблицы для заявок и для обсуждения заявок)
# """

# Забираем обновленные данные из предыдущего состоячния:
# message_text_data = await state.get_data()

# if message.document:
#     file_id = message.document.file_id
#     file_name = message.document.file_name
#     file_type = 'document'
# elif message.photo:
#     file_id = message.photo[-1].file_id  # Получить наибольшее по размеру фото
#     file_name = f"{file_id}.jpg"
#     file_type = 'photo'
# elif message.video:
#     file_id = message.video.file_id
#     file_name = message.video.file_name or f"{file_id}.mp4"
#     file_type = 'video'
# elif message.audio:
#     file_id = message.audio.file_id
#     file_name = message.audio.file_name or f"{file_id}.mp3"
#     file_type = 'audio'
# elif message.voice:
#     file_id = message.voice.file_id
#     file_name = f"{file_id}.ogg"
#     file_type = 'voice'
# elif message.video_note:
#     file_id = message.video_note.file_id
#     file_name = f"{file_id}.mp4"
#     file_type = 'video_note'
# else:
#     return  # Неподдерживаемый тип сообщения
#
# # Получить информацию о файле
# file_info = await bot.get_file(file_id)
# file_path = file_info.file_path
#
# # Скачать файл как бинарные данные
# file_content = await download_file(file_path)
#
# if file_content:
#     # Сохранить информацию о документе в базе данных
#     db = SessionLocal()
#     new_document = Document(file_id=file_id, file_name=file_name, file_content=file_content)
#     db.add(new_document)
#     db.commit()
#     db.refresh(new_document)
#     db.close()

#     переделать функцию, убедиться, что возвращается бинарнрый тип данных и сохраняется в базы данных.

# Запрос в БД на добавление обращения:
# refresh_data = await add_request_message(session, new_data)  # todo вытаскиваем обновленные данные
# print(f'refresh_data = {refresh_data}')
# ================================== тест - неудался, потом удалить.
# логика:
# очищаем состояние
# встаем в новое состояние (ловим это состояние в оаит и в других ветках). что бы не мешать с состоянием выше.
# забираем данные,
# очищаем состояние
# await state.clear()
# await state.set_state(AddRequests.transit_request_message)

# await state.update_data(new_data)
# print(f'Пердача данных из ритейл : {new_data}')
#     # Рассылка задач на исполнителей:
# ================================== тест - неудался, потом удалить.

# # Очистка состояния пользователя:
# await state.clear()  # - работало.
#
# sent_message = await message.answer(f'<b>Обращение зарегистрировано, ожидайте ответа!</b> \n'
#                                     f'Как только обращение будет взято в работу, я направлю уведомление.'
#                                     f'\n'
#                                     f'<em><b>Ваше обращение:</b> {new_data.get("request_message")}</em>'
#                                     )
# # del new_data
#
# # -------------------------- Удаляем введенное сообщение выше 👆:
# # Очищаем данные, тк, на прямую удалить сообщение выше не получится - выходит ошибка
# # (скорее всего из-за удаления сообщения выше)
#
# await asyncio.sleep(5)
#
# # await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
# # Через 2 секунды возвращаем исходное главное меню.
#
# await sent_message.edit_text(f'Терминал:',
#                              reply_markup=get_callback_btns(
#                                  btns={'СОЗДАТЬ ЗАЯВКУ': 'go_create_request',
#                                        'ПЕРЕЙТИ В ЧАТ': 'go_chat_user',
#                                        'ИЗМЕНИТЬ ЗАЯВКУ': 'go_chenge_request',
#                                        'УДАЛИТЬ ЗАЯВКУ': 'go_delete_request',
#                                        'ЗАПРОСИТЬ СТАТУС ЗАЯВКИ': 'go_status_request'
#                                        },
#                                  sizes=(2, 2, 1)))

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

# =----------
# Вытаскиваем идентификеатор сообщения (до того, как обнулим состояние):
# chat_id = callback.message.chat.id   # chat_id_before_entering_text
# message_id = callback.message.message_id  # message_id_before_entering_text

#     # ---------------------------- удаляем инлайновые кнопки (при вводе сообщения):
#     # Формируем полученные данные из другого стейта (chat_id, message_id):
#     data = await state.get_data()
#     chat_id = data['chat_id']
#     message_id = data['message_id']
#
#     # Удаляем конкретное сообщение. +- (может быть ошибка, если до этого бот был выключен и история не очищена \
#     # (протестить еще раз))
#     await bot.delete_message(chat_id=chat_id, message_id=message_id) # todo: надо будет исправить \
#     # todo: удаление на переименование иначе будут лезть ошибки у пользователя
#
#     await message.delete() # Удаляет введенное сообщение пользователя (для чистоты чата) +
