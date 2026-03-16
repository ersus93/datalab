"""API endpoints para gestión de Órdenes de Trabajo."""
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from flask_babel import _

from app.decorators import technician_required
from app.services.orden_trabajo_service import OrdenTrabajoService

ordenes_trabajo_api_bp = Blueprint('ordenes_trabajo_api', __name__, url_prefix='/api/ordenes-trabajo')
clientes_ordenes_api_bp = Blueprint('clientes_ordenes_api', __name__, url_prefix='/api/clientes')


def _pedido_to_dict_simple(pedido):
    """Convertir pedido a diccionario simplificado para respuesta API."""
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


def _orden_trabajo_to_dict(orden):
    """Convertir orden de trabajo a diccionario con formato de respuesta API."""
    # Obtener pedidos relacionados
    pedidos = orden.pedidos.all()
    
    return {
        'id': orden.id,
        'nro_ofic': orden.nro_ofic,
        'codigo': orden.codigo,
        'cliente': {
            'id': orden.cliente.id,
            'nombre': orden.cliente.nombre
        } if orden.cliente else None,
        'descripcion': orden.descripcion,
        'observaciones': orden.observaciones,
        'status': orden.status,
        'progreso': orden.progreso,
        'pedidos_count': orden.pedidos_count,
        'entradas_count': orden.entradas_count,
        'fech_creacion': orden.fech_creacion.isoformat() if orden.fech_creacion else None,
        'fech_completado': orden.fech_completado.isoformat() if orden.fech_completado else None,
        'pedidos': [_pedido_to_dict_simple(p) for p in pedidos]
    }


