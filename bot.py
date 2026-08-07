import telebot
from telebot import types

import os

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 6824091360


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📝 Заполнить анкету")
    btn2 = types.KeyboardButton("ℹ️ О боте")
    markup.add(btn1, btn2)

    bot.send_message(
        message.chat.id,
        "Привет! 👋\n\n"
        "Добро пожаловать в нашего бота.\n"
        "Здесь ты можешь заполнить анкету и отправить заявку.",
        reply_markup=markup
    )


@bot.message_handler(commands=["anketa"])
def anketa(message):
    msg = bot.send_message(
        message.chat.id,
        "Напиши своё имя:"
    )
    bot.register_next_step_handler(msg, get_name)


def get_name(message):
    user_name = message.text

    msg = bot.send_message(
        message.chat.id,
        "Теперь напиши свой возраст:"
    )
    bot.register_next_step_handler(
        msg,
        lambda m: get_age(m, user_name)
    )


def get_age(message, user_name):
    age = message.text

    application = (
        "📩 Новая заявка!\n\n"
        f"👤 Имя: {user_name}\n"
        f"🎂 Возраст пришлите фото паспорта: {age}\n"
        f"🆔 ID: {message.from_user.id}"
    )

    if ADMIN_ID != 0:
        bot.send_message(ADMIN_ID, application)

    bot.send_message(
        message.chat.id,
        "Спасибо! ✅\nТвоя заявка отправлена."
    )


@bot.message_handler(func=lambda message: message.text == "📝 Заполнить анкету")
def button_anketa(message):
    anketa(message)


@bot.message_handler(func=lambda message: message.text == "ℹ️ О боте")
def about(message):
    bot.send_message(
        message.chat.id,
        "Это бот для приёма заявок 🤍"
    )


print("Бот запущен!")

bot.remove_webhook()
bot.infinity_polling()
