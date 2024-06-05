"""
Общий режим сессии для всех типов чартов

Сценарий:
0. Первичное диалоговое окно для любого пользователя, нажавшего старт.
1. Далее, предлагает пройти аутентификацию.
3.

//////// Функции:
0. Первичное приветствие всех пользователей при старте.
1. Выполняет чистку сообщений от брани.
2. Отвечает за логирование пользователей при старте.
"""

# -------------------------------- Стандартные модули
from string import punctuation
import asyncio
# -------------------------------- Сторонние библиотеки
from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, StateFilter, or_f
from aiogram.client.default import DefaultBotProperties  # Обработка текста HTML разметкой
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
# -------------------------------- Локальные модули
from handlers.text_message import swearing_list  # Список ругательств:
from filters.chats_filters import *

# from aiogram.utils.formatting import as_list, as_marked_section, Bold, Italic

# from menu import keyboard_menu  # Кнопки меню - клавиатура внизу
from menu.inline_menu import *  # Кнопки встроенного меню - для сообщений

from working_databases.query_builder import *
from working_databases.orm_query_builder import *
from working_databases.configs import *
from start_sleep_bot.def_start_sleep import *

from handlers.all_states import *
# Назначаем роутер для всех типов чартов:
general_router = Router()

# фильтрует (пропускает) только личные сообщения и только определенных пользователей:
general_router.edited_message.filter(ChatTypeFilter(['private']))
general_router.edited_message.filter(ChatTypeFilter(['private']))


# ----------------------------------------------------------------------------------------------------------------------
# Вспомогательная функция проверки регистрации:
async def check_registration(message: types.Message, state: FSMContext):  # , session_pool: AsyncSession
    """
    Алгоритм:
    Каждое сообщение пользователя проходит проверку на доступ по tg_id ссылаясь во внутреннюю базу.
    Если такого tg_id не находится, то запрос осуществляется к удаленному хосту к таблице бота регистрации
    + смотрим на удаление сотрудника. Если сотрудник удален - None, True - если есть, и False, если отсутствует.
    Далее обновляем локальную базу данных.
    Таким образом избавляемся от лишних нагрузок (запрос через ОРМ в Локал БД более шустрый и удобный,
    а так же избавляемся от избыточных итераций.
    """

    # Вытаскиваем id пользователя при старте:
    user_tg_id: int = message.from_user.id

    # Проверяем tg_id на серваке_DNS (если пользователь регился в авторизационном боте, то tg_id будет в базе.
    # На выходе будет или булевое занчение или NULL !!!
    check_is_deleted_value_in_jarvis = await get_data_in_jarvis_scalar(
        await get_async_engine(CONFIG_JAR_ASYNCPG), is_deleted_value_for_one_id_tg, user_tg_id)

    print(check_is_deleted_value_in_jarvis)
    # ----------------------- Проверяем tg_id на удаление пользователя:

    # Если пользователь не удален (в штате), тогда False:
    if bool(check_is_deleted_value_in_jarvis) is False:

        # Выводим приветствие в зависимости от типа айдишника
        await message.answer(f'✅ <b>Доступ разрешен!</b>',
                             parse_mode='HTML',
                             reply_markup=get_callback_btns(
                                 btns={'Продолжить': 'go_next'})
                             )

        # Чистим состояние от предыдущей итеррации:
        await state.clear()
        # Устанавливаем состояние для цикла проверки (Встает в ожидании нажатия кнопки):
        await state.set_state(StartUser.check_next)


    # Если есть в базе, но удален:
    elif bool(check_is_deleted_value_in_jarvis) is True:

        await message.answer(f'❌ <b> Доступ запрещен! Пользователь удален из системы!</b>',
                             parse_mode='HTML')
        # обратитесь в поддержку, если это ошибочно

        # Чистим состояние от предыдущей итеррации:
        await state.clear()

    # Если нет в базе, отправляем регаться:
    elif bool(check_is_deleted_value_in_jarvis) is None:

        await message.answer(
            # StateFilter(None),
            f'❌ <b>Доступ закрыт!\n Пройдите аутентификацию в <a>@authorize_sv_bot</a></b>'
            , parse_mode='HTML',
            reply_markup=get_callback_btns(
                btns={'Я прошел аутентификацию, продолжить!': 'go_repeat'}))

        # Чистим состояние от предыдущей итеррации:
        await state.clear()
        # Устанавливаем состояние для цикла проверки (Встает в ожидании нажатия кнопки):
        await state.set_state(StartUser.check_repeat)

    else:
        # Отправляем регаться
        await message.answer(
            f'❌ <b>Ошибка в данных на сервере, обратитесь в службу поддержку!</b>'
            , parse_mode='HTML', reply_markup=get_callback_btns(
                btns={'Оставить заявку': 'support'})
        )

        # Чистим состояние от предыдущей итеррации:
        await state.clear()
        # Устанавливаем состояние для цикла проверки (Встает в ожидании нажатия кнопки):
        await state.set_state(StartUser.support_rror)

# -------------------

