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
import random

from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot import asyncio_filters

from src.database import DataBase
from src.commands import commands
from src import messages
from src import markups
from src import helpers
from io import BytesIO
from barcode import EAN13
from barcode.writer import SVGWriter
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

import config


class TemporaryInfoState(StatesGroup):
    registration_request_name = State()
    registration_request_title = State()
    registration_request_phone = State()

    prev_instrumentation_message_id = State()
    instrumentation_message_id = State()

    instrumentation_title = State()
    instrumentation_model = State()
    instrumentation_type_id = State()

    mail_title = State()
    feedback_title = State()

    request_id = State()
    employee_id = State()


bot = AsyncTeleBot(config.bot_config["telegram"]["key"], state_storage=StateMemoryStorage())
database = DataBase(config.bot_config["supabase"]["url"],
                    config.bot_config["supabase"]["key"])


"""
STATE
HANDLERS
"""


async def state_instrumentation_title_query(message):
    prev_message = ""

    instrumentation = {
        'title': "",
        'model': None,
        'calibration_date': None,
        'instr_type_id': None,
        'instr_subject_id': None,
        'instr_employee_id': None,
        'instr_barcode_serial': None
    }

    msg = await bot.send_message(message.chat.id,
                                 "<b>Напишите модель прибора</b>",
                                 parse_mode="HTML")

    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['instrumentation_title'] = message.text

        prev_message = data['prev_instrumentation_message_id']

        data['prev_instrumentation_message_id'] = msg.message_id

        instrumentation['title'] = message.text

        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=data['instrumentation_message_id'],
                                    text=messages.add_new_instrumentation(instrumentation),
                                    parse_mode="HTML")

    await bot.delete_message(message.chat.id,
                             prev_message)
    await bot.delete_message(message.chat.id,
                             message.message_id)

    await bot.set_state(message.chat.id, TemporaryInfoState.instrumentation_model)


async def state_instrumentation_model_query(message):
    prev_message = ""

    instrumentation = {
        'title': "",
        'model': "",
        'instr_type_id': None,
        'instr_subject_id': None,
        'instr_employee_id': None,
        'instr_barcode_serial': None
    }

    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['instrumentation_model'] = message.text

        prev_message = data['prev_instrumentation_message_id']

        instrumentation['title'] = data['instrumentation_title']
        instrumentation['model'] = message.text

        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=data['instrumentation_message_id'],
                                    text=messages.add_new_instrumentation(instrumentation),
                                    parse_mode="HTML")

    await bot.delete_message(message.chat.id,
                             prev_message)
    await bot.delete_message(message.chat.id,
                             message.message_id)

    instrumentation_types = database.get_instrumentation_types()
    page = 1

    await bot.send_message(message.chat.id,
                                 "<b>Тип инструмента:</b>",
                                 parse_mode="HTML",
                                 reply_markup=markups.instrumentation_types_list(instrumentation_types, page))


async def state_registration_name_query(message):
    print(message.text)
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['registration_request_name'] = message.text

    await bot.send_message(message.from_user.id, "Введите номер телефона")
    await bot.set_state(message.from_user.id, TemporaryInfoState.registration_request_phone)


async def state_registration_phone_query(message):
    print(message.text)
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['registration_request_phone'] = message.text

    await bot.send_message(message.from_user.id, "Введите сообщение заявки")
    await bot.set_state(message.from_user.id, TemporaryInfoState.registration_request_title)


async def state_registration_title_query(message):
    print(message.text)
    admin_id_list = database.get_admin_id_list()
    registration_request_data = {}

    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['registration_request_title'] = message.text

        registration_request_data["telegram_id"] = message.from_user.id
        registration_request_data["name"] = data["registration_request_name"]
        registration_request_data["phone"] = data["registration_request_phone"]
        registration_request_data["title"] = data["registration_request_title"]

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

    await bot.delete_state(message.chat.id)


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
                print(f"До {employee['telegram_id']} не дошла рассылка")

    await bot.send_message(message.chat.id,
                           "Рассылка успешно отправлена")


async def state_feedback_title_query(message):
    print(message.text)
    feedback = {
        "telegram_id": message.chat.id,
        "title": message.text
    }

    try:
        database.insert_into_feedbacks(feedback)
        await bot.send_message(message.chat.id,
                               "🟢 <b>Отзыв был успешно отправлен</b>",
                               parse_mode="HTML",
                               reply_markup=markups.open_profile_markup())

    except:
        await bot.send_message(message.chat.id,
                               "🔴 <b>Во время отправки отзыва произошла ошибка</b>",
                               parse_mode="HTML")


