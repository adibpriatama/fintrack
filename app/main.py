# app/main.py
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from app.handlers import start, help


# Load variables from .env file
load_dotenv()

# Read the token from the environment variable
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("No BOT_TOKEN found in .env file!")

# Create the Application
application = Application.builder().token(TOKEN).build()

# Register handlers - this is clean and clear
application.add_handler(CommandHandler("start", start.start_command))
application.add_handler(CommandHandler("help", help.help_command))
# Start the bot
application.run_polling()