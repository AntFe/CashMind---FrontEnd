import os
from app import create_app

# Pega a configuração do ambiente ou usa 'development' como padrão
config_name = os.getenv('FLASK_ENV', 'development')

# Cria a aplicação
app = create_app(config_name)

if __name__ == '__main__':
    # Roda o servidor
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True if config_name == 'development' else False
    )