bot.register_message_handler(state_registration_name_query, state=TemporaryInfoState.registration_request_name)
bot.register_message_handler(state_registration_phone_query, state=TemporaryInfoState.registration_request_phone)
bot.register_message_handler(state_registration_title_query, state=TemporaryInfoState.registration_request_title)

bot.register_message_handler(state_mail_title_query, state=TemporaryInfoState.mail_title)

bot.register_message_handler(state_feedback_title_query, state=TemporaryInfoState.feedback_title)

bot.register_message_handler(state_instrumentation_title_query, state=TemporaryInfoState.instrumentation_title)
bot.register_message_handler(state_instrumentation_model_query, state=TemporaryInfoState.instrumentation_model)

bot.add_custom_filter(asyncio_filters.StateFilter(bot))


"""
COMMAND
HANDLERS
"""

async def command_start_query(message):
    await bot.delete_message(message.chat.id, message.message_id)
    loading_msg = await bot.send_message(message.chat.id,
                                         "♻ Загружаю...")

    await bot.delete_my_commands()
    await bot.set_my_commands(commands=commands)

    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=loading_msg.message_id,
                                text=messages.start_message,
                                parse_mode="HTML")

    telegram_id_in_database = database.telegram_id_in_employees(message.chat.id)

    if not telegram_id_in_database:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=loading_msg.message_id,
                                    text=messages.not_register_user_message,
                                    reply_markup=markups.leave_registration_request_markup(),
                                    parse_mode="HTML")


async def command_help_query(message):
    await bot.delete_message(message.chat.id, message.message_id)
    loading_msg = await bot.send_message(message.chat.id,
                                         "♻ Загружаю...")

    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=loading_msg.message_id,
                                text=messages.help_message,
                                parse_mode="HTML",
                                reply_markup=markups.admin_tg_profile_open_markup())


async def command_profile_query(message):
    await bot.delete_message(message.chat.id, message.message_id)
    loading_msg = await bot.send_message(message.chat.id,
                                         "♻ Загружаю профиль...")

    telegram_id_in_database = database.telegram_id_in_employees(message.chat.id)

    if not telegram_id_in_database:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=loading_msg.message_id,
                                    text=messages.not_register_user_message,
                                    reply_markup=markups.leave_registration_request_markup(),
                                    parse_mode="HTML")
        return

    telegram_id_is_admin = database.telegram_id_is_admin(message.chat.id)

    if telegram_id_is_admin:
        admin = database.get_employee_by_telegram_id(message.chat.id)

        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=loading_msg.message_id,
                                    text=messages.admin_profile_info(admin),
                                    reply_markup=markups.admin_profile_markup(),
                                    parse_mode="HTML")

    else:
        user = database.get_employee_by_telegram_id(message.chat.id)

        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=loading_msg.message_id,
                                    text=messages.user_profile_info(user),
                                    reply_markup=markups.user_profile_markup(),
                                    parse_mode="HTML")


async def command_feedback_query(message):
    await bot.delete_message(message.chat.id, message.message_id)
    loading_msg = await bot.send_message(message.chat.id,
                                         "♻ Загружаю...")

    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=loading_msg.message_id,
                                text="Хотите оставить отзыв? Пожалуйста напиши ниже ваши впечатления от использования бота:",
                                reply_markup=markups.cancel_markup(),
                                parse_mode="HTML")

    await bot.set_state(message.chat.id,
                        TemporaryInfoState.feedback_title)


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
                            TemporaryInfoState.registration_request_name)


        await bot.send_message(call.message.chat.id,
                               "Напишите свое имя и фамилия",
                               reply_markup=markups.cancel_markup())


async def callback_open_registration_requests_query(call):
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text="♻ Загружаю...")

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
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text="♻ Загружаю...")

    request_id = helpers.get_id(call.data)
    request = database.get_registration_request_by_id(request_id)

    await bot.set_state(call.message.chat.id, TemporaryInfoState.request_id)

    async with bot.retrieve_data(call.message.chat.id) as data:
        data['request_id'] = request_id

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=messages.registration_request(request),
                                reply_markup=markups.registration_request_action_markup(),
                                parse_mode="HTML")


