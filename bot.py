import logging
import sqlite3
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace 'YOUR_BOT_TOKEN' with your actual bot token from BotFather
# Replace 'YOUR_BOT_TOKEN' with your actual bot token from BotFather
BOT_TOKEN = "6824493542:AAFKzu1YzORsmjffc3Py6pwg8W0MbtOS9uQ"

# Database setup
DB_NAME = "C:\\Users\\adibpriatama\\Projects\\fintrack\\dbexpenses.db"

# Conversation states
CONFIRM_CLEAR = 1

def init_database():
    """Initialize the SQLite database with expenses table"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create expenses table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        description TEXT,
        date DATE NOT NULL DEFAULT CURRENT_DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def insert_expense(amount, description, date=None):
    """Insert an expense record into the database"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        if date is None:
            cursor.execute('''
            INSERT INTO expenses (amount, description)
            VALUES (?, ?)
            ''', (amount, description))
        else:
            cursor.execute('''
            INSERT INTO expenses (amount, description, date)
            VALUES (?, ?, ?)
            ''', (amount, description, date))
        
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error inserting expense: {e}")
        return False
    finally:
        conn.close()

def get_expenses(limit=15):
    """Get all expenses"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, amount, description, date, created_at 
        FROM expenses 
        ORDER BY date DESC, created_at DESC
        LIMIT ?
        ''', (limit,))
        
        expenses = cursor.fetchall()
        return expenses
    except Exception as e:
        logger.error(f"Error fetching expenses: {e}")
        return []
    finally:
        conn.close()

def get_total_expenses():
    """Get total amount of all expenses"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('SELECT SUM(amount) FROM expenses')
        total = cursor.fetchone()[0]
        return total or 0
    except Exception as e:
        logger.error(f"Error calculating total expenses: {e}")
        return 0
    finally:
        conn.close()

