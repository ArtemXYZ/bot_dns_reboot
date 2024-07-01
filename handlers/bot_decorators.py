"""
Модуль декораторов.
"""

from aiogram.exceptions import TelegramBadRequest
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from working_databases.orm_query_builder import *


# условный декоратор отправки сообщений ботом:
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



# условный декоратор отправки сообщений ботом:
async def decorator_elete_message(input_chat_id: int, input_message_id: int,
                                 input_bot: Bot, input_session: AsyncSession): # , input_reply_markup=None
    """
    Сначала удаляем, если ошибка - изменяем (если ошибка - ничего) и удаляем.

    Отлавливает ошибку исправления сообщения (если пользователь удалил сообщение, изменить и удалить нельзя),

    """
    text='Удалить не получилось, изменим, а после удалим!'

    try:

        # 1 / Пытаемся просто удалить сообщение (если не превышен 48 часовой интервал оно удалится без проблем):
        await input_bot.delete_message(chat_id=input_chat_id, message_id=input_message_id)

    except TelegramBadRequest as e:
        print(f'Полный текст ошибки:  {e}')

        # Если пользователь удалил сообщение из чата:
        if "message to delete not found" in str(e):

            print(f'Собщение для удаления из переписки в режиме дискуссии не было удалено (его уже не существует, '
                  f'удалено пользователем: tg_id - {input_chat_id}')

            # Ничего не делаем в таком случае.

        # Если  превышен временной лимит (48 часовой)  на удаление: RetryAfter
        elif "message can't be deleted" in str(e):

            # 2/ Сначала изменяем, чято бы после удалить:
            await input_bot.edit_message_text(chat_id=input_chat_id, message_id=input_message_id, text=text)
            # Здесь не делаем больше трай эксепт, потому что сообщение уже имеется, значит оно изменится без проблем.

            # 3/ А теперь уже доступно удаление.
            await input_bot.delete_message(chat_id=input_chat_id, message_id=input_message_id)


























# ------------------------------------

#
#
#
#
