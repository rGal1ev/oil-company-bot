from telebot.types import BotCommand

commands = [
    BotCommand("/start", "Если вы здесь впервые"),
    BotCommand("/about", "Для краткой информации про нас"),
    BotCommand("/help", "Используйте, если возникли вопросы"),
    BotCommand("/profile", "Ваш личный профиль, работает только с зарегистрированными пользователями"),
    BotCommand("/feedback", "Оставьте ваш отзыв, а также советы с улучшениями для бота :)")
]