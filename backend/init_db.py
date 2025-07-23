from app import create_app, db
from app.models import User, Category, Transaction, TransactionType, RecurrenceType
from datetime import datetime, timedelta

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
        print("   - transactions")
        print("   - categories")
        
        # Criar categorias padrão se não existirem
        if Category.query.count() == 0:
            print("\n🏷️ Criando categorias padrão...")
            for cat_data in Category.get_default_categories():
                category = Category(
                    name=cat_data['name'],
                    icon=cat_data.get('icon'),
                    color=cat_data.get('color'),
                    is_default=True
                )
                db.session.add(category)
            db.session.commit()
            print("   ✅ Categorias padrão criadas!")
        
        # Opcional: criar um usuário de teste com transações
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
            
            # Criar algumas transações de exemplo
            print("\n💰 Criando transações de exemplo...")
            today = datetime.now().date()
            
            sample_transactions = [
                # Receitas
                Transaction(test_user.id, "Salário", 5000, TransactionType.INCOME, 
                           RecurrenceType.FIXED, "salário", today),
                Transaction(test_user.id, "Freelance Website", 1500, TransactionType.INCOME, 
                           RecurrenceType.VARIABLE, "freelance", today - timedelta(days=5)),
                
                # Despesas
                Transaction(test_user.id, "Aluguel", 1200, TransactionType.EXPENSE, 
                           RecurrenceType.FIXED, "moradia", today - timedelta(days=1)),
                Transaction(test_user.id, "Supermercado", 450, TransactionType.EXPENSE, 
                           RecurrenceType.VARIABLE, "alimentação", today - timedelta(days=2)),
                Transaction(test_user.id, "Plano de Saúde", 350, TransactionType.EXPENSE, 
                           RecurrenceType.FIXED, "saúde", today - timedelta(days=3)),
                Transaction(test_user.id, "Netflix", 39.90, TransactionType.EXPENSE, 
                           RecurrenceType.FIXED, "lazer", today - timedelta(days=4)),
            ]
            
            for transaction in sample_transactions:
                db.session.add(transaction)
            
            db.session.commit()
            print("   ✅ Transações de exemplo criadas!")

if __name__ == "__main__":
    init_database()