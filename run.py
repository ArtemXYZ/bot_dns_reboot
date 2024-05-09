
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from config_bot import *



bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer('Это была команда старт')

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

