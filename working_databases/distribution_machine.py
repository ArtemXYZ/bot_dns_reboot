"""Машина распределения задач (входящих сообщений)."""

from working_databases.orm_query_builder import *

# Определение правил распределения:
async def generator_mailing_list(category_id: int, session_pool: AsyncSession ) ->  list:

    """
    Выполняем проверку пользователей, кто не занят (надо доделать логику), - упраздняем!
     кто не в отпуске - holiday_status
    data_request_message_to_send:  набор данных (категории обращения, текст обращения)
    ищем только по id (что бы в последствии можно было изменять имена категорий).

    # На основе категории обращения делаем выборку (распределение)
    # Если category_id == 1 # (problem_analytics), то весь отдел аналитики
    # -   Выбрать весь отдел аналитики, кто не в отпуске
    #     -    доп проверка по конкретному человеку

    # учитывать статус человека в отпуске!

    branch_id  =  отдел.
    """

    # Принимаем данные в сообщении, вытягиваем категорию обращения
    # category_id: int = data_request_message_to_send['category_id']  # категория

    # todo Пока в первом приближении это не будет использоваться (на будущее) !!!
    # todo subcategory_id: int = data_request_message_to_send['subcategory_id']  # подкатегория

    # Переменные в последующем планируем динамично менять из админки: # todo на будущее вынести это в базу данных
    branch_id_analytics = 6712
    branch_id_formats = 6713
    branch_id_trade_turnover = 6711


    # Для ветки АНАЛИТИКА (problem_analytics):
    if category_id == 1:
        # выборка людей на кого пойдет задача (а будущее).
        # Выбрать весь отдел аналитики, кто не в отпуске
        all_user_id_list = await get_all_user_id_by_branch_id(branch_id_analytics, session_pool)
        # print(f'all_user_id_list 2 !!! {all_user_id_list}')

    # Для ветки ФОРМАТЫ (problem_formats):
    elif category_id == 2:

        all_user_id_list = await get_all_user_id_by_branch_id(branch_id_formats, session_pool)

    # Для ветки ТОВАРООБОРОТ (problem_trade_turnover):
    elif category_id == 3:

        all_user_id_list = await get_all_user_id_by_branch_id(branch_id_trade_turnover, session_pool)

    return all_user_id_list


