"""Blueprint de rutas para gestión de Informes (CRUD + workflow + PDF)."""
import logging
from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, abort
from flask_login import login_required, current_user
from io import BytesIO

from app import db
from app.database.models import Informe, InformeStatus, TipoInforme, MedioEntrega, InformeEnsayo
from app.database.models import Entrada, Cliente, DetalleEnsayo
from app.services import informe_service
from app.services.pdf_service import PDFService

logger = logging.getLogger(__name__)
informes_bp = Blueprint('informes', __name__, url_prefix='/informes')
_pdf_svc = PDFService()


# ─── LIST ───────────────────────────────────────────────────────────────────

@informes_bp.route('/')
@login_required
def listar():
    """Lista todos los informes con filtros opcionales."""
    estado = request.args.get('estado')
    tipo = request.args.get('tipo')
    cliente_id = request.args.get('cliente_id', type=int)
    page = request.args.get('page', 1, type=int)

    query = Informe.query.filter(Informe.anulado == False)

    if estado:
        query = query.filter(Informe.estado == estado)
    if tipo:
        query = query.filter(Informe.tipo_informe == tipo)
    if cliente_id:
        query = query.filter(Informe.cliente_id == cliente_id)

    query = query.order_by(Informe.created_at.desc())
    informes = query.paginate(page=page, per_page=20, error_out=False)

    clientes = Cliente.query.order_by(Cliente.nombre).all()
    estados = [e.value for e in InformeStatus]
    tipos = [t.value for t in TipoInforme]

    return render_template(
        'informes/listar.html',
        informes=informes,
        clientes=clientes,
        estados=estados,
        tipos=tipos,
        filtro_estado=estado,
        filtro_tipo=tipo,
        filtro_cliente=cliente_id,
    )


# ─── DETAIL ─────────────────────────────────────────────────────────────────

@informes_bp.route('/<int:id>')
@login_required
def ver(id):
    """Detalle completo de un informe con historial."""
    informe = Informe.query.get_or_404(id)
    transiciones = Informe.get_valid_transitions(
        informe.estado.value if hasattr(informe.estado, 'value') else informe.estado
    )
    return render_template(
        'informes/ver.html',
        informe=informe,
        transiciones=transiciones,
    )


# ─── CREATE ─────────────────────────────────────────────────────────────────

@informes_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def crear():
    """Crea un nuevo informe en estado BORRADOR."""
    if request.method == 'POST':
        try:
            entrada_id = request.form.get('entrada_id', type=int)
            cliente_id = request.form.get('cliente_id', type=int)
            tipo_informe = request.form.get('tipo_informe')
            medio_entrega = request.form.get('medio_entrega', 'FISICO')
            resumen_resultados = request.form.get('resumen_resultados', '')
            conclusiones = request.form.get('conclusiones', '')
            observaciones = request.form.get('observaciones', '')
            recomendaciones = request.form.get('recomendaciones', '')
            ensayos_ids = request.form.getlist('ensayos_ids', type=int)

            if not entrada_id or not cliente_id or not tipo_informe:
                flash('Entrada, Cliente y Tipo de Informe son obligatorios.', 'danger')
                return _render_form_create()

            # Generar número oficial
            nro_oficial = informe_service.generar_nro_oficial(tipo_informe)

            informe = Informe(
                nro_oficial=nro_oficial,
                tipo_informe=TipoInforme(tipo_informe),
                entrada_id=entrada_id,
                cliente_id=cliente_id,
                estado=InformeStatus.BORRADOR,
                medio_entrega=MedioEntrega(medio_entrega),
                resumen_resultados=resumen_resultados,
                conclusiones=conclusiones,
                observaciones=observaciones,
                recomendaciones=recomendaciones,
                emitido_por_id=current_user.id,
                numero_paginas=1,
                copias_entregadas=1,
            )

            db.session.add(informe)
            db.session.flush()  # obtener id

            # Vincular ensayos
            if ensayos_ids:
                if not informe_service.validar_ensayos_pertenecen_misma_entrada(informe, ensayos_ids):
                    db.session.rollback()
                    flash('Los ensayos seleccionados no son válidos para esta entrada.', 'danger')
                    return _render_form_create()
                for eid in ensayos_ids:
                    db.session.add(InformeEnsayo(informe_id=informe.id, detalle_ensayo_id=eid))

            db.session.commit()
            flash(f'Informe {nro_oficial} creado exitosamente.', 'success')
            return redirect(url_for('informes.ver', id=informe.id))

        except Exception as e:
            db.session.rollback()
            logger.error(f'Error creando informe: {e}')
            flash(f'Error al crear el informe: {str(e)}', 'danger')

    return _render_form_create()


def _render_form_create():
    entradas = Entrada.query.filter(
        Entrada.anulado == False
    ).order_by(Entrada.created_at.desc()).limit(100).all()
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    tipos = [(t.value, t.value.replace('_', ' ').title()) for t in TipoInforme]
    medios = [(m.value, m.value.replace('_', ' ').title()) for m in MedioEntrega]
    return render_template(
        'informes/form.html',
        entradas=entradas,
        clientes=clientes,
        tipos=tipos,
        medios=medios,
        informe=None,
    )


# ─── EDIT ───────────────────────────────────────────────────────────────────

