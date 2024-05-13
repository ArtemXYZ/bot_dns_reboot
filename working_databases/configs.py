"""
Все конфиги проекта
"""
# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------- Импорт стандартных библиотек Пайтона
import os

# ---------------------------------- Импорт сторонних библиотек
from dotenv import find_dotenv, load_dotenv  # Для переменных окружения
load_dotenv(find_dotenv())  # Загружаем переменную окружения

# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------- Конфигурации подключения к базам данных
CONFIG_JAR = {
    'drivername': os.environ.get("CONFIG_JAR_DRIVERNAME"),
    'username': os.environ.get("CONFIG_JAR_USERNAME"),
    'password': os.environ.get("CONFIG_JAR_PASSWORD"),
    'host': os.environ.get("CONFIG_JAR_HOST"),
    'port': os.environ.get("CONFIG_JAR_PORT"),
    'database': os.environ.get("CONFIG_JAR_DATABASE")
}
