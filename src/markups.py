import math

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def leave_registration_request_markup():
    markup = InlineKeyboardMarkup()
    start_registration_button = InlineKeyboardButton(text="🔵 Отправить заявку",
                                                     callback_data="start_registration")
    markup.add(start_registration_button)

    return markup


def admin_tg_profile_open_markup():
    markup = InlineKeyboardMarkup()

    link_button = InlineKeyboardButton(text="Написать администратору",
                                       url="t.me/rgal1ev")

    markup.add(link_button)

    return markup

def get_registration_requests_list_markup():
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton(text="👁 Посмотреть заявки",
                                  callback_data="open_registrations_list")
    markup.add(button)

    return markup


def registration_requests_list_markup(requests):
    markup = InlineKeyboardMarkup()

    for request in requests:
        request_button = InlineKeyboardButton(text=f"{request['name']}",
                                              callback_data=f"registration_request:{request['id']}")
        markup.add(request_button)

    profile_button = InlineKeyboardButton(text="📂 Открыть профиль",
                                          callback_data="profile")

    markup.add(profile_button)

    return markup


def employees_without_telegram_id_list_markup(employees):
    markup = InlineKeyboardMarkup()

    for employee in employees:
        employee_button = InlineKeyboardButton(text=f"{employee['firstname']}",
                                               callback_data=f"handling_registration_employee:{employee['id']}")

        markup.add(employee_button)

    back_button = InlineKeyboardButton(text="⬅ Вернуться назад",
                                       callback_data="open_registrations_list")

    markup.add(back_button)

    return markup


def registration_request_action_markup():
    markup = InlineKeyboardMarkup()
    accept_button = InlineKeyboardButton(text="🟢 Принять заявку",
                                         callback_data=f"accept_registration_request")

    decline_button = InlineKeyboardButton(text="🔴 Отклонить заявку",
                                          callback_data=f"decline_registration_request")

    back_button = InlineKeyboardButton(text="⬅ Вернуться назад",
                                       callback_data="open_registrations_list")

    markup.add(accept_button)
    markup.add(decline_button)
    markup.add(back_button)

    return markup


def accept_request_handling_markup():
    markup = InlineKeyboardMarkup()

    button = InlineKeyboardButton(text="🟢 Да",
                                  callback_data=f"accept_employee_handling")

    second_button = InlineKeyboardButton(text="🔴 Нет",
                                         callback_data=f"accept_registration_request")

    markup.add(button)
    markup.add(second_button)

    return markup


def employee_action_markup(employee):
    markup = InlineKeyboardMarkup()

    delete_button = InlineKeyboardButton(text="🔴 Удалить сотрудника",
                                         callback_data=f"delete_employee:{employee['id']}")

    if employee["telegram_id"] is not None:
        unhandle_button = InlineKeyboardButton(text="⭕ Отвязать телеграмм",
                                               callback_data=f"unhandle_employee:{employee['id']}")
        markup.add(unhandle_button)

    back_button = InlineKeyboardButton(text="⬅ Вернуться назад",
                                       callback_data="open_employees_list")

    profile_button = InlineKeyboardButton(text="📂 Открыть профиль",
                                          callback_data="profile")

    markup.add(delete_button)
    markup.add(back_button, profile_button)

    return markup


