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
from sqlalchemy import DateTime, Float, String, Integer, Text, Boolean, func  # - image LargeBinary
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# -------------------------------- Локальные модули



# ----------------------------------------------------------------------------------------------------------------------
# Тело базы данных:
class Base(DeclarativeBase):

    # Эти поля (в родительском классе) автоматически унаследуются дочерним класам (все ниже).
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


# Сотрудники розницы (кто обращается с проблемой).
class RetailUsers(Base):
    """
    Тянем из удаленного сервака данные о пользователях.
    """
    __tablename__ = 'retail_user_data'


    index_add: Mapped[int] = mapped_column(autoincrement=True) # орядковый номер добавления обратившегося сотрудника.

    tg_id: Mapped[int] = mapped_column(primary_key=True, nullable=False, index=True, unique=True)  # телеграмм id
    # id сотрудника в 1С и первичный ключ в этой таблице.
    code: Mapped[str] = mapped_column(String(50), unique=True)

    full_name: Mapped[str] = mapped_column(String(100))  # ФИО сотрудника
    post_id: Mapped[int] = mapped_column(nullable=False, unique=True)  # id Должности

    branch_name:Mapped[str] = mapped_column(String(200), nullable=False)
    rrs_name: Mapped[str] = mapped_column(String(100), nullable=False)
    division_name: Mapped[str] = mapped_column(String(100), nullable=False)

    user_mail: Mapped[str] = mapped_column(String(100), nullable=True)


# Сотрудники отдела аналитики:
class OAiTDepartment(Base):
    """
    Сделать мезанизм обновления сотрудников отдела с удаленной базы данных:
    """
    __tablename__ = 'oait_staff'

    # Порядковый номер добавления сотрудника.
    index_add: Mapped[int] = mapped_column(autoincrement=True)

    tg_id: Mapped[int] = mapped_column(primary_key=True, nullable=False, index=True, unique=True)  # телеграмм id
    # id сотрудника в 1С и первичный ключ в этой таблице.
    code: Mapped[str] = mapped_column(String(50), unique=True)

    full_name: Mapped[str] = mapped_column(String(100))  # ФИО сотрудника
    post_id: Mapped[int] = mapped_column(nullable=False, unique=True)  # id Должности

    user_mail: Mapped[str] = mapped_column(String(100), nullable=True)

    # статус сотрудника (занят ли или свободен) продумать насчет тех кто в отпуске # free = True, job = False
    employee_status: Mapped[bool] = mapped_column(nullable=False,  server_default='True')  # activity



# Для деловой переписки сотрудников в боте (хранение истории обращений).
class Request(Base):
    __tablename__ = 'requests_history' # request history Problems QuestsProblems tasks

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) # id request history

    code_id: Mapped[str] = mapped_column(String(50))  # id сотрудника в 1С и нешний ключ в этой таблице.
    # телеграмм id обращающегося пользователя
    request_tg_id: Mapped[int] = mapped_column(nullable=False, index=True, unique=True)
    # ответственное лицо - user_id(tg_id) может быть пусто = 0,значит не назначен ответственный (переназначен).
    responsible_person_id: Mapped[int] = mapped_column(nullable=True, server_default='0')
    #  Текст обращения (problem)
    request_message: Mapped[str] = mapped_column(Text())
    # Прикрепленные документы любого типа:
    documents: Mapped[bytes] = mapped_column() # LargeBinary
    # В работе ли заявка at work _complete статус запроса (insert, in_work, done complete (, onupdate='insert') )
    request_status: Mapped[str] = mapped_column(String(150), server_default='insert')

    id_tg: Mapped[int] = mapped_column(nullable=False, index=True, unique=True)  # телеграмм id

    # Ограничение полей:
    # __table_args__ = (ForeignKeyConstraint(['tg_id'],['RetailUsers.id_tg']))

# Список должностей:
# class ListPositions(Base):

# История обсуждения задач заказчика и исполнителя:
class Discussion(Base):
    __tablename__ = 'discussion_history'

    # id сообщения в истории обсуждения задач.
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # id обращения (request history) внешний ключ  [id -> requests_id].
    requests_id: Mapped[int] = mapped_column()
    # телеграмм id написавшего сообщение.
    id_tg: Mapped[int] = mapped_column(nullable=False, index=True, unique=True)
    #  Текст обращения (problem)
    request_message: Mapped[str] = mapped_column(Text())
    # Прикрепленные документы любого типа.
    documents: Mapped[bytes] = mapped_column()



    # дата создания и обновления будут наследоваться автоматически.



# ------------------------------ архив
# session_types: Mapped[float] = mapped_column(Float(asdecimal=True), nullable=False)
# code: Mapped[str] = mapped_column(Integer(), nullable=False, index=True, unique=True) # + # личный код сотрудника
# name:
#     # last_name:


# нужен ли? (разные запросы получатся)

#     # is_deleted?
#     session_types: Mapped[str] = mapped_column(String(50),
#                                                nullable=False)  # разрешенный тип сессии (админ, розница и тд.)
#     # rrs_id: Mapped[int] = mapped_column(nullable=False) # ? не нужно
#     # branch_id: Mapped[int] = mapped_column(nullable=False) # ? не нужно
## Для идентификации зарегистрированных пользователей (сотрудников) в системе.