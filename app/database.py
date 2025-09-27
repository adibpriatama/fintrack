import os
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base, Transaction
from ..config import DB_DIR, DB_FILE_PATTERN

class DatabaseManager:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.db_path = os.path.join(DB_DIR, DB_FILE_PATTERN.format(chat_id=chat_id))
        self.engine = create_engine(f'sqlite:///{self.db_path}', echo=False)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        self._init_db()
    
    def _init_db(self):
        """Initialize database with required tables"""
        Base.metadata.create_all(self.engine)
    
    def add_transaction(self, amount, transaction_type, category=None, description=None, message_id=None):
        """Add a new transaction to the database"""
        session = self.Session()
        
        try:
            transaction = Transaction(
                amount=amount,
                type=transaction_type,
                category=category,
                description=description,
                message_id=message_id
            )
            
            session.add(transaction)
            session.commit()
            return transaction.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_transactions(self, limit=10, offset=0):
        """Get recent transactions"""
        session = self.Session()
        
        try:
            transactions = session.query(Transaction)\
                .order_by(Transaction.created_at.desc())\
                .offset(offset)\
                .limit(limit)\
                .all()
            
            return [trans.to_dict() for trans in transactions]
        finally:
            session.close()
    
    def get_balance(self):
        """Calculate current balance in IDR"""
        session = self.Session()
        
        try:
            # Get total income
            total_income = session.query(func.coalesce(func.sum(Transaction.amount), 0))\
                .filter(Transaction.type == 'income')\
                .scalar()
            
            # Get total expenses
            total_expense = session.query(func.coalesce(func.sum(Transaction.amount), 0))\
                .filter(Transaction.type == 'expense')\
                .scalar()
            
            return total_income - total_expense
        finally:
            session.close()
    
    def delete_transaction(self, transaction_id):
        """Delete a transaction by ID"""
        session = self.Session()
        
        try:
            deleted_count = session.query(Transaction)\
                .filter(Transaction.id == transaction_id)\
                .delete()
            
            session.commit()
            return deleted_count > 0
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_transaction_by_id(self, transaction_id):
        """Get a specific transaction by ID"""
        session = self.Session()
        
        try:
            transaction = session.query(Transaction)\
                .filter(Transaction.id == transaction_id)\
                .first()
            
            return transaction.to_dict() if transaction else None
        finally:
            session.close()
    
    def get_transactions_by_category(self, category, limit=10):
        """Get transactions by category"""
        session = self.Session()
        
        try:
            transactions = session.query(Transaction)\
                .filter(Transaction.category == category)\
                .order_by(Transaction.created_at.desc())\
                .limit(limit)\
                .all()
            
            return [trans.to_dict() for trans in transactions]
        finally:
            session.close()
    
    def get_category_summary(self):
        """Get summary of expenses/income by category"""
        session = self.Session()
        
        try:
            result = session.query(
                Transaction.category,
                Transaction.type,
                func.sum(Transaction.amount).label('total_amount')
            )\
            .filter(Transaction.category.isnot(None))\
            .group_by(Transaction.category, Transaction.type)\
            .all()
            
            return result
        finally:
            session.close()