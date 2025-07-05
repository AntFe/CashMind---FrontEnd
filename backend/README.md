# CashMind Backend

## Instalação

1. Crie o ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env se necessário
```

4. Inicialize o banco de dados:
```bash
python init_db.py
```

5. Execute o servidor:
```bash
python run.py
```

## Endpoints Disponíveis

### Autenticação
- `POST /api/auth/register` - Criar nova conta
- `POST /api/auth/login` - Fazer login
- `POST /api/auth/refresh` - Renovar token
- `GET /api/auth/profile` - Ver perfil (autenticado)

### Health Check
- `GET /api/health` - Verificar se API está rodando