async def callback_decline_registration_request_query(call):
    request_id = None

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text="♻ Загружаю...")

    async with bot.retrieve_data(call.message.chat.id) as data:
        request_id = data['request_id']

    request = database.get_registration_request_by_id(request_id)
    database.set_registration_request_is_cancelled(request_id)

    await bot.send_message(request["telegram_id"],
                           "🔴 <b>Заявка была отклонена администратором</b>",
                           parse_mode="HTML")

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text="🟢 <b>Заявка была отклонена</b>",
                                parse_mode="HTML")

    registration_requests = database.get_registration_requests()
    is_registration_requests_empty = False

    if len(registration_requests) == 0:
        return True

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=messages.select_requests(is_registration_requests_empty),
                                reply_markup=markups.registration_requests_list_markup(registration_requests))


async def callback_profile_query(call):
    telegram_id_in_database = database.telegram_id_in_employees(call.message.chat.id)

    if not telegram_id_in_database:
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=messages.not_register_user_message,
                                    reply_markup=markups.leave_registration_request_markup(),
                                    parse_mode="HTML")
        return

    try:
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text="♻ Загружаю профиль...")

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

    except:
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text="🔴 Произошла ошибка",
                                    reply_markup=markups.open_profile_markup())


async def callback_accept_registration_request_id_query(call):
    employees_without_telegram_id = database.get_employees_without_telegram_id()

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text="Выберите сотрудника для привязки 🔽",
                                reply_markup=markups.employees_without_telegram_id_list_markup(
                                    employees_without_telegram_id),
                                parse_mode="HTML")


async def callback_handling_registration_request_employee_query(call):
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text="♻ Получаю сотрудников...")

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
                        TemporaryInfoState.mail_title)

    await bot.send_message(call.message.chat.id,
                           "💬 <b>Напишите сообщения рассылки:</b>",
                           reply_markup=markups.cancel_markup(),
                           parse_mode="HTML")


async def callback_hide_message_query(call):
    message_id = None

    if ":" in call.data:
        message_id = helpers.get_id(call.data)

    if message_id is not None:
        print(message_id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        await bot.delete_message(call.message.chat.id, message_id)

    else:
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
                                text=messages.employees_list,
                                reply_markup=markups.employees_list(filtered_employees, page),
                                parse_mode="HTML")


async def callback_employee_query(call):
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text="♻ Загружаю сотрудника...")

    employee_id = helpers.get_id(call.data)
    employee = database.get_employee_by_id(employee_id)

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=messages.employee_card(employee),
                                parse_mode="HTML",
                                reply_markup=markups.employee_action_markup(employee))


async def callback_journals_query(call):
    try:
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text="📃 <b>Доступные журналы</b>",
                                    parse_mode="HTML",
                                    reply_markup=markups.journals_list())

    except:
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text="🔴 Произошла ошибка",
                                    reply_markup=markups.open_profile_markup())


async def callback_open_instrumental_types_query(call):
    try:
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=messages.instrumentation_types,
                                    parse_mode="HTML",
                                    reply_markup=markups.open_instrumental_types())

    except:
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text="🔴 Произошла ошибка",
                                    reply_markup=markups.open_profile_markup())


async def callback_open_instrumental_list_query(call):
    telegram_id_is_admin = database.telegram_id_is_admin(call.message.chat.id)

    instrumentations = database.get_instrumentations()
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=messages.instrumentation_list,
                                parse_mode="HTML",
                                reply_markup=markups.instrumental_list(instrumentations, telegram_id_is_admin))



async def callback_instrumentation_query(call):
    is_allowed_to_edit = False

    telegram_id_is_admin = database.telegram_id_is_admin(call.message.chat.id)

    try:
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text="♻ Загружаю прибор...")

        instrumentation_id = helpers.get_id(call.data)
        instrumentation = database.get_instrumentation_by_id(instrumentation_id)

        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=messages.instrumentation_card(instrumentation),
                                    parse_mode="HTML",
                                    reply_markup=markups.instrumentation_action(instrumentation, telegram_id_is_admin))

    except:
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text="🔴 Произошла ошибка",
                                    reply_markup=markups.open_profile_markup())


async def callback_show_barcode_query(call):
    instrumentation_id = helpers.get_id(call.data)
    instrumentation = database.get_instrumentation_by_id(instrumentation_id)

    barcode_img = BytesIO()

    barcode_svg = BytesIO()
    EAN13(instrumentation["barcode_serial"], writer=SVGWriter()).write(barcode_svg)
    barcode_svg.seek(0)

    drawing = svg2rlg(barcode_svg)
    renderPM.drawToFile(drawing, barcode_img, fmt='PNG', dpi=288)

    msg = await bot.send_message(call.message.chat.id,
                           "♻ <b>Генерирую штрих-код</b>",
                           parse_mode="HTML")

    await bot.send_chat_action(call.message.chat.id, "upload_photo")

    await bot.send_photo(call.message.chat.id,
                         barcode_img.getvalue(),
                         reply_markup=markups.hide_message(msg.message_id))

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=msg.message_id,
                                text=f"<b>Прибор №{instrumentation['id']} - Штрих-код</b>",
                                parse_mode="HTML")


