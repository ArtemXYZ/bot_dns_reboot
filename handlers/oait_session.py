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

from menu.inline_menu import *  # Кнопки встроенного меню - для сообщений
from working_databases.orm_query_builder import *
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
                          state: FSMContext, session: AsyncSession, bot: Bot):  # message: types.Message,

    await callback.answer()

    # Запрос в БД на добавление обращения:
    # get_back_data_transit = await state.get_data()
    # print(f'refresh_data = {get_back_data_transit}')

    bot = callback.bot  # только келбек, обычная передача экземпляра бота - просто отправит новое сообщение.

    # -------------------------------------- Идентифицируем пользователя нажавшего кнопку
    # Вытаскиваем message_id отправлденного уведомления:
    get_notification_id = callback.message.message_id
    # print(f'get_notification_id = {get_notification_id}')
    get_user_id_callback = callback.from_user.id

    callback_employee_name = await get_full_name_employee(get_user_id_callback, session)

    # Сравниваем в базе значение  notification_id при нажатии кнопками (идентифицируем кто нажал), узнаем айди задачи
    request_id = await check_notification_id_in_history_distribution(get_notification_id, session)
    # Вернет один результат или ничего. ! Тут нужна проверка на пустоту (исключение ошибки, однако, подразумеваетсмя, \
    # что таких событий быть не должно по сценарию для упрощения кода.
    # --------------------------------------
    # -------------------------------------- Идентифицируем заявителя
    tg_id = await get_tg_id_in_requests_history(request_id, session)  # достать айди заказчика

    # Проверка есть ли оповещение для заявителя (либо айди либо нон)
    check_notification = await check_notification_for_tg_id(request_id, session)
    print(f'есть ли оповещение для заявителя (либо айди либо нон) {check_notification}.')

    # Получаем список id работников кому было разослано уведомление: get_notification_id_and_employees_id_tuples
    id_tuples = await get_notification_id_and_employees_id_tuples(request_id, session)

    # Узнаем количество работников на эту задачу (мы единственный исполнитель или нет? Все со статусом  in_work):
    have_personal_status_in_working = await get_all_personal_status_in_working(request_id, session)  # работает

    # Вытаскиваем имена всех (по айди) остальных ответственных со статусом в работе:
    employees_names = await get_employees_names(have_personal_status_in_working, session)

    # ================================================= 1 ==============================================================
    # 1. Есть ли еще кто то со статусом в работе о этой задаче ? Если никого нет и я нажал первый:
    if not have_personal_status_in_working:  # списки и другие коллекции оцениваются как True, если они не пусты +

        # Перебираем всех назначенных по этой задаче:
        for row in id_tuples:

            notification_employees_id, notification_id = row  # for_chat_id, message_id

            # Если tg_id из рассылки равен tg_id юзера нажимающего кнопку, то изменяем сообщения у остальных.
            if notification_employees_id == get_user_id_callback:  # for_chat_id

                # Апдейтим ответственного в бд (HistoryDistributionRequests) + апдейт статуса в работе ('in_work').
                await update_personal_status(request_id, get_user_id_callback, session)

                # todo текст самого сообщения только сокращенный.

                # # ----------------------- Отправить уведомление тому, кто нажал кнопку.
                await bot.edit_message_text(
                    chat_id=get_user_id_callback, message_id=notification_id,
                    text=f'Обращение принято в работу! Вы назначены ответственным по данной задаче (№_{request_id}).',
                    reply_markup=get_callback_btns(btns={'✅ ЗАВЕРШИТЬ ПОДЗАДАЧУ': '1232',
                                                         '❎ ОТМЕНИТЬ ПОДЗАДАЧУ': '5373'
                                                         }, sizes=(1, 1))
                )


                # ----------------------- Отправить уведомление заказчику (отправителю обращения):

                # Проверка есть ли оповещение для заявителя (либо = айди либо = нон):
                if check_notification is None:

                    # Достать имя ответственного по этой задаче
                    # employee_name = await get_full_name_employee(get_user_id_callback, session)

                    # Если сообщение не доставлялось, -  отправляем новое:
                    send_notification_in_work = await bot.send_message(
                        chat_id=tg_id,
                        text=f'Ваше обращение №_{request_id} принято в работу, исполнитель {callback_employee_name}.',
                        reply_markup=get_callback_btns(
                            btns={
                                '🗣 ОТКРЫТЬ ДИСКУССИЮ': 'open_discussion',
                                '❎ ОТМЕНИТЬ ЗАЯВКУ': 'cancel_request'},
                            sizes=(1, 1))
                    )
                    # -------------------------------------- Запоминае идентиф. уведомления заказчика
                    # идентификатор сообщения заявителя:
                    message_id_applicant = send_notification_in_work.message_id
                    #  Апдейтим айди отправленного сообщения в таблицу обращений Requests (поле: id_notification_for_tg_id)
                    await update_message_id_applicant(request_id, message_id_applicant, session)

                else:
                    # Если сообщение уже доставлялось, изменяем его:
                    await bot.edit_message_text(
                        chat_id=tg_id, message_id=check_notification,
                        text=f'Ваше обращение №_{request_id} принято в работу, исполнитель {callback_employee_name}.',
                        reply_markup=get_callback_btns(
                            btns={
                                '🗣 ОТКРЫТЬ ДИСКУССИЮ': 'open_discussion',
                                '❎ ОТМЕНИТЬ ЗАЯВКУ': 'cancel_request'},
                            sizes=(1, 1))
                    )


            # Если tg_id из рассылки не равен tg_id юзера нажимающего кнопку, то изменяем его сообщение \
            # (у всех остальных).
            else:

                # присоединиться, ЕСЛИ НАДО.
                await bot.edit_message_text(
                    chat_id=notification_employees_id, message_id=notification_id,
                    text=f'Ответственным по задаче №_{request_id} назначен {callback_employee_name}',
                    reply_markup=get_callback_btns(btns={'🧩 ЗАБРАТЬ ПОДЗАДАЧУ': 'pick_up_request'}, sizes=(1, ))
                )


    # ================================================= 2 ==============================================================
    # 2. Есть еще кто то со статусом в работе по этой задаче.  я не первый нажал, уже кто то работает по ней:
    else:

        # Перебираем всех назначенных по этой задаче:
        for row in id_tuples:
            notification_employees_id, notification_id = row

            # -------------------------------------- Выбираем нажавшего
            # Если tg_id из рассылки равен tg_id юзера нажимающего кнопку, то изменяем сообщения у остальных.
            if notification_employees_id == get_user_id_callback:
                # Апдейтим ответственного в бд (HistoryDistributionRequests) + апдейт статуса в работе ('in_work').
                await update_personal_status(request_id, get_user_id_callback, session)

                # Отправляем уведомление для нажавшего кнопку:
                await bot.edit_message_text(
                    chat_id=get_user_id_callback, message_id=notification_id,
                    text=f'Обращение принято в работу! Вы назначены ответственным по данной задаче (№_{request_id}),'
                         f' совместно с {employees_names}.',
                    reply_markup=get_callback_btns(btns={'✅ ЗАВЕРШИТЬ ПОДЗАДАЧУ': '1232',
                                                         '❎ ОТМЕНИТЬ УЧАСТИЕ': '5373'
                                                         }, sizes=(1, 1))
                )

                    # !!! Вся задача будет автоматически завершена. после ттого ,как последний завершит подзадачу.


                # ----------------------- Отправить (исправить) уведомление заказчику (отправителю обращения):
                # проверка на наличие уже отправленного сообщения заказчику (либо айди либо нон):
                # Упраздняем проверку, т.к. второе условие, когда уже кто то есть ответственный, \
                # подразумивает отправку уведоления заказчику. ТАк что достаем его из базы  и редактируем:

                # Добавляем имя нажавшего к остальным, кто работает по задаче.
                # Если Пусто
                if employees_names is None: #
                    all_employees_in_working = callback_employee_name
                # Если множество сотрудников (в employees_names есть сотрудники)
                else:
                    all_employees_in_working = f'{employees_names}, {callback_employee_name}'  # -> "Иванов Иван, ..., "


                # Если сообщение уже доставлялось, изменяем его:
                await bot.edit_message_text(
                    chat_id=tg_id, message_id=check_notification,
                    text=f'Ваше обращение №_{request_id} принято в работу, исполнители: {all_employees_in_working}.',
                    reply_markup=get_callback_btns(
                        btns={
                            '🗣 ОТКРЫТЬ ДИСКУССИЮ': 'open_discussion',
                            '❎ ОТМЕНИТЬ ЗАЯВКУ': 'cancel_request'},
                        sizes=(1, 1))
                )

        # изменяем его сообщение у всех остальных:
        else:

            await bot.edit_message_text(
                chat_id=notification_employees_id, message_id=notification_id,
                text=f'Ответственными по задаче №_{request_id} назначены: {all_employees_in_working}',
                reply_markup=get_callback_btns(btns={'🧩 ЗАБРАТЬ ПОДЗАДАЧУ': 'pick_up_request'}, sizes=(1,))
            )


