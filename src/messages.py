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

set_on_repair = """
🟢 <b>Создана запись в журнале ремонта</b>

<i>Прибор будет отмечен как - В ремонте</i>
"""

not_register_user_message = """
⚠ <b>Кажется, вы не зарегистрированы в нашей системе</b>

<i>Пожалуйста, оставьте заявку на регистрацию</i>
"""

new_registration_request = """
📝 <b>Новая заявка на регистрацию</b>
"""

registration_request_error = """
Во время отправки заявки произошла ошибка

<i>Если она повторится просьба сообщить администратору</i>
"""

help_message = """
<b>Нужна помощь?</b>

🔵 <b>Если вы зарегистрированы</b>
      Пропишите команду /profile
    
🟠 <b>Если вы не зарегистрированы</b>
      Бот сам предложит оставить заявку, если вы попытаетесь прописать команды /start или /profile
    
🟡 <b>Возникли вопросы?</b>
      Напишите администратору бота
"""

unknow_command = """
⚠ <b>Неизвестная команда</b>
 
<i>Напишите</i> /help <i>для помощи</i>
"""

instrumentation_list = """
🔌 <b>Доступные приборы на предприятии</b>

<i>Добавлять или удалять приборы может только администратор</i>

<i>Выберите нужный прибор ниже</i> ↓
"""

employees_instrumentation_list = """
🔌 <b>Приборы, за которые вы ответственны</b>

<i>Выберите нужный прибор ниже</i> ↓
"""

instrumentation_types = """
<b>🔵 Выберите необходимый пункт</b>

<i>Добавлять или удалять приборы может только администратор</i>
"""

contacts = """
<b>📞 Контакты предприятия</b>

<b>Телефон</b>: +7 123 456 78-90
<b>Адрес</b>: <i>Адрес предприятия...</i>
"""

subjects_list = """
⚫ <b>Доступные объекты на предприятии</b>

<i>Добавлять или удалять объекты может только администратор</i>

<i>Выберите нужный объект ниже</i> ↓
"""

employees_list = """
👤 <b>Доступные сотрудники предприятия</b>

<i>Добавлять или удалять сотрудников может только администратор</i>

<i>Выберите нужного сотрудника ниже</i>  ↓
"""

"""
MESSAGES
WITH
FORMATTING
"""


def formed_registration_request(request):
    request = f"""
📝 <b>Заявка успешно сформирована!</b> 

<b>Имя</b>: {request['name']} 
<b>Телефон</b>: {request['phone']} 
<b>Сообщение</b>: {request['title']}

<i>Ожидайте ответа от администратора</i>
"""

    return request


def add_new_instrumentation(instrumentation):
    info = """🛠 <b>Добавление прибора</b>
"""

    if instrumentation['title'] is not None:
        info += f"""
<b>Название</b>: {instrumentation['title']}"""

    if instrumentation['model'] is not None:
        info += f"""
<b>Модель</b>: {instrumentation['model']}"""

    if instrumentation['instr_type_id'] is not None:
        info += f"""
<b>Тип инструмента</b>: {instrumentation['instr_type_id']}"""

    return info

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

    if employee["telegram_id"] is None:
        is_registered = "Не привязан"

    else:
        is_registered = f"Привязан - ID: {employee['telegram_id']}"

    card = f"""
👤 <b>Сотрудник №{employee["id"]}</b>

<b>Имя</b>: {employee["lastname"]} {employee["firstname"]}
<b>Телефон</b>: {employee["phone"]}
<b>Регистрация</b>: {is_registered}

<i>Выберите действие с пользователем</i>
"""

    return card


def instrumentation_card(instrumentation):
    status = ""

    print(instrumentation)

    if instrumentation["status_id"] == 1:
        status = f"🟢 {instrumentation['instrumentation_statuses']['title']}"

    else:
        status = f"🔴 {instrumentation['instrumentation_statuses']['title']}"

    subject_status = ""
    employee_status = ""

    if instrumentation['subject_id'] is None:
        subject_status = "⚠ Не привязан"

    else:
        subject_status = f"{instrumentation['subjects']['title']} - {instrumentation['subjects']['code']}"

    if instrumentation['employee_id'] is None:
        employee_status = "⚠ Не привязан"

    else:
        employee_status = f'{instrumentation["employees"]["lastname"]} {instrumentation["employees"]["firstname"][0]}.'


    card = f"""
<b>🔌 Информация о приборе №{instrumentation['id']}</b>

<b>{status}</b>

<b>Название</b>: {instrumentation['title']}
<b>Модель</b>: {instrumentation['model']}
<b>Объект</b>: {subject_status}
<b>Дата колибровки</b>: {instrumentation['last_calibration_date']}

<b>Ответственный</b>: {employee_status}

<i>Выберите действие с прибором</i>
"""

    return card

def subject_card(subject):
    print(subject)

    card = f"""
⚫ <b>Информация об объекте №{subject['id']}</b>

<b>Название</b>: {subject['title']}
<b>Код</b>: {subject['code']}

<b>Место-нахождения</b>: {subject['description']}

<b>Описание</b>: {subject['location']}
"""

    return card

def select_requests(is_empty):
    if is_empty:
        return "<b>Новых заявок нет</b>"

    return "<b>Выберите заявки на регистрацию ниже</b> 🔽"
