"""API endpoints para búsqueda y consulta de fábricas."""
from flask import Blueprint, jsonify, request
from flask_login import login_required

from app.database.models import Fabrica, Cliente

fabricas_api_bp = Blueprint('fabricas_api', __name__, url_prefix='/api/fabricas')


@fabricas_api_bp.route('/search')
@login_required
def search():
    """Buscar fábricas para Select2 (autocomplete).

    Query params:
      q   — término de búsqueda (min 2 chars)
      cliente_id — filtrar por cliente (opcional)

    Returns JSON lista compatible con Select2:
      [{ id, nombre, cliente: { id, nombre } }]
    """
    q = request.args.get('q', '').strip()
    cliente_id = request.args.get('cliente_id', type=int)

    query = Fabrica.query.filter_by(activo=True)

    if q and len(q) >= 1:
        query = query.filter(Fabrica.nombre.ilike(f'%{q}%'))

    if cliente_id:
        query = query.filter_by(cliente_id=cliente_id)

    fabricas = query.join(Cliente).order_by(Fabrica.nombre).limit(30).all()

    results = [
        {
            'id': f.id,
            'nombre': f.nombre,
            'text': f'{f.nombre} ({f.cliente.nombre})',
            'cliente': {
                'id': f.cliente.id,
                'nombre': f.cliente.nombre,
            } if f.cliente else None,
        }
        for f in fabricas
    ]

    return jsonify(results)


@fabricas_api_bp.route('/<int:fabrica_id>')
@login_required
def get_fabrica(fabrica_id):
    """Obtener datos de una fábrica (para precargar Select2 en modo edición)."""
    fabrica = Fabrica.query.get_or_404(fabrica_id)
    return jsonify({
        'id': fabrica.id,
        'nombre': fabrica.nombre,
        'text': f'{fabrica.nombre} ({fabrica.cliente.nombre})',
        'cliente': {
            'id': fabrica.cliente.id,
            'nombre': fabrica.cliente.nombre,
        } if fabrica.cliente else None,
    })
