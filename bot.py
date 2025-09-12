import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace 'YOUR_BOT_TOKEN' with your actual bot token from BotFather
BOT_TOKEN = "6824493542:AAFKzu1YzORsmjffc3Py6pwg8W0MbtOS9uQ"

# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /start command"""
    await update.message.reply_text(
        "Hello! I'm a simple bot. 🤖\n"
        "Use /help to see what I can do!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /help command"""
    help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
/hello - Say hello
/about - Get information about the bot
/echo [text] - Echo back your text

Just send me a message and I'll respond!
    """
    await update.message.reply_text(help_text)

async def hello_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /hello command"""
    user = update.message.from_user
    await update.message.reply_text(f"Hello {user.first_name}! 👋")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /about command"""
    await update.message.reply_text(
        "I'm a simple Telegram bot created with python-telegram-bot library.\n"
        "I can handle basic commands and respond to messages!"
    )

async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /echo command"""
    if context.args:
        text = ' '.join(context.args)
        await update.message.reply_text(f"You said: {text}")
    else:
        await update.message.reply_text("Please provide some text after /echo")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    user_message = update.message.text.lower()
    
    if 'hello' in user_message or 'hi' in user_message:
        await update.message.reply_text("Hello there! 😊")
    elif 'how are you' in user_message:
        await update.message.reply_text("I'm doing great! Thanks for asking! 🤖")
    elif 'thank' in user_message:
        await update.message.reply_text("You're welcome! 😊")
    else:
        await update.message.reply_text("I received your message! Try /help to see what I can do.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start the bot"""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("hello", hello_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("echo", echo_command))
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)

    # Start the bot
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()