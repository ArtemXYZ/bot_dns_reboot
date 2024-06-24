"""
Режим сессии для ОАИТ
"""

# -------------------------------- Стандартные модули
# -------------------------------- Сторонние библиотеки
from aiogram import F, Router
from aiogram.filters import StateFilter

from aiogram.exceptions import TelegramBadRequest

# -------------------------------- Локальные модули
from filters.chats_filters import *

# from aiogram.utils.formatting import as_list, as_marked_section, Bold, Italic

# from menu import keyboard_menu  # Кнопки меню - клавиатура внизу

from menu.inline_menu import *  # Кнопки встроенного меню - для сообщений
from working_databases.orm_query_builder import *
from handlers.all_states import *
from handlers.data_preparation import *

from handlers.bot_decorators import *

# ----------------------------------------------------------------------------------------------------------------------
# Назначаем роутер для всех типов чартов:
oait_router = Router()

# фильтрует (пропускает) только личные сообщения и только определенных пользователей:
oait_router.message.filter(ChatTypeFilter(['private']), TypeSessionFilter(allowed_types=['oait']))
oait_router.edited_message.filter(ChatTypeFilter(['private']), TypeSessionFilter(allowed_types=['oait']))

lock = asyncio.Lock()


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
    #  Асинхронная блокировка (поможет предотвратить гонку условий при одновременном доступе нескольких пользователей):
    async with lock:

        #  Состояния каждого пользователя отслеживаются отдельно, что предотвращает влияние одного пользователя
        #  на другого
        await state.set_state(AddRequests.pick_up_request)

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

        # Сравниваем в базе значение  notification_id при нажатии кнопками (идентифицируем кто нажал),
        # узнаем айди задачи
        request_id = await check_notification_id_in_history_distribution(get_notification_id, session)
        # Вернет один результат или ничего. ! Тут нужна проверка на пустоту (исключение ошибки, однако,
        # подразумеваетсмя,  что таких событий быть не должно по сценарию для упрощения кода.
        # --------------------------------------
        # ------------------------------------  Получаем екст сообщения
        request_message = await get_request_message(request_id, session)

        # -------------------------------------- Идентифицируем заявителя
        tg_id = await get_tg_id_in_requests_history(request_id, session)  # достать айди заказчика

        # Проверка есть ли оповещение для заявителя (либо айди либо нон)
        check_notification = await check_notification_for_tg_id(request_id, session)
        # print(f'есть ли оповещение для заявителя (либо айди либо нон) {check_notification}.')

        # Получаем список id работников кому было разослано уведомление: get_notification_id_and_employees_id_tuples
        id_tuples = await get_notification_id_and_employees_id_tuples(request_id, session)

        # Узнаем количество работников на эту задачу (мы единственный исполнитель или нет? Все со статусом  in_work):
        have_personal_status_in_working = await get_all_personal_status_in_working(request_id, session)  # работает

        # ================================================= 1 ==========================================================
        # 1. Есть ли еще кто то со статусом в работе о этой задаче ? Если никого нет и я нажал первый:
        if not have_personal_status_in_working:  # списки и другие коллекции оцениваются как True, если они не пусты +
            # Если у вас пустой список, условие if not have_personal_status_in_working: будет истинным.

            # Перебираем всех назначенных по этой задаче:
            for row in id_tuples:

                notification_employees_id, notification_id = row  # for_chat_id, message_id

                # Если tg_id из рассылки равен tg_id юзера нажимающего кнопку, то изменяем сообщения у остальных.
                if notification_employees_id == get_user_id_callback:  # for_chat_id

                    # Апдейтим ответственного в бд (HistoryDistributionRequests) + апдейт статуса в работе ('in_work').
                    await update_personal_status(request_id, get_user_id_callback, 'in_work', session)

                    # Апдейтим статус в работе 'in_work' в бд (Requests)
                    # апдейтим только в этой ветке, т.к. в остальных подразумивается, \
                    # что уже есть записть 'in_work' в Requests
                    await update_requests_status(request_id, 'in_work', session)

                    #  ----------------------- Отправить уведомление тому, кто нажал кнопку.
                    # Здесь декоратор отправки сообщения не нужен.
                    await bot.edit_message_text(
                        chat_id=get_user_id_callback, message_id=notification_id,
                        text=f'Обращение принято в работу! Вы назначены ответственным '
                             f'по данной задаче (№_{request_id}).\n'
                             f'Текст обращения:\n'
                             f'{request_message}'  # todo текст самого сообщения только сокращенный ?
                        ,
                        reply_markup=get_callback_btns(btns={'🗣 ОТКРЫТЬ ДИСКУССИЮ': 'open_discussion',
                                                             '✅ ЗАВЕРШИТЬ ЗАДАЧУ': 'complete_subtask',
                                                             '❎ ОТМЕНИТЬ УЧАСТИЕ': 'abort_subtask'
                                                             }, sizes=(1, 1))
                    )

                    # ----------------------- Отправить уведомление заказчику (отправителю обращения):
                    # Проверка есть ли уже оповещение для заявителя (либо = айди либо = нон):
                    # "Смысл: Когда задача создана, всех причастных оповещает бот, но заказчика оповещает только,
                    # когда задачу возьмут в работу, по этому id_notification_for_tg_id может быть пустым ! "
                    if check_notification is None:

                        # Достать имя ответственного по этой задаче
                        # employee_name = await get_full_name_employee(get_user_id_callback, session)

                        # Если сообщение не доставлялось, -  отправляем новое:
                        send_notification_in_work = await bot.send_message(
                            chat_id=tg_id,
                            text=f'Ваше обращение №_{request_id} принято в работу,'
                                 f' исполнитель {callback_employee_name}.',
                            reply_markup=get_callback_btns(
                                btns={
                                    '🗣 ОТКРЫТЬ ДИСКУССИЮ': 'open_discussion',
                                    '❎ ОТМЕНИТЬ ЗАЯВКУ': 'cancel_request'},
                                sizes=(1, 1))
                        )
                        # -------------------------------------- Запоминае идентиф. уведомления заказчика
                        # идентификатор сообщения заявителя:
                        message_id_applicant = send_notification_in_work.message_id
                        #  Апдейтим айди отправленного сообщения в таблицу обращений Requests \
                        #  (поле: id_notification_for_tg_id)
                        await update_message_id_notification(request_id, message_id_applicant,
                                                             'update_request', session)

                    else:
                        # Если сообщение уже доставлялось, изменяем его:
                        reply_markup = get_callback_btns(btns={'🗣 ОТКРЫТЬ ДИСКУССИЮ': 'open_discussion',
                                                               '❎ ОТМЕНИТЬ ЗАЯВКУ': 'cancel_request'}, sizes=(1, 1))
                        text = (f'Ваше обращение №_{request_id} принято в работу,'
                                f' исполнитель {callback_employee_name}.')

                        # Отправка уведомления: сначала  edit_message_text, если удалено, то send_message,
                        # после апдейт айди нового уведомления
                        await decorator_edit_message(tg_id, check_notification, text, reply_markup,
                                                     request_id, bot, session, 'update_request')

                # Если tg_id из рассылки не равен tg_id юзера нажимающего кнопку, то изменяем его сообщение \
                # (у всех остальных).
                else:
                    # присоединиться, ЕСЛИ НАДО.
                    reply_markup = get_callback_btns(btns={'🧩 ЗАБРАТЬ ПОДЗАДАЧУ': 'pick_up_request'}, sizes=(1,))
                    text = (f'Ответственным по задаче №_{request_id} назначен {callback_employee_name}.\n'
                            f'Текст обращения:\n'
                            f'{request_message}')

                    # Отправка уведомления: сначала  edit_message_text, если удалено, то send_message,
                    # после апдейт айди нового уведомления
                    await decorator_edit_message(notification_employees_id, notification_id, text, reply_markup,
                                                 request_id, bot, session, 'update_distribution')


        # ================================================= 2 ==========================================================
        # 2. Есть еще кто то со статусом в работе по этой задаче.  я не первый нажал, уже кто то работает по ней:
        else:

            # Перебираем всех назначенных по этой задаче:
            for row in id_tuples:
                notification_employees_id, notification_id = row

                # -------------------------------------- Выбираем нажавшего
                # Если tg_id из рассылки равен tg_id юзера нажимающего кнопку, то изменяем сообщения у остальных.
                if notification_employees_id == get_user_id_callback:
                    # Апдейтим ответственного в бд (HistoryDistributionRequests) + апдейт статуса в работе ('in_work').
                    await update_personal_status(request_id, get_user_id_callback, 'in_work', session)  # 'cancel'

                    # Отправляем уведомление для нажавшего кнопку:
                    # ------------------------------------------------
                    # ! необходимо еще раз перепроверить сколько теперь ответственных, т.к произошел апдейт,
                    # а в переменных старые значения.
                    # Узнаем количество работников на эту задачу осле апдейта:
                    have_personal_status_in_working_for_if = await get_all_personal_status_in_working(
                        request_id, session)

                    # Вытаскиваем имена всех (по айди) остальных ответственных со статусом в работе
                    # без нажавшего кнопку:
                    employees_names_minus_get_user_id_callback_for_if = await get_employees_names(
                        have_personal_status_in_working_for_if, session, exception=get_user_id_callback)

                    # Всех нажавших кнопку:
                    all_employees_in_working_for_if = await get_employees_names(
                        have_personal_status_in_working_for_if, session)

                    # ------------------------------------------------ здесь декоратор изменения сообщений не нужен
                    await bot.edit_message_text(
                        chat_id=get_user_id_callback, message_id=notification_id,
                        text=f'Обращение принято в работу! Вы назначены ответственным по данной задаче '
                             f'(№_{request_id}),'
                             f' совместно с {employees_names_minus_get_user_id_callback_for_if}.\n'
                             f'Текст обращения:\n'
                             f'{request_message}',
                        reply_markup=get_callback_btns(btns={'🗣 ОТКРЫТЬ ДИСКУССИЮ': 'open_discussion',
                                                             '✅ ЗАВЕРШИТЬ ПОДЗАДАЧУ': 'complete_subtask',
                                                             '❎ ОТМЕНИТЬ УЧАСТИЕ': 'abort_subtask'
                                                             }, sizes=(1, 1))
                    )

                    # ----------------------- Отправить (исправить) уведомление заказчику (отправителю обращения):
                    # проверка на наличие уже отправленного сообщения заказчику (либо айди либо нон):
                    # Упраздняем проверку, т.к. второе условие, когда уже кто то есть ответственный, \
                    # подразумивает отправку уведоления заказчику. ТАк что достаем его из базы  и редактируем:
                    reply_markup = get_callback_btns(btns={'🗣 ОТКРЫТЬ ДИСКУССИЮ': 'open_discussion',
                                                           '❎ ОТМЕНИТЬ ЗАЯВКУ': 'cancel_request'},
                                                     sizes=(1, 1))
                    text = (f'Ваше обращение №_{request_id} принято в работу,'
                            f' соисполнители: {all_employees_in_working_for_if}.')

                    # Отправка уведомления: сначала  edit_message_text, если удалено, то send_message,
                    # после апдейт айди нового уведомления
                    await decorator_edit_message(tg_id, check_notification, text, reply_markup,
                                                 request_id, bot, session, 'update_request')

                # изменяем сообщение у всех остальных:
                else:

                    # Узнаем количество работников на эту задачу осле апдейта:
                    have_personal_status_in_working_for_else = await get_all_personal_status_in_working(
                        request_id, session)

                    # Вытаскиваем имена всех (по айди) остальных ответственных со статусом в работе без
                    # нажавшего кнопку:
                    employees_names_minus_get_user_id_callback_for_else = await get_employees_names(
                        have_personal_status_in_working_for_else, session, exception=get_user_id_callback)

                    # Всех нажавших кнопку:
                    all_employees_in_working_for_else = await get_employees_names(
                        have_personal_status_in_working_for_else, session)

                    employee_name_for_else = await get_full_name_employee(get_user_id_callback, session)

                    # -------------------  Проверка, является ли человек соучастником по задаче:
                    # роверяем  id сотрудника на наличие  статуса: в работе
                    check_personal_status = await check_personal_status_for_tg_id(
                        notification_employees_id, request_id, session)  # -> int or None

                    # Если сотрудник учавствует в задаче (статус 'in_work'):
                    if check_personal_status is not None:  # содержит значение

                        # Если id рассылки уже со статусом  в работе, то у него изменяем на другое сообщение

                        reply_markup = get_callback_btns(btns={'🗣 ОТКРЫТЬ ДИСКУССИЮ': 'open_discussion',
                                                               '✅ ЗАВЕРШИТЬ ПОДЗАДАЧУ': 'complete_subtask',
                                                               '❎ ОТМЕНИТЬ УЧАСТИЕ': 'abort_subtask'
                                                               }, sizes=(1, 1))
                        text = (f'По данной задаче (№_{request_id}), добавился новый участник:'
                                f' {employee_name_for_else},'
                                f' соисполнители: {employees_names_minus_get_user_id_callback_for_else}.\n'
                                f'Текст обращения:\n'
                                f'{request_message}')

                        # Отправка уведомления: сначала  edit_message_text, если удалено, то send_message,
                        # после апдейт айди нового уведомления
                        await decorator_edit_message(notification_employees_id, notification_id, text, reply_markup,
                                                     request_id, bot, session, 'update_distribution')



                    else:
                        # Тем, кто не соучастник по задаче (оповещенцам):
                        reply_markup = get_callback_btns(btns={'🧩 ЗАБРАТЬ ПОДЗАДАЧУ': 'pick_up_request'}, sizes=(1,))
                        text = (f'Ответственными по задаче №_{request_id} назначены: '
                                f'{all_employees_in_working_for_else}.\n'
                                f'Текст обращения:\n'
                                f'{request_message}')

                        # Отправка уведомления: сначала  edit_message_text, если удалено, то send_message,
                        # после апдейт айди нового уведомления
                        await decorator_edit_message(notification_employees_id, notification_id, text, reply_markup,
                                                     request_id, bot, session, 'update_distribution')

    await callback.answer()
    # Сбрасываем состояние
    await state.clear()


