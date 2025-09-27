import re
from telegram import Update
from telegram.ext import ContextTypes
from .database import DatabaseManager
from ..config import CURRENCY_SYMBOL, DEFAULT_TRANSACTION_TYPE

class MessageHandler:
    def __init__(self):
        # New pattern: [category] [description] [sign][amount]
        # Examples: "makan lunch +50k" or "gaji bulanan +2jt"
        self.transaction_pattern = re.compile(r'^(\S+)\s+(.+?)\s+([+-]?)(\d+(?:[.,]\d+)?\s*(?:k|rb|jt|m)?)$', re.IGNORECASE)
        
        # Fallback pattern for when description is optional
        self.fallback_pattern = re.compile(r'^(\S+)\s+([+-]?)(\d+(?:[.,]\d+)?\s*(?:k|rb|jt|m)?)$', re.IGNORECASE)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process every message in the group"""
        if not update.message or not update.message.text:
            return
        
        message_text = update.message.text.strip()
        chat_id = update.message.chat_id
        
        # Check if message contains multiple transactions (multiple lines)
        lines = message_text.split('\n')
        
        if len(lines) > 1:
            # Process as multiple transactions
            await self._process_multiple_transactions(update, context, lines, chat_id)
        else:
            # Process as single transaction or command
            await self._process_single_transaction(update, context, message_text, chat_id)
    
    async def _process_multiple_transactions(self, update: Update, context: ContextTypes.DEFAULT_TYPE, lines: list, chat_id: int):
        """Process multiple transactions in a single message"""
        transactions = []
        errors = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            # Try to parse the line as a transaction
            transaction_data = self._parse_transaction_line(line)
            
            if transaction_data:
                try:
                    transactions.append({
                        'category': transaction_data['category'],
                        'description': transaction_data['description'],
                        'amount': transaction_data['amount'],
                        'type': transaction_data['type'],
                        'line': line_num
                    })
                except Exception as e:
                    errors.append(f"Line {line_num}: Error - {str(e)}")
            else:
                # Check if it's a command instead of transaction
                if await self._process_command(update, context, line, chat_id):
                    return  # If it's a command, stop processing transactions
                else:
                    errors.append(f"Line {line_num}: Format transaksi tidak dikenali: {line}")
        
        # Process all valid transactions
        if transactions:
            await self._save_transactions(update, context, chat_id, transactions, errors)
        else:
            # No valid transactions found
            if errors:
                error_response = "❌ Tidak ada transaksi yang valid:\n\n" + "\n".join(errors[:10])
                await update.message.reply_text(error_response)
    
    def _parse_transaction_line(self, line: str):
        """Parse a single transaction line in the format [category] [description] [sign][amount]"""
        # Try the main pattern first: category description sign amount
        match = self.transaction_pattern.match(line)
        if match:
            category = match.group(1).lower()
            description = match.group(2).strip()
            sign = match.group(3)
            amount_str = match.group(4).strip()
        else:
            # Try fallback pattern: category sign amount (no description)
            match = self.fallback_pattern.match(line)
            if match:
                category = match.group(1).lower()
                description = ""
                sign = match.group(2)
                amount_str = match.group(3).strip()
            else:
                return None
        
        try:
            amount = self._parse_amount(amount_str)
            transaction_type = 'income' if sign == '+' else DEFAULT_TRANSACTION_TYPE
            
            return {
                'category': category,
                'description': description,
                'amount': amount,
                'type': transaction_type,
                'sign': sign
            }
        except ValueError:
            return None
    
    async def _process_single_transaction(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str, chat_id: int):
        """Process single transaction or command"""
        # Check if it's a command first
        if await self._process_command(update, context, message_text, chat_id):
            return
        
        # Try to parse as transaction
        transaction_data = self._parse_transaction_line(message_text)
        if transaction_data:
            await self._save_single_transaction(update, context, chat_id, transaction_data)
        else:
            await update.message.reply_text("❌ Format transaksi tidak dikenali. Gunakan: [kategori] [deskripsi] [+-][jumlah]")
    
    async def _process_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str, chat_id: int):
        """Process commands and return True if it's a command"""
        message_lower = message_text.lower()
        
        if message_lower in ['/balance', 'balance', 'saldo']:
            await self._show_balance(update, context, chat_id)
            return True
        elif message_lower in ['/history', 'history', 'riwayat']:
            await self._show_history(update, context, chat_id)
            return True
        elif message_lower.startswith('/delete'):
            await self._delete_transaction(update, context, chat_id)
            return True
        elif message_lower in ['/summary', 'summary', 'ringkasan']:
            await self._show_summary(update, context, chat_id)
            return True
        elif message_lower.startswith('/category'):
            await self._show_category(update, context, chat_id)
            return True
        
        return False
    
    async def _save_single_transaction(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int, transaction_data: dict):
        """Save a single transaction"""
        try:
            db = DatabaseManager(chat_id)
            transaction_id = db.add_transaction(
                amount=transaction_data['amount'],
                transaction_type=transaction_data['type'],
                category=transaction_data['category'],
                description=transaction_data['description'],
                message_id=update.message.message_id
            )
            
            balance = db.get_balance()
            await self._send_transaction_confirmation(update, transaction_id, transaction_data, balance)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error menyimpan transaksi: {str(e)}")
    
    async def _save_transactions(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int, transactions: list, errors: list):
        """Save multiple transactions"""
        db = DatabaseManager(chat_id)
        successful_transactions = []
        failed_transactions = []
        
        for transaction in transactions:
            try:
                transaction_id = db.add_transaction(
                    amount=transaction['amount'],
                    transaction_type=transaction['type'],
                    category=transaction['category'],
                    description=transaction['description'],
                    message_id=update.message.message_id
                )
                successful_transactions.append(transaction)
            except Exception as e:
                failed_transactions.append(f"Line {transaction['line']}: {str(e)}")
        
        balance = db.get_balance()
        
        # Prepare response
        response = f"📊 Multiple transactions processed!\n\n"
        response += f"✅ Berhasil: {len(successful_transactions)} transaksi\n"
        
        if failed_transactions:
            response += f"❌ Gagal: {len(failed_transactions)} transaksi\n\n"
            response += "Errors:\n" + "\n".join(failed_transactions[:5])
            if len(failed_transactions) > 5:
                response += f"\n... dan {len(failed_transactions) - 5} error lainnya"
        else:
            response += "❌ Gagal: 0 transaksi\n"
        
        response += f"\n💳 Saldo saat ini: {CURRENCY_SYMBOL} {balance:+,}"
        
        await update.message.reply_text(response)
    
    async def _send_transaction_confirmation(self, update: Update, transaction_id: int, transaction_data: dict, balance: float):
        """Send transaction confirmation message"""
        emoji = "💰" if transaction_data['type'] == 'income' else "💸"
        type_text = "Pemasukan" if transaction_data['type'] == 'income' else "Pengeluaran"
        sign_display = "+" if transaction_data['type'] == 'income' else "-"
        
        response = (
            f"{emoji} Transaksi dicatat!\n"
            f"📊 ID: {transaction_id}\n"
            f"🏷️ Kategori: {transaction_data['category']}\n"
            f"📝 Jenis: {type_text}\n"
        )
        
        if transaction_data['description']:
            response += f"📋 Deskripsi: {transaction_data['description']}\n"
        
        response += f"💵 Jumlah: {sign_display}{CURRENCY_SYMBOL} {transaction_data['amount']:,}\n"
        response += f"\n💳 Saldo saat ini: {CURRENCY_SYMBOL} {balance:+,}"
        
        await update.message.reply_text(response)
    
    def _parse_amount(self, amount_str):
        """Parse amount string with Indonesian abbreviations"""
        amount_str_clean = amount_str.lower().strip()
        amount_str_clean = amount_str_clean.replace(' ', '').replace('.', '').replace(',', '.')
        
        multiplier = 1
        if amount_str_clean.endswith('k') or amount_str_clean.endswith('rb'):
            multiplier = 1000
            amount_str_clean = amount_str_clean[:-1]
        elif amount_str_clean.endswith('jt') or amount_str_clean.endswith('m'):
            multiplier = 1000000
            amount_str_clean = amount_str_clean[:-2] if amount_str_clean.endswith('jt') else amount_str_clean[:-1]
        
        amount = float(amount_str_clean) * multiplier
        return int(amount)
    
    async def _show_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
        """Show current balance in IDR"""
        db = DatabaseManager(chat_id)
        balance = db.get_balance()
        
        response = f"💳 Saldo saat ini: {CURRENCY_SYMBOL} {balance:+,.0f}"
        await update.message.reply_text(response)
    
    async def _show_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
        """Show recent transactions"""
        db = DatabaseManager(chat_id)
        transactions = db.get_transactions(limit=5)
        
        if not transactions:
            await update.message.reply_text("📝 Belum ada transaksi yang dicatat")
            return
        
        response = "📋 Transaksi terbaru:\n\n"
        for trans in transactions:
            sign = "+" if trans['type'] == 'income' else "-"
            type_emoji = "💰" if trans['type'] == 'income' else "💸"
            response += f"{type_emoji} {trans['id']}. {sign}{CURRENCY_SYMBOL} {trans['amount']:,.0f}\n"
            response += f"   🏷️ {trans['category'] or 'Tanpa kategori'}\n"
            if trans['description']:
                response += f"   📝 {trans['description']}\n"
            response += f"   ⏰ {trans['created_at'].strftime('%d/%m/%Y %H:%M')}\n\n"
        
        balance = db.get_balance()
        response += f"💳 Saldo total: {CURRENCY_SYMBOL} {balance:+,.0f}"
        
        await update.message.reply_text(response)
    
    async def _delete_transaction(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
        """Delete a transaction by ID"""
        message_text = update.message.text.strip()
        parts = message_text.split()
        
        if len(parts) != 2:
            await update.message.reply_text("❌ Cara pakai: /delete <id_transaksi>")
            return
        
        try:
            transaction_id = int(parts[1])
            db = DatabaseManager(chat_id)
            
            # Get transaction details before deleting
            transaction = db.get_transaction_by_id(transaction_id)
            if not transaction:
                await update.message.reply_text("❌ Transaksi tidak ditemukan")
                return
            
            if db.delete_transaction(transaction_id):
                balance = db.get_balance()
                type_text = "Pemasukan" if transaction['type'] == 'income' else "Pengeluaran"
                await update.message.reply_text(
                    f"✅ Transaksi {transaction_id} ({type_text}) dihapus\n"
                    f"💳 Saldo saat ini: {CURRENCY_SYMBOL} {balance:+,.0f}"
                )
            else:
                await update.message.reply_text("❌ Gagal menghapus transaksi")
                
        except ValueError:
            await update.message.reply_text("❌ ID transaksi tidak valid")
    
    async def _show_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
        """Show category summary"""
        db = DatabaseManager(chat_id)
        summary = db.get_category_summary()
        
        if not summary:
            await update.message.reply_text("📊 Belum ada data transaksi untuk ringkasan")
            return
        
        response = "📊 Ringkasan per Kategori:\n\n"
        
        # Separate income and expenses
        income_data = [(cat, amount) for cat, type_, amount in summary if type_ == 'income']
        expense_data = [(cat, amount) for cat, type_, amount in summary if type_ == 'expense']
        
        if income_data:
            response += "💰 Pemasukan:\n"
            for category, amount in income_data:
                response += f"  🏷️ {category}: {CURRENCY_SYMBOL} {amount:,.0f}\n"
            response += "\n"
        
        if expense_data:
            response += "💸 Pengeluaran:\n"
            for category, amount in expense_data:
                response += f"  🏷️ {category}: {CURRENCY_SYMBOL} {amount:,.0f}\n"
        
        balance = db.get_balance()
        response += f"\n💳 Saldo total: {CURRENCY_SYMBOL} {balance:+,.0f}"
        
        await update.message.reply_text(response)
    
    async def _show_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
        """Show transactions for a specific category"""
        message_text = update.message.text.strip()
        parts = message_text.split(maxsplit=1)
        
        if len(parts) < 2:
            await update.message.reply_text("❌ Cara pakai: /category <nama_kategori>")
            return
        
        category = parts[1].lower()
        db = DatabaseManager(chat_id)
        transactions = db.get_transactions_by_category(category, limit=5)
        
        if not transactions:
            await update.message.reply_text(f"📝 Tidak ada transaksi untuk kategori '{category}'")
            return
        
        response = f"📋 Transaksi untuk kategori '{category}':\n\n"
        for trans in transactions:
            sign = "+" if trans['type'] == 'income' else "-"
            type_emoji = "💰" if trans['type'] == 'income' else "💸"
            response += f"{type_emoji} {sign}{CURRENCY_SYMBOL} {trans['amount']:,.0f}\n"
            if trans['description']:
                response += f"   📝 {trans['description']}\n"
            response += f"   ⏰ {trans['created_at'].strftime('%d/%m/%Y %H:%M')}\n\n"
        
        await update.message.reply_text(response)