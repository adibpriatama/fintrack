# FinTrack Bot 🤖 

A Telegram bot for tracking household cash flow with SQLite database support, built with Python and SQLAlchemy.

## Features ✨

- 💰 **Income & Expense Tracking** - Simple message format: `[category] [description] [+-][amount]`
- 🏠 **Multi-Group Support** - Separate databases for each Telegram group
- 📊 **Financial Charts** - Visualize spending with pie charts
- 🔍 **Search & Filter** - Find transactions by category or description
- 📈 **Balance Tracking** - Real-time balance calculation
- 🗑️ **Edit & Delete** - Modify or remove transactions
- 💬 **Indonesian Language** - Built with Indonesian users in mind

## Quick Start 🚀

### Prerequisites
- Python 3.8+
- Telegram Bot Token from [BotFather](https://t.me/botfather)

### Installation

1. **Clone the repository**
```
git clone https://github.com/adibpriatama/fintrack.git
cd fintrack
```
2. **Create virtual environment**
```
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```
3. **Install dependencies**
```
pip install -r requirements.txt
```
4. **Configure bot token**
```
echo "BOT_TOKEN=your_bot_token_here" > .env
```
5. **Create run_bot.py file in the parent directory**
```
cd ..
vi run_bot.py
```
  run_bot.py file content
```
from fintrack import main

if __name__ == "__main__":
    main()
```
6. **Run bot**
```
python run_bot.py
```