@oait_router.callback_query(StateFilter(None), F.data.startswith('cancel_request'))
async def cancel_request(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot):
    """
    Отменяем обращение заявителя (апдейт статуса  в таблицу обращений о завершении, рассылка уведомлений, что задача завершена
    (возможно добавить обработку событий, когда сообщение невозможно удалить (удалено, бот недоступен и тд.)
    Возможно нужна будет кнопка, что бы после удалять это сообщение (сначала изменяем, а после удаляем).
    """

    await state.set_state(AddRequests.cancel_request)
    bot = callback.bot

    # -------------------------------------- Идентифицируем пользователя нажавшего кнопку
    # Вытаскиваем message_id отправлденного уведомления :
    get_id_notification_for_tg_id = callback.message.message_id
    get_user_id_callback = callback.from_user.id
    callback_employee_name = await get_full_name_employee(get_user_id_callback, session)

    # Сравниваем в базе значение  notification_id при нажатии кнопками (идентифицируем кто нажал),
    # узнаем айди задачи

    request_id = await get_id_inrequests_by_notification(get_id_notification_for_tg_id, session)
    # Вернет один результат или ничего. ! Тут нужна проверка на пустоту (исключение ошибки, однако,
    # подразумеваетсмя,  что таких событий быть не должно по сценарию для упрощения кода.
    # --------------------------------------
    # ------------------------------------  Получаем екст сообщения
    request_message = await get_request_message(request_id, session)
    # ======================================================================================================

    # 1. ================================== Апдейтим статус заявки на 'cancel' в (Requests):
    await update_requests_status(request_id, 'cancel', session)

    # 2. ================================== Оповещаем остальных участников об отмене задачи:
    #  Находим все оповещения,которые были отправлены по данному обращению и изменяем их
    # Получаем список id работников кому было разослано уведомление (кроме тех, что с ошибкой отправки):
    id_tuples = await get_notification_id_and_employees_id_tuples(request_id, session)

    # Перебираем всех назначенных по этой задаче:
    for row in id_tuples:
        notification_employees_id, notification_id = row
        # print(f"notification_employees_id: {notification_employees_id} notification_id: {notification_id} ")

        # 3. Апдейтим индивидуальный статус на 'cancel' в (HistoryDistributionRequests):
        await update_personal_status(request_id, notification_employees_id, 'cancel', session)

        # --------------------------------- Отправляем остальным
        reply_markup = get_callback_btns(btns={'🗑 ОК, УДАЛИТЬ БАННЕР': 'delete_banner'}, sizes=(1,))
        text = (f'Обращение (№_{request_id}) отменено, инициатор: {callback_employee_name}.\n'
                f'Текст обращения:\n'
                f'{request_message}')

        # Отправка уведомления: сначала  edit_message_text, если удалено, то send_message,
        # после апдейт айди нового уведомления
        await decorator_edit_message(notification_employees_id, notification_id, text, reply_markup,
                                     request_id, bot, session)  # апдейт update_request не нужен (уже есть выше),  \
        # по этому не указываем в аргументах

    # --------------------------------- Отправляем себе:
    # try:  исключения не должно наступить, тк пользователь нажал кнопку, что уже означает, что в этот момент
    # сообщение  существует
    banner = await bot.edit_message_text(
        chat_id=get_user_id_callback, message_id=get_id_notification_for_tg_id,
        text=f'Ваше обращение (№_{request_id}) успешно отменено!\n'
             f'Текст обращения:\n'
             f'{request_message}'
        # ,
        # reply_markup=get_callback_btns(btns={'🗑 ОК, УДАЛИТЬ БАННЕР': '1232'}, sizes=(1,))
    )

    await asyncio.sleep(3)
    await banner.delete()

    # except TelegramBadRequest as e:
    #     if "message to delete not found" in str(e):
    #         print(f"Оповещение по обращению  №_{request_id} для пользователя {callback_employee_name} не удалось "
    #               f"удалить, так как оно уже не существует (удалено).")
    # -------------------------------

    await callback.answer()
    # Сбрасываем состояние
    await state.clear()


