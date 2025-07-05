from app import create_app, db
from app.models import User

def init_database():
    """Inicializa o banco de dados criando todas as tabelas"""
    app = create_app('development')
    
    with app.app_context():
        # Cria todas as tabelas
        db.create_all()
        
        # Verifica se foi criado
        print("✅ Banco de dados criado com sucesso!")
        print("📊 Tabelas criadas:")
        print("   - users")
        
        # Opcional: criar um usuário de teste
        if User.query.count() == 0:
            test_user = User(
                full_name="Usuário Teste",
                email="teste@cashmind.com",
                password="Teste123!"
            )
            db.session.add(test_user)
            db.session.commit()
            print("\n👤 Usuário de teste criado:")
            print("   Email: teste@cashmind.com")
            print("   Senha: Teste123!")

if __name__ == "__main__":
    init_database()