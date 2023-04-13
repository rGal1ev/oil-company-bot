"""
Bot messages
Default parse mode - HTML
"""


"""
MESSAGES
WITHOUT
FORMATTING
"""

start_message = """
🟢 <b>Добро пожаловать</b> 

Данный бот автоматизирует учет контрольно-измерительных приборов внутри нефтяного предприятия

Пропишите /help для получения помощи
"""

not_register_user_message = """
Кажется, вы не зарегистрированы в нашей системе,

<b>Пожалуйста, оставьте заявку на регистрацию</b>
"""

new_registration_request = """
📝 <b>Новая заявка на регистрацию</b>
"""

registration_request_error = """
Во время отпавки заявки произошла ошибка
"""

help_message = """
Если после команды /start вам лишь пришло сообщение о приветствии - это значит, вы зарегистрированы в системе,
пропишите команду /profile для открытия меню со всеми нужными функциями
"""

"""
MESSAGES
WITH
FORMATTING
"""


def formed_registration_request(request):
    request = f"""
Заявка успешно сформирована! 
<b>Имя</b>: {request['name']} 
<b>Телефон</b>: {request['phone']} 
<b>Сообщение</b>: {request['title']}

<b>Ожидайте ответа от администратора</b>
"""

    return request


def registration_request(request):
    request = f"""
Заявка на регистрацию №{request["id"]}

<b>Имя</b>: {request['name']} 
<b>Телефон</b>: {request['phone']} 
<b>Сообщение</b>: {request['title']}

<b>Выберите действие 🔽</b>
"""

    return request


def employee_info(employee):
    info = f"""
<b>Информация о сотруднике</b>

<b>Имя</b>: {employee['lastname']} {employee['firstname']}
<b>Телефон</b>: {employee['phone']}

Привязать заявку к этому сотруднику?
"""

    return info

def admin_profile_info(admin):
    info = f"""
📂 <b>Ваш профиль</b>

<b>Имя:</b> {admin["lastname"]} {admin["firstname"]}
<b>Телефон:</b> {admin["phone"]}
<b>Статус:</b> Администратор
"""

    return info


def user_profile_info(user):
    info =  f"""
📂 <b>Ваш профиль</b>

<b>Имя:</b> {user["lastname"]} {user["firstname"]}
<b>Телефон:</b> {user["phone"]}
<b>Статус:</b> Пользователь
"""

    return info


def employee_card(employee):
    is_registered = ""

    print(employee["telegram_id"], employee["telegram_id"] is None)

    if employee["telegram_id"] is None:
        is_registered = "Не привязан"

    else:
        is_registered = f"Привязан - ID: {employee['telegram_id']}"

    card = f"""
👨 <b>Пользователь №{employee["id"]}</b>
<b>Имя</b>: {employee["lastname"]} {employee["firstname"]}
<b>Телефон</b>: {employee["phone"]}
<b>Регистрация</b>: {is_registered}
"""

    return card


def select_requests(is_empty):
    if is_empty:
        return "<b>Новых заявок нет</b>"

    return "<b>Выберите заявки на регистрацию ниже</b> 🔽"