# Ожидание следующего сообщения пользователя
@general_router.callback_query(StateFilter(StartUser.check_repeat), F.data.startswith('go_repeat'))
async def on_next(call: types.CallbackQuery, session_pool, state: FSMContext):

    # #  todo !!!! Переработать
    #  todo Возможно сюда запихнуть еще раз обращение к базе данных и если зарегался то обновить,
    #  todo прервать цикл

    # Обновляем базу данных
    await updating_local_db(session_pool)  ## Возможно пересмотреть логику
    await check_registration(call.message, state)  # Запускаем проверку заново , session_pool
    await call.answer()  # Закрываем кнопку 'next' чтобы предотвратить повторные нажатия


# @general_router.callback_query(StateFilter(StartUser.check_repeat), F.data.startswith('support_rror'))
# async def on_next(call: types.CallbackQuery, session_pool, state: FSMContext):
#
#     # #  todo !!!! Переработать
#     #  todo Возможно сюда запихнуть еще раз обращение к базе данных и если зарегался то обновить,
#     #  todo прервать цикл
#
#     # Обновляем базу данных
#     await updating_local_db(session_pool)  ## Возможно пересмотреть логику
#     await check_registration(call.message, state)  # Запускаем проверку заново , session_pool
#     await call.answer()





# ------------------- конец


@general_router.message(CommandStart())
async def on_start_user(message: types.Message, state: FSMContext):  # , session_pool: AsyncSession
    await check_registration(message, state)  # , session_pool
    #  todo удалять кнопки и все сообщение раньше, выводить приветствие!

    # await message.delete()  # Удаляем сообщение и кнопки?. todo !!!






# 0. -------------------------- Очистка сообщений от ругательств для всех типов чартов:
# Отлавливает символы в ругательствах (замаскированные ругательства):
def clean_text(text: str):
    return text.translate(str.maketrans('', '', punctuation))


# Ловим все сообщения, ищем в них ругательства:
@general_router.edited_message()  # даже если сообщение редактируется
@general_router.message()  # все входящие
async def cleaner(message: types.Message):
    if swearing_list.intersection(clean_text(message.text.lower()).split()):
        await message.answer(f'<b>Сообщение удалено!</b>\n'
                             f'<b>{message.from_user.first_name}</b>, попрошу конструктивно и без брани!')
        # , parse_mode='HTML'
        # Подобные сообщения, будут удалены!
        await message.delete()  # Удаляем непристойные сообщения.
        # await message.chat.ban(message.from_user.id)  # Если нужно, то в бан!

# ------------------------------------------------------------------------------
# -------------------------------------- Ответ на вариации входящих сообщений:
# Только жесткое совпадение по словам, нужно доделать разделитель слов в сообщении потозже!
# @general_router.message()
# async def echo(message: types.Message):
#     text = message.text
#
#     if text in ['Привет', 'привет', 'hi', 'hello']:
#         await message.answer('И тебе привет!')
#     elif text in ['Пока', 'пока', 'До свидания']:
#         await message.answer('И тебе пока!')
#     else:
#         await message.answer(message.text)


# ------------------------------------------------- Устарело
# 1 Проверяем тип айдишника (админ или зам. или розница)
# * добавить в режиме админа регистрацию сотрудников по типу пользователя и режим входа под другими оболочками


# Если во внутренней базе нет данных на нового пользователя:
# if result is None:
#     result_bool: bool = False
# else:
#     result_bool: bool  = True
# return result_bool

# Проверяем tg_id на серваке_DNS (если пользователь регился в авторизационном боте, то tg_id будет в базе.
#         check_telegram_id_in_jarvis = await async_select('inlet.staff_for_bot', 'tg',
#                                                      'tg', where_columns_value=where_value,
#                                                      engine_obj=await get_async_engine(CONFIG_JAR_ASYNCPG)
#         )  # на выходе: либо Нул либо telegram_id

#        # Если нет данных о пользователе в локальной базе, тогда:
#         if check_telegram_id_in_local_db == None:
#
#
#
#              #todo !!! проверка в косячных (создать отдельную таблицу?)
#
#         else:
# Запрос на сравнение во внутреннюю базу (bool):
# check_telegram_id_in_local_db = await check_id_tg_in_users(id=tg_id_in_jarvis, session=session_pool)
#

# Запрос на сравнение во внутреннюю базу (bool):
# check_telegram_id_in_local_db = await check_id_tg_in_users(id=user_tg_id, session=session_pool)

# Если есть в базе и действующий:


# Добавить проверку на удаление!
# ----------------------------------------

# await message.answer(f'✅ <b>Ваш tg_id: {where_value}</b>', parse_mode='HTML')  # - тест tg_id

# ---------------------------------------- Условия проверки пользователя на регистрацию.
# Если tg_id - совпадает (зарегистрирован) - отправляемся проверять наличие его данных на локал БД:
# tg_id_in_jarvis = int(where_value)
# if tg_id_in_jarvis == async_check_telegram_id:

# Если пользователь есть в зарегистрированных, проверяем внутреннюю базу и полноту его данных \
# что бы наполнить ими базу данных

