"""API endpoints para gestión de entradas de muestras."""
from decimal import Decimal
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from flask_babel import _

from app.decorators import technician_required
from app.services.entrada_service import EntradaService

entradas_api_bp = Blueprint('entradas_api', __name__, url_prefix='/api/entradas')


@entradas_api_bp.route('', methods=['POST'])
@login_required
@technician_required
def crear_entrada():
    """Crear nueva entrada de muestra."""
    try:
        data = request.get_json()
        entrada = EntradaService.crear_entrada(data, current_user.id)
        return jsonify({
            'success': True,
            'data': entrada.to_dict(),
            'message': _('Entrada creada exitosamente')
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


@entradas_api_bp.route('', methods=['GET'])
@login_required
def listar_entradas():
    """Listar entradas con filtros y paginación."""
    try:
        # Obtener parámetros de consulta
        filtros = {
            'cliente_id': request.args.get('cliente_id', type=int),
            'producto_id': request.args.get('producto_id', type=int),
            'status': request.args.get('status'),
            'fecha_desde': request.args.get('fecha_desde'),
            'fecha_hasta': request.args.get('fecha_hasta')
        }
        # Eliminar filtros None
        filtros = {k: v for k, v in filtros.items() if v is not None}

        pagina = request.args.get('page', 1, type=int)
        por_pagina = request.args.get('per_page', 20, type=int)
        ordenar_por = request.args.get('sort_by', 'fech_entrada')
        orden = request.args.get('sort_order', 'desc')

        entradas, meta = EntradaService.obtener_entradas_paginadas(
            filtros=filtros,
            pagina=pagina,
            por_pagina=por_pagina,
            ordenar_por=ordenar_por,
            orden=orden
        )

        return jsonify({
            'success': True,
            'data': {
                'entradas': [e.to_dict() for e in entradas],
                'pagination': meta
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


@entradas_api_bp.route('/<int:entrada_id>', methods=['GET'])
@login_required
def obtener_entrada(entrada_id):
    """Obtener detalles de una entrada."""
    try:
        entrada = EntradaService.obtener_entrada_por_id(entrada_id)
        if not entrada:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': _('Entrada no encontrada'),
                    'details': {}
                }
            }), 404

        return jsonify({
            'success': True,
            'data': entrada.to_dict()
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


@entradas_api_bp.route('/<int:entrada_id>', methods=['PUT'])
@login_required
@technician_required
def actualizar_entrada(entrada_id):
    """Actualizar una entrada existente."""
    try:
        data = request.get_json()
        entrada = EntradaService.actualizar_entrada(
            entrada_id=entrada_id,
            data=data,
            usuario_id=current_user.id
        )
        return jsonify({
            'success': True,
            'data': entrada.to_dict(),
            'message': _('Entrada actualizada exitosamente')
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


@entradas_api_bp.route('/<int:entrada_id>', methods=['DELETE'])
@login_required
@technician_required
def anular_entrada(entrada_id):
    """Anular (soft delete) una entrada."""
    try:
        entrada = EntradaService.eliminar_entrada(
            entrada_id=entrada_id,
            usuario_id=current_user.id
        )
        return jsonify({
            'success': True,
            'data': entrada.to_dict(),
            'message': _('Entrada anulada exitosamente')
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


@entradas_api_bp.route('/<int:entrada_id>/cambiar-estado', methods=['POST'])
@login_required
@technician_required
def cambiar_estado(entrada_id):
    """Cambiar el estado de una entrada con validación."""
    try:
        data = request.get_json()
        nuevo_estado = data.get('status')
        razon = data.get('reason', '')

        if not nuevo_estado:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': _('Nuevo estado requerido'),
                    'details': {}
                }
            }), 400

        entrada = EntradaService.cambiar_estado(
            entrada_id=entrada_id,
            nuevo_estado=nuevo_estado,
            usuario_id=current_user.id,
            razon=razon
        )
        return jsonify({
            'success': True,
            'data': entrada.to_dict(),
            'message': _('Estado actualizado exitosamente')
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


@entradas_api_bp.route('/<int:entrada_id>/saldo', methods=['GET'])
@login_required
def obtener_saldo(entrada_id):
    """Obtener el saldo actual de una entrada."""
    try:
        entrada = EntradaService.obtener_entrada_por_id(entrada_id)
        if not entrada:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': _('Entrada no encontrada'),
                    'details': {}
                }
            }), 404

        return jsonify({
            'success': True,
            'data': {
                'entrada_id': entrada.id,
                'codigo': entrada.codigo,
                'cantidad_recib': str(entrada.cantidad_recib),
                'cantidad_entreg': str(entrada.cantidad_entreg),
                'saldo': str(entrada.saldo)
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


@entradas_api_bp.route('/<int:entrada_id>/entregar', methods=['POST'])
@login_required
@technician_required
def registrar_entrega(entrada_id):
    """Registrar entrega de cantidad."""
    try:
        data = request.get_json()
        cantidad = data.get('cantidad')

        if cantidad is None:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': _('Cantidad requerida'),
                    'details': {}
                }
            }), 400

        entrada = EntradaService.registrar_entrega(
            entrada_id=entrada_id,
            cantidad=Decimal(str(cantidad)),
            usuario_id=current_user.id
        )
        return jsonify({
            'success': True,
            'data': entrada.to_dict(),
            'message': _('Entrega registrada exitosamente')
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
