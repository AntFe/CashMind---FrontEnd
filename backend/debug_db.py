import os
from pathlib import Path

print("=== DEBUG DO BANCO DE DADOS ===")
print(f"Diretório atual: {os.getcwd()}")
print(f"Arquivo config.py existe: {os.path.exists('config.py')}")

# Testa diferentes caminhos
paths_to_test = [
    'instance/cashmind.db',
    './instance/cashmind.db',
    os.path.join(os.getcwd(), 'instance', 'cashmind.db'),
    'cashmind.db',
    '../instance/cashmind.db'
]

print("\nTestando caminhos:")
for path in paths_to_test:
    exists = os.path.exists(path)
    print(f"{path}: {'✅ Existe' if exists else '❌ Não existe'}")
    if exists:
        print(f"  Permissões: {oct(os.stat(path).st_mode)[-3:]}")

# Verifica o conteúdo do .env
print("\n=== CONTEÚDO DO .env ===")
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            if 'DATABASE_URL' in line:
                print(f"DATABASE_URL: {line.strip()}")

# Testa conexão direta
print("\n=== TESTE DE CONEXÃO ===")
import sqlite3
try:
    # Caminho absoluto
    db_path = os.path.join(os.getcwd(), 'instance', 'cashmind.db')
    print(f"Tentando conectar em: {db_path}")
    conn = sqlite3.connect(db_path)
    print("✅ Conexão direta funcionou!")
    conn.close()
except Exception as e:
    print(f"❌ Erro: {e}") 