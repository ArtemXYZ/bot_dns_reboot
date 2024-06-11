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
from sqlalchemy import DateTime, Float, String, Integer, Text, Boolean, func, ForeignKey, LargeBinary
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List


# from __future__ import annotations
# -------------------------------- Локальные модули


# ----------------------------------------------------------------------------------------------------------------------
# Тело базы данных:
class Base(DeclarativeBase):
    # Эти поля (в родительском классе) автоматически унаследуются дочерним класам (все ниже).
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


# Сотрудники все
class Users(Base):
    """
    Тянем из удаленного сервака данные о пользователях.
    """
    __tablename__ = 'user_data'

    # index_add: Mapped[int] = mapped_column(autoincrement=True) # порядковый номер добавления обратившегося сотрудника.
    # телеграмм id
    id_tg: Mapped[int] = mapped_column(primary_key=True, autoincrement=False, nullable=False,
                                       unique=True)  # Pk  index=True,
    # chat_id: Mapped[int] = mapped_column(nullable=True, unique=True)  # server_default=0

    # # id сотрудника в 1С и первичный ключ в этой таблице.
    code: Mapped[str] = mapped_column(String(50), unique=True)
    # session_type_id: Mapped[int] = mapped_column(nullable=True, server_default='None')
    #  session_type_id: 0 - ритейл, 1 - Оаит, 2 -
    session_type: Mapped[str] = mapped_column(String(100), nullable=True)  # под запрос в SQL CASE !

    full_name: Mapped[str] = mapped_column(String(100), nullable=False)  # ФИО сотрудника

    post_id: Mapped[int] = mapped_column(nullable=False)  # id Должности
    post_name: Mapped[str] = mapped_column(Text(), nullable=False)

    branch_id: Mapped[int] = mapped_column(nullable=False)  # + для фильтрации отделов.
    branch_name: Mapped[str] = mapped_column(String(200), nullable=False)
    rrs_name: Mapped[str] = mapped_column(String(100), nullable=False)
    division_name: Mapped[str] = mapped_column(String(100), nullable=False)

    user_mail: Mapped[str] = mapped_column(String(100), nullable=False)

    is_deleted: Mapped[bool] = mapped_column(nullable=True)  # в базе есть пустые значения, по этому True

    # статус сотрудника (занят ли или свободен)  # free = True, job = False (ри добавлении из бд - пусто, после апдейт
    employee_status: Mapped[bool] = mapped_column(nullable=False,
                                                  server_default='False')  # activity , server_default='Null'
    holiday_status: Mapped[bool] = mapped_column(nullable=False)  # Если в отпуске, то тру.
    admin_status: Mapped[bool] = mapped_column(nullable=False, server_default='False')  # Если админ, то тру.

    #
    # Отношение "один ко многим" Users с Request
    one_user_to_many_requests: Mapped[list['Requests']] = relationship(back_populates='many_requests_to_many_users')

    # -------------------------------------- Ограничение полей:
    # __table_args__ = (ForeignKeyConstraint(['tg_id'],['Users.post_id']))


# Для деловой переписки сотрудников в боте (хранение истории обращений).
class Requests(Base):
    __tablename__ = 'requests_history'  # request history Problems QuestsProblems tasks

    # id request history
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # code_id: Mapped[str] = mapped_column(String(50))  # id сотрудника в 1С и внешний ключ в этой таблице.

    # телеграмм id обращающегося пользователя
    tg_id: Mapped[int] = mapped_column(ForeignKey('user_data.id_tg'), nullable=False, index=True)  # Fk

    # ответственное лицо - user_id(tg_id) может быть пусто = 0,значит не назначен ответственный (переназначен).
    responsible_person_id: Mapped[int] = mapped_column(nullable=True, server_default='0')
    #  Текст обращения (problem)
    request_message: Mapped[str] = mapped_column(Text(), nullable=True)
    # Прикрепленные документы любого типа:
    doc_status: Mapped[bool] = mapped_column(nullable=False) # Вложены ли документы.

    #  ---------------------------- Идентификаторы
    # Категория обращения "Главная" (в какой отдел распределять)
    category_id: Mapped[int] = mapped_column(nullable=False, index=True)
    name_category: Mapped[str] = mapped_column(String(50), nullable=False)
    #
    # # Подкатегория обращения (по какому виду деятельности распределять)
    subcategory_id: Mapped[int] = mapped_column(nullable=False, index=True)
    name_subcategory: Mapped[str] = mapped_column(String(50), nullable=False)
    #  ---------------------------- Идентификаторы

    # В работе ли заявка: "at_work" , "complete" - статус запроса (insert, in_work, done или complete (, onupdate='insert') )
    request_status: Mapped[str] = mapped_column(String(150), server_default='insert')

    # Отношение "многие ко одному" Requests с Users
    many_requests_to_many_users: Mapped['Users'] = relationship("Users", back_populates="one_user_to_many_requests")

    # Отношение "один ко многим"  Request c Discussion
    one_requests_to_many_discussion: Mapped[list['Discussion']] = relationship(
        back_populates='many_discussion_to_one_requests')

    # Отношение "один ко многим" Request c DocFileRequests
    one_recuest_to_many_doc: Mapped[list['DocFileRequests']] = relationship(back_populates='many_doc_to_one_recuest')

    # back_populates - В двунаправленной связи доступ к связанным объектам может быть осуществлен из обоих концов связи.

    # Ограничение полей:
    # __table_args__ = (ForeignKeyConstraint(['tg_id'],['RetailUsers.id_tg']))


