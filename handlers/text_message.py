"""
В этом модуле содержатся все переменные с текстом ответных сообщений бота.
Это позволяет не дублировать код при обращении разных категорий пользователей (админ, юзеры, начальники отделов),
т.к. в некоторых участках сценария ответы будут одинаковы для всех.

Справочно:
из-за того, что приходится выносить текст в другой файл, конструкция будет работать правильно для HTML,
только, если будут скобки для ф -строк, а в методе await callback.message.answer(category_problem, parse_mode='HTML')
указан parse_mode='HTML'. Иначе игнорируется разметка тегами, несмотря на то, что parse_mode примененн ко всему боту.
"""

# ---------------------------------------------- 0. Общий раздел
# Список ругательств для фильтрации брани в чатах:
swearing_list = {
    'ахуел', 'чмо', 'ебаное', 'падла', 'падлюка', 'ебучее', 'мразь', 'чухан', 'пидарюга', 'членосос',
    'ахуел', 'чмо', 'ебаное', 'падла', 'падлюка', 'ебучее', 'мразь', 'чухан', 'пидарюга', 'членосос',
    'маразота', 'ебаный', 'блядь', 'ебать', 'пизда', 'хуй', 'беспиздая', 'бля', 'блядва', 'блядиада',
    'блядина', 'блядистость', 'блядки', 'блядовать', 'блядогон', 'блядословник', 'блядский', 'блядский',
    'блядство', 'блядство', 'блядун', 'блядь', 'бляхомудия', 'взбляд', 'взъебнуть', 'взъёбка', 'взъёбывать',
    'взъебщик', 'впиздить', 'впиздиться', 'впиздохать', 'впиздохивать', 'впиздохиваться', 'впиздронивать',
    'впиздрониваться', 'впиздюлить', 'впиздячил', 'впиздячить', 'впизживать', 'впизживаться', 'вхуйнуть',
    'вхуйнуться', 'вхуяривание', 'вхуярить', 'выблядовал', 'выблядок', 'выебать', 'выебок', 'выебон',
    'выёбывается', 'выпиздеться', 'выпиздить', 'выхуяривание', 'выхуячивание', 'выхуякивание', 'въебать',
    'въёбывать', 'глупизди', 'говноёб', 'голоёбица', 'греблядь', 'дерьмохеропиздократ', 'дерьмохеропиздократия',
    'доебался', 'доебаться', 'доёбывать', 'долбоёб', 'допиздеться', 'дохуйнуть', 'дохуякать', 'дохуякивать',
    'дохуяриваться', 'дуроёб', 'дядеёб', 'ебалка', 'ебало', 'ебалово', 'ебальник', 'ебанатик', 'ебандей',
    'ебанёшься', 'ебанул', 'ебанулся', 'ебануть', 'ебануться', 'ебанутый', 'ебанько', 'ебаришка', 'ебаторий',
    'ебаться', 'ебашит', 'ебеня', 'ебёт', 'ебистика', 'еблан', 'ебланить', 'ебливая', 'ебля', 'ебукентий',
    'ёбака', 'ёбаный', 'ёбарь', 'ебарь', 'ёбкость', 'ёбля', 'ёбнул', 'ёбнуться', 'ёбнутый', 'ёбс', 'жидоёб',
    'жидоёбка', 'жидоёбский', 'заебал', 'заебать', 'заебись', 'заебцовый', 'заебенить', 'заебашить', 'заёб',
    'заёбанный', 'заебаться', 'запизденевать', 'запиздеть', 'запиздить', 'запизживаться', 'захуяривать',
    'захуярить', 'злоебучая', 'изъебнулся', 'испизделся', 'испиздить', 'исхуячить', 'козлоёб', 'козоёб',
    'коноёб', 'свиноёб', 'ослоёб', 'козлоёбина', 'козлоёбиться', 'козоёбиться', 'коноёбиться', 'свиноёбиться',
    'ослоёбиться', 'козлоёбище', 'коноёбиться', 'косоёбится', 'многопиздная', 'объебаться', 'наебнулся',
    'мозгоёб', 'мудоёб', 'наблядовал', 'наебалово', 'наебать', 'наебаться', 'наебашился', 'наебениться',
    'наебнуть', 'наёбка', 'нахуевертеть', 'нахуяривать', 'нахуяриться', 'напиздеть', 'напиздить', 'настоебать',
    'невъебенный', 'нехуёвый', 'нехуй', 'оберблядь', 'объебал', 'объебалово', 'объебательство', 'объебать',
    'хуй', 'объебос', 'один', 'однохуйственно', 'один', 'хуй', 'опизденевать', 'опиздихуительный',
    'оскотоёбился', 'остоебал', 'остопиздело', 'остопиздеть', 'остохуеть', 'отпиздить', 'отхуяривать',
    'охуевать', 'прихуевать', 'хуеть', 'охуенно', 'охуительно', 'оххуетительно', 'охуенный', 'охуительный',
    'охуячить', 'переебать', 'перехуяривать', 'перехуярить', 'пёзды', 'пизда', 'пиздабол', 'пиздаёб', 'пиздакрыл',
    'пиздануть', 'пиздануться', 'пиздатый', 'пизделиться', 'пизделякает', 'пиздеть', 'пиздец', 'пиздецкий',
    'пиздить', 'пиздобол', 'пиздоблошка', 'пиздобрат', 'пиздобратия', 'пиздовать', 'опиздоумел', 'отъебаться',
    'пиздюхать', 'пиздовладелец', 'пиздодушие', 'пиздоёбищность', 'пиздолет', 'пиздолиз', 'пиздомания',
    'пиздорванка', 'пиздострадалец', 'пиздострадания', 'пиздохуй', 'пиздошить', 'пиздрик', 'пиздуй', 'пиздун',
    'пиздюлина', 'пиздюлька', 'пиздюля', 'пиздюрить', 'пиздюхать', 'пиздюшник', 'подзаебать', 'подзаебенить',
    'поднаебнуться', 'охуячивать', 'пиздёж', 'пиздёныш', 'пиздопляска', 'пиздорванец', 'пиздюк', 'пиздюли',
    'поднаёбывать', 'подпёздывать', 'подпиздывает', 'подъебнуть', 'подъёбка', 'подъёбки', 'подъёбывать',
    'попиздили', 'похую', 'похуярили', 'приебаться', 'припиздеть', 'припиздить', 'прихуяривать', 'прихуярить',
    'проебаться', 'проёб', 'пропиздить', 'разъебай', 'разъебаться', 'разёбанный', 'распиздон', 'распиздошил',
    'распиздяйство', 'расхуюжить', 'расхуяривать', 'скотоёб', 'скотоёбина', 'сосихуйский', 'спиздил',
    'страхоёбище', 'сухопиздая', 'схуярить', 'съебаться', 'трепездон', 'трепездонит', 'туебень', 'тупиздень',
    'уебался', 'уебать', 'уёбище', 'уёбищенски', 'уёбок', 'уёбывать', 'упиздить', 'хитровыебанный', 'хуев',
    'хуеватенький', 'хуевато', 'худоёбина', 'хуебратия', 'хуеглот', 'хуегрыз', 'хуедин', 'хуелес', 'хуеман',
    'хуемырло', 'хуеплёт', 'хуепутало', 'хуесос', 'хуета', 'хуетень', 'хуёвина', 'хуёвничать', 'хуёво',
    'хуёвый', 'хуила', 'хуйло', 'хуйнуть', 'хуйня', 'хуярить', 'хуячить', 'хуяция', 'хули', 'хуя', 'хуяк',
    'поднаебнуть', 'поебать', 'поебень', 'попиздеть', 'проблядь', 'проебать', 'хуячить', 'шароёбится',
    'распиздяй', 'широкопиздая', 'поебалу', 'нахуй', 'отсоси', 'ебучка', 'ебалу', 'мудило', 'ебаные',
    'залупы', 'ахуели'
}