def clear_all_expenses():
    """Clear all expenses from the database"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM expenses')
        deleted_count = cursor.rowcount
        
        conn.commit()
        return deleted_count
    except Exception as e:
        logger.error(f"Error clearing expenses: {e}")
        return 0
    finally:
        conn.close()

# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /start command"""
    await update.message.reply_text(
        "💸 Expenses Bot is ready! 🤖\n\n"
        "Use /help to see available commands\n"
        "Use /add to add a new expense\n"
        "Use /view to see expenses\n"
        "Use /total to see the total amount"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /help command"""
    help_text = """
💸 Expenses Bot - Available commands:

/add - Add a new expense
/view - View recent expenses
/total - Show total expenses amount
/clear - Clear all expenses
/help - Show this help message

📝 Format for adding expenses:
amount, description, date (optional)

Examples:
/add 15.50, Lunch at restaurant
/add 29.99, Movie tickets, 2023-12-15
/add 100, Groceries

📅 Date format: YYYY-MM-DD (default: today)

You can also just send expenses without commands:
15.50, Lunch at restaurant
29.99, Movie tickets, 2023-12-15
    """
    await update.message.reply_text(help_text)

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /add command"""
    if not context.args:
        await update.message.reply_text(
            "Please provide expense details.\n\n"
            "Format: /add amount, description, date(optional)\n\n"
            "Example: /add 15.50, Lunch at restaurant\n"
            "Example: /add 29.99, Movie tickets, 2023-12-15"
        )
        return
    
    # Join arguments and split by commas
    data_line = ' '.join(context.args)
    fields = [field.strip() for field in data_line.split(',')]
    
    if len(fields) < 2:
        await update.message.reply_text("Please provide at least amount and description.")
        return
    
    # Parse amount
    try:
        amount = float(fields[0])
        if amount <= 0:
            await update.message.reply_text("Amount must be positive.")
            return
    except ValueError:
        await update.message.reply_text("Please provide a valid amount (number).")
        return
    
    description = fields[1]
    date = fields[2] if len(fields) > 2 else None
    
    # Validate date format if provided
    if date:
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            await update.message.reply_text("Date must be in YYYY-MM-DD format.")
            return
    
    success = insert_expense(amount, description, date)
    
    if success:
        response = f"✅ Expense added successfully!\n"
        response += f"💵 Amount: Rp {amount:.2f}\n"
        response += f"📝 Description: {description}\n"
        if date:
            response += f"📅 Date: {date}"
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("❌ Failed to add expense. Please try again.")

async def view_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /view command"""
    expenses = get_expenses(limit=15)
    
    if not expenses:
        await update.message.reply_text("No expenses recorded yet.")
        return
    
    total = sum(expense[1] for expense in expenses)
    
    response = "📋 Recent Expenses:\n\n"
    for expense in expenses:
        expense_id, amount, description, date, created_at = expense
        response += f"💵 Rp {amount:.2f} - {description}\n"
        response += f"📅 {date}\n"
        response += "─" * 30 + "\n"
    
    response += f"\n💰 Total: Rp {total:.2f}"
    
    await update.message.reply_text(response)

async def total_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /total command"""
    total = get_total_expenses()
    await update.message.reply_text(f"💰 Total expenses: Rp {total:.2f}")

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /clear command - starts the confirmation process"""
    total = get_total_expenses()
    if total == 0:
        await update.message.reply_text("There are no expenses to clear.")
        return ConversationHandler.END
    
    # Store chat_id and message_id for conversation context
    context.user_data['clear_chat_id'] = update.message.chat_id
    context.user_data['clear_message_id'] = update.message.message_id
    
    await update.message.reply_text(
        f"⚠️  WARNING: Are you sure you want to clear ALL expenses?\n\n"
        f"💰 Total amount: Rp {total:.2f}\n"
        f"🗑️  This action cannot be undone!\n\n"
        f"Type 'YES' to confirm or 'NO' to cancel."
    )
    return CONFIRM_CLEAR

async def confirm_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirmation for clear command"""
    user_response = update.message.text.upper().strip()
    
    if user_response == 'YES':
        deleted_count = clear_all_expenses()
        await update.message.reply_text(f"✅ Successfully cleared {deleted_count} expense(s).")
    elif user_response == 'NO':
        await update.message.reply_text("❌ Clear operation cancelled.")
    else:
        await update.message.reply_text("❌ Please type 'YES' to confirm or 'NO' to cancel.")
        return CONFIRM_CLEAR
    
    # Clear conversation data
    if 'clear_chat_id' in context.user_data:
        del context.user_data['clear_chat_id']
    if 'clear_message_id' in context.user_data:
        del context.user_data['clear_message_id']
    
    return ConversationHandler.END

async def cancel_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the clear operation"""
    # Clear conversation data
    if 'clear_chat_id' in context.user_data:
        del context.user_data['clear_chat_id']
    if 'clear_message_id' in context.user_data:
        del context.user_data['clear_message_id']
    
    await update.message.reply_text("❌ Clear operation cancelled.")
    return ConversationHandler.END

async def handle_expense_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle expense messages without commands"""
    # Skip if we're in a conversation
    if context.user_data.get('clear_chat_id'):
        return
    
    message_text = update.message.text.strip()
    
    # Skip if message is too short or doesn't contain a comma
    if len(message_text) < 3 or ',' not in message_text:
        return
    
    # Split by first comma to separate amount from description
    parts = message_text.split(',', 1)
    if len(parts) < 2:
        return
    
    amount_str = parts[0].strip()
    rest = parts[1].strip()
    
    # Check if rest contains a date (YYYY-MM-DD pattern)
    date = None
    description = rest
    
    # Look for date pattern at the end
    if len(rest.split(',')) >= 2:
        # If there's another comma, check if the last part is a date
        rest_parts = rest.rsplit(',', 1)
        possible_date = rest_parts[1].strip()
        
        try:
            datetime.strptime(possible_date, '%Y-%m-%d')
            date = possible_date
            description = rest_parts[0].strip()
        except ValueError:
            # Not a valid date, treat everything as description
            pass
    
    # Parse amount
    try:
        amount = float(amount_str)
        if amount <= 0:
            return
    except ValueError:
        return  # Not a valid amount
    
    success = insert_expense(amount, description, date)
    
    if success:
        response = f"✅ Expense recorded!\n"
        response += f"💵 Rp {amount:.2f} - {description}"
        if date:
            response += f"\n📅 {date}"
        await update.message.reply_text(response)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start the bot"""
    # Initialize database
    init_database()
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add conversation handler for clear command with proper filters
    clear_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('clear', clear_command)],
        states={
            CONFIRM_CLEAR: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND & filters.Regex(r'^(YES|NO)$'),
                    confirm_clear
                )
            ]
        },
        fallbacks=[
            CommandHandler('cancel', cancel_clear),
            MessageHandler(filters.TEXT & ~filters.COMMAND, cancel_clear)
        ],
        allow_reentry=True
    )

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add", add_command))
    application.add_handler(CommandHandler("view", view_command))
    application.add_handler(CommandHandler("total", total_command))
    application.add_handler(clear_conv_handler)
    
    # Add message handlers for expense detection (should come after conversation handler)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_expense_message
    ))
    
    # Add error handler
    application.add_error_handler(error_handler)

    # Start the bot
    print("Expenses bot is running and ready for your group...")
    application.run_polling()

if __name__ == "__main__":
    main()