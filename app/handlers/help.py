async def help_command(update, context):
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