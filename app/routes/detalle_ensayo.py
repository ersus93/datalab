"""Rutas web para la interfaz de asignación de ensayos a entradas."""
from flask import Blueprint, render_template, abort
from flask_login import login_required

detalle_ensayo_bp = Blueprint('detalle_ensayo', __name__, url_prefix='/entradas')


@detalle_ensayo_bp.route('/<int:entrada_id>/ensayos', methods=['GET'])
@login_required
def asignacion(entrada_id):
    """Mostrar la interfaz de asignación de ensayos para una entrada.

    Carga la entrada, los detalles de ensayo agrupados por área, el catálogo
    de ensayos activos (también agrupados por área) y la lista de técnicos
    disponibles para asignación.

    Args:
        entrada_id: ID de la entrada cuyo panel de ensayos se mostrará.

    Returns:
        Renderizado de `entradas/ensayos/asignacion.html` con contexto completo.
    """
    # Importaciones lazy para evitar importaciones circulares
    from app.database.models.entrada import Entrada
    from app.database.models.ensayo import Ensayo
    from app.database.models.reference import Area
    from app.database.models.user import User, UserRole
    from app.services.detalle_ensayo_service import DetalleEnsayoService

    # Verificar que la entrada existe (404 si no se encuentra)
    entrada = Entrada.query.get_or_404(entrada_id)

    # Detalles de ensayo ya asignados, agrupados por área
    detalles_agrupados = DetalleEnsayoService.get_detalles_agrupados_por_area(entrada_id)

    # Catálogo de ensayos activos agrupados por área para el selector
    areas = Area.query.order_by(Area.nombre).all()
    ensayos_por_area = []
    for area in areas:
        ensayos = Ensayo.query.filter_by(
            area_id=area.id, activo=True
        ).order_by(Ensayo.nombre_corto).all()
        if ensayos:
            ensayos_por_area.append({
                'area': area,
                'ensayos': ensayos,
            })

    # Técnicos disponibles: TECHNICIAN y LABORATORY_MANAGER activos
    tecnicos = User.query.filter(
        User.activo == True,
        User.role.in_([UserRole.TECHNICIAN, UserRole.LABORATORY_MANAGER])
    ).order_by(User.nombre_completo).all()

    return render_template(
        'entradas/ensayos/asignacion.html',
        entrada=entrada,
        detalles_agrupados=detalles_agrupados,
        ensayos_por_area=ensayos_por_area,
        tecnicos=tecnicos,
    )
