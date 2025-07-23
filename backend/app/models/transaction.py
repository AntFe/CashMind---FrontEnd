from datetime import datetime
from app import db
from sqlalchemy import Enum
import enum

class TransactionType(enum.Enum):
    """Tipo de transação"""
    INCOME = 'income'      # Receita
    EXPENSE = 'expense'    # Despesa

class RecurrenceType(enum.Enum):
    """Tipo de recorrência"""
    FIXED = 'fixed'        # Fixo (todo mês)
    VARIABLE = 'variable'  # Variável (ocasional)

class Transaction(db.Model):
    """Modelo de transação financeira"""
    
    __tablename__ = 'transactions'
    
    # Colunas principais
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    recurrence_type = db.Column(db.Enum(RecurrenceType), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com usuário
    user = db.relationship('User', backref=db.backref('transactions', lazy='dynamic'))
    
    def __init__(self, user_id, name, amount, transaction_type, recurrence_type, category, date=None, description=None):
        self.user_id = user_id
        self.name = name
        self.amount = abs(amount)  # Sempre positivo
        self.transaction_type = transaction_type
        self.recurrence_type = recurrence_type
        self.category = category.lower()  # Padroniza em minúsculas
        self.date = date or datetime.utcnow().date()
        self.description = description
    
    def to_dict(self):
        """Converte a transação para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.amount,
            'type': self.transaction_type.value,
            'recurrence': self.recurrence_type.value,
            'category': self.category,
            'date': self.date.isoformat() if self.date else None,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Transaction {self.name}: R${self.amount}>'