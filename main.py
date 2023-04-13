"""
Бот автоматизирует учет приборов
на нефтяных предприятиях

Требуемые библиотеки:
- pyTelegramBotAPI
- supabase
- aiohttp

Другие требования:
- Настроенная БД в SupaBase
- Минимум один сотрудник-администратор
"""

from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot import asyncio_filters

from src.database import DataBase
from src.commands import commands
from src import messages
from src import markups
from src import helpers

import config


class RegistrationRequest(StatesGroup):
    name = State()
    title = State()
    phone = State()


class EmployeeRegistration(StatesGroup):
    request_id = State()
    employee_id = State()


class MailTitle(StatesGroup):
    title = State()


class FeedbackTitle(StatesGroup):
    title = State()


class CurrentPage(StatesGroup):
    page = State()


bot = AsyncTeleBot(config.bot_config["telegram"]["key"], state_storage=StateMemoryStorage())
database = DataBase(config.bot_config["supabase"]["url"],
                    config.bot_config["supabase"]["key"])

"""
COMMAND
HANDLERS
"""


async def command_start_query(message):
    await bot.delete_message(message.chat.id, message.message_id)
    await bot.set_my_commands(commands=commands)
    await bot.send_message(message.chat.id,
                           messages.start_message,
                           parse_mode="html")

    telegram_id_in_database = database.telegram_id_in_employees(message.chat.id)

    if not telegram_id_in_database:
        await bot.send_message(message.chat.id,
                               messages.not_register_user_message,
                               reply_markup=markups.leave_registration_request_markup(),
                               parse_mode="HTML")


async def command_help_query(message):
    await bot.delete_message(message.chat.id, message.message_id)

    await bot.send_message(message.chat.id,
                           messages.help_message,
                           parse_mode="HTML")


async def command_profile_query(message):
    await bot.delete_message(message.chat.id, message.message_id)
    telegram_id_is_admin = database.telegram_id_is_admin(message.chat.id)

    if telegram_id_is_admin:
        admin = database.get_employee_by_telegram_id(message.chat.id)

        await bot.send_message(message.chat.id,
                               messages.admin_profile_info(admin),
                               reply_markup=markups.admin_profile_markup(),
                               parse_mode="HTML")

    else:
        user = database.get_employee_by_telegram_id(message.chat.id)

        await bot.send_message(message.chat.id,
                               messages.user_profile_info(user),
                               reply_markup=markups.user_profile_markup(),
                               parse_mode="HTML")


async def command_feedback_query(message):
    await bot.send_message(message.chat.id,
                           "Хотите оставить отзыв? Пожалуйста напиши ниже ваши впечатления от использования бота:",
                           parse_mode="HTML")

    await bot.set_state(message.chat.id,
                        FeedbackTitle.title)

bot.register_message_handler(command_start_query, commands=['start'])
bot.register_message_handler(command_help_query, commands=['help'])
bot.register_message_handler(command_profile_query, commands=['profile'])
bot.register_message_handler(command_feedback_query, commands=['feedback'])

"""
CALLBACK
HANDLERS
"""


async def callback_start_registration_query(call):
    registration_requests = database.get_all_registration_requests()
    request_for_processing = False
    telegram_id_in_database = database.telegram_id_in_employees(call.message.chat.id)

    if telegram_id_in_database:
        await bot.send_message(call.message.chat.id, "Вы уже зарегистрированы")
        request_for_processing = True

    else:
        for request in registration_requests:
            if request["telegram_id"] == call.message.chat.id and request["is_cancelled"] is not True:
                await bot.send_message(call.message.chat.id,
                                       "Вы уже отправляли заявку, подождите пока администратор ее примет")
                request_for_processing = True
                break

    if not request_for_processing:
        await bot.set_state(call.message.chat.id,
                            RegistrationRequest.name)

        await bot.send_message(call.message.chat.id,
                               "Напиши свое имя и фамилия")


async def callback_open_registration_requests_query(call):
    telegram_id = call.message.chat.id
    is_admin = helpers.is_admin(database, telegram_id)

    if not is_admin:
        await bot.send_message(telegram_id, "Недостаточно прав для просмотра")
        return

    registration_requests = database.get_registration_requests()

    is_requests_empty = ""

    if len(registration_requests) == 0:
        is_requests_empty = True

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=messages.select_requests(is_requests_empty),
                                reply_markup=markups.registration_requests_list_markup(registration_requests),
                                parse_mode="HTML")


