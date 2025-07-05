from flask import Blueprint

bp = Blueprint('transactions', __name__)

@bp.route('/test')
def test():
    return {'message': 'Transactions route working!'}, 200