# ишем функцию в отдельлном модуле тк она будет вызываться еще и при старте:
# выбираем все telegram_id из таблицы регистрации (бота регистрации) в джарвисе \
# и джойним с аналогичной выборкой из локал бд (юзерс):

# если на внутреннюю, то лезем в бд, где находится клон (или запускаем клонирование сразу)
# * придумать механизм аутентификации если сотрудник удален.

# Если tg_id - отсутствует - отправляем регаться

# await message.answer(f'✅ <b>Ошибка подключения к серверу!</b>', parse_mode='HTML')

# ----------------------------------------# ----------------------------------------# ----------------------------------
# async def check_registration(message: types.Message):  # , session_pool: AsyncSession
#     """
#     Алгоритм:
#     Каждое сообщение пользователя проходит проверку на доступ по tg_id ссылаясь во внутреннюю базу.
#     Если такого tg_id не находится, то запрос осуществляется к удаленному хосту к таблице бота регистрации
#     + смотрим на удаление сотрудника. Если сотрудник удален - None, True - если есть, и False, если отсутствует.
#     Далее обновляем локальную базу данных.
#     Таким образом избавляемся от лишних нагрузок (запрос через ОРМ в Локал БД более шустрый и удобный,
#     а так же избавляемся от избыточных итераций.
#     """
#
#     # Вытаскиваем id пользователя при старте:
#     user_tg_id: int = message.from_user.id
#
#     while True:  # Цикличная проверка:
#
#         # Проверяем tg_id на серваке_DNS (если пользователь регился в авторизационном боте, то tg_id будет в базе.
#         # На выходе будет или булевое занчение или NULL !!!
#         check_is_deleted_value_in_jarvis = await get_data_in_jarvis_scalar(
#             await get_async_engine(CONFIG_JAR_ASYNCPG), is_deleted_value_for_one_id_tg, user_tg_id)
#
#         print(check_is_deleted_value_in_jarvis)
#         # ----------------------- Проверяем tg_id на удаление пользователя:
#
#         # Если пользователь не удален (в штате), тогда False:
#         if bool(check_is_deleted_value_in_jarvis) is False:
#
#             # @general_router.callback_query(StateFilter(None, StartUser.check_repeat), F.data.startswith('go_repeat'))
#             # Выводим приветствие в зависимости от типа айдишника
#             await message.answer(f'✅ <b>Доступ разрешен!</b>',
#                                  parse_mode='HTML',
#                                  reply_markup=get_callback_btns(
#                                      btns={'Продолжить': 'go_next'})
#                                  )  # прикрутить кнопку поддержки +)
#
#             # Чистим состояние от предыдущей итеррации:
#             await state.clear()
#
#             # Устанавливаем состояние для цикла проверки (Встает в ожидании нажатия кнопки):
#             await state.set_state(StartUser.check_next)
#
#             break
#
#         # Если есть в базе, но удален:
#         elif bool(check_is_deleted_value_in_jarvis) is True:
#
#             await message.answer(f'❌ <b> Доступ запрещен! Пользователь удален из системы!</b>',
#                                  parse_mode='HTML')
#             # обратитесь в поддержку, если это ошибочно
#
#             # Чистим состояние от предыдущей итеррации:
#             await state.clear()
#
#             break  # нужен ли?
#
#         # Если нет в базе, отправляем регаться:
#         elif bool(check_is_deleted_value_in_jarvis) is None:
#
#             await message.answer(
#                 # StateFilter(None),
#                 f'❌ <b>Доступ закрыт!\n Пройдите аутентификацию в <a>@authorize_sv_bot</a></b>'
#                 , parse_mode='HTML',
#                 reply_markup=get_callback_btns(
#                     btns={'Я прошел аутентификацию, продолжить!': 'go_repeat'}))
#
#             # Чистим состояние от предыдущей итеррации:
#             await state.clear()
#
#             # Устанавливаем состояние для цикла проверки (Встает в ожидании нажатия кнопки):
#             await state.set_state(StartUser.check_repeat)
#
#             # Ожидание следующего сообщения пользователя
#             @general_router.callback_query(
#                 StateFilter(StartUser.check_repeat), F.data.startswith('go_repeat'))
#
#             async def on_next(call: types.CallbackQuery, session_pool):
#
#                 #  todo Возможно сюда запихнуть еще раз обращение к базе данных и если зарегался то обновить,
#                 #  todo прервать цикл
#
#                 # Обновляем базу данных
#                 await updating_local_db(session_pool)  ## Возможно пересмотреть логику
#
#                 await check_registration(call.message)  # Запускаем проверку заново , session_pool
#                 await call.answer()  # Закрываем кнопку 'next' чтобы предотвратить повторные нажатия
#
#             break  # Прерываем цикл, чтобы избежать бесконечного ожидания сообщений
#
#         else:
#             # Отправляем регаться
#             await message.answer(
#                 f'❌ <b>Ошибка в данных на сервере, обратитесь в службу поддержку!</b>'
#                 , parse_mode='HTML', reply_markup=get_callback_btns(
#                     btns={'Оставить заявку': 'support'})
#             )  # прикрутить кнопку поддержки +
#
#             break
#
#
# # ------------------- конец