from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Transaction, TransactionType
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from collections import defaultdict

bp = Blueprint('dashboard', __name__)

@bp.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    """Retorna resumo financeiro do usuário"""
    try:
        current_user_id = get_jwt_identity()
        
        # Parâmetros opcionais
        month = request.args.get('month', datetime.now().month, type=int)
        year = request.args.get('year', datetime.now().year, type=int)
        
        # Buscar transações do mês
        transactions = Transaction.query.filter(
            Transaction.user_id == current_user_id,
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        ).all()
        
        # Calcular totais
        total_income = sum(t.amount for t in transactions if t.transaction_type == TransactionType.INCOME)
        total_expense = sum(t.amount for t in transactions if t.transaction_type == TransactionType.EXPENSE)
        balance = total_income - total_expense
        
        # Separar fixas e variáveis
        fixed_expenses = sum(t.amount for t in transactions 
                           if t.transaction_type == TransactionType.EXPENSE 
                           and t.recurrence_type.value == 'fixed')
        variable_expenses = sum(t.amount for t in transactions 
                              if t.transaction_type == TransactionType.EXPENSE 
                              and t.recurrence_type.value == 'variable')
        
        # Calcular porcentagem de gastos
        expense_percentage = (total_expense / total_income * 100) if total_income > 0 else 0
        
        return jsonify({
            'summary': {
                'month': month,
                'year': year,
                'income': round(total_income, 2),
                'expense': round(total_expense, 2),
                'balance': round(balance, 2),
                'fixed_expenses': round(fixed_expenses, 2),
                'variable_expenses': round(variable_expenses, 2),
                'expense_percentage': round(expense_percentage, 2),
                'total_transactions': len(transactions)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar resumo: {str(e)}'}), 500

@bp.route('/expenses-by-category', methods=['GET'])
@jwt_required()
def get_expenses_by_category():
    """Retorna despesas agrupadas por categoria"""
    try:
        current_user_id = get_jwt_identity()
        
        # Parâmetros opcionais
        month = request.args.get('month', datetime.now().month, type=int)
        year = request.args.get('year', datetime.now().year, type=int)
        
        # Buscar despesas do mês agrupadas por categoria
        expenses = db.session.query(
            Transaction.category,
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.user_id == current_user_id,
            Transaction.transaction_type == TransactionType.EXPENSE,
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        ).group_by(Transaction.category).all()
        
        # Formatar resultado
        categories = []
        total_expenses = 0
        
        for category, amount in expenses:
            categories.append({
                'category': category,
                'amount': round(amount, 2)
            })
            total_expenses += amount
        
        # Adicionar porcentagem
        for cat in categories:
            cat['percentage'] = round((cat['amount'] / total_expenses * 100) if total_expenses > 0 else 0, 2)
        
        # Ordenar por valor
        categories.sort(key=lambda x: x['amount'], reverse=True)
        
        return jsonify({
            'expenses_by_category': categories,
            'total': round(total_expenses, 2)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar despesas por categoria: {str(e)}'}), 500

@bp.route('/monthly-trend', methods=['GET'])
@jwt_required()
def get_monthly_trend():
    """Retorna tendência de gastos dos últimos 6 meses"""
    try:
        current_user_id = get_jwt_identity()
        
        # Calcular período de 6 meses
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=180)
        
        # Buscar transações dos últimos 6 meses
        transactions = db.session.query(
            extract('year', Transaction.date).label('year'),
            extract('month', Transaction.date).label('month'),
            Transaction.transaction_type,
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.user_id == current_user_id,
            Transaction.date >= start_date
        ).group_by(
            extract('year', Transaction.date),
            extract('month', Transaction.date),
            Transaction.transaction_type
        ).all()
        
        # Organizar dados por mês
        monthly_data = defaultdict(lambda: {'income': 0, 'expense': 0})
        
        for year, month, trans_type, total in transactions:
            key = f"{int(year)}-{int(month):02d}"
            if trans_type == TransactionType.INCOME:
                monthly_data[key]['income'] = round(total, 2)
            else:
                monthly_data[key]['expense'] = round(total, 2)
        
        # Converter para lista ordenada
        result = []
        for key in sorted(monthly_data.keys()):
            year, month = key.split('-')
            result.append({
                'year': int(year),
                'month': int(month),
                'income': monthly_data[key]['income'],
                'expense': monthly_data[key]['expense'],
                'balance': round(monthly_data[key]['income'] - monthly_data[key]['expense'], 2)
            })
        
        return jsonify({
            'monthly_trend': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar tendência mensal: {str(e)}'}), 500

@bp.route('/recent-transactions', methods=['GET'])
@jwt_required()
def get_recent_transactions():
    """Retorna as transações mais recentes"""
    try:
        current_user_id = get_jwt_identity()
        
        # Limite de transações
        limit = request.args.get('limit', 10, type=int)
        
        # Buscar transações recentes
        transactions = Transaction.query.filter_by(
            user_id=current_user_id
        ).order_by(
            Transaction.date.desc(),
            Transaction.created_at.desc()
        ).limit(limit).all()
        
        return jsonify({
            'recent_transactions': [t.to_dict() for t in transactions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar transações recentes: {str(e)}'}), 500

@bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    """Retorna análise completa para o dashboard"""
    try:
        current_user_id = get_jwt_identity()
        
        # Mês atual
        month = request.args.get('month', datetime.now().month, type=int)
        year = request.args.get('year', datetime.now().year, type=int)
        
        # Buscar todas as análises
        summary_response = get_summary()
        categories_response = get_expenses_by_category()
        trend_response = get_monthly_trend()
        recent_response = get_recent_transactions()
        
        # Combinar respostas
        analytics = {
            'summary': summary_response[0].json['summary'],
            'expenses_by_category': categories_response[0].json['expenses_by_category'],
            'monthly_trend': trend_response[0].json['monthly_trend'],
            'recent_transactions': recent_response[0].json['recent_transactions']
        }
        
        return jsonify(analytics), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar análises: {str(e)}'}), 500

# Mantém a rota de teste
@bp.route('/test')
def test():
    return {'message': 'Dashboard route working!'}, 200