"""API endpoints para dashboard de DataLab."""
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from flask_login import login_required

from app import db
from app.services.dashboard_service import DashboardService

dashboard_api_bp = Blueprint('dashboard_api', __name__, url_prefix='/api/dashboard')


def _orden_trabajo_to_dict_mini(orden):
    """
    Convertir orden de trabajo a diccionario resumido.

    Args:
        orden: Instancia de OrdenTrabajo

    Returns:
        Dict con datos minimos de la orden
    """
    return {
        'id': orden.id,
        'nro_ofic': orden.nro_ofic,
        'cliente': orden.cliente.nombre if orden.cliente else None,
        'status': orden.status
    }


@dashboard_api_bp.route('/sample-status-counts', methods=['GET'])
@login_required
def sample_status_counts():
    """
    Obtener conteos de muestras por estado.

    Returns:
        JSON con conteos por estado, total y timestamp.
    """
    try:
        counts = DashboardService.get_sample_status_counts()
        total = sum(counts.values())

        return jsonify({
            'success': True,
            'data': {
                'status_counts': counts,
                'total': total,
                'last_updated': datetime.utcnow().isoformat()
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


@dashboard_api_bp.route('/status-trends', methods=['GET'])
@login_required
def status_trends():
    """
    Obtener tendencias de estados en el tiempo.

    Query params:
        days: Numero de dias a analizar (default: 30)

    Returns:
        JSON con tendencias diarias y configuracion.
    """
    try:
        days = request.args.get('days', 30, type=int)

        # Validar rango razonable
        if days < 1 or days > 365:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'El parametro days debe estar entre 1 y 365',
                    'details': {}
                }
            }), 400

        trends = DashboardService.get_status_trends(days=days)

        return jsonify({
            'success': True,
            'data': {
                'trends': trends,
                'days': days
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


@dashboard_api_bp.route('/recent-activity', methods=['GET'])
@login_required
def recent_activity():
    """
    Obtener actividad reciente de cambios de estado.

    Query params:
        limit: Cantidad maxima de registros (default: 10)

    Returns:
        JSON con lista de cambios de estado recientes.
    """
    try:
        limit = request.args.get('limit', 10, type=int)

        # Validar rango razonable
        if limit < 1 or limit > 100:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'El parametro limit debe estar entre 1 y 100',
                    'details': {}
                }
            }), 400

        activity = DashboardService.get_recent_activity(limit=limit)

        return jsonify({
            'success': True,
            'data': {
                'activity': activity,
                'limit': limit,
                'count': len(activity)
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


@dashboard_api_bp.route('/pending-deliveries', methods=['GET'])
@login_required
def pending_deliveries():
    """
    Obtener muestras pendientes de entrega.

    Retorna entradas con estado COMPLETADO y saldo > 0.

    Returns:
        JSON con lista de entregas pendientes.
    """
    try:
        pending = DashboardService.get_pending_deliveries()

        return jsonify({
            'success': True,
            'data': {
                'deliveries': pending,
                'count': len(pending)
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


@dashboard_api_bp.route('/full', methods=['GET'])
@login_required
def full_dashboard():
    """
    Obtener todos los datos del dashboard en una sola llamada.

    Combina todas las metricas individuales para el consumo del frontend.

    Returns:
        JSON con datos completos del dashboard.
    """
    try:
        data = DashboardService.get_full_dashboard_data()

        return jsonify({
            'success': True,
            'data': data
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


@dashboard_api_bp.route('/ordenes-trabajo/estadisticas', methods=['GET'])
@login_required
def ordenes_trabajo_estadisticas():
    """
    Obtener estadisticas de ordenes de trabajo para dashboard.

    Returns:
        JSON con estadisticas por status, totales, ordenes recientes
        y ordenes que requieren atencion.
    """
    from app.database.models.orden_trabajo import OrdenTrabajo, OTStatus
    from app.database.models.pedido import Pedido, PedidoStatus
    from app.services.orden_trabajo_service import OrdenTrabajoService

    try:
        # Obtener estadisticas base del servicio
        stats_servicio = OrdenTrabajoService.obtener_estadisticas()

        # Estadisticas por status
        por_status = {}
        for status in [OTStatus.PENDIENTE, OTStatus.EN_PROGRESO, OTStatus.COMPLETADA]:
            por_status[status] = OrdenTrabajo.query.filter_by(status=status).count()

        # Total de ordenes
        total_ordenes = OrdenTrabajo.query.filter(
            OrdenTrabajo.status != 'ELIMINADA'
        ).count()

        # Contar pedidos asociados a ordenes de trabajo
        total_pedidos_asociados = db.session.query(Pedido).filter(
            Pedido.orden_trabajo_id.isnot(None)
        ).count()

        # Completadas este mes
        hoy = datetime.utcnow()
        inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        completadas_este_mes = OrdenTrabajo.query.filter(
            OrdenTrabajo.status == OTStatus.COMPLETADA,
            OrdenTrabajo.fech_completado >= inicio_mes
        ).count()

        # Ordenes recientes (ultimas 5 creadas)
        recientes = OrdenTrabajo.query.filter(
            OrdenTrabajo.status != 'ELIMINADA'
        ).order_by(db.desc(OrdenTrabajo.fech_creacion)).limit(5).all()

        # Ordenes que requieren atencion
        # OTs EN_PROGRESO con pedidos antiguos (> 30 dias)
        fecha_limite = hoy - timedelta(days=30)

        # Buscar OTs EN_PROGRESO que tienen pedidos con fech_pedido > 30 dias
        ordenes_con_pedidos_antiguos = db.session.query(OrdenTrabajo).join(
            Pedido, OrdenTrabajo.id == Pedido.orden_trabajo_id
        ).filter(
            OrdenTrabajo.status == OTStatus.EN_PROGRESO,
            Pedido.fech_pedido < fecha_limite,
            Pedido.status != PedidoStatus.COMPLETADO
        ).distinct().all()

        requieren_atencion = []
        for orden in ordenes_con_pedidos_antiguos:
            requieren_atencion.append({
                'id': orden.id,
                'nro_ofic': orden.nro_ofic,
                'motivo': 'Pedidos pendientes > 30 dias'
            })

        return jsonify({
            'success': True,
            'data': {
                'por_status': por_status,
                'totales': {
                    'ordenes': total_ordenes,
                    'pedidos_asociados': total_pedidos_asociados,
                    'completadas_este_mes': completadas_este_mes
                },
                'recientes': [_orden_trabajo_to_dict_mini(o) for o in recientes],
                'requieren_atencion': requieren_atencion
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
