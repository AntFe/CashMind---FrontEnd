from flask import Blueprint

bp = Blueprint('dashboard', __name__)

@bp.route('/test')
def test():
    return {'message': 'Dashboard route working!'}, 200
