# CashMind - Sistema de Gestão Financeira com IA

Sistema completo de gestão financeira pessoal com análise inteligente de gastos.

## 🚀 Tecnologias

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python Flask, SQLAlchemy, JWT
- **Banco de Dados**: SQLite
- **IA**: Google Gemini API (em desenvolvimento)

## 📁 Estrutura do Projeto

```
CashMind/
├── frontend/         # Interface do usuário
│   ├── index.html   # Página de login
│   ├── pages/       # Outras páginas
│   ├── scripts/     # JavaScript
│   ├── styles/      # CSS
│   └── content/     # Imagens e assets
│
└── backend/         # API REST
    ├── app/         # Aplicação Flask
    ├── instance/    # Banco de dados
    └── venv/        # Ambiente virtual
```

## 🛠️ Como Executar

### Backend (Terminal 1):
```bash
cd backend
source venv/bin/activate  # Linux/Mac
python3 run.py
```
API rodando em: http://localhost:5000

### Frontend (Terminal 2):
```bash
cd frontend
python3 -m http.server 8000
```
Interface em: http://localhost:8000

## 👥 Equipe
- Antonio Ferreira
- Arthur Maciel
- Daniel Gobbi
