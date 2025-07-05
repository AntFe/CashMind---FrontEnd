from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    """Modelo de usuário para o sistema CashMind"""
    
    __tablename__ = 'users'
    
    # Colunas da tabela
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relacionamentos (vamos adicionar depois)
    # transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    
    def __init__(self, full_name, email, password):
        """Inicializa um novo usuário"""
        self.full_name = full_name
        self.email = email.lower()  # Sempre salva email em minúsculas
        self.set_password(password)
    
    def set_password(self, password):
        """Cria o hash da senha"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Converte o usuário para dicionário (útil para APIs)"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        """Representação do objeto"""
        return f'<User {self.email}>'