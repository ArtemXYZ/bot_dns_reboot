"""Машина распределения задач (входящих сообщений)."""


# Определение правил распределения:

# 'АНАЛИТИКА'
# category_id = 1
# 'ФОРМАТЫ'
# 'ТОВАРООБОРОТ'
# 'ОТМЕНА'
#
#
#
#
#
# # def generator_mailing_list(data_request_message_to_send: str) ->  list:
#     """
#     Выполняем проверку пользователей, кто не занят (надо доделать логику), кто не в отпуске - holiday_status
#     data_request_message_to_send:  набор данных (категории обращения, текст обращения)
#     """


    #
    # # Принимаем данные в сообщении, вытягиваем категорию обращения
    # category_id: str = data_request_message_to_send['category_id']  # категория
    # subcategory_id: str = data_request_message_to_send['subcategory_id']  # подкатегория

    # На основе категории обращения делаем выборку (распределение)