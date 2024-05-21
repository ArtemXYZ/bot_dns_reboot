""""Модуль подключений к базам данных."""

# ---------------------------------- Импорт стандартных библиотек Пайтона
# ---------------------------------- Импорт сторонних библиотек
from sqlalchemy import create_engine  # Библиотека для создания подключений к БД
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import OperationalError
# from sqlalchemy.sql.expression import table
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import text

from working_databases.configs import *


# import psycopg2
# ---------------------------------- Импорт локальных модулей

# ----------------------------------------------------------------------------------------------------------------------

# ------------------------------------------------------------ Подключение к martsv БД
# @debug_requests
def get_connect(ANY_CONFIG: dict | URL | str):  # +
    '''Функция создания подключения к базе данных. На вход принимает файл конфигурации'''
    # добавить позже описание переменных

    try:  # Блок исключений ошибок при осуществлении подключения:
        # any_config # 1.Проверка на отсутствие файла концигурации подкючения: если нет данных на вход: !!

        # Проверка типа входной конфигурации подключения:
        # # Если на вход url_string:
        # if isinstance(any_config, URL) == True:
        #     url_string = any_config

        # Если на вход конфигурация в словаре:
        if isinstance(ANY_CONFIG, dict) == True:
            url_string = URL.create(**ANY_CONFIG)  # 1. Формируем URL-строку соединения с БД.
            #  Эквивалент: url_string = (f'{drivername}://{username}:{password}@{host}:{port}/{database}')
        elif isinstance(ANY_CONFIG, str) == True:
            url_string = ANY_CONFIG
        else:
            url_string = None

        engine = create_engine(url_string)  # 2. Создаем переменную подключения к БД.
        #  pool_pre_ping=True - параметр проверяет соединения на жизнеспособность при каждом извлечении из пула
        # ,echo=True - выводит логирование всех действий.

        connection = engine.connect()

        return connection
    # except Exception:
    #     # 1. Значит выведет:
    #     print(f'No connection configuration database!\n(Отсутствует конфигурация подключения к базе данных!')
    except OperationalError as first_error:
        print(f'Ошибка подключения к серверу: {first_error}')  # PostgreSQL
    #     Эта ошибка является ошибкой DBAPI и возникает из драйвера базы данных (DBAPI)

    #  Если наступит ошибка в значениях:
    except (ValueError, TypeError):
        print(f'Ошибка подключения к базе данных! Проверьте входные данные {ANY_CONFIG} \n'
              f'и зависимые переменные: формирование url_string: {ANY_CONFIG}, engine: {engine}')

    #  Другие любые ошибки (скорее всего будут относиться к синтаксису):
    except Exception as error:
        print(f'Ошибка синтаксиса: {type(error).__name__}, сообщение: {str(error)}!')  #


def select_values(ANY_CONFIG, tb_name: str, columns_search: str, where_columns_name: str,
                  where_columns_value: any):  # , any_config , results_aal_or: str schema_name: str,
    """
    Функция выбирает данные по идентификатору (id) через сырой запрос.

    """
    connection = get_connect(ANY_CONFIG)  # Создаем подключение через локальный модуль

    # Это работает.
    sql = text(
        f"SELECT {tb_name}.{columns_search} FROM {tb_name} WHERE {tb_name}.{where_columns_name} = '{where_columns_value}'")
    # {schema_and_table} WHERE {where_columns_name} = {where_columns_value}

    # Сохраняем в базу:
    with connection:
        result_temp = connection.execute(sql)

        # if results_aal_or == 'all':
        #     result = result_temp.all()
        #
        # elif results_aal_or == 'first':
        #     result = result_temp.first()
        #
        # elif results_aal_or == 'one':
        #     result = result_temp.one()
        #
        # elif results_aal_or == 'one_or_none':
        #     result = result_temp.one_or_none()

    return result_temp.scalar()

# Работает !
# a = select_values(CONFIG_MART_SV, 'inlet.staff_for_bot', 'code',
#                   'tg', 473592116)
#
# print(a)

# connection.close()  # Закрытие соединения вручную. Важно! Если не закрыть соединение, будут ошибки!
# schema_and_table = table(schema=schema_name, name=tb_name,columns=columns_search)
#     select(schema_and_table.where(t1.c.name == "some name 1"))
