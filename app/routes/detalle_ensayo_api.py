"""API endpoints para gestión de detalles de ensayo (asignación de pruebas a entradas)."""
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

detalle_ensayo_api_bp = Blueprint('detalle_ensayo_api', __name__, url_prefix='/api/entradas')


# ---------------------------------------------------------------------------
# Catálogo de ensayos (para el selector multi-selección del frontend)
# ---------------------------------------------------------------------------

ensayos_catalog_bp = Blueprint('ensayos_catalog', __name__, url_prefix='/api')


@ensayos_catalog_bp.route('/ensayos', methods=['GET'])
@login_required
def listar_ensayos_catalogo():
    """Listar ensayos del catálogo con filtros para el selector de la UI.

    Query params:
        area_id (int, opcional): Filtrar por área de laboratorio.
        activo (str, opcional): Filtrar por estado activo (default: true).
        q (str, opcional): Buscar por nombre_corto o nombre_oficial.

    Returns:
        JSON con lista de ensayos: id, nombre_corto, nombre_oficial, precio, area_id, area_nombre.
    """
    try:
        # Importación lazy para evitar importaciones circulares
        from app.database.models.ensayo import Ensayo
        from app.database.models.reference import Area

        area_id = request.args.get('area_id', type=int)
        # Por defecto mostrar solo activos
        activo_param = request.args.get('activo', 'true').lower()
        solo_activos = activo_param != 'false'
        q = request.args.get('q', '').strip()

        query = Ensayo.query

        if solo_activos:
            query = query.filter_by(activo=True)

        if area_id:
            query = query.filter_by(area_id=area_id)

        if q:
            query = query.filter(
                Ensayo.nombre_corto.ilike(f'%{q}%') |
                Ensayo.nombre_oficial.ilike(f'%{q}%')
            )

        # Unir con área para obtener nombre sin N+1 queries
        ensayos = query.join(Area, Ensayo.area_id == Area.id).order_by(
            Area.nombre, Ensayo.nombre_corto
        ).all()

        data = [
            {
                'id': e.id,
                'nombre_corto': e.nombre_corto,
                'nombre_oficial': e.nombre_oficial,
                'precio': str(e.precio) if e.precio is not None else None,
                'area_id': e.area_id,
                'area_nombre': e.area.nombre if e.area else None,
            }
            for e in ensayos
        ]

        return jsonify({'success': True, 'data': data}), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e),
                'details': {}
            }
        }), 500


# ---------------------------------------------------------------------------
# Detalles de ensayo por entrada
# ---------------------------------------------------------------------------

