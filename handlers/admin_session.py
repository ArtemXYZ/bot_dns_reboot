"""
Модуль обработки событий для дмина
"""

# -------------------------------- Стандартные модули

# -------------------------------- Сторонние библиотеки
from aiogram import types,Bot, Router, F
from aiogram.filters import CommandStart, Command, StateFilter, or_f
from aiogram.client.default import DefaultBotProperties  # Обработка текста HTML разметкой

# -------------------------------- Локальные модули
from filters.chats_filters import * #, IsAdmin


from menu.button_generator import get_keyboard


admin_router = Router()

# Устанавливаем фильтр на входящие события для роутера админа:
admin_router.message.filter(ChatTypeFilter(['private']), UsersAdminSession())
# UsersAdminSession - фильтрует только для админа
admin_router.edited_message.filter(ChatTypeFilter(['privat']), UsersAdminSession())
#  ChatTypeFilter - 'group', 'supergroup'

# ------------------------------------------------- Тело модуля
ADMIN_KB = get_keyboard(
    "Добавить товар",
    "Изменить товар",
    "Удалить товар",
    "Я так, просто посмотреть зашел",
    placeholder="Выберите действие",
    sizes=(2, 1, 1)
)


@admin_router.message(Command("new"))
async def add_product(message: types.Message):
    await message.answer("Привет админ! Что хочешь сделать?", reply_markup=ADMIN_KB)


# Функция вытаскивает из сообщений id админа и наполняет ими список:





# -------------------------------------- Ответ на вариации входящих сообщений:
# Только жесткое совпадение по словам, нужно доделать разделитель слов в сообщении потозже!
@admin_router.message()
async def echo(message: types.Message):
    text = message.text

    if text in ['Привет', 'привет', 'hi', 'hello']:
        await message.answer('И тебе привет!')
    elif text in ['Пока', 'пока', 'До свидания']:
        await message.answer('И тебе пока!')
    else:
        await message.answer(message.text)



#  -------------------------------------------------- Огрызки прозапас

# # Админ = создатель группы (переделать потом)
# # Функция вытаскивает из сообщений id админа и наполняет ими список:
# @admin_router.message(Command("admin"))
# async def get_admins(message: types.Message, bot: Bot):
#     chat_id = message.chat.id
#
#     # У бота метод get_chat_administrators принимает id группы (chat_id) и выдает список из участников.
#     # В нем будут перечисленны участники с правами как creator и administrator.
#     admins_list = await bot.get_chat_administrators(chat_id)
#
#
#     #  Далее, пробегаемся по списку и в зависимости от условия наполняем список
#     admins_list = [
#         member.user.id
#         for member in admins_list
#         if member.status == "creator" or member.status == "administrator"
#     ]
#
#     # 'Апдейтим' список админов:
#     bot.my_admins_list = admins_list
#
#     # Если написавший пользователь есть в админ листе, то мы удаляем эту команду.
#     if message.from_user.id in admins_list:
#         await message.delete()









# @admin_router.message(F.text == "Я так, просто посмотреть зашел")
# async def starring_at_product(message: types.Message):
#     await message.answer("ОК, вот список товаров")
#
#
#
#     @admin_router.message(CommandStart())
# async def start_cmd(message: types.Message):
#     await message.answer(
#         "Привет, я виртуальный помощник",
#         reply_markup=get_keyboard(
#             "Меню",
#             "О магазине",
#             "Варианты оплаты",
#             "Варианты доставки",
#             placeholder="Что вас интересует?",
#             sizes=(2, 2)
#         ),
#     )
