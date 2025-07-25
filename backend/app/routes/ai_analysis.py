from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ai_service import AIService
from datetime import datetime

bp = Blueprint('ai_analysis', __name__)

# Instância do serviço de IA
ai_service = AIService()

@bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_expenses():
    """Endpoint para análise de despesas com IA"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        # Parâmetros opcionais
        month = data.get('month', datetime.now().month)
        year = data.get('year', datetime.now().year)
        
        # Fazer análise
        result = ai_service.analyze_expenses(current_user_id, month, year)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar análise: {str(e)}'}), 500

@bp.route('/insights', methods=['GET'])
@jwt_required()
def get_insights():
    """Endpoint para obter insights rápidos"""
    try:
        current_user_id = get_jwt_identity()
        
        # Obter insights
        insights = ai_service.get_spending_insights(current_user_id)
        
        return jsonify({
            'insights': insights
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar insights: {str(e)}'}), 500

@bp.route('/status', methods=['GET'])
@jwt_required()
def get_ai_status():
    """Verifica se a IA está configurada e funcionando"""
    return jsonify({
        'enabled': ai_service.enabled,
        'message': 'IA configurada e pronta' if ai_service.enabled else 'Configure a API Key do Google Gemini no arquivo .env'
    }), 200