# 0. Общее приветствие для замов ОАИТ и розницы:
hello_users_retail: str = (
    '     <b>Привет</b>, {0} 🖖 !\n'
    f'-----------------------------------------------\n'
    f'     На связи <b>"Tasks bot meneger". 🦾</b>\n'  # <strong> </strong>
    f'-----------------------------------------------\n'
    f'\n'
    f'  *  🤝   Я помогаю в решении вопросов и проблем розничных подразделений'
    f', возникающих в ходе повседневной деятельности.\n'
    f'\n'
    f'   * 🤙   Создаю заявки по обращениям и распределяю их на исполнителей в отделе ОАиТ СВ '
    f'в соответствии с их профилем деятельности, исходя из категории обращения.\n'
    f'\n'
    f'   *  👍  Направляю уведомления по завершении обработки заявки заказчику, и много другое...'
)


# 0. Общее приветствие для всех:





# .as_html()


category_problem = (f'Выбери тему обращения (категорию вопроса / проблемы):\n'
                    f'\n'
                    # ---------------------- Отправить к Аналитикам:
                    f'<b><u>I. АНАЛИТИКА</u></b>\n'  # Жирный, подчеркнутый.
                    f'Вопросы (проблемы) с:\n'
                    f' *  <b>Дашбордами:</b> <em>/dashboards</em>.\n'  # 17
                    f' *  <b>Ценниками:</b> <em>/price_tags_tool</em>\n'
                    f' *  <b>Telegram-ботами:</b> <em>/bots</em>\n'  # 14
                    f' *  <b>Ценниками:</b> <em>/analytics</em>\n'  # 18

                    f'\n'
                    # ---------------------- Отправить к Форматам:
                    f'<b><u>II. ФОРМАТЫ</u></b>\n'
                    f'Вопросы (проблемы) по:\n'
                    f' *  <b>АР (везет товар):</b> <em>/coming</em>.\n'  # prod_coming
                    f' *  <b>АР (не везет товар):</b> <em>/no_coming</em>\n'  # not_prod_coming
                    f' *  <b>СЕ:</b> <em>/ce</em>\n'
                    f' *  <b>Границам категорий:</b> <em>/borders</em>\n'
                    f' *  <b>Лежакам:</b> <em>/unsold</em>\n'

                    f'\n'
                    # ---------------------- Отправить товарообору:
                    f'<b><u>III. ТОВАРООБОРОТ</u></b>\n'
                    f'Вопросы (проблемы) по:\n'
                    f' *  <b>МП:</b> <em>/sales</em>.\n'
                    f' *  <b>Мерчам:</b> <em>/merch</em>\n'
                    f' *  <b>Ценам на товар:</b> <em>/price</em>\n'
                    f' *  <b>Закупке товара:</b> <em>/purchase</em>\n'
                    f' *  <b>ВЕ:</b> <em>/be</em>\n'
                    f' *  <b>СТМ:</b> <em>/stm</em>\n'
                    f' *  <b>Уценке:</b> <em>/discount</em>\n'
                    # f'или напиши мне прямо в чарт '
                    f'\n'
                    f'и я направлю твою <b>"БОЛЬ"</b> нужным людям!')