# todo обновление статуса в рекуест если все завершили, то завершено, если 1 взял то в работе,
#  если второй добавляется и есть в работе в реквест то ничего


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


# ----------------------------------- устарело  - работало
# @oait_router.callback_query(StateFilter(None), F.data.startswith('pick_up_request'))
# async def pick_up_request(callback: types.CallbackQuery,
#                           state: FSMContext, session: AsyncSession, bot: Bot):  # message: types.Message,
#
#     await callback.answer()
#
#     # Запрос в БД на добавление обращения:
#     # get_back_data_transit = await state.get_data()
#     # print(f'refresh_data = {get_back_data_transit}')
#
#     # Вытаскиваем message_id отправлденного уведомления:
#     get_notification_id = callback.message.message_id
#     # print(f'get_notification_id = {get_notification_id}')
#     get_user_id_callback = callback.from_user.id
#
#     # Сравниваем в базе значение  notification_id при нажатии кнопками (идентифицируем кто нажал), узнаем айди задачи
#     request_id = await check_notification_id_in_history_distribution(get_notification_id, session)
#     # Вернет один результат или ничего.
#
#     if request_id is None:
#         # todo  !!Доработать
#         print(f'Ошибка поиска уведомления о поступившем обращении) {request_id}')
#
#     else:
#
#         bot = callback.bot # только келбек, обычная передача экземпляра бота - просто отправит новое сообщение.
#
#         # Получаем список id работников кому было разослано уведомление: get_notification_id_and_employees_id_tuples
#         id_tuples = await get_notification_id_and_employees_id_tuples(request_id, session)
#
#         # Перебираем всех и в зависимости от логики ...
#         for row in id_tuples:
#
#             notification_employees_id, notification_id = row  # for_chat_id, message_id
#
#             # Если tg_id из рассылки равен tg_id юзера нажимающего кнопку, то изменяем сообщения у остальных.
#             if  notification_employees_id == get_user_id_callback:  # for_chat_id
#
#                 # Апдейтим ответственного в бд (Responsible) + апдейт статуса в работе ('in_work').
#                 await update_responsible_person_id(request_id, get_user_id_callback, session)
#
#                 # await callback.message.edit_text(
#                 await bot.edit_message_text(chat_id=get_user_id_callback, message_id=notification_id,
#                     text=f'Обращение принято в работу! Вы назначены ответственным по данной задаче (№_{request_id}).')
#
#
#
#                 #  Отправить уведомление заказчику (отправителю обращения):
#                 tg_id = await get_tg_id_in_requests_history(request_id, session)  # достать айди заказчика
#
#                 send_notification_in_work = await bot.send_message(chat_id=tg_id,
#                     text=f'Ваше обращение №_{request_id} принято в работу, исполнитель {employee_name}.',
#                     reply_markup=get_callback_btns(
#                         btns={'🗣 ОТКРЫТЬ ДИСКУССИЮ': 'open_discussion',
#                               '❎ ОТМЕНИТЬ ЗАЯВКУ': 'cancel_request'},
#                         sizes=(1, 1))
#                 )
#
#                 # Исполнители (заменяем)
#             #     может задержку при отправке обратки , как все прожмут.
#
#
#             # Если tg_id из рассылки не равен tg_id юзера нажимающего кнопку, то изменяем его сообщение.
#             else:
#
#                 employee_name = await get_full_name_employee(get_user_id_callback, session)
#
#                 await bot.edit_message_text(
#                     chat_id=notification_employees_id, message_id=notification_id,
#                     text=f'Ответственным по задаче №_{request_id} назначен {employee_name}')
