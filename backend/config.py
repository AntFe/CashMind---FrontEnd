import os
from datetime import timedelta
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class Config:
    """Configurações base do aplicativo"""
    
    # Configurações do Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-mudar-em-producao'
    
    # Configurações do banco de dados - CORREÇÃO DEFINITIVA
    # Se DATABASE_URL estiver no .env, usa ela. Senão, usa caminho relativo
    if os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    else:
        # Caminho relativo para funcionar em qualquer máquina
        SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/cashmind.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-mudar-em-producao'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Configurações CORS
    CORS_HEADERS = 'Content-Type'
    
    # Configuração da API do Google Gemini
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

class DevelopmentConfig(Config):
    """Configurações de desenvolvimento"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configurações de produção"""
    DEBUG = False
    TESTING = False

# Dicionário de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}