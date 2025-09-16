import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Replace 'YOUR_BOT_TOKEN' with your actual bot token from BotFather
BOT_TOKEN = os.getenv('BOT_TOKEN')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Create inline keyboard
    keyboard = [
        [InlineKeyboardButton("Option 1", callback_data='opt1')],
        [InlineKeyboardButton("Option 2", callback_data='opt2')],
        [InlineKeyboardButton("Option 3", callback_data='opt3')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Please choose an option:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge the button press
    
    if query.data == 'opt1':
        await query.edit_message_text("You selected Option 1!")
    elif query.data == 'opt2':
        await query.edit_message_text("You selected Option 2!")
    elif query.data == 'opt3':
        await query.edit_message_text("You selected Option 3!")

# Setup
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))
application.run_polling()