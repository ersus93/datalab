"""Rutas para el dashboard de técnicos y ejecución de ensayos (Issue #32)."""
from datetime import datetime
from flask import Blueprint, render_template, jsonify, request, abort
from flask_login import current_user, login_required
from sqlalchemy import func

from app import db
from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus
from app.database.models.ensayo import Ensayo
from app.database.models.reference import Area

tecnico_bp = Blueprint('tecnico', __name__, url_prefix='/tecnico')


# ----------------------------------------------------------------------
# Dashboard del Técnico
# ----------------------------------------------------------------------

@tecnico_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard del técnico con estadísticas y ensayos pendientes."""
    # Obtener todos los detalles en estado ASIGNADO o EN_PROCESO para el técnico actual
    detalles_asignados = DetalleEnsayo.query.filter(
        DetalleEnsayo.tecnico_asignado_id == current_user.id
    ).all()

    # Calcular estadísticas
    stats = {
        'asignado': 0,
        'en_proceso': 0,
        'completado_hoy': 0,
        'reportado': 0,
    }

    hoy = datetime.utcnow().date()
    for d in detalles_asignados:
        if d.estado == DetalleEnsayoStatus.ASIGNADO.value:
            stats['asignado'] += 1
        elif d.estado == DetalleEnsayoStatus.EN_PROCESO.value:
            stats['en_proceso'] += 1
        elif d.estado == DetalleEnsayoStatus.COMPLETADO.value:
            if d.fecha_completado and d.fecha_completado.date() == hoy:
                stats['completado_hoy'] += 1
        elif d.estado == DetalleEnsayoStatus.REPORTADO.value:
            stats['reportado'] += 1

    # Obtener ensayos pendientes de ejecución (ASIGNADO o EN_PROCESO)
    detalles_pendientes = (
        DetalleEnsayo.query
        .join(Ensayo)
        .join(Area)
        .filter(
            DetalleEnsayo.tecnico_asignado_id == current_user.id,
            DetalleEnsayo.estado.in_([
                DetalleEnsayoStatus.ASIGNADO.value,
                DetalleEnsayoStatus.EN_PROCESO.value
            ])
        )
        .order_by(Area.nombre, Ensayo.nombre_corto)
        .all()
    )

    # Agrupar por área
    pendientes_por_area = {}
    for detalle in detalles_pendientes:
        area_nombre = detalle.ensayo.area.nombre if detalle.ensayo.area else 'Sin Área'
        if area_nombre not in pendientes_por_area:
            pendientes_por_area[area_nombre] = []
        pendientes_por_area[area_nombre].append(detalle)

    # Obtener áreas para filtro
    areas = Area.query.order_by(Area.sigla).all()

    return render_template(
        'tecnico/dashboard.html',
        stats=stats,
        pendientes_por_area=pendientes_por_area,
        areas=areas,
        detalles_pendientes=detalles_pendientes,
    )


@tecnico_bp.route('/api/stats')
@login_required
def api_stats():
    """API para obtener estadísticas del técnico."""
    detalles = DetalleEnsayo.query.filter(
        DetalleEnsayo.tecnico_asignado_id == current_user.id
    ).all()

    stats = {
        'total': len(detalles),
        'asignado': sum(1 for d in detalles if d.estado == DetalleEnsayoStatus.ASIGNADO.value),
        'en_proceso': sum(1 for d in detalles if d.estado == DetalleEnsayoStatus.EN_PROCESO.value),
        'completado': sum(1 for d in detalles if d.estado == DetalleEnsayoStatus.COMPLETADO.value),
        'reportado': sum(1 for d in detalles if d.estado == DetalleEnsayoStatus.REPORTADO.value),
    }

    return jsonify(stats)


# ----------------------------------------------------------------------
# Ejecución de Ensayos
# ----------------------------------------------------------------------

@tecnico_bp.route('/ejecutar/<int:detalle_id>')
@login_required
def ejecutar_form(detalle_id):
    """Formulario para ejecutar un ensayo y registrar resultados."""
    detalle = DetalleEnsayo.query.get_or_404(detalle_id)

    # Verificar que el técnico tiene asignado este ensayo
    if detalle.tecnico_asignado_id != current_user.id:
        abort(403)

    # Solo permitir iniciar si está en estado ASIGNADO
    if detalle.estado != DetalleEnsayoStatus.ASIGNADO.value:
        abort(400)

    return render_template(
        'tecnico/ejecutar.html',
        detalle=detalle,
    )


@tecnico_bp.route('/api/ejecutar/<int:detalle_id>', methods=['POST'])
@login_required
def api_ejecutar(detalle_id):
    """API para iniciar la ejecución de un ensayo."""
    from app.services.detalle_ensayo_service import DetalleEnsayoService

    try:
        detalle = DetalleEnsayoService.iniciar_ensayo(
            detalle_id=detalle_id,
            usuario_id=current_user.id
        )
        return jsonify({
            'success': True,
            'data': detalle.to_dict(),
            'message': 'Ensayo iniciado correctamente'
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@tecnico_bp.route('/api/resultado/<int:detalle_id>', methods=['POST'])
@login_required
def api_registrar_resultado(detalle_id):
    """API para registrar el resultado de un ensayo."""
    from app.services.detalle_ensayo_service import DetalleEnsayoService

    data = request.get_json() or {}
    resultado = data.get('resultado')
    observaciones = data.get('observaciones')

    if not resultado:
        return jsonify({
            'success': False,
            'error': 'El resultado es obligatorio'
        }), 400

    try:
        # Completar el ensayo con el resultado
        detalle = DetalleEnsayoService.completar_ensayo(
            detalle_id=detalle_id,
            observaciones=observaciones,
            usuario_id=current_user.id
        )

        # Guardar el resultado en el campo observaciones (o crear campo dedicado si existe)
        detalle.resultado = resultado
        db.session.commit()

        return jsonify({
            'success': True,
            'data': detalle.to_dict(),
            'message': 'Resultado registrado correctamente'
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ----------------------------------------------------------------------
# Vista de Historial
# ----------------------------------------------------------------------

@tecnico_bp.route('/historial')
@login_required
def historial():
    """Historial de ensayos completados por el técnico."""
    # Obtener parámetros de filtro
    area_id = request.args.get('area_id', type=int)
    estado = request.args.get('estado')
    busqueda = request.args.get('q', '').strip()

    # Query base
    query = (
        DetalleEnsayo.query
        .join(Ensayo)
        .join(Area)
        .filter(DetalleEnsayo.tecnico_asignado_id == current_user.id)
    )

    # Aplicar filtros
    if area_id:
        query = query.filter(Area.id == area_id)

    if estado:
        query = query.filter(DetalleEnsayo.estado == estado)

    if busqueda:
        query = query.filter(Ensayo.nombre_corto.ilike(f'%{busqueda}%'))

    # Ordenar por fecha de completado descendente
    detalles = query.order_by(DetalleEnsayo.fecha_completado.desc()).all()

    # Obtener áreas para el filtro
    areas = Area.query.order_by(Area.sigla).all()

    return render_template(
        'tecnico/historial.html',
        detalles=detalles,
        areas=areas,
        filtros={'area_id': area_id, 'estado': estado, 'q': busqueda}
    )


# ----------------------------------------------------------------------
# Operaciones por Lote
# ----------------------------------------------------------------------

@tecnico_bp.route('/api/batch/iniciar', methods=['POST'])
@login_required
def api_batch_iniciar():
    """Iniciar múltiples ensayos simultáneamente."""
    from app.services.detalle_ensayo_service import DetalleEnsayoService

    data = request.get_json() or {}
    detalle_ids = data.get('detalle_ids', [])

    if not detalle_ids:
        return jsonify({
            'success': False,
            'error': 'Se requiere una lista de IDs de ensayos'
        }), 400

    resultados = []
    errores = []

    for detalle_id in detalle_ids:
        try:
            detalle = DetalleEnsayoService.iniciar_ensayo(
                detalle_id=detalle_id,
                usuario_id=current_user.id
            )
            resultados.append({'id': detalle_id, 'success': True})
        except ValueError as e:
            errores.append({'id': detalle_id, 'error': str(e)})

    return jsonify({
        'success': True,
        'data': {
            'iniciados': resultados,
            'errores': errores
        },
        'message': f'{len(resultados)} ensayos iniciados'
    })


@tecnico_bp.route('/api/batch/completar', methods=['POST'])
@login_required
def api_batch_completar():
    """Completar múltiples ensayos simultáneamente."""
    from app.services.detalle_ensayo_service import DetalleEnsayoService

    data = request.get_json() or {}
    detalle_ids = data.get('detalle_ids', [])
    observaciones = data.get('observaciones', '')

    if not detalle_ids:
        return jsonify({
            'success': False,
            'error': 'Se requiere una lista de IDs de ensayos'
        }), 400

    resultados = []
    errores = []

    for detalle_id in detalle_ids:
        try:
            detalle = DetalleEnsayoService.completar_ensayo(
                detalle_id=detalle_id,
                observaciones=observaciones,
                usuario_id=current_user.id
            )
            resultados.append({'id': detalle_id, 'success': True})
        except ValueError as e:
            errores.append({'id': detalle_id, 'error': str(e)})

    return jsonify({
        'success': True,
        'data': {
            'completados': resultados,
            'errores': errores
        },
        'message': f'{len(resultados)} ensayos completados'
    })