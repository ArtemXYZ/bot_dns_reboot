"""
Модуль декораторов.
"""
from aiogram.exceptions import TelegramBadRequest
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from working_databases.orm_query_builder import *


# словный декоратор отправки сообщений ботом:
async def decorator_edit_message(input_chat_id: int, input_message_id: int, input_text: str, input_reply_markup,
                                 request_id: int, input_bot: Bot, input_session: AsyncSession, update_type: str = None):
    """
            Отлавливает ошибку исправления сообщения (если пользователь удалил сообщение, изменить и удалить нельзя),
            По этому отправляем новое
            нужен апдейт айди нового сообщения.
            # search_notification_employees_id: int = None - устарело.
    """
    # Если исключение не наступило:
    send_message = None

    try:
        await input_bot.edit_message_text(  # Изменяем доставленное уведомление:
            chat_id=input_chat_id, message_id=input_message_id, text=input_text, reply_markup=input_reply_markup)

        # в этом блоке возврат - send_message = None
        send_message = None

    except TelegramBadRequest as e:
        if "message to edit not found" in str(e):
            # Вытаскиваем из бд полное имя сотрудника:
            employee_name = await get_full_name_employee(input_chat_id, input_session)

            print(f'Оповещение  №_{input_message_id} для пользователя: {employee_name},'
                  f' chat_id: {input_chat_id} не удалось изменить, так как оно уже не существует (удалено).')

            # Отправляем еще одно и опять апдейтим в реквест:
            send_message = await input_bot.send_message(chat_id=input_chat_id, text=input_text,
                                                        reply_markup=input_reply_markup)

            message_id_update = send_message.message_id

            # Если указан тип апдейта (return вернет None).
            if update_type is not None:

                # Апдейтим айди отправленного нового оповещения заявителю, т.к. старое он удалил и оно не действительно.
                if update_type == 'update_request':
                    await update_message_id_notification(
                        request_id, message_id_update, 'update_request', input_session)

                elif update_type == 'update_distribution':
                    await update_message_id_notification(
                        request_id, message_id_update, 'update_distribution', input_session,
                        input_chat_id) # Не забудь указать этот параметр ! для update_distribution

                print(f'Было отправлено новое оповещение  №_{message_id_update} для пользователя: {employee_name},'
                      f' chat_id: {input_chat_id}.')


            # Если апдейтить не нужно, то просто экземпляр отправленного сообщения (можно потом вытянуть данные).
            else:
                send_message

    # finally:
    # Либо Нон либо send_message
    return send_message

# ------------------------------------
# async def decorator_edit_message(input_chat_id: int, input_message_id: int, input_text: str, input_reply_markup,
#                                  input_bot: Bot, input_session: AsyncSession):
#     try:
#         await input_bot.edit_message_text(  # Изменяем доставленное уведомление:
#             chat_id=input_chat_id, message_id=input_message_id, text=input_text, reply_markup=input_reply_markup)
#
#         # в этом блоке возврат - send_message = None
#
#     except TelegramBadRequest as e:
#         if "message to edit not found" in str(e):
#             print(
#                 f'Оповещение  №_{input_message_id} для пользователя: , chat_id: {input_chat_id} не удалось изменить, '
#                 f'так как оно уже не существует (удалено).')
#
#             # Отправляем еще одно и опять апдейтим в реквест:
#             send_message = await input_bot.send_message(chat_id=input_chat_id, text=input_text,
#                                                         reply_markup=input_reply_markup)
#
#     # finally:
#     return send_message


# async def decorator_edit_message(func):
#     """
#         Отлавливает ошибку исправления сообщения (если пользователь удалил сообщение, изменить и удалить нельзя),
#         По этому отправляем новое
#         нужен апдейт айди нового сообщения.
#     """
#     async def wrapper_edit_message(*args, **kwargs):
#         try:
#             original = func(*args, **kwargs)
#
#
#
#