@detalle_ensayo_api_bp.route('/<int:entrada_id>/ensayos', methods=['GET'])
@login_required
def listar_detalles(entrada_id):
    """Listar detalles de ensayo agrupados por área para una entrada.

    Args:
        entrada_id: ID de la entrada.

    Returns:
        JSON con detalles agrupados por área de laboratorio.
    """
    try:
        from app.services.detalle_ensayo_service import DetalleEnsayoService

        detalles_agrupados = DetalleEnsayoService.get_detalles_agrupados_por_area(entrada_id)

        return jsonify({
            'success': True,
            'data': detalles_agrupados
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


@detalle_ensayo_api_bp.route('/<int:entrada_id>/ensayos', methods=['POST'])
@login_required
def asignar_ensayos(entrada_id):
    """Asignar en lote ensayos a una entrada.

    Body JSON:
        ensayo_ids (list[int]): Lista de IDs de ensayos a asignar.
        cantidad (int, opcional): Cantidad por ensayo (default: 1).

    Returns:
        JSON con lista de detalles creados.
    """
    try:
        from app.services.detalle_ensayo_service import DetalleEnsayoService

        data = request.get_json() or {}
        ensayo_ids = data.get('ensayo_ids')
        cantidad = data.get('cantidad', 1)

        if not ensayo_ids or not isinstance(ensayo_ids, list):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'ensayo_ids debe ser una lista no vacía',
                    'details': {}
                }
            }), 400

        detalles = DetalleEnsayoService.asignar_ensayos(
            entrada_id=entrada_id,
            ensayo_ids=ensayo_ids,
            cantidad=cantidad
        )

        return jsonify({
            'success': True,
            'data': [d.to_dict() for d in detalles]
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


@detalle_ensayo_api_bp.route('/<int:entrada_id>/ensayos/<int:detalle_id>', methods=['DELETE'])
@login_required
def eliminar_detalle(entrada_id, detalle_id):
    """Eliminar un detalle de ensayo (solo si está en estado PENDIENTE).

    Args:
        entrada_id: ID de la entrada asociada.
        detalle_id: ID del detalle a eliminar.

    Returns:
        JSON indicando éxito o error.
    """
    try:
        from app.services.detalle_ensayo_service import DetalleEnsayoService

        DetalleEnsayoService.eliminar_detalle(
            detalle_id=detalle_id,
            entrada_id=entrada_id
        )

        return jsonify({
            'success': True,
            'data': {'detalle_id': detalle_id}
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


# ---------------------------------------------------------------------------
# Transiciones de estado
# ---------------------------------------------------------------------------

@detalle_ensayo_api_bp.route(
    '/<int:entrada_id>/ensayos/<int:detalle_id>/asignar-tecnico',
    methods=['POST']
)
@login_required
def asignar_tecnico(entrada_id, detalle_id):
    """Asignar un técnico a un detalle de ensayo (PENDIENTE → ASIGNADO).

    Body JSON:
        tecnico_id (int): ID del técnico a asignar.

    Args:
        entrada_id: ID de la entrada asociada.
        detalle_id: ID del detalle a actualizar.

    Returns:
        JSON con el detalle actualizado.
    """
    try:
        from app.services.detalle_ensayo_service import DetalleEnsayoService

        data = request.get_json() or {}
        tecnico_id = data.get('tecnico_id')

        if tecnico_id is None:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'tecnico_id es requerido',
                    'details': {}
                }
            }), 400

        detalle = DetalleEnsayoService.asignar_tecnico(
            detalle_id=detalle_id,
            tecnico_id=tecnico_id,
            entrada_id=entrada_id
        )

        return jsonify({
            'success': True,
            'data': detalle.to_dict()
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


@detalle_ensayo_api_bp.route(
    '/<int:entrada_id>/ensayos/<int:detalle_id>/iniciar',
    methods=['POST']
)
@login_required
def iniciar_ensayo(entrada_id, detalle_id):
    """Iniciar la ejecución de un ensayo (ASIGNADO → EN_PROCESO).

    Args:
        entrada_id: ID de la entrada asociada.
        detalle_id: ID del detalle a actualizar.

    Returns:
        JSON con el detalle actualizado.
    """
    try:
        from app.services.detalle_ensayo_service import DetalleEnsayoService

        detalle = DetalleEnsayoService.iniciar_ensayo(
            detalle_id=detalle_id,
            entrada_id=entrada_id
        )

        return jsonify({
            'success': True,
            'data': detalle.to_dict()
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


@detalle_ensayo_api_bp.route(
    '/<int:entrada_id>/ensayos/<int:detalle_id>/completar',
    methods=['POST']
)
@login_required
def completar_ensayo(entrada_id, detalle_id):
    """Marcar un ensayo como completado (EN_PROCESO → COMPLETADO).

    Body JSON:
        observaciones (str, opcional): Observaciones finales del ensayo.

    Args:
        entrada_id: ID de la entrada asociada.
        detalle_id: ID del detalle a actualizar.

    Returns:
        JSON con el detalle actualizado.
    """
    try:
        from app.services.detalle_ensayo_service import DetalleEnsayoService

        data = request.get_json() or {}
        observaciones = data.get('observaciones')

        detalle = DetalleEnsayoService.completar_ensayo(
            detalle_id=detalle_id,
            entrada_id=entrada_id,
            observaciones=observaciones
        )

        return jsonify({
            'success': True,
            'data': detalle.to_dict()
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


@detalle_ensayo_api_bp.route(
    '/<int:entrada_id>/ensayos/<int:detalle_id>/reportar',
    methods=['POST']
)
@login_required
def reportar_ensayo(entrada_id, detalle_id):
    """Registrar el reporte de un ensayo completado (COMPLETADO → REPORTADO).

    Args:
        entrada_id: ID de la entrada asociada.
        detalle_id: ID del detalle a actualizar.

    Returns:
        JSON con el detalle actualizado.
    """
    try:
        from app.services.detalle_ensayo_service import DetalleEnsayoService

        detalle = DetalleEnsayoService.reportar_ensayo(
            detalle_id=detalle_id,
            entrada_id=entrada_id
        )

        return jsonify({
            'success': True,
            'data': detalle.to_dict()
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
