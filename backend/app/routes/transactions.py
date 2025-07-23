from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Transaction, TransactionType, RecurrenceType, Category
from datetime import datetime
from sqlalchemy import extract

bp = Blueprint('transactions', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_transactions():
    """Lista todas as transações do usuário"""
    try:
        current_user_id = get_jwt_identity()
        
        # Filtros opcionais
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        transaction_type = request.args.get('type')
        category = request.args.get('category')
        
        # Query base
        query = Transaction.query.filter_by(user_id=current_user_id)
        
        # Aplicar filtros
        if month and year:
            query = query.filter(
                extract('month', Transaction.date) == month,
                extract('year', Transaction.date) == year
            )
        elif year:
            query = query.filter(extract('year', Transaction.date) == year)
        
        if transaction_type:
            query = query.filter_by(transaction_type=TransactionType(transaction_type))
        
        if category:
            query = query.filter_by(category=category.lower())
        
        # Ordenar por data decrescente
        transactions = query.order_by(Transaction.date.desc()).all()
        
        return jsonify({
            'transactions': [t.to_dict() for t in transactions],
            'total': len(transactions)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar transações: {str(e)}'}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
def create_transaction():
    """Cria uma nova transação"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validações
        required_fields = ['name', 'amount', 'type', 'recurrence', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Validar tipo
        try:
            transaction_type = TransactionType(data['type'])
        except ValueError:
            return jsonify({'error': 'Tipo deve ser "income" ou "expense"'}), 400
        
        # Validar recorrência
        try:
            recurrence_type = RecurrenceType(data['recurrence'])
        except ValueError:
            return jsonify({'error': 'Recorrência deve ser "fixed" ou "variable"'}), 400
        
        # Validar valor
        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({'error': 'Valor deve ser maior que zero'}), 400
        except ValueError:
            return jsonify({'error': 'Valor inválido'}), 400
        
        # Processar data
        date = None
        if 'date' in data:
            try:
                date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Data inválida. Use formato YYYY-MM-DD'}), 400
        
        # Criar transação
        transaction = Transaction(
            user_id=current_user_id,
            name=data['name'],
            amount=amount,
            transaction_type=transaction_type,
            recurrence_type=recurrence_type,
            category=data['category'],
            date=date,
            description=data.get('description')
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Transação criada com sucesso',
            'transaction': transaction.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao criar transação: {str(e)}'}), 500

@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_transaction(id):
    """Atualiza uma transação"""
    try:
        current_user_id = get_jwt_identity()
        transaction = Transaction.query.filter_by(id=id, user_id=current_user_id).first()
        
        if not transaction:
            return jsonify({'error': 'Transação não encontrada'}), 404
        
        data = request.get_json()
        
        # Atualizar campos se fornecidos
        if 'name' in data:
            transaction.name = data['name']
        
        if 'amount' in data:
            try:
                amount = float(data['amount'])
                if amount > 0:
                    transaction.amount = amount
            except ValueError:
                pass
        
        if 'type' in data:
            try:
                transaction.transaction_type = TransactionType(data['type'])
            except ValueError:
                pass
        
        if 'recurrence' in data:
            try:
                transaction.recurrence_type = RecurrenceType(data['recurrence'])
            except ValueError:
                pass
        
        if 'category' in data:
            transaction.category = data['category'].lower()
        
        if 'date' in data:
            try:
                transaction.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if 'description' in data:
            transaction.description = data['description']
        
        transaction.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Transação atualizada com sucesso',
            'transaction': transaction.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao atualizar transação: {str(e)}'}), 500

@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(id):
    """Deleta uma transação"""
    try:
        current_user_id = get_jwt_identity()
        transaction = Transaction.query.filter_by(id=id, user_id=current_user_id).first()
        
        if not transaction:
            return jsonify({'error': 'Transação não encontrada'}), 404
        
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({'message': 'Transação deletada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao deletar transação: {str(e)}'}), 500

@bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """Lista todas as categorias disponíveis"""
    try:
        # Pegar categorias padrão
        default_categories = Category.query.filter_by(is_default=True).all()
        
        # Pegar categorias únicas usadas pelo usuário
        current_user_id = get_jwt_identity()
        user_categories = db.session.query(Transaction.category).filter_by(
            user_id=current_user_id
        ).distinct().all()
        
        # Combinar categorias
        all_categories = set()
        
        # Adicionar categorias padrão
        for cat in default_categories:
            all_categories.add(cat.name)
        
        # Adicionar categorias do usuário
        for cat in user_categories:
            all_categories.add(cat[0])
        
        return jsonify({
            'categories': sorted(list(all_categories))
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar categorias: {str(e)}'}), 500

# Mantém a rota de teste
@bp.route('/test')
def test():
    return {'message': 'Transactions route working!'}, 200