@oait_router.callback_query(StateFilter(None), F.data.startswith('delete_banner'))
async def delete_banner(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot):
    """
    Удаляем баннер об отмене обращения заявителя (сначала изменяем, а после удаляем - ТГ АПИ).
    """

    await state.set_state(AddRequests.delete_banner)
    bot = callback.bot

    # Вытаскиваем user_id и message_id отправлденного уведомления
    user_id_callback = callback.from_user.id
    notification_id = callback.message.message_id

    del_banner = await bot.edit_message_text(
        chat_id=user_id_callback, message_id=notification_id,
        text=f'Баннер удален')

    await del_banner.delete()

    await callback.answer()
    # Сбрасываем состояние
    await state.clear()


@oait_router.callback_query(StateFilter(None), F.data.startswith('complete_subtask'))
async def complete_subtask(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot):
    """
        Заввершаем подзадачу:
        (апдейт статуса в персонального ответственного, изменение баннера  у других участников оповещения).

        Вся задача будет автоматически завершена. после ттого, как последний завершит подзадачу.
        (смотрим, последний ли нажавший кнопку по созадаче? Если да, то апдейт статуса в таблице AddRequests на
        complete
    """

    #  Асинхронная блокировка (поможет предотвратить гонку условий при одновременном доступе нескольких пользователей):
    async with (lock):

        await state.set_state(AddRequests.complete_subtask)
        bot = callback.bot

        # ------------------------------------ Вытаскиваем user_id и message_id отправлденного уведомления
        user_id_callback = callback.from_user.id
        callback_notification_id = callback.message.message_id
        callback_employee_name = await get_full_name_employee(user_id_callback, session)

        # ------------------------------------ Получаем номер задачи:
        request_id = await check_notification_id_in_history_distribution(callback_notification_id, session)
        # ------------------------------------  Получаем текст сообщения
        request_message = await get_request_message(request_id, session)

        # -------------------------------------- Идентифицируем заявителя
        tg_id = await get_tg_id_in_requests_history(request_id, session)  # достать айди заказчика

        # Проверка есть ли оповещение для заявителя (либо айди либо нон) - не особо нужна в этом обработчике,  \
        # т.к  у  заказчика уже есть оповещение (если только не было ошибки доставки какой то)
        # эту ошибку оставить на потом
        # "Смысл: Когда задача создана, всех причастных оповещает бот, но заказчика оповещает только,
        # когда задачу возьмут в работу, по этому id_notification_for_tg_id может быть пустым ! "
        check_notification = await check_notification_for_tg_id(request_id, session)

        # Получаем список id работников кому было разослано уведомление:
        id_tuples = await get_notification_id_and_employees_id_tuples(request_id, session)

        # Узнаем количество работников на эту задачу (мы единственный исполнитель или нет?
        # Выборка всех со статусом  in_work):
        have_personal_status_in_working = await get_all_personal_status_in_working(request_id, session)  # работает

        # ================================================= 1 ==========================================================

        # 1. Если со статусом в работе только один человек:
        # Если нажимается кнопка complete_subtask, значит хотя бы 1 есть со статусом в работе,  \
        # по этому логика проверки изменяется на подсчет количества людей по этой задаче:
        if len(have_personal_status_in_working) == 1:

            # Перебираем всех назначенных по этой задаче (всех кому была рассылка):
            for row in id_tuples:
                notification_employees_id, notification_id = row  # for_chat_id, message_id

                # Если tg_id из рассылки равен tg_id юзера нажимающего кнопку, то изменяем сообщения у остальных.
                if notification_employees_id == user_id_callback:  # for_chat_id

                    # Апдейтим статус ответственного в (HistoryDistributionRequests): +
                    await update_personal_status(request_id, user_id_callback, 'complete', session)

                    # Апдейтим статус в работе 'complete' в бд (Requests) +
                    await update_requests_status(request_id, 'complete', session)

                    #  ----------------------- 1. Отправить уведомление тому, кто нажал кнопку.
                    # Здесь проверка не нужна на удаленное сообщение)
                    await bot.edit_message_text(
                        chat_id=user_id_callback, message_id=notification_id,
                        text=f'Работа по обращению (№_{request_id}) успешно завершена, заявителю направлено'
                             f' уведомление.\n'
                             f'Текст обращения:\n'
                             f'{request_message}'  # todo текст самого сообщения только сокращенный ?
                        , reply_markup=get_callback_btns(btns={'🗑 ОК, УДАЛИТЬ БАННЕР': 'delete_banner'}, sizes=(1,))
                    )

                    # -------------------------------------- 2. Отправить уведомление заказчику (отправителю обращения):
                    # Обработка ошибки: если пользователь удалил оповещение, то отправим еще одно:
                    # ----------------------- Данные на отправку
                    reply_markup = get_callback_btns(btns={'🗑 ОК, УДАЛИТЬ БАННЕР': 'delete_banner'}, sizes=(1,))
                    text = (f'Работа по вашему обращению (№_{request_id}) завершена, '
                            f'ответственный: {callback_employee_name}.\n'
                            f'Текст обращения:\n'
                            f'{request_message}')

                    # Отправка уведомления: сначала  edit_message_text, если удалено, то send_message, после апдейт айди
                    await decorator_edit_message(tg_id, check_notification, text, reply_markup, request_id,
                                                 bot, session, 'update_request')
                    # !  check_notification юзаказчика уже есть оповещение (если только не было ошибки доставки какой то)
                    #         # эту ошибку оставить на потом
                    # ---------------------------------------- Отправить уведомление заказчику (отправителю обращения):

                # -----------------------  Всем остальным:
                # (*Если tg_id из рассылки не равен tg_id юзера нажимающего кнопку)
                else:
                    # ------------------------------------------------------------------
                    reply_markup = get_callback_btns(btns={'🗑 ОК, УДАЛИТЬ БАННЕР': 'delete_banner'}, sizes=(1,))
                    text = (f'Работа по обращению (№_{request_id}) успешно завершена, '
                            f'ответственный: {callback_employee_name}.\n'
                            f'Текст обращения:\n'
                            f'{request_message}')
                    # ------------------------------------------------------------------
                    # Отправка ведомления: сначала  edit_message_text, если удалено, то send_message,
                    # после апдейт айди в таблице distribution
                    await decorator_edit_message(notification_employees_id, notification_id, text, reply_markup,
                                                 request_id,  bot, session, 'update_distribution')

                    # Апдейтим статус у остальных в (HistoryDistributionRequests): +
                    await update_personal_status(
                        request_id, notification_employees_id, 'complete_another', session)

        # ================================================= 2 ==========================================================
        # 2. Если список содержит больше одного человека:
        elif len(have_personal_status_in_working) > 1:
            # Перебираем всех назначенных по этой задаче (всех имеющихся в базе под этой задачей):
            for row in id_tuples:
                notification_employees_id, notification_id = row
                # -------------------------------------- Выбираем нажавшего
                # Если tg_id из рассылки равен tg_id юзера нажимающего кнопку, то .
                if notification_employees_id == user_id_callback:
                    # Апдейтим ответственного в бд (HistoryDistributionRequests) + апдейт статуса в работе ('in_work').
                    await update_personal_status(request_id, user_id_callback, 'complete', session)

                    # Отправляем уведомление для нажавшего кнопку:
                    # ------------------------------------------------
                    # ! необходимо еще раз перепроверить сколько теперь ответственных, т.к произошел апдейт,
                    # а в переменных старые значения.
                    # Узнаем количество работников на эту задачу после апдейта:
                    have_personal_status_in_working_for_if = await get_all_personal_status_in_working(
                        request_id, session)

                    # Всех оставшихся после апдейта со статусом в работе (нажавших кнопку взять в работу:)
                    all_employees_in_working_for_if = await get_employees_names(
                        have_personal_status_in_working_for_if, session)

                    # -------------------------- 1.  нажавшему ЗАВЕРШИТЬ ПОДЗАДАЧУ
                    # Здесь проверка на наличие уведомления не нужна (если есть callback = есть уведомление).
                    await bot.edit_message_text(
                        chat_id=user_id_callback, message_id=notification_id,
                        text=f'Подзадача по обращению №_{request_id}, завершена.\n'
                             f'Текст обращения:\n'
                             f'{request_message}'
                        , reply_markup=get_callback_btns(
                            btns={'📨 ВОЗОБНОВИТЬ РАБОТУ ПО ЗАЯВКЕ': 'pick_up_request',
                                  '📂 ДЕЛЕГИРОВАТЬ ЗАЯВКУ': 'delegate_request'},  # передать часть работы.
                            sizes=(1, 1)))

                    # ----------------------- 2. Отправить (исправить) уведомление заказчику (отправителю обращения):
                    # ----------------------- Данные на отправку
                    text = (f'Состав участников по вашему обращению №_{request_id} изменился,'
                            f' соисполнители: {all_employees_in_working_for_if}.')
                    reply_markup = get_callback_btns(btns={'🗣 ОТКРЫТЬ ДИСКУССИЮ': 'open_discussion',
                                                           '❎ ОТМЕНИТЬ ЗАЯВКУ': 'cancel_request'}, sizes=(1, 1))
                    # Отправка уведомления: сначала  edit_message_text, если удалено, то send_message,
                    # после апдейт айди нового уведомления
                    await decorator_edit_message(tg_id, check_notification, text, reply_markup, request_id,
                                                 bot, session, 'update_distribution')


                # Иизменяем уведомления у всех остальных:
                else:

                    # ---------------------------------- ОТПРАВЛЯЕМ ТЕМ КТО СО СТАТУСОМ 'in_work' (УЧАСТВУЕТ В ЗАДАЧЕ):
                    # Узнаем количество работников на эту задачу после апдейта:
                    have_personal_status_in_working_for_else = await get_all_personal_status_in_working(
                        request_id, session)

                    # -------------------  Проверка, является ли человек соучастником по задаче:
                    # Проверяем id сотрудника на наличие статуса: в работе (имеют только статус 'in_work')
                    check_personal_status = await check_personal_status_for_tg_id(
                        notification_employees_id, request_id, session)  # -> int or None

                    # Если сотрудник учавствует в созадаче (только статус 'in_work'):
                    if check_personal_status is not None:  # содержит значение 'in_work'

                        # Если id рассылки уже со статусом  в работе, то у него изменяем на другое сообщение
                        # Отправить (исправить) уведомление
                        # ----------------------- Данные на отправку
                        # Вытаскиваем имена всех (по айди) остальных ответственных со статусом в работе \
                        # без (исключаем)  notification_employees_id следующего по итерации в цикле:
                        employees_names_minus_notification_employees_id = await get_employees_names(
                            have_personal_status_in_working_for_else, session, exception=notification_employees_id)

                        text = (f'Состав участников по обращению №_{request_id} изменился,'
                                f' совместно с Вами соисполнители: {employees_names_minus_notification_employees_id}.\n'
                                f'Текст обращения:\n'
                                f'{request_message}')

                        reply_markup = get_callback_btns(btns={'🗣 ОТКРЫТЬ ДИСКУССИЮ': 'open_discussion',
                                                               '✅ ЗАВЕРШИТЬ ПОДЗАДАЧУ': 'complete_subtask',
                                                               '❎ ОТМЕНИТЬ УЧАСТИЕ': 'abort_subtask'
                                                               }, sizes=(1, 1))

                        # Отправка уведомления: сначала  edit_message_text, если удалено, то send_message,
                        # после апдейт айди нового уведомления
                        await decorator_edit_message(notification_employees_id, notification_id, text, reply_markup,
                                                     request_id, bot, session, 'update_distribution')


                    else:
                        # Тем, кто не соучастник по задаче (оповещенцам):
                        # ----------------------- Данные на отправку
                        # Имена всех, кто не участвует в задаче:
                        all_employees_in_working_for_else = await get_employees_names(
                            have_personal_status_in_working_for_else, session)

                        text = (f'Состав участников по обращению №_{request_id} изменился,'
                                f' соисполнители: {all_employees_in_working_for_else}.\n'
                                f'Текст обращения:\n'
                                f'{request_message}')

                        reply_markup = reply_markup = get_callback_btns(btns={'🧩 ЗАБРАТЬ ПОДЗАДАЧУ': 'pick_up_request'},
                                                                        sizes=(1,))

                        # Отправка уведомления: сначала  edit_message_text, если удалено, то send_message,
                        # после апдейт айди нового уведомления
                        await decorator_edit_message(notification_employees_id, notification_id, text, reply_markup,
                                                     request_id, bot, session, 'update_distribution')

        else:
            # Обработка непредвиденных случаев, но это событие скорее невозможно вовсе из за логики оповещения,
            # однако, для более жестких условий проверки исключаем это.
            print("В обработчике complete_subtask список have_personal_status_in_working - пустой, "
                  "это не должно происходить.")

    await callback.answer()
    # Сбрасываем состояние
    await state.clear()