@ordenes_trabajo_api_bp.route('', methods=['GET'])
@login_required
def listar_ordenes_trabajo():
    """Listar órdenes de trabajo con filtros y paginación."""
    try:
        # Obtener parámetros de consulta
        filtros = {
            'cliente_id': request.args.get('cliente_id', type=int),
            'status': request.args.get('status'),
            'fecha_desde': request.args.get('desde'),
            'fecha_hasta': request.args.get('hasta')
        }
        
        # Filtro de búsqueda por nro_ofic (parámetro 'q')
        q = request.args.get('q')
        if q:
            filtros['nro_ofic'] = q
        
        # Eliminar filtros None
        filtros = {k: v for k, v in filtros.items() if v is not None}

        pagina = request.args.get('page', 1, type=int)
        por_pagina = request.args.get('per_page', 20, type=int)
        ordenar_por = request.args.get('sort_by', 'fech_creacion')
        orden = request.args.get('sort_order', 'desc')

        ordenes, meta = OrdenTrabajoService.obtener_ordenes_paginadas(
            filtros=filtros,
            pagina=pagina,
            por_pagina=por_pagina,
            ordenar_por=ordenar_por,
            orden=orden
        )

        return jsonify({
            'success': True,
            'data': [_orden_trabajo_to_dict(o) for o in ordenes],
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


@ordenes_trabajo_api_bp.route('', methods=['POST'])
@login_required
@technician_required
def crear_orden_trabajo():
    """Crear nueva orden de trabajo."""
    try:
        data = request.get_json()
        orden = OrdenTrabajoService.crear_orden_trabajo(data, current_user.id)
        return jsonify({
            'success': True,
            'data': _orden_trabajo_to_dict(orden),
            'message': _('Orden de trabajo creada exitosamente')
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


@ordenes_trabajo_api_bp.route('/<int:orden_id>', methods=['GET'])
@login_required
def obtener_orden_trabajo(orden_id):
    """Obtener detalles de una orden de trabajo."""
    try:
        orden = OrdenTrabajoService.obtener_orden_por_id(orden_id)
        if not orden:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': _('Orden de trabajo no encontrada'),
                    'details': {}
                }
            }), 404

        return jsonify({
            'success': True,
            'data': _orden_trabajo_to_dict(orden)
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


@ordenes_trabajo_api_bp.route('/<int:orden_id>', methods=['PUT'])
@login_required
@technician_required
def actualizar_orden_trabajo(orden_id):
    """Actualizar una orden de trabajo existente."""
    try:
        data = request.get_json()
        orden = OrdenTrabajoService.actualizar_orden(
            orden_id=orden_id,
            data=data,
            usuario_id=current_user.id
        )
        return jsonify({
            'success': True,
            'data': _orden_trabajo_to_dict(orden),
            'message': _('Orden de trabajo actualizada exitosamente')
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


@ordenes_trabajo_api_bp.route('/<int:orden_id>', methods=['DELETE'])
@login_required
@technician_required
def eliminar_orden_trabajo(orden_id):
    """Eliminar (soft delete) una orden de trabajo."""
    try:
        orden = OrdenTrabajoService.eliminar_orden(
            orden_id=orden_id,
            usuario_id=current_user.id
        )
        return jsonify({
            'success': True,
            'data': _orden_trabajo_to_dict(orden),
            'message': _('Orden de trabajo eliminada exitosamente')
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


@ordenes_trabajo_api_bp.route('/<int:orden_id>/asignar-pedido', methods=['POST'])
@login_required
@technician_required
def asignar_pedido(orden_id):
    """Asignar un pedido a una orden de trabajo."""
    try:
        data = request.get_json()
        pedido_id = data.get('pedido_id')
        
        if not pedido_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': _('El pedido_id es obligatorio'),
                    'details': {}
                }
            }), 400
        
        orden = OrdenTrabajoService.asignar_pedido(
            orden_id=orden_id,
            pedido_id=pedido_id,
            usuario_id=current_user.id
        )
        return jsonify({
            'success': True,
            'data': _orden_trabajo_to_dict(orden),
            'message': _('Pedido asignado exitosamente')
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


@ordenes_trabajo_api_bp.route('/<int:orden_id>/quitar-pedido', methods=['POST'])
@login_required
@technician_required
def quitar_pedido(orden_id):
    """Quitar un pedido de una orden de trabajo."""
    try:
        data = request.get_json()
        pedido_id = data.get('pedido_id')
        
        if not pedido_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': _('El pedido_id es obligatorio'),
                    'details': {}
                }
            }), 400
        
        orden = OrdenTrabajoService.quitar_pedido(
            orden_id=orden_id,
            pedido_id=pedido_id,
            usuario_id=current_user.id
        )
        return jsonify({
            'success': True,
            'data': _orden_trabajo_to_dict(orden),
            'message': _('Pedido quitado exitosamente')
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


@ordenes_trabajo_api_bp.route('/buscar', methods=['GET'])
@login_required
def buscar_por_nro_ofic():
    """Buscar orden de trabajo por número oficial."""
    try:
        nro_ofic = request.args.get('nro_ofic')
        
        if not nro_ofic:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': _('El parámetro nro_ofic es obligatorio'),
                    'details': {}
                }
            }), 400
        
        orden = OrdenTrabajoService.buscar_por_nro_ofic(nro_ofic)
        if not orden:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': _('Orden de trabajo no encontrada'),
                    'details': {}
                }
            }), 404

        return jsonify({
            'success': True,
            'data': _orden_trabajo_to_dict(orden)
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


@clientes_ordenes_api_bp.route('/<int:cliente_id>/ordenes-trabajo', methods=['GET'])
@login_required
def obtener_ordenes_por_cliente(cliente_id):
    """Obtener órdenes de trabajo de un cliente específico."""
    try:
        pagina = request.args.get('page', 1, type=int)
        por_pagina = request.args.get('per_page', 20, type=int)
        ordenar_por = request.args.get('sort_by', 'fech_creacion')
        orden = request.args.get('sort_order', 'desc')

        ordenes, meta = OrdenTrabajoService.obtener_ordenes_paginadas(
            filtros={'cliente_id': cliente_id},
            pagina=pagina,
            por_pagina=por_pagina,
            ordenar_por=ordenar_por,
            orden=orden
        )

        return jsonify({
            'success': True,
            'data': [_orden_trabajo_to_dict(o) for o in ordenes],
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