async def callback_cancel_query(call):
    try:
        await bot.delete_state(call.message.chat.id)
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text="<b>Операция отменена</b>",
                                    parse_mode="HTML",
                                    reply_markup=markups.open_profile_markup())

    except:
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text="<b>При отмене операции произошла ошибка</b>",
                                    parse_mode="HTML")


async def callback_feedback_query(call):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    loading_msg = await bot.send_message(call.message.chat.id,
                                         "♻ Загружаю...")

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=loading_msg.message_id,
                                text="Хотите оставить отзыв? Пожалуйста напиши ниже ваши впечатления от использования бота:",
                                reply_markup=markups.cancel_markup(),
                                parse_mode="HTML")

    await bot.set_state(call.message.chat.id,
                             TemporaryInfoState.feedback_title)


async def callback_open_employee_instrumentation_query(call):
    telegram_id_is_admin = database.telegram_id_is_admin(call.message.chat.id)

    instrumentations = database.get_instrumentations()

    employees_instrumentations = list(filter(lambda dict: dict['employees']['telegram_id'] == call.message.chat.id, instrumentations))

    if len(employees_instrumentations) == 0:
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text="<b>⚠ У вас нет привязанных приборов</b>",
                                    parse_mode="HTML",
                                    reply_markup=markups.open_profile_markup())

    else:
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=messages.employees_instrumentation_list,
                                    parse_mode="HTML",
                                    reply_markup=markups.instrumental_list(employees_instrumentations, telegram_id_is_admin))


async def callback_contacts_query(call):
    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text="♻ Загружаю...")

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=messages.contacts,
                                reply_markup=markups.open_profile_markup(),
                                parse_mode="HTML")

async def callback_unhandle_employee_query(call):
    employee_id = helpers.get_id(call.data)
    employee = database.get_employee_by_id(employee_id)

    try:
        database.set_telegram_id_unhandle(employee_id)

        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text="🟢 <b>Телеграмм отвязан</b>",
                                    reply_markup=markups.open_profile_markup(),
                                    parse_mode="HTML")

        await bot.send_message(employee["telegram_id"],
                               "⚠ Вы были отвязаны от сотрудника")

    except:
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text="🔴 <b>При отвязке телеграмма произошла ошибка</b>",
                                    reply_markup=markups.open_profile_markup(),
                                    parse_mode="HTML")


async def callback_delete_employee_query(call):
    print(call.data)
    employee_id = helpers.get_id(call.data)
    employee = database.get_employee_by_id(employee_id)

    try:
        database.delete_employee_by_id(employee_id)

        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text="🟢 <b>Сотрудник был удален</b>",
                                    reply_markup=markups.open_profile_markup(),
                                    parse_mode="HTML")

        if employee["telegram_id"] is not None:
            await bot.send_message(employee["telegram_id"],
                                   "🔴 <b>Сотрудник, к которому вы были привязаны удален администратором</b>",
                                   parse_mode="HTML")

    except:
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text="🔴 При удалении сотрудника произошла ошибка",
                                    reply_markup=markups.open_profile_markup())


async def callback_delete_instrumentation_query(call):
    print(call.data)
    instrumentation_id = helpers.get_id(call.data)

    try:
        database.delete_instrumentation_by_id(instrumentation_id)

        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text="🟢 <b>Прибор был удален</b>",
                                    reply_markup=markups.open_profile_markup(),
                                    parse_mode="HTML")

    except:
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text="🔴 <b>При удалении прибора произошла ошибка</b>",
                                    reply_markup=markups.open_profile_markup(),
                                    parse_mode="HTML")

async def callback_return_from_repair_query(call):
    instrumentation_id = helpers.get_id(call.data)
    employee_id = database.get_employee_by_telegram_id(call.message.chat.id)["id"]

    repair =  {
        "instrumentation_id": instrumentation_id,
        "employee_id": employee_id,
        "status_id": 2,
        "is_successfull": True
    }

    database.insert_into_repairs(repair)

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text="🟢 <b>Зафиксировано получение прибора с ремонта</b>",
                                reply_markup=markups.open_profile_markup(),
                                parse_mode="HTML")

