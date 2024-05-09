"""
Модуль обработки событий для обычных пользователей (филиалы)
"""

from aiogram import types, Router
from aiogram.filters import CommandStart, Command

user_private_router = Router()

# -------------------------------------------------  Тело модуля
# Обработка событий на команду /start
@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    user = message.from_user.first_name  # Имя пользователя
    await message.answer(f'<b>Привет</b>, {user}!  На связи <b>"Tasks bot meneger".</b>\n'
                         f'Я помогаю в решении вопросов и проблем, возникающих в ходе повседневной деятельности '
                         f'филиалов по дивизиону "Средняя Волга".\n'
                         f'Создаю заявки и распределяю их на исполнителей в соответствии с их компетенцией, '
                         f'исходя из категории обращения. '
                         f'Направляю уведомления по завершении обработки заявки заказчику, и много другое...')

    await asyncio.sleep(1)  # Добавляем задержку для второго сообщения.

    # Краткое описание возможностей бота, зачем нужен:
    await message.answer(f'Давай попробуем решить твой вопрос!')

    # здесь вызвать кнопки контекстные: создать обращение, вызвать справку.











# /new
@user_private_router.message(Command('new'))
async def new_cmd(message: types.Message):

    #  0. Окно выбора категории обращения +
    # пробелы не трогать внутри текста (настроено методом подбора)! Иначе, собъется выравнивание (ТЛГ сжимает пробелы)
    await message.answer(f'Выбери тему обращения (категорию вопроса / проблемы):\n'     
                                                                   
                         f'\n'     
                         # ---------------------- Отпрвить к Аналитикам:                   
                         f'<b><u>I. АНАЛИТИКА</u></b>\n' # Жирный, подчеркнутый
                         f'Вопросы (проблемы) с:\n' 
                         f' *  <b>Дашбордами:</b>                            <em>/dashboards</em>.\n' # 17
                         f' *  <b>Ценниками:</b>                                <em>/price_tags_tool</em>\n'
                         f' *  <b>Telegram-ботами:</b>                     <em>/bots</em>\n'   # 14
                         f' *  <b>Ценниками:</b>                                <em>/analytics</em>\n'  # 18
                                                  
                         f'\n' 
                         # ---------------------- Отпрвить к Форматам:
                         f'<b><u>II. ФОРМАТЫ</u></b>\n'
                         f'Вопросы (проблемы) по:\n' 
                         f' *  <b>АР (везет товар):</b>                       <em>/prod_coming</em>.\n' 
                         f' *  <b>АР (не везет товар):</b>                 <em>/not_prod_coming</em>\n'
                         f' *  <b>СЕ:</b>                                                   <em>/ce</em>\n'
                         f' *  <b>Границам категорий:</b>             <em>/borders</em>\n'
                         f' *  <b>Лежакам:</b>                                     <em>/unsold</em>\n'

                         f'\n'
                         # ---------------------- Отпрвить товарообору:
                         f'<b><u>III. ТОВАРООБОРОТ</u></b>\n' 
                         f'Вопросы (проблемы) по:\n'                                     
                         f' *  <b>МП:</b>                                                 <em>/sales</em>.\n' 
                         f' *  <b>Мерчам (не везет товар):</b>      <em>/merch</em>\n'
                         f' *  <b>Ценам на товар:</b>                        <em>/price</em>\n'
                         f' *  <b>Закупке товара:</b>                        <em>/purchase</em>\n'                         
                         f' *  <b>ВЕ:</b>                                                  <em>/be</em>\n'
                         f' *  <b>СТМ:</b>                                               <em>/stm</em>\n'
                         f' *  <b>Уценке:</b>                                         <em>/discount</em>\n'
                         # f'или напиши мне прямо в чарт '
                         f'\n'
                         f'и я направлю твою <b>"БОЛЬ"</b> нужным людям!')




# Кнопка создать обращение.


# инлайн кнопка выбрать обращение
# копка клавиатура внизу создать обращение



# Ответ на вариации входящих сообщений:
# Только жесткое совпадение по словам, нужно доделать разделитель слов в сообщении потозже!
@user_private_router.message()
async def echo(message: types.Message):
    text = message.text

    if text in ['Привет', 'привет', 'hi', 'hello']:
        await message.answer('И тебе привет!')
    elif text in ['Пока', 'пока', 'До свидания']:
        await message.answer('И тебе пока!')
    else:
        await message.answer(message.text)




# @user_private_router.message(CommandStart())
# async def start_cmd(message: types.Message):
#     await message.answer("Привет, я виртуальный помощник")