@informes_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edita un informe en estado BORRADOR."""
    informe = Informe.query.get_or_404(id)
    estado_val = informe.estado.value if hasattr(informe.estado, 'value') else informe.estado
    if estado_val != InformeStatus.BORRADOR.value:
        flash('Solo se pueden editar informes en estado BORRADOR.', 'warning')
        return redirect(url_for('informes.ver', id=id))

    if request.method == 'POST':
        try:
            informe.resumen_resultados = request.form.get('resumen_resultados', '')
            informe.conclusiones = request.form.get('conclusiones', '')
            informe.observaciones = request.form.get('observaciones', '')
            informe.recomendaciones = request.form.get('recomendaciones', '')
            informe.medio_entrega = MedioEntrega(request.form.get('medio_entrega', 'FISICO'))
            informe.numero_paginas = request.form.get('numero_paginas', 1, type=int)
            informe.copias_entregadas = request.form.get('copias_entregadas', 1, type=int)

            # Actualizar ensayos
            nuevos_ids = request.form.getlist('ensayos_ids', type=int)
            if nuevos_ids:
                if not informe_service.validar_ensayos_pertenecen_misma_entrada(informe, nuevos_ids):
                    flash('Los ensayos seleccionados no son válidos.', 'danger')
                    return redirect(url_for('informes.editar', id=id))
                # Eliminar vínculos anteriores
                InformeEnsayo.query.filter_by(informe_id=informe.id).delete()
                for eid in nuevos_ids:
                    db.session.add(InformeEnsayo(informe_id=informe.id, detalle_ensayo_id=eid))

            db.session.commit()
            flash('Informe actualizado correctamente.', 'success')
            return redirect(url_for('informes.ver', id=id))
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error editando informe {id}: {e}')
            flash(f'Error al actualizar: {str(e)}', 'danger')

    ensayos_entrada = DetalleEnsayo.query.filter_by(entrada_id=informe.entrada_id).all() if informe.entrada_id else []
    ensayos_vinculados = {ie.detalle_ensayo_id for ie in InformeEnsayo.query.filter_by(informe_id=id).all()}
    medios = [(m.value, m.value.replace('_', ' ').title()) for m in MedioEntrega]
    return render_template(
        'informes/form.html',
        informe=informe,
        ensayos_entrada=ensayos_entrada,
        ensayos_vinculados=ensayos_vinculados,
        medios=medios,
        entradas=None,
        clientes=None,
        tipos=None,
    )


# ─── ESTADO WORKFLOW ────────────────────────────────────────────────────────

@informes_bp.route('/<int:id>/estado', methods=['POST'])
@login_required
def cambiar_estado(id):
    """Cambia el estado de un informe validando la máquina de estados."""
    informe = Informe.query.get_or_404(id)
    nuevo_estado_str = request.form.get('nuevo_estado')
    motivo = request.form.get('motivo', '')

    if not nuevo_estado_str:
        flash('Debe especificar el nuevo estado.', 'danger')
        return redirect(url_for('informes.ver', id=id))

    try:
        nuevo_estado = InformeStatus(nuevo_estado_str)
    except ValueError:
        flash(f'Estado inválido: {nuevo_estado_str}', 'danger')
        return redirect(url_for('informes.ver', id=id))

    exito = informe_service.cambiar_estado(informe, nuevo_estado, current_user, motivo)
    if exito:
        flash(f'Estado cambiado a {nuevo_estado_str} exitosamente.', 'success')
    else:
        flash('No se pudo cambiar el estado. Verifique permisos y transición válida.', 'danger')

    return redirect(url_for('informes.ver', id=id))


# ─── PDF ENDPOINTS ──────────────────────────────────────────────────────────

@informes_bp.route('/<int:id>/pdf')
@login_required
def descargar_pdf(id):
    """Genera y descarga el PDF oficial del informe."""
    informe = Informe.query.get_or_404(id)
    estado_val = informe.estado.value if hasattr(informe.estado, 'value') else informe.estado
    # Preview si no está emitido aún
    es_preview = estado_val not in (InformeStatus.EMITIDO.value, InformeStatus.ENTREGADO.value)

    try:
        pdf_bytes = _pdf_svc.generar_informe(id, preview=es_preview)
        filename = f"{informe.nro_oficial}.pdf"
        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        logger.error(f'Error generando PDF del informe {id}: {e}')
        flash(f'Error al generar el PDF: {str(e)}', 'danger')
        return redirect(url_for('informes.ver', id=id))


@informes_bp.route('/<int:id>/pdf/preview')
@login_required
def preview_pdf(id):
    """Genera el PDF con marca de agua BORRADOR para previsualización."""
    try:
        pdf_bytes = _pdf_svc.generar_informe(id, preview=True)
        return send_file(
            BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=False,
            download_name=f"preview_{id}.pdf",
        )
    except Exception as e:
        logger.error(f'Error generando preview PDF informe {id}: {e}')
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('informes.ver', id=id))


# ─── API JSON ────────────────────────────────────────────────────────────────

@informes_bp.route('/api/por-entrada/<int:entrada_id>')
@login_required
def api_por_entrada(entrada_id):
    """Retorna los informes de una entrada en JSON (para uso en forms)."""
    from flask import jsonify
    informes = Informe.query.filter_by(entrada_id=entrada_id).all()
    return jsonify([{'id': i.id, 'nro_oficial': i.nro_oficial, 'estado': str(i.estado)} for i in informes])


@informes_bp.route('/api/ensayos-entrada/<int:entrada_id>')
@login_required
def api_ensayos_entrada(entrada_id):
    """Retorna los detalles de ensayo de una entrada para vincularlos al informe."""
    from flask import jsonify
    detalles = DetalleEnsayo.query.filter_by(entrada_id=entrada_id).all()
    return jsonify([{
        'id': d.id,
        'ensayo': d.ensayo.nombre_corto if d.ensayo else '—',
        'estado': str(d.estado),
    } for d in detalles])
