"""
Режим сессии для розницы

Основная ветка по работе с обращениями
"""

# -------------------------------- Стандартные модули
import asyncio
# -------------------------------- Сторонние библиотеки
from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, StateFilter, or_f
from aiogram.client.default import DefaultBotProperties  # Обработка текста HTML разметкой

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
# -------------------------------- Локальные модули
from handlers.text_message import *  # Список ругательств:
from filters.chats_filters import *

# from aiogram.utils.formatting import as_list, as_marked_section, Bold, Italic

from menu import keyboard_menu  # Кнопки меню - клавиатура внизу
from menu import inline_menu  # Кнопки встроенного меню - для сообщений

from menu.button_generator import get_keyboard

# ----------------------------------------------------------------------------------------------------------------------
# Назначаем роутер для чата под розницу:
retail_router = Router()

# Фильтруем события на этом роутере:
# 1-й фильтр: чат может быть “приватным”, ”групповым“, ”супер групповым“ или "каналом” - > \
#  ( “private”, “group”, “supergroup”, “channel”)
# 2-й фильтр: по типу юзеров (тип сессии).
retail_router.message.filter(ChatTypeFilter(['private']), UsersRetailSession())
retail_router.edited_message.filter(ChatTypeFilter(['private']), UsersRetailSession())

# ----------------------------------------------------------------------------------------------------------------------
# Кнопки меню внизу (первый старт)
RETAIL_KEYB_MAIN = get_keyboard(
    'Создать заявку',
    'Изменить заявку',
    'Удалить заявку',
    'Запросить статус заявки',
    'Перейти в чат с исполнителем',
    placeholder='Выберите действие',
    sizes=(2, 1, 1)  # кнопок в ряду, по порядку 1й ряд и тд.
)

REQUEST_PROBLEM = get_keyboard(
    # 'Изменить категорию',
    'Отменить заявку',
    'Показать справку по категориям',

    placeholder='Выберите действие',
    sizes=(1, 1)  # кнопок в ряду, по порядку 1й ряд и тд. 2, 1
)


# ---------------------------------- Код ниже для машины состояний (FSM)
class AddRequests(StatesGroup):
    """Шаги состояний для обращений"""
    request_message = State()
    # documents = State()


#
# texts = {
#     'AddRequests:request_message': 'Введите текст обращения заново:'
#     # + ЕЩЕ
# }

class Instructor(StatesGroup):
    """Шаги состояний для кнопок инструктаж и приступить к работе:"""
    # Шаги состояний:
    instruct_or_gowork = State()



class CetCategory(StatesGroup):
    """
    Шаги выбора категории.
    Выбираем сначала родительскую категорию - содержит в себе подкатегории, после подкатегорию.
    """
    category = State()
    sab_category = State()


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------- 0. Первичное приветствие всех пользователей при старте.
# @retail_router.callback_query(callback.data == 'next')   # После аутентификации нажимает кнопку продолжить...
# async def hello_after_on_next(callback: types.CallbackQuery): # todo потом переделать на келбек квери
@retail_router.message(StateFilter(None), F.text == 'next')  # todo потом переделать на келбек квери
async def hello_after_on_next(message: types.Message, state: FSMContext):
    user = message.from_user.first_name  # Имя пользователя
    await message.answer((hello_users_retail.format(user)),
                         parse_mode='HTML')

    await asyncio.sleep(1)
    await message.answer(f'\u00A0\u00A0\u00A0\u00A0Если хочешь, я кратко расскажу, как со мной работать, '
                         f'а после уже помогу в решении твоих вопросов, ну или '
                         f'можешь приступать самостоятельно!',
                         parse_mode='HTML',
                         reply_markup=inline_menu.get_callback_btns(
                             btns={'▶️ КРАТКИЙ ИНСТРУКТАЖ': 'instruction',
                                   '⏩ ПРИСТУПИТЬ К РАБОТЕ': 'go_work'
                                   },
                             sizes=(1, 1)
                         ))
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

    await callback.message.answer(f'Сейчас я включу специальное меню внизу экрана.\n'
                                  f'С помощью него ты сможешь взаимодействовать с моим функционалом.')

    await asyncio.sleep(1)
    await callback.message.answer(f'Для того, чтобы обратиться в ОАиТ за помощью в решении проблем '
                                  f'и прочих рабочих моментов, необходимо нажать кнопку в меню:\n'
                                  f'<b> * Создать заявку *</b>.',
                                  reply_markup=RETAIL_KEYB_MAIN)

    await asyncio.sleep(2)
    await callback.message.answer(f'Далее, необходимо будет выбрать: <b> * Категория заявки *</b> \n'
                                  f', чтобы я точно понял, кому из сотрудников направить твою <b>боль</b>,\n')

    await asyncio.sleep(2)
    await callback.message.answer(
        f'В дальнейшем, я всегда буду подсказывать по ходу твоих действий, так что не запутаешься!')

    await asyncio.sleep(1)
    await callback.message.answer(f'Но если вдруг у тебя возникнут какие то проблемы или вопросы по работе со мной, '
                                  f'всегда можно обратиться за помощью, нажав кнопку "Меню", '
                                  f'далее команду <i>help</i>')

    await asyncio.sleep(2)
    await callback.message.answer(f'Надеюсь, теперь ты разобрался и можем приступать к работе!')

    await asyncio.sleep(3)
    await callback.message.answer(f'Если что, - я готов! Жалуйся ✍️ !')

    # Очистка состояния пользователя:
    await state.clear()

    # # todo замутить удаление всех сообщений с меню


