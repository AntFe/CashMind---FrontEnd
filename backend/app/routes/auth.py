from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from app.models import User
import re

bp = Blueprint('auth', __name__)

def validate_email(email):
    """Valida formato do email"""
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Valida a senha conforme as regras do frontend"""
    errors = []
    
    if len(password) < 8:
        errors.append("Senha deve ter no mínimo 8 caracteres")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Senha deve conter pelo menos uma letra maiúscula")
    
    if not re.search(r'[#%&*!?]', password):
        errors.append("Senha deve conter um caractere especial (#%&*!?)")
    
    if not re.search(r'\d', password):
        errors.append("Senha deve conter pelo menos um número")
    
    # Verifica números sequenciais
    numbers = re.findall(r'\d', password)
    for i in range(len(numbers) - 1):
        if int(numbers[i+1]) == int(numbers[i]) + 1:
            errors.append("Senha não pode conter números sequenciais")
            break
    
    return errors

@bp.route('/register', methods=['POST'])
def register():
    """Endpoint para registro de novo usuário"""
    try:
        data = request.get_json()
        
        # Validação dos dados
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validações
        if not full_name:
            return jsonify({'error': 'Nome completo é obrigatório'}), 400
        
        if not email or not validate_email(email):
            return jsonify({'error': 'Email inválido'}), 400
        
        # Valida senha
        password_errors = validate_password(password)
        if password_errors:
            return jsonify({'error': password_errors[0]}), 400
        
        # Verifica se usuário já existe
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email já cadastrado'}), 409
        
        # Cria novo usuário
        new_user = User(
            full_name=full_name,
            email=email,
            password=password
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Cria tokens JWT
        access_token = create_access_token(identity=new_user.id)
        refresh_token = create_refresh_token(identity=new_user.id)
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'user': new_user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao criar usuário: {str(e)}'}), 500

@bp.route('/login', methods=['POST'])
def login():
    """Endpoint para login de usuário"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validações básicas
        if not email or not password:
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        # Busca usuário
        user = User.query.filter_by(email=email).first()
        
        # Verifica credenciais
        if not user or not user.check_password(password):
            return jsonify({'error': 'Email ou senha incorretos'}), 401
        
        # Verifica se usuário está ativo
        if not user.is_active:
            return jsonify({'error': 'Usuário desativado'}), 403
        
        # Cria tokens JWT
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao realizar login: {str(e)}'}), 500

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Endpoint para renovar o token de acesso"""
    try:
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': new_access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao renovar token: {str(e)}'}), 500

@bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """Endpoint para obter dados do usuário logado"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar perfil: {str(e)}'}), 500

# Mantém a rota de teste
@bp.route('/test')
def test():
    return {'message': 'Auth route working!'}, 200