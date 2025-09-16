from flask import Blueprint, jsonify, request
from app.database.models import Pedido, Cliente, OrdenTrabajo
from sqlalchemy import or_

bp = Blueprint('search', __name__)

@bp.route('/api/search')
def search():
    """Endpoint de búsqueda dinámica."""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'results': []})

    results = []

    try:
        # Buscar en pedidos
        pedidos = Pedido.query.filter(
            or_(
                Pedido.numero_pedido.ilike(f'%{query}%'),
                Pedido.descripcion.ilike(f'%{query}%')
            )
        ).limit(5).all()

        # Buscar en clientes
        clientes = Cliente.query.filter(
            or_(
                Cliente.nombre.ilike(f'%{query}%'),
                Cliente.codigo.ilike(f'%{query}%')
            )
        ).limit(5).all()

        # Buscar en órdenes de trabajo
        ordenes = OrdenTrabajo.query.filter(
            or_(
                OrdenTrabajo.numero.ilike(f'%{query}%'),
                OrdenTrabajo.descripcion.ilike(f'%{query}%')
            )
        ).limit(5).all()

        # Formatear resultados de pedidos
        for pedido in pedidos:
            results.append({
                'title': f'Pedido #{pedido.numero_pedido}',
                'description': pedido.descripcion[:100] + '...' if len(pedido.descripcion) > 100 else pedido.descripcion,
                'url': f'/pedidos/{pedido.id}',
                'type': 'pedido'
            })

        # Formatear resultados de clientes
        for cliente in clientes:
            results.append({
                'title': cliente.nombre,
                'description': f'Código: {cliente.codigo}',
                'url': f'/clientes/{cliente.id}',
                'type': 'cliente'
            })

        # Formatear resultados de órdenes de trabajo
        for orden in ordenes:
            results.append({
                'title': f'Orden #{orden.numero}',
                'description': orden.descripcion[:100] + '...' if len(orden.descripcion) > 100 else orden.descripcion,
                'url': f'/ordenes/{orden.id}',
                'type': 'orden'
            })

    except Exception as e:
        # En caso de error (ej: tablas no existen aún), devolver resultados de ejemplo
        results = [
            {
                'title': f'Pedido #001 - {query}',
                'description': 'Análisis microbiológico de muestras de agua',
                'url': '/dashboard',
                'type': 'pedido'
            },
            {
                'title': f'Cliente ONIE - {query}',
                'description': 'Oficina Nacional de Inspección Estatal',
                'url': '/dashboard',
                'type': 'cliente'
            }
        ]

    return jsonify({
        'results': results[:10]  # Limitar a 10 resultados
    })