async def callback_set_on_repair_query(call):
    instrumentation_id = helpers.get_id(call.data)
    employee_id = database.get_employee_by_telegram_id(call.message.chat.id)["id"]

    repair = {
        "instrumentation_id": instrumentation_id,
        "employee_id": employee_id,
        "status_id": 1,
        "is_successfull": None
    }

    database.insert_into_repairs(repair)

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=messages.set_on_repair,
                                reply_markup=markups.open_profile_markup(),
                                parse_mode="HTML")


async def callback_open_subjects_list_query(call):
    telegram_id_is_admin = database.telegram_id_is_admin(call.message.chat.id)
    page = 1

    if ":" in call.data:
        page = helpers.get_id(call.data)

    subjects = database.get_subjects()

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=messages.subjects_list,
                                reply_markup=markups.subjects_list(subjects, page, telegram_id_is_admin),
                                parse_mode="HTML")


async def callback_subject_card_query(call):
    telegram_id_is_admin = database.telegram_id_is_admin(call.message.chat.id)
    subject_id = helpers.get_id(call.data)

    subject = database.get_subject_by_id(subject_id)

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=messages.subject_card(subject),
                                reply_markup=markups.subject_action(subject, telegram_id_is_admin),
                                parse_mode="HTML")


async def callback_open_subject_in_map_query(call):
    subject_id = helpers.get_id(call.data)
    subject = database.get_subject_by_id(subject_id)

    msg = await bot.send_message(call.message.chat.id,
                                 "♻ Загружаю карту")

    await bot.send_location(call.message.chat.id,
                            subject['latitude'],
                            subject['longitude'],
                            reply_markup=markups.hide_message(msg.message_id))

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=msg.message_id,
                                text=f"<b>Карта объекта</b> {subject['title']} - {subject['code']}",
                                parse_mode="HTML")


async def callback_add_new_instrumentation_query(call):
    instrumentation_card = await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text="🛠 <b>Добавление прибора</b>",
                                parse_mode="HTML")

    await bot.set_state(call.message.chat.id, TemporaryInfoState.instrumentation_message_id)

    msg = await bot.send_message(call.message.chat.id,
                           "<b>Напишите название прибора</b>",
                           parse_mode="HTML")

    print(msg.message_id)

    async with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
        data['instrumentation_message_id'] = instrumentation_card.message_id
        data['prev_instrumentation_message_id'] = msg.message_id

    await bot.set_state(call.message.chat.id, TemporaryInfoState.instrumentation_title)


async def callback_open_new_instrumentation_type_list_query(call):
    page = 1
    instrumentation_types = database.get_instrumentation_types()

    if ":" in call.data:
        page = helpers.get_id(call.data)

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text="<b>Тип инструмента:</b>",
                                reply_markup=markups.instrumentation_types_list(instrumentation_types, page),
                                parse_mode="HTML")


async def callback_new_instrumentation_type_handling_query(call):
    instr_type_id = helpers.get_id(call.data)

    instrumentation = {
        'title': "",
        'model': "",
        'instr_type_id': ""
    }

    async with bot.retrieve_data(call.message.chat.id) as data:
        data['instrumentation_type_id'] = instr_type_id

        instrumentation['title'] = data['instrumentation_title']
        instrumentation['model'] = data['instrumentation_model']
        instrumentation['instr_type_id'] = instr_type_id

        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=data['instrumentation_message_id'],
                                    text=messages.add_new_instrumentation(instrumentation),
                                    reply_markup=markups.adding_new_instrumentation_action(),
                                    parse_mode="HTML")

    await bot.delete_message(call.message.chat.id,
                             call.message.message_id)


async def callback_accept_instrumentation_adding_query(call):
    msg = ""

    instrumentation = {
        'title': "",
        'model': "",
        'calibration_date': "",
        'instr_type_id': ""
    }

    async with bot.retrieve_data(call.message.chat.id) as data:
        instrumentation['title'] = data['instrumentation_title']
        instrumentation['model'] = data['instrumentation_model']
        instrumentation['instr_type_id'] = data['instrumentation_type_id']

        msg = data['instrumentation_message_id']

    database.insert_into_instrumentations(instrumentation)

    await bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=msg,
                                text="🟢 <b>Прибор был успешно добавлен</b>",
                                reply_markup=markups.open_profile_markup(),
                                parse_mode="HTML")


async def callback_on_development_query(call):
    await bot.answer_callback_query(call.id,
                                    "Функция находиться на разработке",
                                    show_alert=True)

