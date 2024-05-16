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

# -------------------------------- Локальные модули
from handlers.text_message import swearing_list  # Список ругательств:
from filters.chats_filters import ChatTypeFilter

# from aiogram.utils.formatting import as_list, as_marked_section, Bold, Italic

# from menu import keyboard_menu  # Кнопки меню - клавиатура внизу
from menu import inline_menu  # Кнопки встроенного меню - для сообщений

from working_databases.query_builder import *

from working_databases.configs import *

# Назначаем роутер для всех типов чартов:
general_router = Router()


# фильтрует (пропускает) только личные сообщения и только определенных пользователей:
# general_router.edited_message.filter(ChatTypeFilter(['privat']), )

# engine_obj = get_async_engine(CONFIG_JAR_ASYNCPG)


# ----------------------------------------------------------------------------------------------------------------------
# Вспомогательная функция проверки регистрации:
async def chek_registration(message: types.Message):
    while True:  # Цикличная проверка:

        # ---------------------------------------- Подготовка данных:
        # Вытаскиваем id пользователя при старте:
        where_value: int = message.from_user.id  # Тут все норм.
        # where_value: int = 460378146  # (Димон для теста)

        # Проверяем tg_id на серваке_DNS (если пользователь регился в авторизационном боте, то tg_id будет в базе.
        async_check_telegram_id = await async_select('inlet.staff_for_bot', 'tg',
                                                     'tg', where_columns_value=where_value,
                                                     engine_obj=await get_async_engine(CONFIG_JAR_ASYNCPG)
                                                     )  # на выходе: либо Нул либо telegram_id
        # ----------------------------------------

        # await message.answer(f'✅ <b>Ваш tg_id: {where_value}</b>', parse_mode='HTML')  # - тест tg_id

        # ---------------------------------------- Условия проверки пользователя на регистрацию.
        # Если tg_id - отсутствует - отправляем регаться
        if int(where_value) == async_check_telegram_id:

            # 1 Проверяем тип айдишника (админ или зам. или розница)
            # * добавить в режиме админа регистрацию сотрудников по типу пользователя и режим входа под другими оболочками

            # Ссылаемся на внутреннюю базу или удаленную.

            # если на внутреннюю, то лезем в бд, где находится клон (или запускаем клонирование сразу)
            # * придумать механизм аутентификации если сотрудник удален.

            # создание базы при запуске бюота = тестовую программу, какую нибудь.

            # Выводим приветствие в зависимости от типа айдишника
            await message.answer(f'✅ <b>Доступ разрешен!</b>', parse_mode='HTML')

            break  # Прерываем цикл, если доступ разрешен:

        # Если tg_id - отсутствует - отправляем регаться
        else:
            if async_check_telegram_id is not None:
                await message.answer(
                    f'❌ <b>Ошибка в данных на сервере, обратитесь в службу поддержку!</b>'
                    , parse_mode='HTML', reply_markup=inline_menu.get_callback_btns(
                        btns={'Оставить заявку': 'support'})
                )  # прикрутить кнопку поддержки +

            else:
                await message.answer(
                    f'❌ <b>Доступ закрыт!'
                    f'\n Пройдите аутентификацию в <a>@authorize_sv_bot</a></b>'
                    , parse_mode='HTML', reply_markup=inline_menu.get_callback_btns(
                        btns={'Я прошел аутентификацию, продолжить!': 'next'}))

            # Ожидание следующего сообщения пользователя
            @general_router.callback_query(lambda call: call.data == 'next')
            async def on_next(call: types.CallbackQuery):
                await chek_registration(call.message)  # Запускаем проверку заново
                await call.answer()  # Закрываем кнопку 'next' чтобы предотвратить повторные нажатия

            break  # Прерываем цикл, чтобы избежать бесконечного ожидания сообщений


@general_router.message(CommandStart())
async def on_start(message: types.Message):
    await chek_registration(message)
    #  todo удалять кнопки и все сообщение раньше, выводить приветствие!

    await message.delete()  # Удаляем сообщение и кнопки?. todo !!!

    # await message.answer(f'✅ <b>Ошибка подключения к серверу!</b>', parse_mode='HTML')


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


# # 0. Первичное приветствие всех пользователей при старте.
# # await message.answer(
#         #     f'Вас приветствует корпоративный бот <b>"DNS requests Helper"</b> одноименной торговой розничной сети.\n'
#         #     f'Я создан для веддения служебных обращений по возникающим вопросам подразделений '
#         #     f'в ходе их повседневной деятельности..добавить....:\n'
#         #     f'Для дальнейшей работы, необходимо пройти атентификацию, доступ разрешен <b>только сотрудникам сети</b>.'
#         #     , parse_mode='HTML', reply_markup=inline_menu.get_callback_btns(btns={
#         #                          'Пройти атентификацию': 'get_type_users'}))   # , parse_mode='HTML'
#         #
#         #     # todo Добавить приветственную картинку и отредактить текст.
