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
    
    # Cria a aplicação Flask com instance_relative_config
    app = Flask(__name__, instance_relative_config=True)
    
    # Garante que a pasta instance existe no lugar certo
    import os
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Carrega configurações
    app.config.from_object(config[config_name])
    
    # Se estiver usando caminho relativo, ajusta para o instance_path
    if 'sqlite:///' in app.config['SQLALCHEMY_DATABASE_URI']:
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(app.instance_path, "cashmind.db")}'
    
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
    from app.routes import auth, transactions, dashboard, ai_analysis

    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(transactions.bp, url_prefix='/api/transactions')
    app.register_blueprint(dashboard.bp, url_prefix='/api/dashboard')
    app.register_blueprint(ai_analysis.bp, url_prefix='/api/ai')
    
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