async def callback_registration_request_id_query(call):
    request_id = helpers.get_id(call.data)
    request = database.get_registration_request_by_id(request_id)

    await bot.set_state(call.message.chat.id, EmployeeRegistration.request_id)

    async with bot.retrieve_data(call.message.chat.id) as data:
        data['request_id'] = request_id

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=messages.registration_request(request),
                                reply_markup=markups.registration_request_action_markup(),
                                parse_mode="HTML")


async def callback_decline_registration_request_query(call):
    request_id = helpers.get_id(call.data)
    request = database.get_registration_request_by_id(request_id)

    database.set_registration_request_is_cancelled(request_id)

    await bot.send_message(request["telegram_id"],
                           "🔴 Заявка была отклонена администратором")

    registration_requests = database.get_registration_requests()
    is_registration_requests_empty = False

    if len(registration_requests) == 0:
        return True

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=messages.select_requests(is_registration_requests_empty),
                                reply_markup=markups.registration_requests_list_markup(registration_requests))


async def callback_profile_query(call):
    telegram_id_is_admin = database.telegram_id_is_admin(call.message.chat.id)

    if telegram_id_is_admin:
        admin = database.get_employee_by_telegram_id(call.message.chat.id)

        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=messages.admin_profile_info(admin),
                                    reply_markup=markups.admin_profile_markup(),
                                    parse_mode="HTML")

    else:
        user = database.get_employee_by_telegram_id(call.message.chat.id)

        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=messages.user_profile_info(user),
                                    reply_markup=markups.user_profile_markup(),
                                    parse_mode="HTML")


async def callback_accept_registration_request_id_query(call):
    employees_without_telegram_id = database.get_employees_without_telegram_id()

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text="Выберите сотрудника для привязки 🔽",
                                reply_markup=markups.employees_without_telegram_id_list_markup(
                                    employees_without_telegram_id),
                                parse_mode="HTML")


async def callback_handling_registration_request_employee_query(call):
    employee_id = helpers.get_id(call.data)

    async with bot.retrieve_data(call.message.chat.id) as data:
        data['employee_id'] = employee_id

    employee = database.get_employee_by_id(employee_id)

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=messages.employee_info(employee),
                                reply_markup=markups.accept_request_handling_markup(),
                                parse_mode="HTML")


async def callback_accept_employee_handling_query(call):
    async with bot.retrieve_data(call.message.chat.id) as data:
        request_id = data["request_id"]
        employee_id = data["employee_id"]

        request_telegram_id = database.get_registration_request_by_id(request_id)["telegram_id"]
        try:
            database.set_telegram_id_into_employee(request_telegram_id, employee_id)
            database.set_registration_request_is_cancelled(request_id)

            await bot.edit_message_text(chat_id=call.message.chat.id,
                                        message_id=call.message.message_id,
                                        text="Привязка была успешно совершена!",
                                        reply_markup=markups.open_profile_markup(),
                                        parse_mode="HTML")

            await bot.send_message(request_telegram_id, "🟢 Заявка была успешно одобрена")

        except:
            await bot.edit_message_text(chat_id=call.message.chat.id,
                                        message_id=call.message.message_id,
                                        text="Во время привязки произошла ошибка",
                                        reply_markup=markups.open_profile_markup(),
                                        parse_mode="HTML")


async def callback_mail_query(call):
    await bot.set_state(call.message.chat.id,
                        MailTitle.title)

    await bot.send_message(call.message.chat.id,
                           "Напишите сообщения рассылки:")


async def callback_hide_message_query(call):
    await bot.delete_message(call.message.chat.id, call.message.message_id)


async def callback_open_employees_list_query(call):
    page = 1

    if ":" in call.data:
        page = helpers.get_id(call.data)

    employees = database.get_employees()
    filtered_employees = []

    for employee in employees:
        if employee["telegram_id"] != call.message.chat.id:
            filtered_employees.append(employee)

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text="<b>Список сотрудников</b>",
                                reply_markup=markups.employees_list(filtered_employees, page),
                                parse_mode="HTML")


async def callback_employee_query(call):
    print(call.data)
    employee_id = helpers.get_id(call.data)
    employee = database.get_employee_by_id(employee_id)

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=messages.employee_card(employee),
                                parse_mode="HTML",
                                reply_markup=markups.back_to_employee_list())


async def callback_journals_query(call):
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text="📃 <b>Доступные журналы</b>",
                                parse_mode="HTML",
                                reply_markup=markups.journals_list())


bot.register_callback_query_handler(callback_start_registration_query,
                                    func=lambda call: call.data == "start_registration")

