import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot token from BotFather
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Database path
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db")
os.makedirs(DB_DIR, exist_ok=True)

# Database file pattern
DB_FILE_PATTERN = "expenses_{chat_id}.db"

# Currency settings
CURRENCY = "IDR"
CURRENCY_SYMBOL = "Rp"

# Default transaction type (when no sign is specified)
DEFAULT_TRANSACTION_TYPE = "expense"