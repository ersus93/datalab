"""API endpoints para gestión de Pedidos."""
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from flask_babel import _

from app.decorators import technician_required
from app.services.pedido_service import PedidoService

pedidos_api_bp = Blueprint('pedidos_api', __name__, url_prefix='/api/pedidos')
clientes_pedidos_api_bp = Blueprint('clientes_pedidos_api', __name__, url_prefix='/api/clientes')


def _pedido_to_dict(pedido):
    """Convertir pedido a diccionario con formato de respuesta API."""
    return {
        'id': pedido.id,
        'codigo': pedido.codigo,
        'cliente': {
            'id': pedido.cliente.id,
            'nombre': pedido.cliente.nombre
        } if pedido.cliente else None,
        'producto': {
            'id': pedido.producto.id,
            'nombre': pedido.producto.nombre
        } if pedido.producto else None,
        'lote': pedido.lote,
        'fech_fab': pedido.fech_fab.isoformat() if pedido.fech_fab else None,
        'fech_venc': pedido.fech_venc.isoformat() if pedido.fech_venc else None,
        'cantidad': float(pedido.cantidad) if pedido.cantidad else None,
        'status': pedido.status,
        'entradas_count': pedido.entradas_count,
        'entradas_completadas': pedido.entradas_completadas
    }


@pedidos_api_bp.route('', methods=['POST'])
@login_required
@technician_required
def crear_pedido():
    """Crear nuevo pedido."""
    try:
        data = request.get_json()
        pedido = PedidoService.crear_pedido(data, current_user.id)
        return jsonify({
            'success': True,
            'data': _pedido_to_dict(pedido),
            'message': _('Pedido creado exitosamente')
        }), 201
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e),
                'details': {}
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e),
                'details': {}
            }
        }), 500


@pedidos_api_bp.route('', methods=['GET'])
@login_required
def listar_pedidos():
    """Listar pedidos con filtros y paginación."""
    try:
        # Obtener parámetros de consulta
        filtros = {
            'cliente_id': request.args.get('cliente_id', type=int),
            'producto_id': request.args.get('producto_id', type=int),
            'status': request.args.get('status'),
            'fecha_desde': request.args.get('desde'),
            'fecha_hasta': request.args.get('hasta')
        }
        # Eliminar filtros None
        filtros = {k: v for k, v in filtros.items() if v is not None}

        pagina = request.args.get('page', 1, type=int)
        por_pagina = request.args.get('per_page', 20, type=int)
        ordenar_por = request.args.get('sort_by', 'fech_pedido')
        orden = request.args.get('sort_order', 'desc')

        pedidos, meta = PedidoService.obtener_pedidos_paginados(
            filtros=filtros,
            pagina=pagina,
            por_pagina=por_pagina,
            ordenar_por=ordenar_por,
            orden=orden
        )

        return jsonify({
            'success': True,
            'data': [_pedido_to_dict(p) for p in pedidos],
            'meta': {
                'page': meta['pagina'],
                'per_page': meta['por_pagina'],
                'total': meta['total'],
                'total_pages': meta['total_paginas']
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e),
                'details': {}
            }
        }), 500


@pedidos_api_bp.route('/<int:pedido_id>', methods=['GET'])
@login_required
def obtener_pedido(pedido_id):
    """Obtener detalles de un pedido."""
    try:
        pedido = PedidoService.obtener_pedido_por_id(pedido_id)
        if not pedido:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': _('Pedido no encontrado'),
                    'details': {}
                }
            }), 404

        return jsonify({
            'success': True,
            'data': _pedido_to_dict(pedido)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e),
                'details': {}
            }
        }), 500


@pedidos_api_bp.route('/<int:pedido_id>', methods=['PUT'])
@login_required
@technician_required
def actualizar_pedido(pedido_id):
    """Actualizar un pedido existente."""
    try:
        data = request.get_json()
        pedido = PedidoService.actualizar_pedido(
            pedido_id=pedido_id,
            data=data,
            usuario_id=current_user.id
        )
        return jsonify({
            'success': True,
            'data': _pedido_to_dict(pedido),
            'message': _('Pedido actualizado exitosamente')
        }), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e),
                'details': {}
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e),
                'details': {}
            }
        }), 500


@pedidos_api_bp.route('/<int:pedido_id>', methods=['DELETE'])
@login_required
@technician_required
def eliminar_pedido(pedido_id):
    """Eliminar (soft delete) un pedido."""
    try:
        pedido = PedidoService.eliminar_pedido(
            pedido_id=pedido_id,
            usuario_id=current_user.id
        )
        return jsonify({
            'success': True,
            'data': _pedido_to_dict(pedido),
            'message': _('Pedido eliminado exitosamente')
        }), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e),
                'details': {}
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e),
                'details': {}
            }
        }), 500


@pedidos_api_bp.route('/<int:pedido_id>/entradas', methods=['GET'])
@login_required
def obtener_entradas_pedido(pedido_id):
    """Obtener entradas relacionadas a un pedido."""
    try:
        entradas = PedidoService.obtener_entradas_de_pedido(pedido_id)
        return jsonify({
            'success': True,
            'data': entradas
        }), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e),
                'details': {}
            }
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e),
                'details': {}
            }
        }), 500


@clientes_pedidos_api_bp.route('/<int:cliente_id>/pedidos', methods=['GET'])
@login_required
def obtener_pedidos_por_cliente(cliente_id):
    """Obtener pedidos de un cliente específico."""
    try:
        pagina = request.args.get('page', 1, type=int)
        por_pagina = request.args.get('per_page', 20, type=int)
        ordenar_por = request.args.get('sort_by', 'fech_pedido')
        orden = request.args.get('sort_order', 'desc')

        pedidos, meta = PedidoService.obtener_pedidos_paginados(
            filtros={'cliente_id': cliente_id},
            pagina=pagina,
            por_pagina=por_pagina,
            ordenar_por=ordenar_por,
            orden=orden
        )

        return jsonify({
            'success': True,
            'data': [_pedido_to_dict(p) for p in pedidos],
            'meta': {
                'page': meta['pagina'],
                'per_page': meta['por_pagina'],
                'total': meta['total'],
                'total_pages': meta['total_paginas']
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e),
                'details': {}
            }
        }), 500
