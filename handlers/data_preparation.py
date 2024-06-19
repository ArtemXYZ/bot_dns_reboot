"""Модуль предназначен для подготовки данных пришедших из келбеков
(интерпретация келбек ключей для генерации данных)
"""

# from working_databases.orm_query_builder import *
# from aiogram.types import CallbackQuery


def generator_category_data(selected_subcategory: str) -> dict:
    """Позже переписать и упростить"""

    # def generator_category_data(callback_data: CallbackQuery):
    # Узнаем какая кнопка была нажата:
    # selected_subcategory = callback_data.data

    # Отбрасываем не нужные события для последующей записи:
    if selected_subcategory in ('problem_cancel', 'problem_inline_back'):
        pass
    else:
        # Для ветки АНАЛИТИКА (problem_analytics):
        if selected_subcategory == 'problem_dashboards':

            write_to_base = {
                'name_category': 'problem_analytics', 'name_subcategory': 'problem_dashboards',
                'category_id': 1, 'subcategory_id': 1}  # tg_id - получим в функции отлавливания текста.
            # print(write_to_base)

        elif selected_subcategory == 'problem_tags':

            write_to_base = {
                'name_category': 'problem_analytics', 'name_subcategory': 'problem_tags',
                'category_id': 1, 'subcategory_id': 2}
            # print(write_to_base)

        elif selected_subcategory == 'problem_bot':

            write_to_base = {
                'name_category': 'problem_analytics', 'name_subcategory': 'problem_bot',
                'category_id': 1, 'subcategory_id': 3}
            # print(write_to_base)


        # Для ветки ФОРМАТЫ (problem_formats):
        elif selected_subcategory == 'problem_coming':

            write_to_base = {
                'name_category': 'problem_formats', 'name_subcategory': 'problem_coming',
                'category_id': 2, 'subcategory_id': 4}
            # print(write_to_base)

        elif selected_subcategory == 'problem_no_coming':

            write_to_base = {
                'name_category': 'problem_formats', 'name_subcategory': 'problem_no_coming',
                'category_id': 2, 'subcategory_id': 5}
            # print(write_to_base)

        elif selected_subcategory == 'problem_ce':

            write_to_base = {
                'name_category': 'problem_formats', 'name_subcategory': 'problem_ce',
                'category_id': 2, 'subcategory_id': 6}
            # print(write_to_base)

        elif selected_subcategory == 'problem_borders':

            write_to_base = {
                'name_category': 'problem_formats', 'name_subcategory': 'problem_borders',
                'category_id': 2, 'subcategory_id': 7}
            # print(write_to_base)

        elif selected_subcategory == 'problem_unsold':

            write_to_base = {
                'name_category': 'problem_formats', 'name_subcategory': 'problem_unsold',
                'category_id': 2, 'subcategory_id': 8}
            # print(write_to_base)


        # Для ветки ТОВАРООБОРОТ (problem_trade_turnover):
        elif selected_subcategory == 'problem_sales':

            write_to_base = {
                'name_category': 'problem_trade_turnover', 'name_subcategory': 'problem_sales',
                'category_id': 3, 'subcategory_id': 9}
            # print(write_to_base)

        elif selected_subcategory == 'problem_merch':

            write_to_base = {
                'name_category': 'problem_trade_turnover', 'name_subcategory': 'problem_merch',
                'category_id': 3, 'subcategory_id': 10}
            #print(write_to_base)

        elif selected_subcategory == 'problem_price':

            write_to_base = {
                'name_category': 'problem_trade_turnover', 'name_subcategory': 'problem_price',
                'category_id': 3, 'subcategory_id': 11}
            # print(write_to_base)

        elif selected_subcategory == 'problem_purchase':

            write_to_base = {
                'name_category': 'problem_trade_turnover', 'name_subcategory': 'problem_purchase',
                'category_id': 3, 'subcategory_id': 12}
            # print(write_to_base)

        elif selected_subcategory == 'problem_ve':

            write_to_base = {
                'name_category': 'problem_trade_turnover', 'name_subcategory': 'problem_ve',
                'category_id': 3, 'subcategory_id': 13}
            # print(write_to_base)

        elif selected_subcategory == 'problem_stm':

            write_to_base = {
                'name_category': 'problem_trade_turnover', 'name_subcategory': 'problem_stm',
                'category_id': 3, 'subcategory_id': 14}
            # print(write_to_base)

        elif selected_subcategory == 'problem_discount':

            write_to_base = {
                'name_category': 'problem_trade_turnover', 'name_subcategory': 'problem_discount',
                'category_id': 3, 'subcategory_id': 15}
            # print(write_to_base)

    return write_to_base











#
# async def download_file(file_path: str):
#     # Формируем URL для скачивания файла с сервера Telegram
#     download_url = f'https://api.telegram.org/file/bot{API_TOKEN}/{file_path}'
#
#     async with aiohttp.ClientSession() as session:
#         # Выполняем HTTP GET запрос для скачивания файла
#         async with session.get(download_url) as resp:
#             if resp.status == 200:
#                 # Возвращаем бинарное содержимое файла
#                 return await resp.read()
#             else:
#                 return None