"""
Режим сессии для ОАИТ
"""

# -------------------------------- Стандартные модули
# -------------------------------- Сторонние библиотеки
from aiogram import F, Router
from aiogram.filters import StateFilter

from aiogram.exceptions import TelegramBadRequest

import time
# -------------------------------- Локальные модули
from filters.chats_filters import *

# from aiogram.utils.formatting import as_list, as_marked_section, Bold, Italic

# from menu import keyboard_menu  # Кнопки меню - клавиатура внизу

from menu.inline_menu import *  # Кнопки встроенного меню - для сообщений
from working_databases.orm_query_builder import *
from handlers.all_states import *
from handlers.data_preparation import *

from handlers.bot_decorators import *
from menu import keyboard_menu  # Кнопки меню - клавиатура внизу
from menu.button_generator import get_keyboard
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
                        # open_discussion_distribution - дальше мы будем понимать от кого келбек \
                        # (от заявителя или от исполнителя) !!! нажмет исполнитель.
                        reply_markup=get_callback_btns(btns={'🗣 ОТКРЫТЬ ДИСКУССИЮ': 'open_discussion_distribution',
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
                                    '🗣 ОТКРЫТЬ ДИСКУССИЮ': 'open_discussion_requests',
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
                        reply_markup = get_callback_btns(btns={'🗣 ОТКРЫТЬ ДИСКУССИЮ': 'open_discussion_requests',
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
                        reply_markup=get_callback_btns(btns={'🗣 ОТКРЫТЬ ДИСКУССИЮ': 'open_discussion_distribution',
                                                             '✅ ЗАВЕРШИТЬ ПОДЗАДАЧУ': 'complete_subtask',
                                                             '❎ ОТМЕНИТЬ УЧАСТИЕ': 'abort_subtask'
                                                             }, sizes=(1, 1))
                    )

                    # ----------------------- Отправить (исправить) уведомление заказчику (отправителю обращения):
                    # проверка на наличие уже отправленного сообщения заказчику (либо айди либо нон):
                    # Упраздняем проверку, т.к. второе условие, когда уже кто то есть ответственный, \
                    # подразумивает отправку уведоления заказчику. ТАк что достаем его из базы  и редактируем:
                    reply_markup = get_callback_btns(btns={'🗣 ОТКРЫТЬ ДИСКУССИЮ': 'open_discussion_requests',
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
                        reply_markup = get_callback_btns(btns={'🗣 ОТКРЫТЬ ДИСКУССИЮ': 'open_discussion_distribution',
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
                                                 request_id, bot, session, 'update_distribution')

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


# Принимаем 2 келбека и понимаем какой тип пользователя нажал кнопку:
@oait_router.callback_query(StateFilter(None), (F.data.startswith('open_discussion_requests') |
                                                F.data.startswith('open_discussion_distribution')
                                                )
                            ) # StateFilter(None) ?

async def open_discussion(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot):
    """Переходим в дискуссию (чат)/ Первичное окно. """

    await state.set_state(LetsChat.start_chat)
    # ---------------------------------------
    bot = callback.bot
    callback_data = callback.data
    user_id_callback = callback.from_user.id
    callback_notification_id = callback.message.message_id
    # ---------------------------------------
    # Апдейт статуса в Users (что мы сейчас в режиме дискуссии):
    await update_discussion_status(user_id_callback,True ,session)  #  ! без кавычек True

    # Проверка откуда пришел келбек (какой тип пользователя нажал кнопку):
    # -----------------------------------------------------------------------------------------------------
    # Если это заявитель нажал кнопку:
    if callback_data.startswith('open_discussion_requests'):

        callback_startswith = 'open_discussion_requests' # Сохраняем идентификатор келбека

        # Ищем в таблице Requests по id сообщения
        request_id = await get_requests_id_in_requests_history(callback_notification_id, session)

    # Если это ответственый нажал кнопку:
    elif callback_data.startswith('open_discussion_distribution'):

        callback_startswith = 'open_discussion_distribution'  # Сохраняем идентификатор келбека

        # Ищем в HistoryDistributionRequests (Залезть в бд забрать данные о задаче (по айди сообщения из келбека)):
        request_id = await check_notification_id_in_history_distribution(callback_notification_id, session)

    # Получаем айди задачи
    # -----------------------------------------------------------------------------------------------------

    # Отправляем сообщение после нажатия кнопки перейти в чат.
    lets_chat = await bot.send_message(
        chat_id=user_id_callback,
        text=f'Вы находитесь в режиме диалога по обращению №_{request_id}, введите текст.\n'
             f'\n'
             f'❗️ Сообщения будут адресованы только определенн(ому-ым) участник(у-ам), до выхода из данного режима. '
             f'После выхода из диалоа, сообщения очистятся, что бы не мешать переписке по другим темам. '
             # f'При возобновлени диалога все сообщения будут доступны (по умолчанию 10 последних, если необходимо '
             # f'подрузить более раннюю историю нажмите "Загрузить всю историю переписки".',
             , reply_markup=get_callback_btns(
                                    btns={' ЗАКРЫТЬ РЕЖИМ ДИСКУССИИ': 'close_discussion_mode'
                                          },
                                    sizes=(1,))
                                )

             # get_keyboard('Выйти из дискуссии', 'Загрузить всю историю переписки',
             #                           placeholder='Введите сообщение',
             #                           sizes=(1, 1))


             #  todo логика подгрузки сообщений из истории (удаляются первые, загружаются предшествующие 10 + 10)
             #  todo   + другие варианты

        # reply_markup=get_callback_btns(btns={'⏹ ОТМЕНА': 'chat_cancel'}, sizes=(1,))
        # text=f'Вы першли в диалог по задаче №_{request_id}, введите текст.',


    lets_chat_message_id = lets_chat.message_id  # id нового сообщения

    # # Перекидываем в стейт-дату данные для дальнейшего использования в следующем обработчике get_messege_discussion:
    # await state.update_data(request_id=request_id, edit_chat_id=user_id_callback, edit_message_id=message_id)

    # message_id_list - Создаем пустой список, в него мы будем помещать все айди всех входящих сообщений
    # от бота (другие пользователи через бота) и от пользователя в следующем обработчике:
    #

    await state.update_data(request_id=request_id, startswith=callback_startswith,
                            lets_chat_message_id=lets_chat_message_id, message_id_list=[])
    # await state.update_data(request_id=request_id, edit_chat_id=user_id_callback, edit_message_id=message_id)

    await callback.answer()

# Обработчик будет принимать сообщения от бота и от пользователя:
@oait_router.message(StateFilter(LetsChat.start_chat), F.text )  #  F.text
async def get_message_discussion(message: types.Message, state: FSMContext, session: AsyncSession, bot: Bot):



    # Получаем данные из предыдущего стейта:
    # ---------------------------------------------------------------------
    back_data = await state.get_data()
    # Создаем пустой список, в него мы будем помещать все айди всех входящих сообщений
    # от бота (другие пользователи через бота) и от пользователя:
    message_id_list = back_data.get('message_id_list') # +
    print(f'0/ message_id_list - {message_id_list}')

    back_request_id = back_data.get('request_id')  # Получаем айди задачи.
    back_startswith = back_data.get('startswith')  # Получаем идентификатор келбека

    # Получаем идентификаторы сообщения, для редактирования:
    # beck_tg_id = data_write_to_base.get('edit_chat_id')  # tg_id = edit_chat_id ! ? нужно ли?
    # edit_message_id_new = data_write_to_base.get('edit_message_id')

    # Получаем данные message
    # Проверяем, принадлежит ли входящее сообщение боту или нет:
    is_bot: bool = message.from_user.is_bot

    # {'insert_message_id': message_by_distribution.message_id,   'insert_user_id': user_id})

    user_id = message.from_user.id
    insert_message_id = message.message_id  # Получаем айди сообщения

    save_text = message.text  # Вытягиваем текст

    print(f'0/0 insert_message_id - {insert_message_id}') # +
    # ---------------------------------------------------------------------


    # --------------------------------- Если входящее сообщение принадлежит боту, то:
    if is_bot:

        # todo проверка принадлежности сообщения (для дискуссии ли это предназначалось сообщение?) \
        # варианты (сравнение всех айди в бд по реквесту дискуссии и оповещениям.
        # !!! можно добавить проверку состояния
        ...

        message_id_list.append(insert_message_id)

        print(f'1/ is_bot message_id_list - {message_id_list}')
        # Сохраняем обновленный список сообщений в состояние
        await state.update_data(message_id_list=message_id_list)


    # --------------------------------- Если входящее сообщение принадлежит нам (пользователю), то:
    else:

        # Сохраняем поступившее сообщение в таблицу дискуссий:
        await add_row_in_discussion_history(back_request_id, user_id, save_text, insert_message_id, session)

        message_id_list.append(insert_message_id)
        print(f'else - {message_id_list}')
        # Сохраняем обновленный список сообщений в состояние
        await state.update_data(message_id_list=message_id_list)


        # ----------------------------  Выполняем рассылку ответственным по обращению
        # 1. ------------------ Выбираем всех кто в этой задаче включая инициатора

        # Получаем айди инициатора (делаем выборку из реквест):
        tg_id_request = await get_tg_id_in_requests_history(back_request_id, session)

        # Получаем список айди ответственных (делаем выборку из distribution):
        # ! Тут всегда будет хотя бы 1 (не нужна проверка на нон)
        tg_id_distribution_tuple = await get_all_personal_status_in_working(back_request_id, session)
        # возвращает список кортежей  [(1,), (2,), (3,)] или []
        # каждая итерация цикла будет предоставлять вам один кортеж из списка.
        # employee_id = i[0]  # По этому, Извлекаем конкретное значение ( каждый кортеж содержит только одно значение)

        # 1.  Если это заявитель пишет в чат:
        if back_startswith == 'open_discussion_requests':
            # Тогда его оповещать не нужно (уже его сообщение в чате есть у него)

            # ----------------------------------  Оповещаем всех ответственных сотрудников по этой задаче:
            # Перебираем всех назначенных по этой задаче:
            for tg_id in tg_id_distribution_tuple:

                # каждая итерация цикла будет предоставлять вам один кортеж из списка, по этому [0].
                employee_id = tg_id[0]
                tg_id_int = int(employee_id)

                # Проверка статуса адресата (находится ли он в дискуссии?):
                discussion_status_distribution = await check_discussion_status(tg_id_int, session)

                # если да то отправляем в дискуссию
                if discussion_status_distribution is True:

                    # Достаем имя написавшего:
                    name_user_id = await get_full_name_employee(user_id, session)
                    # Отправляем в чат дискуссии:
                    message_by_distribution = await bot.send_message(
                        chat_id=tg_id_int, text=f'Пишет: {name_user_id}.\n{save_text}')
                    # save_text Текст сообщения.

                    # Сохраняем айди сообщения в data состояния:
                    message_id_list.append(message_by_distribution.message_id)
                    print(f'2/ is not bot message_id_list - {message_id_list}') # -
                    # Сохраняем обновленный список сообщений в состояние
                    await state.update_data(message_id_list=message_id_list)

                # если нет, то меняем баннер
                elif discussion_status_distribution is False:
                    print(f'Адресат вне режима дискуссии: {tg_id_int}')

                    ...




        # 2. Если это ответственный сотрудник пишет в чат:
        elif back_startswith == 'open_discussion_distribution':
            # Тогда его оповещать не нужно (уже его сообщение в чате есть у него), но нужно оповестить заявителя и всех \
            # ответственных, кроме того, что написал.

            # ----------------------------------  Оповещаем заявителя по этой задаче:
            # Проверка статуса адресата (находится ли он в дискуссии?):
            discussion_status_requests = await check_discussion_status(tg_id_request, session)

            # Если статуса адресата - в режиме дискуссии:
            if discussion_status_requests is True:

                # Достаем имя написавшего:
                name_user_id = await get_full_name_employee(user_id, session) # tg_id_request


                # Отправляем в чат дискуссии заявителю:
                message_by_requests = await bot.send_message(chat_id=tg_id_request,
                                                             text=f'Пишет: {name_user_id}.\n{save_text}')

                # Сохраняем айди сообщения в data состояния:
                message_id_list.append(message_by_requests.message_id)
                print(f'3/ is not bot message_id_list - {message_id_list}')
                # Сохраняем обновленный список сообщений в состояние
                await state.update_data(message_id_list=message_id_list)

            # если нет, то меняем баннер
            elif discussion_status_requests is False:
                print(f'Адресат вне режима дискуссии: {tg_id_request}')

                ...

            # ----------------------------------  Оповещаем всех ответственных сотрудников по этой задаче:
            # Перебираем всех назначенных по этой задаче, кроме написавшего:
            for tg_id_distribution in tg_id_distribution_tuple:

                # каждая итерация цикла будет предоставлять вам один кортеж из списка, по этому [0].
                employee_id = tg_id_distribution[0]
                tg_id_int = int(employee_id)

                # отправляем всем, кроме написавшего (айди написавшего не совпадает с ади ответственных, \
                # если совпадет то ничего не отправляем.
                if tg_id_int != user_id:

                    # Проверка статуса адресата (находится ли он в дискуссии?):
                    discussion_status_distribution = await check_discussion_status(tg_id_int, session)

                    # Если статуса адресата - в режиме дискуссии:
                    if discussion_status_distribution is True:

                        # Достаем имя написавшего:
                        name_user_id = await get_full_name_employee(user_id, session)
                        # Отправляем в чат дискуссии:
                        message_by_requests = await bot.send_message(chat_id=tg_id_int,
                                                                     text=f'Пишет: {name_user_id}.\n{save_text}')

                        # Сохраняем айди сообщения в data состояния:
                        message_id_list.append(message_by_requests.message_id)
                        print(f'4/ Оповещаем всех ответственных сотрудников по этой задаче message_id_list - {message_id_list}')
                        # Сохраняем обновленный список сообщений в состояние
                        await state.update_data(message_id_list=message_id_list)

                    # если нет то меняем баннер
                    elif discussion_status_distribution is False:
                        print(f'Адресат вне режима дискуссии: {tg_id_int}')



    # await state.clear() - !!! чистить стейт нельзя иначе каждый раз надо будет открывать дискуссии.



@oait_router.callback_query(StateFilter(LetsChat.start_chat), F.data.startswith('close_discussion_mode'))
async def delete_message_discussion(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot):

    #  Асинхронная блокировка (поможет предотвратить гонку условий при одновременном доступе нескольких пользователей):
    async with (lock):

        await callback.answer()  # ОТВЕТ ДЛЯ СЕРВЕРА
        # ---------------------------------------------------------------------
        user_id = callback.from_user.id
        # input_bot = callback.bot
        input_bot = bot
        back_data = await state.get_data() # из предыдущего стейта:
        # Получаем список айди всех входящих сообщений полученных и переданных в режиме дискуссии
        # от бота (другие пользователи через бота) и от пользователя:
        message_id_list = back_data.get('message_id_list')
        lets_chat_message_id = back_data.get('lets_chat_message_id')

        print(f'Достаем весь список из предыдущего стейта message_id_list {message_id_list}')  # !
        # ---------------------------------------------------------------------

        # Удаляем всю перписку из дискуссии:
        for del_mesid in message_id_list:

            # Сначала удаляем, если ошибка - изменяем (если ошибка - ничего) и удаляем.
            await decorator_elete_message(user_id, del_mesid, input_bot, session)

        # Удаляеем заголовок дискуссии:
        await decorator_elete_message(user_id, lets_chat_message_id, input_bot, session)

        # После того, как сообщения все удалены, очищаем состояние  \
        # (это очистит все айди сообщений из переписки в дискуссиях, что обязательно для вызова обработчика в последующем.
        await state.clear()

        # Апдейт статуса в Users (что мы сейчас в режиме дискуссии):
        await update_discussion_status(user_id, False, session)  # ! без кавычек True


        #
#








# ------------------ отложено.
# Если никто не взял задачу в работу:
# @oait_router.callback_query(F.data.startswith('skip_and_send') | F.data.startswith('pick_up_request')
#                             | F.data.startswith('cancel_request'))
# async def alarm_message(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot):
#     """
#     Реагируем на отправку заявки пользователем с помощью фильтра (отправка 'skip_and_send'),
#     Отмену тревоги по 'pick_up_request'. Возобновление по последнему (завершить задачу: 'cancel_request',
#
#     Логика:
#     Как только отправили (skip_and_send), получаем это в обработчике ожидаем некоторое время, проверяем состояние,
#     какой кнопке оно соответствует и в зависимости от жэтого отправляем или не отправляем оповещение.
#
#     # Устанавить состояниенельзя, тк. нарушается работа других сотояний.
#     # По этому проверяем начение статуса в реквест.
#
#     """
#
#
#
#     data = callback.data
#     bot = callback.bot
#     input_chat_id = 1262916285  # Эльвира
#     reply_markup = get_callback_btns(btns={'🗑 ОК, УДАЛИТЬ БАННЕР': 'delete_banner'}, sizes=(1,))
#     text = (f'Тест оповещения, если никто не взял в работу.')
#
#     # Прилетела команда на отправку обращения (произошла рассылка уведомлений):
#     if data.startswith('skip_and_send'):
#
#         # Cохраняем текущее время:
#         # start_time = time.time()
#         # print(f'Время срабатывания в ОАИТ: {start_time}')
#         ...
#
#         # Ожидаем некоторое время:
#         # todo добавить переменную и таблицу в базе данных под это, что бы с админки можно было менять это
#         # await asyncio.sleep(5)
#
#
#
#
#
#         # # Достать айди заявки:
#         # request_id = 15
#         #
#         # # Проверяем текущий статус заявки:
#         # request_status = await get_request_status(request_id, session)
#         #
#         # # Если статус заявки соответствует
#         # if request_status == 'insert':
#         #     # Если состояние не изменилось, отправляем сообщение
#         #     send_message = await bot.send_message(chat_id=input_chat_id, text=text, reply_markup=reply_markup)
#
#
#     # elif data.startswith('pick_up_request'):
#     #
#     #
#     # elif data.startswith('cancel_request'):
