from flask import Blueprint, render_template

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route('/clientes')
def index():
    return render_template('pages/clientes/index.html')