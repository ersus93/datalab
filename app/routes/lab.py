"""Rutas para vistas por área de laboratorio (FQ, MB, ES, OS)."""
from flask import Blueprint, render_template, abort
from flask_login import login_required

lab_bp = Blueprint('lab', __name__, url_prefix='/lab')


# ----------------------------------------------------------------------
# Rutas principales
# ----------------------------------------------------------------------

@lab_bp.route('/')
@login_required
def index():
    """Página principal del laboratorio con tabs para cada área."""
    from app.database.models.reference import Area

    areas = Area.query.order_by(Area.sigla).all()
    return render_template('lab/index.html', areas=areas)


@lab_bp.route('/<string:area_sigla>/')
@login_required
def area_view(area_sigla):
    """Vista específica para un área de laboratorio.

    Args:
        area_sigla: Sigla del área (FQ, MB, ES, OS).
    """
    from app.database.models.reference import Area

    # Mapear siglas a nombres completos
    area_map = {
        'FQ': {'nombre': 'Físico-Químico', 'sigla': 'FQ', 'color': 'blue', 'icon': 'fa-flask'},
        'MB': {'nombre': 'Microbiología', 'sigla': 'MB', 'color': 'green', 'icon': 'fa-bacteria'},
        'ES': {'nombre': 'Evaluación Sensorial', 'sigla': 'ES', 'color': 'purple', 'icon': 'fa-wine-glass'},
        'OS': {'nombre': 'Otros Servicios', 'sigla': 'OS', 'color': 'orange', 'icon': 'fa-tools'},
    }

    area_info = area_map.get(area_sigla.upper())
    if not area_info:
        abort(404)

    # Obtener el área de la base de datos
    area = Area.query.filter_by(sigla=area_sigla.upper()).first()

    # Obtener ensayos del área
    from app.database.models.ensayo import Ensayo
    ensayos = []
    if area:
        ensayos = Ensayo.query.filter_by(area_id=area.id, activo=True).order_by(Ensayo.nombre_corto).all()

    # Obtener estadísticas de la entrada
    from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus

    stats = {
        'pendiente': 0,
        'asignado': 0,
        'en_proceso': 0,
        'completado': 0,
        'reportado': 0,
    }

    if area:
        # Contar detalles por estado para esta área
        detalles = DetalleEnsayo.query.join(Ensayo).filter(Ensayo.area_id == area.id).all()
        for d in detalles:
            if d.estado == DetalleEnsayoStatus.PENDIENTE.value:
                stats['pendiente'] += 1
            elif d.estado == DetalleEnsayoStatus.ASIGNADO.value:
                stats['asignado'] += 1
            elif d.estado == DetalleEnsayoStatus.EN_PROCESO.value:
                stats['en_proceso'] += 1
            elif d.estado == DetalleEnsayoStatus.COMPLETADO.value:
                stats['completado'] += 1
            elif d.estado == DetalleEnsayoStatus.REPORTADO.value:
                stats['reportado'] += 1

    return render_template(
        'lab/area.html',
        area_info=area_info,
        area=area,
        ensayos=ensayos,
        stats=stats,
    )


# ----------------------------------------------------------------------
# API endpoints para el laboratorio
# ----------------------------------------------------------------------

@lab_bp.route('/api/<string:area_sigla>/stats')
@login_required
def area_stats(area_sigla):
    """API para obtener estadísticas de un área."""
    from flask import jsonify
    from app.database.models.reference import Area
    from app.database.models.ensayo import Ensayo
    from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus

    area = Area.query.filter_by(sigla=area_sigla.upper()).first()
    if not area:
        return jsonify({'error': 'Área no encontrada'}), 404

    # Contar ensayos activos del área
    total_ensayos = Ensayo.query.filter_by(area_id=area.id, activo=True).count()

    # Contar detalles por estado
    detalles = DetalleEnsayo.query.join(Ensayo).filter(Ensayo.area_id == area.id).all()

    stats = {
        'area': area_sigla.upper(),
        'total_ensayos': total_ensayos,
        'pendiente': sum(1 for d in detalles if d.estado == DetalleEnsayoStatus.PENDIENTE.value),
        'asignado': sum(1 for d in detalles if d.estado == DetalleEnsayoStatus.ASIGNADO.value),
        'en_proceso': sum(1 for d in detalles if d.estado == DetalleEnsayoStatus.EN_PROCESO.value),
        'completado': sum(1 for d in detalles if d.estado == DetalleEnsayoStatus.COMPLETADO.value),
        'reportado': sum(1 for d in detalles if d.estado == DetalleEnsayoStatus.REPORTADO.value),
    }

    return jsonify(stats)