# ---------------------------------------------- 1. Раздел для розницы

# ---------------------------------------------- 1. Раздел для админа

# __________________________________

#  по дивизиону "Средняя Волга"

# <pre> </pre> -  выделяет для копирования
# p - абзац. Блочный тег, разделяет текст на отдельные абзацы, в конце добавляется отступ
# u - подчеркивает текст снизу
# mark - отображает текст как выделенный - не работает здесь
# ul - маркированный список. Каждый элемент списка оборачивается тегами li
#
# ol - нумерованный список. Каждый элемент списка оборачивается тегами li
# hr - вставляет горизонтальную полосу

# (f'     <b>Привет</b>, {0} 🖖 !\n'
#                           f'--------------------------------------------------------------------------------------------'
#                           f'---------\n'
#                           f'     На связи <b>"Tasks bot meneger". 🦾</b>\n'  # <strong> </strong>
#                           f'--------------------------------------------------------------------------------------------'
#                           f'---------\n'
#                           f'\n'
#                           f'  *  🤝   Я помогаю в решении вопросов и проблем розничных подразделений'
#                           f', возникающих в ходе повседневной деятельности.\n'
#                           f'\n'
#                           f'   * 🤙   Создаю заявки по обращениям и распределяю их на исполнителей в отделе ОАиТ СВ '
#                           f'в соответствии с их профилем деятельности, исходя из категории обращения.\n'
#                           f'\n'
#                           f'   *  👍  Направляю уведомления по завершении обработки заявки заказчику, и много другое...')
