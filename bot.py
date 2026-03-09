import sqlite3

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = "8688678667:AAH_ughK0qx-D3hpkm6Cr-24itNH3dLACV8"

ADMIN_ID = 1339971434  # сюда вставь свой telegram id


# DATABASE

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY,
username TEXT
)
""")

conn.commit()


def save_user(user_id, username):

    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
        (user_id, username)
    )

    conn.commit()


# MENU

def main_menu():

    keyboard = [

        [InlineKeyboardButton("📖 О проекте", callback_data="about")],
        [InlineKeyboardButton("📢 Открытый канал", callback_data="open_channel")],
        [InlineKeyboardButton("🔒 Закрытый канал", callback_data="private_channel")],
        [InlineKeyboardButton("💬 Связаться со мной", callback_data="contact")]

    ]

    return InlineKeyboardMarkup(keyboard)


# START

async def start(update, context):

    user = update.effective_user

    save_user(user.id, user.username)

    await update.message.reply_text(
        "Добро пожаловать в AthleteLords ⚽",
        reply_markup=main_menu()
    )


# BUTTONS

async def button(update, context):

    query = update.callback_query
    await query.answer()

    back_button = InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅ Назад", callback_data="menu")]]
    )

    if query.data == "about":

        text = "AthleteLords — система развития футболиста."

        await query.edit_message_text(text, reply_markup=back_button)

    elif query.data == "open_channel":

        text = "Открытый канал 👇\nhttps://t.me/athletelords"

        await query.edit_message_text(text, reply_markup=back_button)

    elif query.data == "private_channel":

        text = "Закрытый канал AthleteLords 🔒"

        await query.edit_message_text(text, reply_markup=back_button)

    elif query.data == "contact":

        text = "Напиши свой вопрос следующим сообщением."

        await query.edit_message_text(text, reply_markup=back_button)

    elif query.data == "menu":

        await query.edit_message_text(
            "Главное меню:",
            reply_markup=main_menu()
        )


# HANDLE USER MESSAGES

async def handle_message(update, context):

    user = update.effective_user
    text = update.message.text

    if user.id != ADMIN_ID:

        message = f"""
Новое сообщение от пользователя

Username: @{user.username}
ID: {user.id}

Сообщение:
{text}
"""

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=message
        )


# ADMIN COMMANDS

async def users(update, context):

    if update.effective_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM users")

    count = cursor.fetchone()[0]

    await update.message.reply_text(f"Пользователей в базе: {count}")


async def broadcast(update, context):

    if update.effective_user.id != ADMIN_ID:
        return

    message = " ".join(context.args)

    cursor.execute("SELECT user_id FROM users")

    users = cursor.fetchall()

    for user in users:

        try:

            await context.bot.send_message(
                chat_id=user[0],
                text=message
            )

        except:

            pass


async def reply(update, context):

    if update.effective_user.id != ADMIN_ID:
        return

    user_id = int(context.args[0])

    message = " ".join(context.args[1:])

    await context.bot.send_message(
        chat_id=user_id,
        text=message
    )


# RUN BOT

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("users", users))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("reply", reply))

app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()