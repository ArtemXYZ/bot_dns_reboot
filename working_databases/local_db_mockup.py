"""
ОРМ макет локальной базы данных.
Содержит перечень всех полей базы данных.

Логика:
Перед входом в бот, пользователь проходит регистрацию
и если прошел, то продолжает сессию под определенным типом (админ, розница и тд.).
тип сессии определяется как розница (retail), если не другое значение (admin, oait
"""

# -------------------------------- Стандартные модули
# -------------------------------- Сторонние библиотеки
from sqlalchemy import DateTime, Float, String, Integer, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# -------------------------------- Локальные модули


# Тело базы данных:
# ----------------------------------------------------------------------------------------------------------------------
class Base(DeclarativeBase):

    # Эти поля (в родительском классе) автоматически унаследуются дочерним класам (все ниже).
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

# Для идентификации зарегистрированных пользователей (сотрудников) в системе.
class User(Base):
    __tablename__ = 'user_dataid'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) # +
    id_tg: Mapped[int] = mapped_column(Integer(), nullable=False, index=True, unique=True)  # телеграмм id
    session_types:Mapped[str] = mapped_column(String(50), nullable=False)  # разрешенный тип сессии (админ, розница и тд.)


# Для деловой переписки сотрудников в боте (хранение истории обращений).
class RequestHistory(Base):
    __tablename__ = 'history_requests' # request history Problems QuestsProblems tasks

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) # +
    tg_id: Mapped[int] = mapped_column(Integer(), nullable=False, index=True, unique=True)  # телеграмм id
    post_id: Mapped[int] = mapped_column(Integer(), nullable=False, unique=True)  # id Должности

    # name:
    # last_name:
    full_name: Mapped[str] = mapped_column(String(100))

    rrs: Mapped[str] = mapped_column(String(100))  # !!
    division: Mapped[str] = mapped_column(String(100))  # !!

    problem_message: Mapped[str] = mapped_column(Text())
    image: Mapped[str] = mapped_column(String(150))  # todo переделать в сохранение не текста а картинки.
    status: Mapped[str] = mapped_column(String(150), default='insert') # insert, in_work, done (, onupdate='insert')
    # branch_id ?

    # Ограничение полей:
    __table_args__ = (ForeignKeyConstraint(['tg_id'],['User.id_tg']))

# Список должностей:
# class ListPositions(Base):



# session_types: Mapped[float] = mapped_column(Float(asdecimal=True), nullable=False)
# code: Mapped[str] = mapped_column(Integer(), nullable=False, index=True, unique=True) # + # личный код сотрудника