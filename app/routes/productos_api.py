"""API endpoints para búsqueda y consulta de productos."""
from flask import Blueprint, jsonify, request
from flask_login import login_required

from app.database.models import Producto, Rama

productos_api_bp = Blueprint('productos_api', __name__, url_prefix='/api/productos')


@productos_api_bp.route('/search')
@login_required
def search():
    """Buscar productos para Select2 (autocomplete).

    Query params:
      q      — término de búsqueda
      rama_id — filtrar por rama / sector (opcional)

    Returns JSON lista compatible con Select2:
      [{ id, nombre, text, destino, rama }]
    """
    q = request.args.get('q', '').strip()
    rama_id = request.args.get('rama_id', type=int)

    query = Producto.query.filter_by(activo=True)

    if q and len(q) >= 1:
        query = query.filter(Producto.nombre.ilike(f'%{q}%'))

    if rama_id:
        query = query.filter_by(rama_id=rama_id)

    productos = query.order_by(Producto.nombre).limit(30).all()

    results = [
        {
            'id': p.id,
            'nombre': p.nombre,
            'text': p.nombre,
            'destino': p.destino.nombre if p.destino else None,
            'rama': p.rama.nombre if hasattr(p, 'rama') and p.rama else None,
        }
        for p in productos
    ]

    return jsonify(results)


@productos_api_bp.route('/<int:producto_id>')
@login_required
def get_producto(producto_id):
    """Obtener datos de un producto (para precargar Select2 en modo edición)."""
    producto = Producto.query.get_or_404(producto_id)
    return jsonify({
        'id': producto.id,
        'nombre': producto.nombre,
        'text': producto.nombre,
        'destino': producto.destino.nombre if producto.destino else None,
    })
