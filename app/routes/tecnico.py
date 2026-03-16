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
    from datetime import timedelta

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
        'pausado': 0,
    }

    hoy = datetime.utcnow().date()
    for d in detalles_asignados:
        if d.estado == DetalleEnsayoStatus.ASIGNADO.value:
            stats['asignado'] += 1
        elif d.estado == DetalleEnsayoStatus.EN_PROCESO.value:
            stats['en_proceso'] += 1
        elif d.estado == DetalleEnsayoStatus.PAUSADO.value:
            stats['pausado'] += 1
        elif d.estado == DetalleEnsayoStatus.COMPLETADO.value:
            if d.fecha_completado and d.fecha_completado.date() == hoy:
                stats['completado_hoy'] += 1
        elif d.estado == DetalleEnsayoStatus.REPORTADO.value:
            stats['reportado'] += 1

    # Obtener ensayos pendientes de ejecución (ASIGNADO, EN_PROCESO o PAUSADO)
    detalles_pendientes = (
        DetalleEnsayo.query
        .join(Ensayo)
        .join(Area)
        .filter(
            DetalleEnsayo.tecnico_asignado_id == current_user.id,
            DetalleEnsayo.estado.in_([
                DetalleEnsayoStatus.ASIGNADO.value,
                DetalleEnsayoStatus.EN_PROCESO.value,
                DetalleEnsayoStatus.PAUSADO.value
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

    # Obtener actividad reciente (últimos 10 completados)
    actividad_reciente = (
        DetalleEnsayo.query
        .filter(
            DetalleEnsayo.tecnico_asignado_id == current_user.id,
            DetalleEnsayo.estado.in_([
                DetalleEnsayoStatus.COMPLETADO.value,
                DetalleEnsayoStatus.REPORTADO.value
            ])
        )
        .order_by(DetalleEnsayo.fecha_completado.desc())
        .limit(10)
        .all()
    )

    # Obtener alertas de vencimiento (ASIGNADOS o EN_PROCESO con más de 3 días)
    fecha_limite = datetime.utcnow() - timedelta(days=3)
    alertas_vencimiento = (
        DetalleEnsayo.query
        .join(Ensayo)
        .filter(
            DetalleEnsayo.tecnico_asignado_id == current_user.id,
            DetalleEnsayo.estado.in_([
                DetalleEnsayoStatus.ASIGNADO.value,
                DetalleEnsayoStatus.EN_PROCESO.value
            ]),
            DetalleEnsayo.fecha_asignacion < fecha_limite
        )
        .order_by(DetalleEnsayo.fecha_asignacion)
        .all()
    )

    return render_template(
        'tecnico/dashboard.html',
        stats=stats,
        pendientes_por_area=pendientes_por_area,
        areas=areas,
        detalles_pendientes=detalles_pendientes,
        actividad_reciente=actividad_reciente,
        alertas_vencimiento=alertas_vencimiento,
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

    # Solo permitir ejecutar si está en estado ASIGNADO, EN_PROCESO o PAUSADO
    if detalle.estado not in [
        DetalleEnsayoStatus.ASIGNADO.value,
        DetalleEnsayoStatus.EN_PROCESO.value,
        DetalleEnsayoStatus.PAUSADO.value
    ]:
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


@tecnico_bp.route('/api/pausar/<int:detalle_id>', methods=['POST'])
@login_required
def api_pausar(detalle_id):
    """API para pausar un ensayo en proceso."""
    from app.services.detalle_ensayo_service import DetalleEnsayoService

    try:
        detalle = DetalleEnsayoService.pausar_ensayo(
            detalle_id=detalle_id,
            usuario_id=current_user.id
        )
        return jsonify({
            'success': True,
            'data': detalle.to_dict(),
            'message': 'Ensayo pausado correctamente'
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@tecnico_bp.route('/api/reanudar/<int:detalle_id>', methods=['POST'])
@login_required
def api_reanudar(detalle_id):
    """API para reanudar un ensayo pausado."""
    from app.services.detalle_ensayo_service import DetalleEnsayoService

    try:
        detalle = DetalleEnsayoService.reanudar_ensayo(
            detalle_id=detalle_id,
            usuario_id=current_user.id
        )
        return jsonify({
            'success': True,
            'data': detalle.to_dict(),
            'message': 'Ensayo reanudado correctamente'
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
    tipo_resultado = data.get('tipo_resultado', 'numerico')
    valor_numerico = data.get('valor_numerico')
    valor_texto = data.get('valor_texto')
    valor_booleano = data.get('valor_booleano')
    parametros_json = data.get('parametros_json')
    observaciones = data.get('observaciones')
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')

    try:
        # Completar el ensayo
        detalle = DetalleEnsayoService.completar_ensayo(
            detalle_id=detalle_id,
            observaciones=observaciones,
            usuario_id=current_user.id
        )

        # Guardar los valores del resultado
        if valor_numerico:
            try:
                detalle.valor_numerico = float(valor_numerico)
            except (ValueError, TypeError):
                pass

        if valor_texto:
            detalle.valor_texto = valor_texto

        if valor_booleano is not None:
            if valor_booleano == 'true' or valor_booleano is True:
                detalle.valor_booleano = True
            elif valor_booleano == 'false' or valor_booleano is False:
                detalle.valor_booleano = False

        if parametros_json:
            detalle.parametros_json = parametros_json

        # Validar si cumple especificaciones
        if detalle.ensayo and detalle.valor_numerico is not None:
            espec_min = detalle.ensayo.especificacion_min
            espec_max = detalle.ensayo.especificacion_max
            if espec_min is not None and espec_max is not None:
                try:
                    detalle.resultado_cumple = float(valor_numerico) >= float(espec_min) and float(valor_numerico) <= float(espec_max)
                except (ValueError, TypeError):
                    detalle.resultado_cumple = None
            elif espec_min is not None:
                detalle.resultado_cumple = float(valor_numerico) >= float(espec_min) if valor_numerico else None
            elif espec_max is not None:
                detalle.resultado_cumple = float(valor_numerico) <= float(espec_max) if valor_numerico else None

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


# ----------------------------------------------------------------------
# Métricas del Técnico
# ----------------------------------------------------------------------

@tecnico_bp.route('/metricas')
@login_required
def metricas():
    """Dashboard de métricas del técnico."""
    from datetime import timedelta

    ahora = datetime.utcnow()
    hoy = ahora.date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_mes = hoy.replace(day=1)

    # Tests completados hoy
    completados_hoy = DetalleEnsayo.query.filter(
        DetalleEnsayo.tecnico_asignado_id == current_user.id,
        DetalleEnsayo.estado == DetalleEnsayoStatus.COMPLETADO.value,
        func.date(DetalleEnsayo.fecha_completado) == hoy
    ).count()

    # Tests completados esta semana
    completados_semana = DetalleEnsayo.query.filter(
        DetalleEnsayo.tecnico_asignado_id == current_user.id,
        DetalleEnsayo.estado == DetalleEnsayoStatus.COMPLETADO.value,
        func.date(DetalleEnsayo.fecha_completado) >= inicio_semana
    ).count()

    # Tests completados este mes
    completados_mes = DetalleEnsayo.query.filter(
        DetalleEnsayo.tecnico_asignado_id == current_user.id,
        DetalleEnsayo.estado == DetalleEnsayoStatus.COMPLETADO.value,
        func.date(DetalleEnsayo.fecha_completado) >= inicio_mes
    ).count()

    # Tests por tipo (FQ, MB, ES)
    tests_por_tipo = {}
    for area_sigla in ['FQ', 'MB', 'ES']:
        area = Area.query.filter_by(sigla=area_sigla).first()
        if area:
            count = DetalleEnsayo.query.join(Ensayo).filter(
                DetalleEnsayo.tecnico_asignado_id == current_user.id,
                DetalleEnsayo.estado == DetalleEnsayoStatus.COMPLETADO.value,
                Ensayo.area_id == area.id
            ).count()
            tests_por_tipo[area_sigla] = count

    # Eficiencia: completados a tiempo / total completados
    # Consideramos "a tiempo" si se completaron en menos de 48 horas desde asignación
    eficiencia = 0
    total_completados = DetalleEnsayo.query.filter(
        DetalleEnsayo.tecnico_asignado_id == current_user.id,
        DetalleEnsayo.estado == DetalleEnsayoStatus.COMPLETADO.value,
        DetalleEnsayo.fecha_completado.isnot(None),
        DetalleEnsayo.fecha_asignacion.isnot(None)
    ).all()

    if total_completados:
        a_tiempo = sum(
            1 for d in total_completados
            if d.fecha_completado and d.fecha_asignacion
            and (d.fecha_completado - d.fecha_asignacion).total_seconds() < 48 * 3600
        )
        eficiencia = round((a_tiempo / len(total_completados)) * 100, 1)

    # Tendencia semanal (últimos 7 días)
    tendencia_semanal = []
    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        count = DetalleEnsayo.query.filter(
            DetalleEnsayo.tecnico_asignado_id == current_user.id,
            DetalleEnsayo.estado == DetalleEnsayoStatus.COMPLETADO.value,
            func.date(DetalleEnsayo.fecha_completado) == dia
        ).count()
        tendencia_semanal.append({
            'dia': dia.strftime('%a'),
            'fecha': dia.isoformat(),
            'count': count
        })

    # Tests en curso
    en_proceso = DetalleEnsayo.query.filter(
        DetalleEnsayo.tecnico_asignado_id == current_user.id,
        DetalleEnsayo.estado == DetalleEnsayoStatus.EN_PROCESO.value
    ).count()

    pausados = DetalleEnsayo.query.filter(
        DetalleEnsayo.tecnico_asignado_id == current_user.id,
        DetalleEnsayo.estado == DetalleEnsayoStatus.PAUSADO.value
    ).count()

    stats = {
        'completados_hoy': completados_hoy,
        'completados_semana': completados_semana,
        'completados_mes': completados_mes,
        'tests_por_tipo': tests_por_tipo,
        'eficiencia': eficiencia,
        'tendencia_semanal': tendencia_semanal,
        'en_proceso': en_proceso,
        'pausados': pausados,
        'total_completados': len(total_completados),
    }

    return render_template('tecnico/metricas.html', stats=stats)


@tecnico_bp.route('/api/metricas')
@login_required
def api_metricas():
    """API de métricas en JSON."""
    from datetime import timedelta

    ahora = datetime.utcnow()
    hoy = ahora.date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_mes = hoy.replace(day=1)

    # Completados por período
    completados_hoy = DetalleEnsayo.query.filter(
        DetalleEnsayo.tecnico_asignado_id == current_user.id,
        DetalleEnsayo.estado == DetalleEnsayoStatus.COMPLETADO.value,
        func.date(DetalleEnsayo.fecha_completado) == hoy
    ).count()

    completados_semana = DetalleEnsayo.query.filter(
        DetalleEnsayo.tecnico_asignado_id == current_user.id,
        DetalleEnsayo.estado == DetalleEnsayoStatus.COMPLETADO.value,
        func.date(DetalleEnsayo.fecha_completado) >= inicio_semana
    ).count()

    completados_mes = DetalleEnsayo.query.filter(
        DetalleEnsayo.tecnico_asignado_id == current_user.id,
        DetalleEnsayo.estado == DetalleEnsayoStatus.COMPLETADO.value,
        func.date(DetalleEnsayo.fecha_completado) >= inicio_mes
    ).count()

    # Tests por área
    tests_por_tipo = {}
    for area_sigla in ['FQ', 'MB', 'ES']:
        area = Area.query.filter_by(sigla=area_sigla).first()
        if area:
            count = DetalleEnsayo.query.join(Ensayo).filter(
                DetalleEnsayo.tecnico_asignado_id == current_user.id,
                DetalleEnsayo.estado == DetalleEnsayoStatus.COMPLETADO.value,
                Ensayo.area_id == area.id
            ).count()
            tests_por_tipo[area_sigla] = count

    # Tendencia semanal
    tendencia_semanal = []
    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        count = DetalleEnsayo.query.filter(
            DetalleEnsayo.tecnico_asignado_id == current_user.id,
            DetalleEnsayo.estado == DetalleEnsayoStatus.COMPLETADO.value,
            func.date(DetalleEnsayo.fecha_completado) == dia
        ).count()
        tendencia_semanal.append({
            'dia': dia.strftime('%a'),
            'fecha': dia.isoformat(),
            'count': count
        })

    return jsonify({
        'success': True,
        'data': {
            'completados_hoy': completados_hoy,
            'completados_semana': completados_semana,
            'completados_mes': completados_mes,
            'tests_por_tipo': tests_por_tipo,
            'tendencia_semanal': tendencia_semanal,
        }
    })