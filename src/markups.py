from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def leave_registration_request_markup():
    markup = InlineKeyboardMarkup()
    start_registration_button = InlineKeyboardButton(text="🔵 Отправить заявку",
                                                     callback_data="start_registration")
    markup.add(start_registration_button)

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

def back_to_employee_list():
    markup = InlineKeyboardMarkup()

    back_button = InlineKeyboardButton(text="⬅ Вернуться назад",
                                       callback_data="open_employees_list")

    markup.add(back_button)

    return markup


def employees_list(employees, page):
    markup = InlineKeyboardMarkup()

    page = int(page)
    previous_page = None
    max_employees_count = 4

    if page == 1:
        previous_page = 0

    else:
        previous_page = page - 1

    page_employees = employees[previous_page * max_employees_count:page * max_employees_count]

    for employee in page_employees:
        employee_button = InlineKeyboardButton(text=f"{employee['firstname']}",
                                               callback_data=f"employee_card:{employee['id']}")

        markup.add(employee_button)

    if page == 1:
        next_page_button = InlineKeyboardButton(text="▶",

                                                callback_data=f"open_employees_list:{page + 1}")
        markup.add(next_page_button)

    else:
        if len(page_employees) < 4:
            previous_page_button = InlineKeyboardButton(text="◀",
                                                        callback_data=f"open_employees_list:{page - 1}")
            markup.add(previous_page_button)

        else:
            next_page_button = InlineKeyboardButton(text="▶",
                                                    callback_data=f"open_employees_list:{page + 1}")

            previous_page_button = InlineKeyboardButton(text="◀",
                                                    callback_data=f"open_employees_list:{page - 1}")

            markup.add(previous_page_button, next_page_button)

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
                                                 callback_data="...")
    instrumentations_button = InlineKeyboardButton(text="🔌 Приборы",
                                                         callback_data="...")
    employees_button = InlineKeyboardButton(text="👨 Пользователи",
                                                  callback_data="open_employees_list")

    journals_button = InlineKeyboardButton(text="📃 Журналы",
                                           callback_data="journals")

    subjects_button = InlineKeyboardButton(text="⚫ Объекты",
                                                 callback_data="...")
    send_mail_button = InlineKeyboardButton(text="💬 Отправить рассылку",
                                                  callback_data="mail")

    more_button = InlineKeyboardButton(text="✳ Еще",
                                       callback_data="more")

    hide_message_button = InlineKeyboardButton(text="👁 Скрыть",
                                                     callback_data="hide")

    markup.add(requests_button)
    markup.add(feedback_button)
    markup.add(employees_button, journals_button)
    markup.add(instrumentations_button, subjects_button)
    markup.add(send_mail_button)
    markup.add(more_button)
    markup.add(hide_message_button)

    return markup


def user_profile_markup():
    markup = InlineKeyboardMarkup()

    all_instrumentals = InlineKeyboardButton(text="🔌 Приборы",
                                                   callback_data="...")
    my_instrumentals = InlineKeyboardButton(text="🔌 Мои приборы",
                                                  callback_data="...")
    subjects_button = InlineKeyboardButton(text="⚫ Объекты",
                                                 callback_data="...")
    hide_message_button = InlineKeyboardButton(text="👁 Скрыть",
                                                     callback_data="hide")

    markup.add(all_instrumentals, my_instrumentals)
    markup.add(subjects_button)
    markup.add(hide_message_button)

    return markup


def journals_list():
    markup = InlineKeyboardMarkup()

    repairs_button = InlineKeyboardButton(text="🛠 Ремонты",
                                           callback_data="open_repairs_list")

    calibrations_button = InlineKeyboardButton(text="🔌 Поверки",
                                               callback_data="open_calibrations_list")

    profile_button = InlineKeyboardButton(text="📂 Открыть профиль",
                                          callback_data="profile")

    markup.add(repairs_button)
    markup.add(calibrations_button)
    markup.add(profile_button)

    return markup