"""
Хранятся все классы для машины состояний (FSM), для обработки нажатий кнопок.
"""
# ----------------------------------------------------------------------------------------------------------------------
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
# general_router, admin_router, oait_manager_router, oait_router, retail_router) #
# ----------------------------------------------------------------------------------------------------------------------



# -------------------------------------------------- general_router
class StartUser(StatesGroup):
    """Шаги состояний для кнопок в ветвлении проверки регистрации пользователя"""

    check_next = State()
    # check_support = State()
    check_repeat = State()
    support_rror = State()


# -------------------------------------------------- retail_router
class AddRequests(StatesGroup):
    """Шаги состояний для обращений"""
    request_message = State()
    # documents = State()
    transit_request_message = State()


#
# texts = {
#     'AddRequests:request_message': 'Введите текст обращения заново:'
#     # + ЕЩЕ
# }

class Instructor(StatesGroup):
    """Шаги состояний для кнопок инструктаж и приступить к работе:"""
    # Шаги состояний:
    instruct_or_gowork = State()


class SetCategory(StatesGroup):
    """
    Шаги выбора категории.
    Выбираем сначала родительскую категорию - содержит в себе подкатегории, после подкатегорию.
    """

    main_category = State()
    sab_category = State()
    # SetCategory.main_category  SetCategory.sab_category

    # sab_category_problem_analytics = State()
    # main_category_problem_formats = State()
    # main_category_problem_trade_turnover = State()