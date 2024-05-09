"""
Чат бот телеграмм

ЗадаЧа:

1. Приветственные сообщения (сразу без лишней воды:

"""

import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart  # Фильтор только для старта

from config_bot import *

# ----------------------------------------------------------------------------------------------------------------------
bot = Bot(token=API_TOKEN)
dp = Dispatcher()





# ------------------------ Тело
# Реакция на старт бота:
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    user = message.from_user.first_name  # Имя поальзователя
    await message.answer(f'Привет, {user}  на связи "Tasks bot"! \n'
                         f'Давай попробуем решить твой вопрос.')

# Ответ на вариации входящих сообщений:
@dp.message()
async def echo(message: types.Message):
    text = message.text

    if text in ['Привет', 'привет', 'hi', 'hello']:
        await message.answer('И тебе привет!')
    elif text in ['Пока', 'пока', 'До свидания']:
        await message.answer('И тебе пока!')
    else:
        await message.answer(message.text)






# ------------------------ Зацикливание работы бота
# Отслеживание событий на сервере тг бота:
async def run_bot():
    await dp.start_polling(bot)


# Запуск асинхронной функции run_bot:
asyncio.run(run_bot())
