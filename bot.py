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
        "📸 Теперь отправь фото паспорта, где видно твоё фото и Telegram username:"
    )
    bot.register_next_step_handler(
        msg,
        lambda m: get_passport(m, user_name)
    )


def get_passport(message, user_name):
    if not message.photo:
        msg = bot.send_message(
            message.chat.id,
            "❗Пожалуйста, отправь именно фото паспорта."
        )
        bot.register_next_step_handler(
            msg,
            lambda m: get_passport(m, user_name)
        )
        return

    photo_id = message.photo[-1].file_id

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True
    )

    emerald_btn = types.KeyboardButton("💚 Emerald")
    ruby_btn = types.KeyboardButton("❤️ Ruby")

    markup.add(emerald_btn, ruby_btn)

    msg = bot.send_message(
        message.chat.id,
        "💬 Выберите чат, в который хотите вступить:",
        reply_markup=markup
    )

    bot.register_next_step_handler(
        msg,
        lambda m: get_chat(m, user_name, photo_id)
    )


def get_chat(message, user_name, photo_id):
    chat_choice = message.text

    if chat_choice not in ["💚 Emerald", "❤️ Ruby"]:
        msg = bot.send_message(
            message.chat.id,
            "❗Пожалуйста, выберите Emerald или Ruby."
        )
        bot.register_next_step_handler(
            msg,
            lambda m: get_chat(m, user_name, photo_id)
        )
        return

    bot.send_message(
        message.chat.id,
        "⏳ Спасибо! Твоя заявка почти готова."
    )

    username = message.from_user.username

    if username:
        username = "@" + username
    else:
        username = "Не указан"

    application = (
        "📩 Новая заявка!\n\n"
        f"👤 Имя: {user_name}\n"
        f"📱 Telegram: {username}\n"
        f"💬 Чат: {chat_choice}\n"
        f"🆔 ID: {message.from_user.id}"
    )

    chat_code = "emerald" if chat_choice == "💚 Emerald" else "ruby"

    markup = types.InlineKeyboardMarkup()

    approve_btn = types.InlineKeyboardButton(
        "🟢 Одобрить",
        callback_data=f"approve_{message.from_user.id}_{chat_code}"
    )

    reject_btn = types.InlineKeyboardButton(
        "🔴 Отклонить",
        callback_data=f"reject_{message.from_user.id}_{chat_code}"
    )

    markup.add(approve_btn, reject_btn)

    bot.send_photo(
        ADMIN_ID,
        photo_id,
        caption=application,
        reply_markup=markup
    )

    bot.send_message(
        message.chat.id,
        "✅ Спасибо! Твоя анкета отправлена."
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
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data.split("_", 2)

    action = data[0]
    user_id = data[1]
    chat_code = data[2]

    CHAT_LINKS = {
        "emerald": ("💚 Emerald", "https://t.me/+969IILczHrFhZjli"),
        "ruby": ("❤️ Ruby", "https://t.me/+QHf2PYZfIroyODAy")
    }

    chat_name, chat_link = CHAT_LINKS.get(
        chat_code,
        ("Неизвестный чат", "")
    )

    if action == "approve":
        bot.send_message(
            user_id,
            f"✅ Ваша заявка одобрена!\n\n"
            f"💬 Ваш чат: {chat_name}\n\n"
            f"🔗 Ссылка для вступления:\n{chat_link}"
        )

        bot.answer_callback_query(
            call.id,
            f"Заявка одобрена — {chat_name}"
        )

    elif action == "reject":
        bot.send_message(
            user_id,
            "❌ К сожалению, ваша заявка не одобрена."
        )

        bot.answer_callback_query(
            call.id,
            f"Заявка отклонена — {chat_name}"
        )


bot.infinity_polling()
