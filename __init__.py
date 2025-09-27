"""
FinTrack - Telegram Bot for Household Cash Flow Tracking
"""

from .app.bot import FinTrackBot
from .config import BOT_TOKEN, DB_DIR, CURRENCY, CURRENCY_SYMBOL

__version__ = "1.0.0"
__author__ = "DeepSeek + Adib as prompter :("
__all__ = ['FinTrackBot', 'main']

def main():
    """Main function to start the bot"""
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Please set your bot token in config.py")
        return
    
    bot = FinTrackBot(BOT_TOKEN)
    bot.run()

if __name__ == "__main__":
    main()