def employees_list(employees, page):
    markup = InlineKeyboardMarkup()

    employees = sorted(employees, key=lambda dict: dict['id'])

    page = int(page)
    previous_page = None
    max_employees_count = 4
    max_page = math.ceil(len(employees) / max_employees_count)

    if page == 1:
        previous_page = 0

    else:
        previous_page = page - 1

    page_employees = employees[previous_page * max_employees_count:page * max_employees_count]

    for employee in page_employees:
        employee_button = InlineKeyboardButton(text=f"№{employee['id']} {employee['lastname']} {employee['firstname'][0]}.",
                                               callback_data=f"employee_card:{employee['id']}")

        markup.add(employee_button)

    if page == 1:
        next_page_button = InlineKeyboardButton(text="▶",

                                                callback_data=f"open_employees_list:{page + 1}")
        markup.add(next_page_button)

    elif page == max_page:
        previous_page_button = InlineKeyboardButton(text="◀",
                                                    callback_data=f"open_employees_list:{page - 1}")
        markup.add(previous_page_button)

    else:
        next_page_button = InlineKeyboardButton(text="▶",
                                                callback_data=f"open_employees_list:{page + 1}")

        previous_page_button = InlineKeyboardButton(text="◀",
                                                callback_data=f"open_employees_list:{page - 1}")

        markup.add(previous_page_button, next_page_button)

    add_employee_button = InlineKeyboardButton(text="✳ Добавить сотрудника",
                                               callback_data="on_development")

    markup.add(add_employee_button)

    profile_button = InlineKeyboardButton(text="📂 Открыть профиль",
                                          callback_data="profile")

    markup.add(profile_button)

    return markup


def subjects_list(subjects, page, is_admin):
    markup = InlineKeyboardMarkup()

    subjects = sorted(subjects, key=lambda dict: dict['id'])

    page = int(page)
    previous_page = None
    max_objects_count = 4
    max_page = math.ceil(len(subjects) / max_objects_count)

    if page == 1:
        previous_page = 0

    else:
        previous_page = page - 1

    page_subjects = subjects[previous_page * max_objects_count:page * max_objects_count]

    for subject in page_subjects:
        object_button = InlineKeyboardButton(text=f"{subject['title']} - {subject['code']}",
                                             callback_data=f"subject_card:{subject['id']}")

        markup.add(object_button)

    if page == 1:
        next_page_button = InlineKeyboardButton(text="▶",
                                                callback_data=f"open_subjects_list:{page + 1}")
        markup.add(next_page_button)

    elif page == max_page:
        previous_page_button = InlineKeyboardButton(text="◀",
                                                    callback_data=f"open_subjects_list:{page - 1}")
        markup.add(previous_page_button)

    else:
        next_page_button = InlineKeyboardButton(text="▶",
                                                callback_data=f"open_subjects_list:{page + 1}")

        previous_page_button = InlineKeyboardButton(text="◀",
                                                    callback_data=f"open_subjects_list:{page - 1}")

        markup.add(previous_page_button, next_page_button)

    if is_admin:
        add_employee_button = InlineKeyboardButton(text="✳ Добавить обьект",
                                                   callback_data="on_development")
        markup.add(add_employee_button)

    profile_button = InlineKeyboardButton(text="📂 Открыть профиль",
                                          callback_data="profile")

    markup.add(profile_button)

    return markup


def open_profile_markup():
    markup = InlineKeyboardMarkup()
    profile_button = InlineKeyboardButton(text="📂 Открыть профиль",
                                          callback_data="profile")

    markup.add(profile_button)
    return markup


def admin_profile_markup():
    markup = InlineKeyboardMarkup()
    requests_button = InlineKeyboardButton(text="📝 Посмотреть заявки на регистрацию",
                                                 callback_data="open_registrations_list")

    feedback_button = InlineKeyboardButton(text="⚡ Посмотреть отзывы",
                                                 callback_data="on_development")
    instrumentations_button = InlineKeyboardButton(text="🔌 Приборы",
                                                         callback_data="open_instrumentation_list")
    employees_button = InlineKeyboardButton(text="👨 Сотрудники",
                                                  callback_data="open_employees_list")

    journals_button = InlineKeyboardButton(text="📃 Журналы",
                                           callback_data="journals")

    subjects_button = InlineKeyboardButton(text="⚫ Объекты",
                                                 callback_data="open_subjects_list")
    send_mail_button = InlineKeyboardButton(text="💬 Отправить рассылку",
                                                  callback_data="mail")

    more_button = InlineKeyboardButton(text="✳ Еще",
                                       callback_data="on_development")

    contacts_button = InlineKeyboardButton(text="📞 Контакты",
                                    callback_data="contacts")

    hide_message_button = InlineKeyboardButton(text="👁 Скрыть",
                                                     callback_data="hide")

    markup.add(requests_button)
    markup.add(employees_button, journals_button)
    markup.add(instrumentations_button, subjects_button)
    markup.add(feedback_button)
    markup.add(send_mail_button)
    markup.add(more_button)
    markup.add(contacts_button, hide_message_button)

    return markup