#  f'Поступило новое обращение: {data_request_message_to_send['request_message']}'
# , reply_markup = get_callback_btns(
#     btns={'📨 ЗАБРАТЬ ЗАЯВКУ': 'pick_up_request',
#           '📂 ДЕЛЕГИРОВАТЬ ЗАЯВКУ': 'delegate_request'},  # передать часть работы.
#     sizes=(1, 1))
# )


# a
#
# # -------------- Получаем список активных участников (соучастников с подзадачами)  по request_id:
#         # Апдейт персонального статуса:
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
#         #   !!Доработать
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


#  ----------------- до эксперимента  !!!
# try:
#     # проверка на наличие уже отправленного сообщения заказчику (либо айди либо нон):
#     # Упраздняем проверку, т.к. второе условие, когда уже кто то есть ответственный, \
#     # подразумивает отправку уведоления заказчику. ТАк что достаем его из базы  и редактируем:
#     await bot.edit_message_text(  # Изменяем доставленное уведомление:
#         chat_id=tg_id, message_id=check_notification,
#         text=f'Состав участников по вашему обращению №_{request_id} изменился,'
#              f' соисполнители: {all_employees_in_working_for_if}.',
#         reply_markup=get_callback_btns(
#             btns={
#                 '🗣 ОТКРЫТЬ ДИСКУССИЮ': 'open_discussion',
#                 '❎ ОТМЕНИТЬ ЗАЯВКУ': 'cancel_request'},
#             sizes=(1, 1))
#     )
# # Если удалено
# except TelegramBadRequest as e:
#     if "message to edit not found" in str(e):
#         print(f"Оповещение  №_{notification_id} для пользователя "
#               f"{tg_id} не удалось изменить, "
#               f"так как оно уже не существует (удалено).")
#
#         # Отправляем еще одно и опять апдейтим в реквест:
#         send_notification_again = await bot.send_message(chat_id=tg_id,
#                                                          text=f'Работа по вашему обращению (№_{request_id}) завершена, '
#                                                               f'ответственный: {callback_employee_name}.\n'
#                                                               f'Текст обращения:\n'
#                                                               f'{request_message}',
#                                                          reply_markup=get_callback_btns(
#                                                              btns={
#                                                                  '🗑 ОК, УДАЛИТЬ БАННЕР': 'delete_banner'},
#                                                              sizes=(1,)))