# 0.2. Если нажали кнопку "ПРИСТУПИТЬ К РАБОТЕ" - ответ на кнопку:
@retail_router.callback_query(StateFilter(Instructor.instruct_or_gowork), F.data.startswith('go_work'))
async def get_instruction(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()  # Для сервера ответ о нажатии кнопки (кнопка не будет переливаться в ожидании).



    await callback.message.answer(f'Вот тебе рабочий инструмент (меню внизу 👇 экрана), думаю разберешься 😉.',
                                  reply_markup=RETAIL_KEYB_MAIN)

    # Очистка состояния пользователя:
    await state.clear()
# ----------------------------- Конец 0.1/2

#
#

# ----------------------------- 1.0. Работа с нижней клавиатурой меню.
# -------------- 1.1. Ветка при создании заявки:
@retail_router.message(StateFilter(None), F.text == 'Создать заявку')
async def get_request_problem(message: types.Message, state: FSMContext):

    # удалит сообщение 'Создать заявку' - отправляется в чат после нажатия клавиатуры (не изменяемое поведение)
    await message.delete()

    # Заменяет старое меню на новое
    # await message.answer(f'Задачу понял!', reply_markup=REQUEST_PROBLEM)

    # await message.answer(f'Задачу понял!', reply_markup=types.ReplyKeyboardRemove())  # удаляет клаву
    # todo удаляем полностью клаву! Оставить только инлайн меню.

    # Вывод инлайнового меню (категории обращений), реакция при создании заявки
    await asyncio.sleep(1)
    await message.answer(f'Выберите категорию обращения',
                         reply_markup=inline_menu.get_callback_btns(
                             btns={'АНАЛИТИКА': 'analytics',
                                   'ФОРМАТЫ': 'formats',
                                   'ТОВАРООБОРОТ': 'trade _turnover',
                                   'ОТМЕНА': 'cancel'},
                             sizes=(1, 1, 1)
                         )
                         )
    # Очистка состояния пользователя: ??
    # await state.clear()

#
#
#

# # # # 1.1.0 Родитель (Ветка при создании заявки) -> Реакции на нажатие кнопок инлайнового меню на категории обращений:
@retail_router.callback_query(StateFilter(None), F.data.startswith('cancel'))
# Если у пользователя нет активного состояния (StateFilter(None) + он ввел команду "cancel")
async def get_cancel(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()  #
    await callback.message.answer('Ушли назад. доделай нормальное инлайновое меню!!!')
    # await state.set_state(AddRequests.request_message)




@retail_router.callback_query(StateFilter(None), F.data.startswith('analytics'))
# Если у пользователя нет активного состояния (StateFilter(None) + он ввел команду "analytics")
async def add_request_message(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()  # ?
    await callback.message.answer('Введите текст обращения', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddRequests.request_message)
    # todo замутить удаление всех сообщений с меню


# Становимся в состояние ожидания ввода
# Пользователь ввел текст
@retail_router.message(StateFilter(AddRequests.request_message), F.text)
# Если ввел текст обращения (AddRequests.request_message, F.text):
async def get_request_message(message: types.Message, state: FSMContext, session: AsyncSession):
    # Передам словарь с данными ( ключ = request_message, к нему присваиваем данные message.text), после апдейтим
    await state.update_data(request_message=message.text)
    # await state.update_data(tg_id=message.from_user.id)

    # Формируем полученные данные:
    data = await state.get_data()
    print(data)
    tg_id = message.from_user.id
    print(tg_id)
    # Запрос в БД на добавление обращения:
    # session.add(Requests(request_message=data['request_message'], tg_id=message.from_user.id))
    # await session.commit()
    await add_request_message(session, data)

    await message.answer(f'Обращение отправлено, ожидайте ответа!', reply_markup=RETAIL_KEYB_MAIN)

    await asyncio.sleep(1)
    await message.answer(f'Я направлю уведомление, как только обращение будет взято в работу.')

    # Отправка для наглядности записанного сообщения: text=f'Ваша жалоба: {str(data)}'
    await message.answer(f'Ваша жалоба: {data.get("request_message")}')

    # Очистка состояния пользователя:
    await state.clear()

# -------------- 1.2. Ветка при отмене заявки:
# back_step
@retail_router.message(StateFilter(None), F.text == 'Отменить заявку')
async def get_back_request(message: types.Message):
    await message.delete()

    # Заменяет старое меню на новое
    await message.answer(f'Ок!', reply_markup=RETAIL_KEYB_MAIN)

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
