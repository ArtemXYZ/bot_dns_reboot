"""
# Модуль отслеживания новых оповещений:
"""

# import asyncio
from working_databases.orm_query_builder import *
from menu.inline_menu import *


# Асинхронная очередь (все новые сообщения будут добавляться сюда):
message_queue = asyncio.Queue()

# ------------------------- Функции проверки новых сообщений на просрочку по времени взятия в работу.
# Функция для обработки задачи
async def check_new_message(request_id: int, input_chat_id: int, wait_time, input_bot, session_pool: AsyncSession):

    """
    # 7200 - 2 ч.
    input_bot = ередается из callback.bot
    На вход время через которое надо проверить, request_id, input_chat_id = телеграмм айди.
    Основная функция проверки просрочки задачи (проверяем в БД задачу на просрочку более 2 часов по статусу
    и времени создания (если через 2 часа статус не изменился (request_status == 'insert'),
    то выставляем статус просрочено и ортправляем руководителю.)
    """

    reply_markup = get_callback_btns(btns={'🗑 ОК, УДАЛИТЬ БАННЕР': 'delete_banner'}, sizes=(1,))
    text = (f'Тест оповещения, если никто не взял в работу.')

    # Задержка
    await asyncio.sleep(wait_time)

    # Проверяем текущий статус заявки:
    request_status = await get_request_status(request_id, session_pool)

    if request_status == 'insert':

        # Если состояние не изменилось, отправляем сообщение
        send_message = await input_bot.send_message(chat_id=input_chat_id, text=text, reply_markup=reply_markup)

        # Апдейт поля под  alarm_status ! ? нужно ли этополе? наверное нужно
#         нужно ли время просрочки? - после развитие уже.


# Функция для добавления нового сообщения в очередь проверки на просрочку сроков взятия в работу:
async def add_new_message_in_queue(request_id: int, input_chat_id: int, wait_time):
    """
    put(item): Асинхронно добавляет элемент в конец очереди.
    # Добавляем в очередь данные для последующей обработки
    # (через определенное время они изымутся из очереди и предадуться далее в функцию, что будет с ними работать).
    """

    # Добавляем в очередь данные для последующей обработки:
    await message_queue.put((request_id, input_chat_id, wait_time))
    # print(f"Новое сообщение {task_id} добалено в очередь проверки.")


# Функция для обработки задач из очереди
async def cycle_checking_new_messages(input_bot, session_pool: AsyncSession):
    while True:
        # Получаем задачу из очереди
        request_id, input_chat_id, wait_time = await message_queue.get()
        await check_new_message(request_id, input_chat_id, wait_time, input_bot, session_pool)
        message_queue.task_done()  # Указываем, что задача завершена



# Прослушка базы данных (ищем обращения, где статус 'insert' на протяжении N не взят в работу)
async def alarm_message(input_bot: Boot, te, session: AsyncSession, bot: Bot):

    """

    """
    #  объект корутины
    coroutine_object = asyncio.create_task(cycle_checking_new_messages())

    # Добавляем задачи в очередь
    await add_new_message_in_queue(request_id, input_chat_id, wait_time)

    # # Ждем завершения всех задач
    # await task_queue.join()
    #
    # # Завершаем воркер после выполнения всех задач
    # worker_task.cancel()