#  ----------------- эксперимент  !!!


# ---------------------------------------- Отправить уведомление заказчику (отправителю обращения):
# Обработка ошибки: если пользователь удалил оповещение, то отправим еще одно:


# Проверка есть ли уже оповещение для заявителя (либо = айди либо = нон):
# "Смысл: Когда задача создана, всех причастных оповещает бот, но заказчика оповещает только,
# когда задачу возьмут в работу, по этому id_notification_for_tg_id может быть пустым ! "
# if check_notification is None:
#     # Если сообщение не доставлялось, -  отправляем новое:
#     send_notification_complete = await bot.send_message(chat_id=tg_id,
#         text=f'Работа по вашему обращению (№_{request_id}) завершена, '
#              f'ответственный: {callback_employee_name}.\n'
#              f'Текст обращения:\n'
#              f'{request_message}' , reply_markup=get_callback_btns(
#             btns={'🗑 ОК, УДАЛИТЬ БАННЕР': 'delete_banner'}, sizes=(1,)))
#     # -------------------------------------- Запоминае идентиф. уведомления заказчика
#     # идентификатор сообщения заявителя (applicant):
#     message_id_applicant = send_notification_complete.message_id
#     #  Апдейтим айди отправленного сообщения в таблицу обращений Requests \
#     #  (поле: id_notification_for_tg_id)
#     await update_message_id_notification(request_id, message_id_applicant, session)

