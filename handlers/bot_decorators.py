"""
Модуль декораторов.
"""
from aiogram.exceptions import TelegramBadRequest
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from working_databases.orm_query_builder import *


# словный декоратор отправки сообщений ботом:
async def decorator_edit_message(input_chat_id: int, input_message_id: int, input_text: str, input_reply_markup,
                                 request_id: int, update_request: str,  input_bot: Bot, input_session: AsyncSession):
    """
            Отлавливает ошибку исправления сообщения (если пользователь удалил сообщение, изменить и удалить нельзя),
            По этому отправляем новое
            нужен апдейт айди нового сообщения.
    """

    try:
        await input_bot.edit_message_text(  # Изменяем доставленное уведомление:
            chat_id=input_chat_id, message_id=input_message_id, text=input_text, reply_markup=input_reply_markup)

        # в этом блоке возврат - send_message = None

    except TelegramBadRequest as e:
        if "message to edit not found" in str(e):
            print(
                f'Оповещение  №_{input_message_id} для пользователя: , chat_id: {input_chat_id} не удалось изменить, '
                f'так как оно уже не существует (удалено).')

            # Отправляем еще одно и опять апдейтим в реквест:
            send_message = await input_bot.send_message(chat_id=input_chat_id, text=input_text,
                                                        reply_markup=input_reply_markup)

            if update_request == 'update_request':
                message_id_update = send_message.message_id
                await update_message_id_applicant(request_id, message_id_update, input_session)

            elif update_request == 'update_distribution':
                ...

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
