import os
from app import create_app

print("=== TESTE FINAL ===")
print(f"Diretório atual: {os.getcwd()}")

try:
    app = create_app('development')
    with app.app_context():
        print(f"Instance path: {app.instance_path}")
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Tenta criar as tabelas
        from app import db
        db.create_all()
        print("✅ Banco criado/verificado com sucesso!")
        
    # Tenta rodar
    print("\n🚀 Iniciando servidor...")
    app.run(debug=False, port=5001)
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc() 