# else:
# Обработка ошибки: если пользователь удалил оповещение, то отправим еще одно:

# try:
#     # Если сообщение уже доставлялось, изменяем его:
#     await bot.edit_message_text(
#         chat_id=tg_id, message_id=check_notification,
#         text=f'Работа по вашему обращению (№_{request_id}) завершена, '
#              f'ответственный: {callback_employee_name}.\n'
#              f'Текст обращения:\n'
#              f'{request_message}'
#         #  текст самого сообщения только сокращенный ?
#         , reply_markup=get_callback_btns(btns={'🗑 ОК, УДАЛИТЬ БАННЕР': 'delete_banner'},
#                                          sizes=(1,)))
#     #  кнопку не согласен с решением продолжить возобновить.
#
# except TelegramBadRequest as e:
#     if "message to edit not found" in str(e):
#         print(f"Оповещение  №_{check_notification} для пользователя "
#               f"{tg_id} не удалось изменить, "
#               f"так как оно уже не существует (удалено).")
#
#         # Отправляем еще одно и опять апдейтим в реквест:
#         send_notification_again = await bot.send_message(chat_id=tg_id,
#             text=f'Работа по вашему обращению (№_{request_id}) завершена, '
#                  f'ответственный: {callback_employee_name}.\n'
#                  f'Текст обращения:\n'
#                  f'{request_message}', reply_markup=get_callback_btns(
#             btns={'🗑 ОК, УДАЛИТЬ БАННЕР': 'delete_banner'}, sizes=(1,)))
#         #  кнопку не согласен с решением продолжить возобновить.

# # --------------- Запоминае идентиф. уведомления заказчика
# # идентификатор сообщения заявителю:
# message_id_applicant = send_notification_again.message_id
# await update_message_id_notification(request_id, message_id_applicant, session)

# # ----------------------- Данные на отправку
# text = (f'Работа по вашему обращению (№_{request_id}) завершена, '
#         f'ответственный: {callback_employee_name}.\n'
#         f'Текст обращения:\n'
#         f'{request_message}')
#
# reply_markup = get_callback_btnsbtns(
#     btns={'🗑 ОК, УДАЛИТЬ БАННЕР': 'delete_banner'}, sizes=(1,))
#
# # Отправка ведомления: сначала  edit_message_text, если удалено, то send_message
# await decorator_edit_message(tg_id, check_notification, text, reply_markup, request_id,
#                              'update_request', bot, session)
# ---------------------------------------- Отправить уведомление заказчику (отправителю обращения):
