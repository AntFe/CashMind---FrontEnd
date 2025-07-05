from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import config

# Inicializa extensões
db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_name='default'):
    """Factory pattern para criar a aplicação Flask"""
    
    # Cria a aplicação Flask
    app = Flask(__name__)
    
    # Garante que a pasta instance existe
    import os
    os.makedirs('instance', exist_ok=True)
    
    # Carrega configurações
    app.config.from_object(config[config_name])
    
    # Inicializa extensões com a app
    db.init_app(app)
    jwt.init_app(app)
    
    # Configura CORS para permitir requisições do frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:*", "http://127.0.0.1:*"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Importa e registra blueprints
    from app.routes import auth, transactions, dashboard
    
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(transactions.bp, url_prefix='/api/transactions')
    app.register_blueprint(dashboard.bp, url_prefix='/api/dashboard')
    
    # Cria as tabelas do banco de dados
    with app.app_context():
        db.create_all()
    
    # Rota de teste
    @app.route('/api/health')
    def health_check():
        return {'status': 'OK', 'message': 'CashMind API is running!'}, 200
    
    # Rota raiz
    @app.route('/')
    def index():
        return {
            'message': 'Welcome to CashMind API!',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'auth': '/api/auth/*',
                'transactions': '/api/transactions/*',
                'dashboard': '/api/dashboard/*'
            },
            'status': 'running'
        }, 200
    
    return app