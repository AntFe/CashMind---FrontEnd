from app import db
from datetime import datetime

class Category(db.Model):
    """Modelo de categoria para sugestões ao usuário"""
    
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    icon = db.Column(db.String(50), nullable=True)  # Para ícones futuros
    color = db.Column(db.String(7), nullable=True)  # Cor em hex
    is_default = db.Column(db.Boolean, default=False)  # Categorias padrão do sistema
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, name, icon=None, color=None, is_default=False):
        self.name = name.lower()
        self.icon = icon
        self.color = color
        self.is_default = is_default
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'color': self.color,
            'is_default': self.is_default
        }
    
    @staticmethod
    def get_default_categories():
        """Retorna categorias padrão para popular o banco"""
        return [
            # Despesas
            {'name': 'alimentação', 'icon': '🍽️', 'color': '#FF6B6B'},
            {'name': 'transporte', 'icon': '🚗', 'color': '#4ECDC4'},
            {'name': 'moradia', 'icon': '🏠', 'color': '#45B7D1'},
            {'name': 'saúde', 'icon': '💊', 'color': '#96CEB4'},
            {'name': 'educação', 'icon': '📚', 'color': '#9B59B6'},
            {'name': 'lazer', 'icon': '🎮', 'color': '#F39C12'},
            {'name': 'compras', 'icon': '🛍️', 'color': '#E74C3C'},
            {'name': 'serviços', 'icon': '💡', 'color': '#95A5A6'},
            # Receitas
            {'name': 'salário', 'icon': '💰', 'color': '#27AE60'},
            {'name': 'freelance', 'icon': '💻', 'color': '#3498DB'},
            {'name': 'investimentos', 'icon': '📈', 'color': '#2ECC71'},
            {'name': 'outros', 'icon': '📦', 'color': '#7F8C8D'}
        ]
    
    def __repr__(self):
        return f'<Category {self.name}>'