"""
Режим сессии для ОАИТ
"""

# -------------------------------- Стандартные модули
# -------------------------------- Сторонние библиотеки
from aiogram import F, Router
from aiogram.filters import StateFilter
# -------------------------------- Локальные модули
from filters.chats_filters import *

# from aiogram.utils.formatting import as_list, as_marked_section, Bold, Italic

# from menu import keyboard_menu  # Кнопки меню - клавиатура внизу

# from OLD.events import *
from handlers.all_states import *

# ----------------------------------------------------------------------------------------------------------------------
# Назначаем роутер для всех типов чартов:
oait_router = Router()

# фильтрует (пропускает) только личные сообщения и только определенных пользователей:
oait_router.message.filter(ChatTypeFilter(['private']), TypeSessionFilter(allowed_types=['oait']))
oait_router.edited_message.filter(ChatTypeFilter(['private']), TypeSessionFilter(allowed_types=['oait']))


# ----------------------------------------------------------------------------------------------------------------------
# Приветствие для ОАИТ
# @oait_router.message(StateFilter(None), F.text == 'next')
# async def hello_after_on_next(message: types.Message):
#     user = message.from_user.first_name  # Имя пользователя
#     await message.answer((hello_users_oait.format(user)),
#                          parse_mode='HTML')



@oait_router.callback_query(StateFilter(None), F.data.startswith('pick_up_request'))
async def pick_up_request(callback: types.CallbackQuery,
                                      state: FSMContext, session: AsyncSession):  #message: types.Message, , bot: Bot

    await callback.answer()

    # Запрос в БД на добавление обращения:
    # get_back_data_transit = await state.get_data()
    # print(f'refresh_data = {get_back_data_transit}')

    # Вытаскиваем message_id отправлденного уведомления:
    get_notification_id = callback.message.message_id
    print(f'get_notification_id = {get_notification_id}')

    # Сравниваем в базе значение  notification_id при нажатии кнопкми (идентифицируеми кто нажал)
    await check_notification_id_in_history_distribution(get_notification_id)


    # Сначала меняем у всех сообщение, что бы остальные не успели нажать кнопку (или придумать механизм для такого)
    # потом апдейтим ответственного в бд.

    # Алгоритм:
    #





# ----------------------------------- тестовый вариант  - не работал
#
# @oait_router.callback_query(StateFilter(AddRequests.send_message_or_add_doc), F.data.startswith('skip_and_send'))
# async def skip_and_send_message_users(callback: types.CallbackQuery,
#                                       state: FSMContext, session: AsyncSession, bot: Bot):  #message: types.Message,
#     await callback.answer()
#     print(f'refresh_data = ')
#
#     # Получаем данные из предыдущего стейта:
#     back_data_tmp = await state.get_data()
#
#
#
#     # Передадим на изменение в следущее сообщение:
#     # edit_chat_id_final = back_data_tmp['edit_chat_id']
#     # edit_message_id_final = back_data_tmp['edit_message_id']
#
#     # удаляем их для корректной передачи на запись в бд.
#     del back_data_tmp['edit_chat_id']
#     # edit_chat_id_new = data_write_to_base.get('edit_chat_id')
#     del back_data_tmp['edit_message_id']
#
#
#
#     await state.clear()
#
#     await state.set_state(AddRequests.transit_request_message_id)
#
#     # обновляем изменения
#     await state.update_data(back_data_tmp)
#     # Значение для колонки в обращениях, что нет документов (data_request_message['doc_status'] = False)
#     await state.update_data(doc_status=False)
#
#     # Запрос в БД на добавление обращения:
#     data_request_message_to_send = await state.get_data()
#
#     # Вытаскиваем данные из базы после записи (обновленные всю строку полностью) и отправляем ее в другие стейты:
#     # Забираю только айди что бы идентифицировать задачу:
#     refresh_data = await add_request_message(session, data_request_message_to_send)
#     print(f'refresh_data = {refresh_data}')
#
#     await state.update_data(requests_ia = refresh_data)
#     back_data_transit = await state.get_data()
#
#
#     bot = callback.bot
#     # bot = message.bot
#     await bot.send_message(chat_id=826087669,
#                            text=f'Новая задача, id: {back_data_transit}' #  ЗАМЕНИТЬ НА refresh_data
#                            , reply_markup=get_callback_btns(
#             btns={'📨 ЗАБРАТЬ ЗАЯВКУ': 'pick_up_request',
#                   '📂 ПЕРЕДАТЬ ЗАЯВКУ': 'transfer_request'},
#             sizes=(1, 1))
#                            )
#
#     await state.clear()
#     await state.set_state(AddRequests.take_request_message)
#     await state.update_data(back_data_transit)

# ----------------------------------- тестовый вариант  - не работал




# ------------------------------  тест - неудался, потом удалить
# @oait_router.message(StateFilter(AddRequests.request_message), F.text) # , F.data - НЕ РАБОТАЕТ F.text - РАБОТАЕТ + без F.text
# # Сообщение приходит
# async def send_request_text_for_users(message: types.Message, state: FSMContext, session): # callback_query: types.CallbackQuery
#
#         transit_message_data = await state.get_data()
#         print(f'Пришли данные в оаит: {transit_message_data}')
#
#         transit_message = transit_message_data.get('request_message')
#
        # bot = callback_query.bot
#         bot = message.bot
#         await bot.send_message(chat_id=826087669, text=f'Новая запись в Requests: {transit_message_data}')
#         print(f'Новая запись в Requests: {transit_message_data}')



# ---------------------------
#  if target_requests == 0:
#         ...
#     else:

#
# async def get_event(): 0
#
#     event = await after_insert_requests()
#     message_text = f'Новая запись в Requests: {event}'
#
#     await message.answer(message_text)

# ------------ работает но не вариант
# # @oait_router.message() # StateFilter(StartUser.check_next), F.data.startswith('go_next')
# async def send_request_text_for_users(callback_query: types.CallbackQuery, state: FSMContext, session, target_requests):
#         sdgsd = target_requests.request_message
#         bot = callback_query.bot
#         await bot.send_message(chat_id=0, text=f'Новая запись в Requests: {sdgsd}')