def user_profile_markup():
    markup = InlineKeyboardMarkup()

    all_instrumentals = InlineKeyboardButton(text="🔌 Приборы",
                                             callback_data="open_instrumentation_types")

    subjects_button = InlineKeyboardButton(text="⚫ Объекты",
                                           callback_data="open_subjects_list")

    feedback_button = InlineKeyboardButton(text="⚡ Оставить отзыв",
                                           callback_data="feedback")

    get_employee_help_button = InlineKeyboardButton(text="🟡 Получить помощь",
                                                    callback_data="on_development")

    more_button = InlineKeyboardButton(text="✳ Еще",
                                       callback_data="on_development")

    contacts_button = InlineKeyboardButton(text="📞 Контакты",
                                    callback_data="contacts")

    hide_message_button = InlineKeyboardButton(text="👁 Скрыть",
                                               callback_data="hide")

    markup.add(all_instrumentals, subjects_button)
    markup.add(feedback_button)
    markup.add(get_employee_help_button)
    markup.add(more_button)
    markup.add(contacts_button, hide_message_button)

    return markup

def hide_message(message_id):
    markup = InlineKeyboardMarkup()

    hide_message_button = InlineKeyboardButton(text="👁 Скрыть",
                                               callback_data=f"hide:{message_id}")

    markup.add(hide_message_button)

    return markup

def journals_list():
    markup = InlineKeyboardMarkup()

    repairs_button = InlineKeyboardButton(text="🛠 Ремонты",
                                           callback_data="on_development")

    calibrations_button = InlineKeyboardButton(text="⚙ Поверки",
                                               callback_data="on_development")

    profile_button = InlineKeyboardButton(text="📂 Открыть профиль",
                                          callback_data="profile")

    markup.add(repairs_button)
    markup.add(calibrations_button)
    markup.add(profile_button)

    return markup


def open_instrumental_types():
    markup = InlineKeyboardMarkup()

    my_repairs_button = InlineKeyboardButton(text="🔌 Мои приборы",
                                             callback_data="open_employee_instrumentation")

    all_repairs_button = InlineKeyboardButton(text="🔌 Все приборы",
                                              callback_data="open_instrumentation_list")

    profile_button = InlineKeyboardButton(text="📂 Открыть профиль",
                                          callback_data="profile")

    markup.add(my_repairs_button)
    markup.add(all_repairs_button)
    markup.add(profile_button)

    return markup


def instrumental_list(instrumentations, is_admin):
    markup = InlineKeyboardMarkup()

    for instrumentation in instrumentations:
        instrumentation_title = ""

        if instrumentation['status_id'] == 2:
            instrumentation_title = f"🔴 {instrumentation['title']} - На ремонте"

        else:
            instrumentation_title = f"🟢 {instrumentation['title']}"

        instrumentation_button = InlineKeyboardButton(text=instrumentation_title,
                                                      callback_data=f"instrumentation:{instrumentation['id']}")
        markup.add(instrumentation_button)

    if is_admin:
        add_instrumentation_button = InlineKeyboardButton(text="✳ Добавить прибор",
                                                          callback_data="add_new_instrumentation")
        markup.add(add_instrumentation_button)

    profile_button = InlineKeyboardButton(text="📂 Открыть профиль",
                                          callback_data="profile")

    markup.add(profile_button)

    return markup

