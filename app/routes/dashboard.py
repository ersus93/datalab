"""Rutas para dashboard principal."""
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, render_template
from flask_login import login_required

from app import db
from app.database.models import Cliente, Fabrica, Producto, Provincia, Rama

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
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
    })


@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard principal con resumen de datos maestros."""

    # Estadísticas principales
    stats = {
        'total_clientes': Cliente.query.filter_by(activo=True).count(),
        'total_fabricas': Fabrica.query.filter_by(activo=True).count(),
        'total_productos': Producto.query.filter_by(activo=True).count(),
        'total_provincias': Provincia.query.count(),
    }

    # Distribución por provincia (para gráfico)
    provincia_data = db.session.query(
        Provincia.nombre,
        Provincia.sigla,
        db.func.count(Fabrica.id).label('count')
    ).outerjoin(Fabrica).group_by(Provincia.id).all()

    # Top 10 clientes por cantidad de fábricas
    top_clientes = db.session.query(
        Cliente.id,
        Cliente.nombre,
        db.func.count(Fabrica.id).label('factory_count')
    ).join(Fabrica).group_by(Cliente.id).order_by(
        db.desc('factory_count')
    ).limit(10).all()

    # Distribución por sector (rama)
    sector_data = db.session.query(
        Rama.nombre,
        db.func.count(Producto.id).label('count')
    ).outerjoin(Producto).group_by(Rama.id).all()

    # Últimos registros agregados
    latest_clientes = Cliente.query.order_by(
        Cliente.fecha_creacion.desc()
    ).limit(5).all()

    latest_fabricas = Fabrica.query.order_by(
        Fabrica.creado_en.desc()
    ).limit(5).all()

    latest_productos = Producto.query.order_by(
        Producto.creado_en.desc()
    ).limit(5).all()

    return render_template('dashboard/index.html',
                           stats=stats,
                           provincia_data=provincia_data,
                           top_clientes=top_clientes,
                           sector_data=sector_data,
                           latest_clientes=latest_clientes,
                           latest_fabricas=latest_fabricas,
                           latest_productos=latest_productos)