# История обсуждения задач заказчика и исполнителя:
class Discussion(Base):
    __tablename__ = 'discussion_history'

    # id сообщения в истории обсуждения задач.
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # id обращения (request history) внешний ключ  [id -> requests_id].
    requests_id: Mapped[int] = mapped_column(ForeignKey('requests_history.id'), nullable=False)  # Fk

    # телеграмм id написавшего сообщение.
    tg_id: Mapped[int] = mapped_column(nullable=False, index=True, unique=False)
    #  Текст обращения (problem)
    request_message: Mapped[str] = mapped_column(Text())
    # Прикрепленные документы любого типа:
    doc_status: Mapped[bool] = mapped_column(nullable=False)  # Вложены ли документы.

    # Отношение "многие ко одному" Discussion c Requests
    many_discussion_to_one_requests: Mapped['Requests'] = relationship("Requests",
                                                                       back_populates="one_requests_to_many_discussion")

    # Отношение "один ко многим" Discussion c DocFileDiscussion
    one_discussion_to_many_doc: Mapped[list['DocFileDiscussion']] = relationship(
        back_populates='many_doc_to_one_discussion')

    # дата создания и обновления будут наследоваться автоматически.


class DocFileRequests(Base):
    """
    Сохраняем все документы из обращений.
    """
    __tablename__ = 'all_doc_requests'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # id - либо обращения ли бо дискусии
    requests_id: Mapped[int] = mapped_column(ForeignKey('requests_history.id'), index=True, unique=False)

    file_id: Mapped[str] = mapped_column(String(256))  # Telegram использует строки для идентификаторов файлов,
    # чтобы обеспечить уникальность и избежать коллизий.
    file_name: Mapped[str] = mapped_column(String(256))
    file_content: Mapped[bytes] = mapped_column(LargeBinary)
    comment: Mapped[str] = mapped_column(Text())

    # Отношение "многие ко одному" DocFileRequests с Requests
    many_doc_to_one_recuest: Mapped['Requests'] = relationship("Requests",
                                                               back_populates="one_recuest_to_many_doc")


class DocFileDiscussion(Base):
    """
    Сохраняем все документы из дискуссий.
    """
    __tablename__ = 'all_doc_discussion'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # id - либо обращения ли бо дискусии
    discussion_id: Mapped[int] = mapped_column(ForeignKey('discussion_history.id'), index=True, unique=True)

    file_id: Mapped[str] = mapped_column(String(256))  # Telegram использует строки для идентификаторов файлов,
    # чтобы обеспечить уникальность и избежать коллизий.
    file_name: Mapped[str] = mapped_column(String(256))
    file_content: Mapped[bytes] = mapped_column(LargeBinary)
    comment: Mapped[str] = mapped_column(Text())

    # Отношение "многие ко одному" DocFileDiscussion с Discussion
    many_doc_to_one_discussion: Mapped['Discussion'] = relationship("Discussion",
                                                                    back_populates="one_discussion_to_many_doc")

# ------------------------------ архив

# Должности:
# class Post(Base):
#     """
#         Тянем из удаленного сервака данные о должностях.
#     """
#     __tablename__ = 'post'
#
#     index_add: Mapped[int] = mapped_column(autoincrement=True) # порядковый номер добавления обратившегося сотрудника.
#     id: Mapped[int] = mapped_column(primary_key=True, index=True, nullable=False, unique=True)  # id Должности
#     post_name: Mapped[str] = mapped_column(Text())
#
#     # Ограничение полей:
#     __table_args__ = (ForeignKeyConstraint(['id'],['Users.post_id']))


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


# --------------
# # Сотрудники розницы (кто обращается с проблемой).
# class RetailUsers(Base):
#     """
#     Тянем из удаленного сервака данные о пользователях.
#     """
#     __tablename__ = 'retail_user_data'
#
#
#     index_add: Mapped[int] = mapped_column(autoincrement=True) # орядковый номер добавления обратившегося сотрудника.
#
#     tg_id: Mapped[int] = mapped_column(primary_key=True, nullable=False, index=True, unique=True)  # телеграмм id
#     # id сотрудника в 1С и первичный ключ в этой таблице.
#     code: Mapped[str] = mapped_column(String(50), unique=True)
#
#     full_name: Mapped[str] = mapped_column(String(100))  # ФИО сотрудника
#     post_id: Mapped[int] = mapped_column(nullable=False, unique=True)  # id Должности
#
#     branch_name:Mapped[str] = mapped_column(String(200), nullable=False)
#     rrs_name: Mapped[str] = mapped_column(String(100), nullable=False)
#     division_name: Mapped[str] = mapped_column(String(100), nullable=False)
#
#     user_mail: Mapped[str] = mapped_column(String(100), nullable=True)
#
#
# # Сотрудники отдела аналитики:
# class OAiTDepartment(Base):
#     """
#     Сделать мезанизм обновления сотрудников отдела с удаленной базы данных:
#     """
#     __tablename__ = 'oait_staff'
#
#     # Порядковый номер добавления сотрудника.
#     index_add: Mapped[int] = mapped_column(autoincrement=True)
#
#     tg_id: Mapped[int] = mapped_column(primary_key=True, nullable=False, index=True, unique=True)  # телеграмм id
#     # id сотрудника в 1С и первичный ключ в этой таблице.
#     code: Mapped[str] = mapped_column(String(50), unique=True)
#
#     full_name: Mapped[str] = mapped_column(String(100))  # ФИО сотрудника
#     post_id: Mapped[int] = mapped_column(nullable=False, unique=True)  # id Должности
#
#     user_mail: Mapped[str] = mapped_column(String(100), nullable=True)
#
#     # статус сотрудника (занят ли или свободен) продумать насчет тех кто в отпуске # free = True, job = False
#     employee_status: Mapped[bool] = mapped_column(nullable=False,  server_default='True')  # activity
