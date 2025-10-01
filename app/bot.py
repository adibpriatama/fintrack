import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
from .handlers import MessageHandler as FinTrackMessageHandler

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

class FinTrackBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.message_handler = FinTrackMessageHandler()
        
        # Add command handlers
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(CommandHandler("help", self._help_command))
        self.application.add_handler(CommandHandler("balance", self._balance_command))
        self.application.add_handler(CommandHandler("history", self._history_command))
        self.application.add_handler(CommandHandler("summary", self._summary_command))
        self.application.add_handler(CommandHandler("delete", self._delete_command))
        self.application.add_handler(CommandHandler("category", self._category_command))
        self.application.add_handler(CommandHandler("edit", self._edit_command))
        self.application.add_handler(CommandHandler("search", self._search_command))
        self.application.add_handler(CommandHandler("chart", self._chart_command))

        
        # Add message handler for all text messages (should be after command handlers)
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler.handle_message)
        )
    
    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message when command /start is issued."""
        welcome_text = """
🤖 **FinTrack Bot - Pelacak Keuangan Rumah Tangga**

**Format:**
`[kategori] [deskripsi] [tanda][jumlah]`

**Cara menggunakan:**
- **Pemasukan**: `gaji bulanan +2jt` atau `bonus proyek +500k`
- **Pengeluaran**: `makan siang 50k` atau `belanja 200rb`
- **Multiple entries** (baris berbeda):
```
gaji bulanan +2jt
makan siang 50k
transport 100rb
belanja 300k
```

**Singkatan:**
- k/rb = ribu (1k = 1,000)
- jt/m = juta (1jt = 1,000,000)

**Perintah lain:**
- `/balance` - Cek saldo
- `/history` - Lihat riwayat
- `/delete <id>` - Hapus transaksi
- `/summary` - Ringkasan per kategori
- `/search <kata>` - Cari transaksi
- `/edit <id> <field> <value>` - Edit transaksi
- `/category <nama>` - Lihat transaksi per kategori


Saldo akan otomatis terhitung! 💰
        """
        await update.message.reply_text(welcome_text)
    
    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send help message when command /help is issued."""
        help_text = """
📖 **Bantuan FinTrack Bot**

**Format Transaksi:**
``[kategori] [deskripsi] [tanda][jumlah]``

**Perintah yang tersedia:**
- `/start` - Memulai bot
- `/help` - Menampilkan bantuan ini
- `/balance` - Cek saldo saat ini
- `/history` - Lihat 5 transaksi terakhir
- `/edit <id> <field> <value>` - Edit transaksi
- `/search <kata>` - Cari transaksi
- `/delete <id>` - Hapus transaksi
- `/summary` - Ringkasan per kategori
- `/category <nama>` - Lihat transaksi per kategori

**Contoh Transaksi:**
- `makan siang 50k`
- `gaji bulanan +2jt`
- `transport gojek 15k`

**Catatan:**
- Gunakan **+** untuk pemasukan
- Tanpa tanda atau **-** untuk pengeluaran
- Mata uang: Indonesian Rupiah (IDR)

**Pencarian:**
- `/search makan` - Cari semua transaksi makanan
- `/search gaji` - Cari transaksi gaji
- `/search transport` - Cari transaksi transportasi

**Edit Transaksi:**
- `/edit 1 amount 75000` - Ubah jumlah
- `/edit 1 category makanan` - Ubah kategori
- `/edit 1 description lunch` - Ubah deskripsi
- `/edit 1 type income` - Ubah jenis
        """
        await update.message.reply_text(help_text)
    
    async def _balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /balance command"""
        chat_id = update.message.chat_id
        handler = FinTrackMessageHandler()
        await handler._show_balance(update, context, chat_id)
    
    async def _history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /history command"""
        chat_id = update.message.chat_id
        handler = FinTrackMessageHandler()
        await handler._show_history(update, context, chat_id)
    
    async def _summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /summary command"""
        chat_id = update.message.chat_id
        handler = FinTrackMessageHandler()
        await handler._show_summary(update, context, chat_id)
    
    async def _delete_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /delete command"""
        chat_id = update.message.chat_id
        handler = FinTrackMessageHandler()
        await handler._delete_transaction(update, context, chat_id)
    
    async def _category_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /category command"""
        chat_id = update.message.chat_id
        handler = FinTrackMessageHandler()
        await handler._show_category(update, context, chat_id)
    
    async def _edit_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /edit command"""
        chat_id = update.message.chat_id
        handler = FinTrackMessageHandler()
        await handler._edit_transaction(update, context, chat_id)
    
    async def _search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search command"""
        chat_id = update.message.chat_id
        await self.message_handler._search_transactions(update, context, chat_id)
    
    async def _chart_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search command"""
        chat_id = update.message.chat_id
        await self.message_handler._show_chart(update, context, chat_id)
    
    def run(self):
        """Start the bot"""
        print("Bot FinTrack sedang berjalan...")
        self.application.run_polling()