bot.register_callback_query_handler(callback_open_registration_requests_query,
                                    func=lambda call: call.data == "open_registrations_list")

bot.register_callback_query_handler(callback_mail_query,
                                    func=lambda call: call.data == "mail")

bot.register_callback_query_handler(callback_hide_message_query,
                                    func=lambda call: call.data == "hide")

bot.register_callback_query_handler(callback_profile_query,
                                    func=lambda call: call.data == "profile")

bot.register_callback_query_handler(callback_journals_query,
                                    func=lambda call: call.data == "journals")

bot.register_callback_query_handler(callback_employee_query,
                                    func=lambda call: "employee_card" in call.data)

bot.register_callback_query_handler(callback_open_employees_list_query,
                                    func=lambda call: "open_employees_list" in call.data)

bot.register_callback_query_handler(callback_accept_registration_request_id_query,
                                    func=lambda call: "accept_registration_request" in call.data)

bot.register_callback_query_handler(callback_decline_registration_request_query,
                                    func=lambda call: "decline_registration_request" in call.data)

bot.register_callback_query_handler(callback_registration_request_id_query,
                                    func=lambda call: "registration_request" in call.data)

bot.register_callback_query_handler(callback_handling_registration_request_employee_query,
                                    func=lambda call: "handling_registration_employee" in call.data)

bot.register_callback_query_handler(callback_accept_employee_handling_query,
                                    func=lambda call: "accept_employee_handling" in call.data)

"""
STATE
HANDLERS
"""


async def state_registration_name_query(message):
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['name'] = message.text

    await bot.send_message(message.from_user.id, "Введите номер телефона")
    await bot.set_state(message.from_user.id, RegistrationRequest.phone)


async def state_registration_phone_query(message):
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['phone'] = message.text

    await bot.send_message(message.from_user.id, "Введите сообщение заявки")
    await bot.set_state(message.from_user.id, RegistrationRequest.title)


async def state_registration_title_query(message):
    admin_id_list = database.get_admin_id_list()
    registration_request_data = {}

    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['title'] = message.text

        registration_request_data["telegram_id"] = message.from_user.id
        registration_request_data["name"] = data["name"]
        registration_request_data["phone"] = data["phone"]
        registration_request_data["title"] = data["title"]

    try:
        database.insert_into_registration_request(registration_request_data)
        await bot.send_message(message.from_user.id,
                               messages.formed_registration_request(registration_request_data),
                               parse_mode="HTML")

        for admin_id in admin_id_list:
            await bot.send_message(admin_id,
                                   messages.new_registration_request,
                                   reply_markup=markups.get_registration_requests_list_markup(),
                                   parse_mode="HTML")

    except:
        await bot.send_message(message.from_user.id, messages.registration_request_error)

    await bot.delete_state(message.from_user.id, message.chat.id)


async def state_mail_title_query(message):
    mail_header = "⚡ <b>Рассылка от администратора</b>"
    admin_id_list = database.get_admin_id_list()

    registered_employees = database.get_registered_employees()

    for employee in registered_employees:
        if employee["telegram_id"] not in admin_id_list:
            try:
                await bot.send_message(employee["telegram_id"],
                                       mail_header + """

    """ + message.text,
                                       parse_mode="HTML")

            except:
                print("Нет")

    await bot.send_message(message.chat.id,
                           "Рассылка успешно отправлена")

    await bot.delete_state(message.from_user.id, message.chat.id)


async def state_feedback_title_query(message):
    feedback = {
        "telegram_id": message.chat.id,
        "title": message.text
    }

    try:
        database.insert_into_feedbacks(feedback)
        await bot.send_message(message.chat.id,
                               "🟢 <b>Отзыв был успешно отправлен</b>",
                               parse_mode="HTML")

    except:
        await bot.send_message(message.chat.id,
                               "🔴 <b>Во время отправки отзыва произошла ошибка</b>",
                               parse_mode="HTML")

    await bot.delete_state(message.from_user.id, message.chat.id)


bot.register_message_handler(state_registration_name_query, state=RegistrationRequest.name)
bot.register_message_handler(state_registration_phone_query, state=RegistrationRequest.phone)
bot.register_message_handler(state_registration_title_query, state=RegistrationRequest.title)
bot.register_message_handler(state_mail_title_query, state=MailTitle.title)
bot.register_message_handler(state_feedback_title_query, state=FeedbackTitle.title)

bot.add_custom_filter(asyncio_filters.StateFilter(bot))

if __name__ == "__main__":
    import asyncio

    asyncio.run(bot.polling())