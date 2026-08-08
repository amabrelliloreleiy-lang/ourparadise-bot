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
    btn2 = types.KeyboardButton("👑 Стать админом")
    btn3 = types.KeyboardButton("ℹ️ О боте")

    markup.add(btn1, btn2)
    markup.add(btn3)

    bot.send_message(
        message.chat.id,
        "Привет! 👋\n\n"
        "Добро пожаловать в нашего бота.\n"
        "Здесь ты можешь заполнить анкету или подать заявку на администратора.",
        reply_markup=markup
    )


@bot.message_handler(func=lambda message: message.text == "👑 Стать админом")
def admin_button(message):
    admin_application_start(message)


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

    remove_keyboard = types.ReplyKeyboardRemove()

    bot.send_message(
        message.chat.id,
        "⏳ Спасибо! Твоя заявка почти готова.",
        reply_markup=remove_keyboard
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

        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None
        )

        bot.edit_message_caption(
            f"{call.message.caption}\n\n"
            f"━━━━━━━━━━━━━━\n"
            f"✅ ЗАЯВКА ОДОБРЕНА — {chat_name}",
            call.message.chat.id,
            call.message.message_id
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

        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None
        )

        bot.edit_message_caption(
            f"{call.message.caption}\n\n"
            f"━━━━━━━━━━━━━━\n"
            f"❌ ЗАЯВКА ОТКЛОНЕНА — {chat_name}",
            call.message.chat.id,
            call.message.message_id
        )

def admin_application_start(message):
    msg = bot.send_message(
        message.chat.id,
        "👑 Заявка на администратора\n\n"
        "Напиши своё имя:"
    )

    bot.register_next_step_handler(
        msg,
        get_admin_name
    )


def get_admin_name(message):
    admin_name = message.text

    msg = bot.send_message(
        message.chat.id,
        "🆔 Теперь напиши свой Telegram username:"
    )

    bot.register_next_step_handler(
        msg,
        lambda m: get_admin_username(m, admin_name)
    )


def get_admin_username(message, admin_name):
    admin_username = message.text

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True
    )

    emerald_btn = types.KeyboardButton("💚 Emerald")
    ruby_btn = types.KeyboardButton("❤️ Ruby")

    markup.add(emerald_btn, ruby_btn)

    msg = bot.send_message(
        message.chat.id,
        "💬 В какой чат ты хочешь быть админом?",
        reply_markup=markup
    )

    bot.register_next_step_handler(
        msg,
        lambda m: get_admin_chat(
            m,
            admin_name,
            admin_username
        )
    )


def get_admin_chat(message, admin_name, admin_username):
    admin_chat = message.text

    if admin_chat not in ["💚 Emerald", "❤️ Ruby"]:
        msg = bot.send_message(
            message.chat.id,
            "❗Пожалуйста, выбери Emerald или Ruby."
        )

        bot.register_next_step_handler(
            msg,
            lambda m: get_admin_chat(
                m,
                admin_name,
                admin_username
            )
        )
        return

    remove_keyboard = types.ReplyKeyboardRemove()

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True
    )

    senior_btn = types.KeyboardButton("👑 Старший админ")
    junior_btn = types.KeyboardButton("🛡️ Младший админ")
    chat_admin_btn = types.KeyboardButton("💬 Админ по чату")
    active_btn = types.KeyboardButton("🔥 Админ по активу")
    edit_btn = types.KeyboardButton("🎬 Админ по монтажу")

    markup.add(senior_btn, junior_btn)
    markup.add(chat_admin_btn)
    markup.add(active_btn, edit_btn)

    msg = bot.send_message(
        message.chat.id,
        "👑 Каким админом ты хочешь быть?",
        reply_markup=markup
    )

    bot.register_next_step_handler(
        msg,
        lambda m: get_admin_role(
            m,
            admin_name,
            admin_username,
            admin_chat
        )
    )


def get_admin_role(
    message,
    admin_name,
    admin_username,
    admin_chat
):
    admin_role = message.text

    roles = [
        "👑 Старший админ",
        "🛡️ Младший админ",
        "💬 Админ по чату",
        "🔥 Админ по активу",
        "🎬 Админ по монтажу"
    ]

    if admin_role not in roles:
        msg = bot.send_message(
            message.chat.id,
            "❗Пожалуйста, выбери одну из предложенных ролей."
        )

        bot.register_next_step_handler(
            msg,
            lambda m: get_admin_role(
                m,
                admin_name,
                admin_username,
                admin_chat
            )
        )
        return

    remove_keyboard = types.ReplyKeyboardRemove()

    bot.send_message(
        message.chat.id,
        "⏳ Формирую твою заявку...",
        reply_markup=remove_keyboard
    )

    telegram_id = message.from_user.id

    application = (
        "👑 НОВАЯ ЗАЯВКА НА АДМИНИСТРАТОРА!\n\n"
        f"👤 Имя: {admin_name}\n"
        f"🆔 Telegram: {admin_username}\n"
        f"💬 Чат: {admin_chat}\n"
        f"👑 Роль: {admin_role}\n"
        f"🆔 ID: {telegram_id}"
    )

    bot.send_message(
        ADMIN_ID,
        application
    )

    bot.send_message(
        message.chat.id,
        "✅ Твоя заявка на администратора отправлена!\n\n"
        "Ожидай решения."
    )
    
bot.infinity_polling()