bot.register_callback_query_handler(callback_on_development_query,
                                    func=lambda call: call.data == "on_development")

bot.register_callback_query_handler(callback_delete_employee_query,
                                    func=lambda call: "delete_employee" in call.data)

bot.register_callback_query_handler(callback_delete_instrumentation_query,
                                    func=lambda call: "delete_instrumentation" in call.data)

bot.register_callback_query_handler(callback_start_registration_query,
                                    func=lambda call: call.data == "start_registration")

bot.register_callback_query_handler(callback_open_registration_requests_query,
                                    func=lambda call: call.data == "open_registrations_list")

bot.register_callback_query_handler(callback_open_subjects_list_query,
                                    func=lambda call: "open_subjects_list" in call.data)

bot.register_callback_query_handler(callback_mail_query,
                                    func=lambda call: call.data == "mail")

bot.register_callback_query_handler(callback_hide_message_query,
                                    func=lambda call: "hide" in call.data)

bot.register_callback_query_handler(callback_profile_query,
                                    func=lambda call: call.data == "profile")

bot.register_callback_query_handler(callback_journals_query,
                                    func=lambda call: call.data == "journals")

bot.register_callback_query_handler(callback_feedback_query,
                                    func=lambda call: call.data == "feedback")

bot.register_callback_query_handler(callback_cancel_query,
                                    func=lambda call: call.data == "cancel")

bot.register_callback_query_handler(callback_contacts_query,
                                    func=lambda call: call.data == "contacts")

bot.register_callback_query_handler(callback_add_new_instrumentation_query,
                                    func=lambda call: call.data == "add_new_instrumentation")

bot.register_callback_query_handler(callback_open_instrumental_types_query,
                                    func=lambda call: call.data == "open_instrumentation_types")

bot.register_callback_query_handler(callback_open_employee_instrumentation_query,
                                    func=lambda call: call.data == "open_employee_instrumentation")

bot.register_callback_query_handler(callback_open_instrumental_list_query,
                                    func=lambda call: call.data == "open_instrumentation_list")

bot.register_callback_query_handler(callback_accept_instrumentation_adding_query,
                                    func=lambda call: call.data == "accept_instrumentation_adding")

bot.register_callback_query_handler(callback_new_instrumentation_type_handling_query,
                                    func=lambda call: "new_instrumentation_type_handling" in call.data)

bot.register_callback_query_handler(callback_add_new_instrumentation_query,
                                    func=lambda call: "open_new_instrumentation_type_list" in call.data)

bot.register_callback_query_handler(callback_employee_query,
                                    func=lambda call: "employee_card" in call.data)

bot.register_callback_query_handler(callback_open_employees_list_query,
                                    func=lambda call: "open_employees_list" in call.data)

bot.register_callback_query_handler(callback_decline_registration_request_query,
                                    func=lambda call: "decline_registration_request" in call.data)

bot.register_callback_query_handler(callback_accept_registration_request_id_query,
                                    func=lambda call: "accept_registration_request" in call.data)

bot.register_callback_query_handler(callback_registration_request_id_query,
                                    func=lambda call: "registration_request" in call.data)

bot.register_callback_query_handler(callback_handling_registration_request_employee_query,
                                    func=lambda call: "handling_registration_employee" in call.data)

bot.register_callback_query_handler(callback_accept_employee_handling_query,
                                    func=lambda call: "accept_employee_handling" in call.data)

bot.register_callback_query_handler(callback_instrumentation_query,
                                    func=lambda call: "instrumentation" in call.data)

bot.register_callback_query_handler(callback_show_barcode_query,
                                    func=lambda call: "show_barcode" in call.data)

bot.register_callback_query_handler(callback_unhandle_employee_query,
                                    func=lambda call: "unhandle_employee" in call.data)

bot.register_callback_query_handler(callback_return_from_repair_query,
                                    func=lambda call: "return_from_repair" in call.data)

bot.register_callback_query_handler(callback_set_on_repair_query,
                                    func=lambda call: "set_on_repair" in call.data)

bot.register_callback_query_handler(callback_subject_card_query,
                                    func=lambda call: "subject_card" in call.data)

bot.register_callback_query_handler(callback_open_subject_in_map_query,
                                    func=lambda call: "open_subject_in_map" in call.data)

@bot.message_handler(func=lambda message: True)
async def alert_warning(message):
    await bot.send_message(message.chat.id,
                           "⚠ Неизвестная команда, напишите /help для помощи")


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.polling())
