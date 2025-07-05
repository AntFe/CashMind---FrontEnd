#!/usr/bin/env python3
"""
Visualizar dados do banco SQLite
USO: python3 view_database.py
"""

import sqlite3
import os
from datetime import datetime

def view_database():
    db_path = "instance/cashmind.db"
    
    if not os.path.exists(db_path):
        print("Banco de dados não encontrado!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("BANCO DE DADOS CASHMIND")
        print("=" * 50)
        
        file_size = os.path.getsize(db_path)
        print(f"Tamanho: {file_size} bytes")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"Tabelas: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        print("\n" + "=" * 50)
        
        if ('user',) in tables:
            print("USUÁRIOS:")
            cursor.execute("SELECT COUNT(*) FROM user;")
            user_count = cursor.fetchone()[0]
            
            if user_count > 0:
                print(f"Total: {user_count}")
                print("-" * 30)
                
                cursor.execute("""
                    SELECT id, username, email, password_hash, full_name, is_active, created_at 
                    FROM user 
                    ORDER BY created_at DESC
                """)
                users = cursor.fetchall()
                
                for user in users:
                    user_id, username, email, password_hash, full_name, is_active, created_at = user
                    status = "Ativo" if is_active else "Inativo"
                    print(f"ID: {user_id}")
                    print(f"Usuário: {username}")
                    print(f"Email: {email}")
                    print(f"Senha (hash): {password_hash}")
                    print(f"Nome: {full_name}")
                    print(f"Status: {status}")
                    print(f"Criado: {created_at}")
                    print("-" * 30)
            else:
                print("Nenhum usuário cadastrado.")
        
        for table in tables:
            if table[0] not in ['user', 'sqlite_sequence']:
                print(f"\nTABELA: {table[0].upper()}")
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
                count = cursor.fetchone()[0]
                print(f"Registros: {count}")
                
                if count > 0:
                    cursor.execute(f"PRAGMA table_info({table[0]});")
                    columns = cursor.fetchall()
                    print("Colunas:")
                    for col in columns:
                        print(f"  - {col[1]} ({col[2]})")
                    
                    print("Dados:")
                    cursor.execute(f"SELECT * FROM {table[0]} LIMIT 5;")
                    rows = cursor.fetchall()
                    for i, row in enumerate(rows, 1):
                        print(f"  {i}: {row}")
        
        conn.close()
        print("\nVisualização concluída.")
        
    except Exception as e:
        print(f"Erro: {e}")

def clear_database():
    db_path = "instance/cashmind.db"
    
    if not os.path.exists(db_path):
        print("Banco de dados não encontrado!")
        return
    
    try:
        backup_path = f"{db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"Backup: {backup_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("Limpando banco...")
        for table in tables:
            if table[0] != 'sqlite_sequence':
                cursor.execute(f"DELETE FROM {table[0]};")
                print(f"  - {table[0]}")
        
        cursor.execute("DELETE FROM sqlite_sequence;")
        
        conn.commit()
        conn.close()
        
        print("Banco limpo.")
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        print("ATENÇÃO: Limpar todos os dados do banco!")
        response = input("Confirmar? (sim): ")
        if response.lower() == 'sim':
            clear_database()
        else:
            print("Cancelado.")
    else:
        view_database() 