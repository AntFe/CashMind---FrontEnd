#!/usr/bin/env python3
"""
Script SEGURO para visualizar dados do banco de dados SQLite
USO: python3 view_database.py
"""

import sqlite3
import os
from datetime import datetime

def view_database():
    """Visualiza os dados do banco de dados de forma segura"""
    
    db_path = "instance/cashmind.db"
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        print("💡 Execute o backend primeiro para criar o banco.")
        return
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 VISUALIZANDO BANCO DE DADOS CASHMIND")
        print("=" * 50)
        
        # Verificar tamanho do arquivo
        file_size = os.path.getsize(db_path)
        print(f"📁 Tamanho do banco: {file_size} bytes")
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📋 Tabelas encontradas: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        print("\n" + "=" * 50)
        
        # Verificar tabela de usuários
        if ('user',) in tables:
            print("👥 USUÁRIOS CADASTRADOS:")
            cursor.execute("SELECT COUNT(*) FROM user;")
            user_count = cursor.fetchone()[0]
            
            if user_count > 0:
                print(f"Total de usuários: {user_count}")
                print("-" * 30)
                
                # Buscar usuários (sem mostrar senhas)
                cursor.execute("""
                    SELECT id, username, email, full_name, is_active, created_at 
                    FROM user 
                    ORDER BY created_at DESC
                """)
                users = cursor.fetchall()
                
                for user in users:
                    user_id, username, email, full_name, is_active, created_at = user
                    status = "✅ Ativo" if is_active else "❌ Inativo"
                    print(f"ID: {user_id}")
                    print(f"Usuário: {username}")
                    print(f"Email: {email}")
                    print(f"Nome: {full_name}")
                    print(f"Status: {status}")
                    print(f"Criado em: {created_at}")
                    print("-" * 30)
            else:
                print("Nenhum usuário cadastrado.")
                print("💡 Teste o registro de usuários para ver dados aqui.")
        
        # Verificar outras tabelas se existirem
        for table in tables:
            if table[0] not in ['user', 'sqlite_sequence']:
                print(f"\n📊 TABELA: {table[0].upper()}")
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
                count = cursor.fetchone()[0]
                print(f"Registros: {count}")
                
                if count > 0:
                    # Mostrar apenas estrutura, não dados sensíveis
                    cursor.execute(f"PRAGMA table_info({table[0]});")
                    columns = cursor.fetchall()
                    print("Colunas:")
                    for col in columns:
                        print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        print("\n✅ Visualização concluída!")
        print("🔒 Dados sensíveis (senhas) não foram exibidos por segurança.")
        
    except Exception as e:
        print(f"❌ Erro ao acessar banco: {e}")

def clear_database():
    """Função para limpar o banco de dados (APENAS PARA DESENVOLVIMENTO)"""
    
    db_path = "instance/cashmind.db"
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        return
    
    try:
        # Fazer backup antes de limpar
        backup_path = f"{db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"💾 Backup criado: {backup_path}")
        
        # Conectar e limpar
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Listar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("🗑️ Limpando banco de dados...")
        for table in tables:
            if table[0] != 'sqlite_sequence':
                cursor.execute(f"DELETE FROM {table[0]};")
                print(f"  - Limpada tabela: {table[0]}")
        
        # Resetar sequências
        cursor.execute("DELETE FROM sqlite_sequence;")
        
        conn.commit()
        conn.close()
        
        print("✅ Banco de dados limpo com sucesso!")
        print("💡 Execute o backend novamente para recriar as tabelas.")
        
    except Exception as e:
        print(f"❌ Erro ao limpar banco: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        print("⚠️  ATENÇÃO: Isso irá LIMPAR todos os dados do banco!")
        response = input("Tem certeza? (digite 'sim' para confirmar): ")
        if response.lower() == 'sim':
            clear_database()
        else:
            print("Operação cancelada.")
    else:
        view_database() 