def instrumentation_action(instrumentation, isAllowedToEdit):
    markup = InlineKeyboardMarkup()

    if instrumentation['status_id'] == 2:
        back_from_repair_button = InlineKeyboardButton(text="🛠🟢 Вернуть с ремонта",
                                                       callback_data=f"return_from_repair:{instrumentation['id']}")
        markup.add(back_from_repair_button)

    else:
        repair_button = InlineKeyboardButton(text="🛠 Отправить на ремонт",
                                             callback_data=f"set_on_repair:{instrumentation['id']}")

        calibration_button = InlineKeyboardButton(text="⚙ Зафиксировать поверку",
                                                  callback_data="on_development")

        markup.add(repair_button)
        markup.add(calibration_button)

    barcode_button = InlineKeyboardButton(text="📝 Показать штрих-код",
                                          callback_data=f"show_barcode:{instrumentation['id']}")

    back_button = InlineKeyboardButton(text="⬅ Вернуться назад",
                                       callback_data="open_instrumentation_list")

    profile_button = InlineKeyboardButton(text="📂 Открыть профиль",
                                          callback_data="profile")

    markup.add(barcode_button)

    if isAllowedToEdit:
        delete_button = InlineKeyboardButton(text="🔴 Удалить прибор",
                                             callback_data=f"delete_instrumentation:{instrumentation['id']}")
        markup.add(delete_button)

    markup.add(back_button, profile_button)

    return markup


def subject_action(subject, is_admin):
    markup = InlineKeyboardMarkup()

    if is_admin:
        delete_subject_button = InlineKeyboardButton(text="🔴 Удалить объект",
                                                     callback_data="on_development")

        markup.add(delete_subject_button)

    back_button = InlineKeyboardButton(text="⬅ Вернуться назад",
                                       callback_data="open_subjects_list")

    open_in_map = InlineKeyboardButton(text="🗺️ Показать на карте",
                                       callback_data=f"open_subject_in_map:{subject['id']}")

    profile_button = InlineKeyboardButton(text="📂 Открыть профиль",
                                          callback_data="profile")

    markup.add(open_in_map)
    markup.add(back_button, profile_button)

    return markup


def instrumentation_types_list(instrumentation_types, page):
    markup = InlineKeyboardMarkup()

    instrumentation_types = sorted(instrumentation_types, key=lambda dict: dict['id'])

    page = int(page)
    previous_page = None
    max_instrumentation_count = 4
    max_page = math.ceil(len(instrumentation_types) / max_instrumentation_count)

    if page == 1:
        previous_page = 0

    else:
        previous_page = page - 1

    page_instrumentations = instrumentation_types[previous_page * max_instrumentation_count:page * max_instrumentation_count]

    for instrumentation in page_instrumentations:
        object_button = InlineKeyboardButton(text=f"{instrumentation['title']}",
                                             callback_data=f"new_instrumentation_type_handling:{instrumentation['id']}")

        markup.add(object_button)

    if page == max_page and page == 1:
        return markup

    if page == 1:
        next_page_button = InlineKeyboardButton(text="▶",
                                                callback_data=f"open_new_instrumentation_type_list:{page + 1}")
        markup.add(next_page_button)

    elif page == max_page:
        previous_page_button = InlineKeyboardButton(text="◀",
                                                    callback_data=f"open_new_instrumentation_type_list:{page - 1}")
        markup.add(previous_page_button)

    else:
        next_page_button = InlineKeyboardButton(text="▶",
                                                callback_data=f"open_new_instrumentation_type_list:{page + 1}")

        previous_page_button = InlineKeyboardButton(text="◀",
                                                    callback_data=f"open_new_instrumentation_type_list:{page - 1}")

        markup.add(previous_page_button, next_page_button)

    return markup


def adding_new_instrumentation_action():
    markup = InlineKeyboardMarkup()

    add_button = InlineKeyboardButton(text="🟢 Добавить прибор",
                                      callback_data="accept_instrumentation_adding")

    cancel_button = InlineKeyboardButton(text="🔴 Отменить",
                                         callback_data="cancel")

    markup.add(add_button)
    markup.add(cancel_button)

    return markup

def cancel_markup():
    markup = InlineKeyboardMarkup()

    cancel_button = InlineKeyboardButton(text="🔴 Отменить",
                                         callback_data="cancel")

    markup.add(cancel_button)

    return markup