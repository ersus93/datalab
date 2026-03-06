"""Rutas CRUD para entradas de muestras."""
from datetime import date, timedelta
from decimal import Decimal

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_babel import _

from app import db
from app.database.models import Cliente, Fabrica, Producto, Pedido
from app.database.models.entrada import Entrada, EntradaStatus
from app.decorators import technician_required
from app.forms.entrada import EntradaForm

entradas_bp = Blueprint('entradas', __name__, url_prefix='/entradas')


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _date_context():
    """Devuelve variables de fecha usadas por list_mejorado.html."""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end   = week_start + timedelta(days=6)
    month_start = today.replace(day=1)
    return dict(
        today=today.isoformat(),
        week_start=week_start.isoformat(),
        week_end=week_end.isoformat(),
        month_start=month_start.isoformat(),
    )


# ---------------------------------------------------------------------------
# List / index
# ---------------------------------------------------------------------------

@entradas_bp.route('/')
@login_required
def listar():
    """Listar entradas con filtros avanzados."""
    page       = request.args.get('page',    1,    type=int)
    cliente_id = request.args.get('cliente', type=int)
    producto_id = request.args.get('producto', type=int)
    status      = request.args.get('status')
    desde       = request.args.get('desde')
    hasta       = request.args.get('hasta')
    q           = request.args.get('q', '')

    query = Entrada.query.filter_by(anulado=False)

    if cliente_id:
        query = query.filter_by(cliente_id=cliente_id)
    if producto_id:
        query = query.filter_by(producto_id=producto_id)
    if status:
        query = query.filter_by(status=status)
    if desde:
        query = query.filter(Entrada.fech_entrada >= desde)
    if hasta:
        query = query.filter(Entrada.fech_entrada <= hasta)
    if q:
        query = query.filter(
            db.or_(
                Entrada.codigo.ilike(f'%{q}%'),
                Entrada.lote.ilike(f'%{q}%'),
            )
        )

    entradas = query.order_by(Entrada.fech_entrada.desc()).paginate(
        page=page, per_page=25, error_out=False
    )

    clientes  = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    productos = Producto.query.filter_by(activo=True).order_by(Producto.nombre).all()

    return render_template(
        'entradas/list_mejorado.html',
        entradas=entradas,
        clientes=clientes,
        productos=productos,
        q=q,
        **_date_context(),
    )


# ---------------------------------------------------------------------------
# Detail
# ---------------------------------------------------------------------------

@entradas_bp.route('/<int:id>')
@login_required
def ver(id):
    """Ver detalle de entrada."""
    entrada = Entrada.query.get_or_404(id)
    return render_template('entradas/ver.html', entrada=entrada)


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

@entradas_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
@technician_required
def nueva():
    """Crear nueva entrada."""
    form = EntradaForm()

    if form.validate_on_submit():
        entrada = Entrada(
            codigo=form.codigo.data,
            lote=form.lote.data or None,
            nro_parte=form.nro_parte.data or None,
            fech_entrada=form.fech_entrada.data or date.today(),
            producto_id=form.producto_id.data,
            fabrica_id=form.fabrica_id.data,
            cliente_id=form.cliente_id.data,
            rama_id=form.rama_id.data     if form.rama_id.data    and form.rama_id.data    > 0 else None,
            pedido_id=form.pedido_id.data if form.pedido_id.data  and form.pedido_id.data  > 0 else None,
            cantidad_recib=form.cantidad_recib.data,
            cantidad_entreg=Decimal('0'),
            cantidad_muest=form.cantidad_muest.data or None,
            unidad_medida_id=form.unidad_medida_id.data if form.unidad_medida_id.data and form.unidad_medida_id.data > 0 else None,
            fech_fab=form.fech_fab.data,
            fech_venc=form.fech_venc.data,
            fech_muestreo=form.fech_muestreo.data,
            observaciones=form.observaciones.data or '',
            en_os=form.en_os.data,
            status=EntradaStatus.RECIBIDO,
        )

        db.session.add(entrada)
        db.session.commit()

        flash(_('Entrada creada exitosamente.'), 'success')
        return redirect(url_for('entradas.ver', id=entrada.id))

    # Pre-poblar fecha entrada con hoy para la UI
    if not form.fech_entrada.data:
        form.fech_entrada.data = date.today()

    return render_template(
        'entradas/form_mejorado.html',
        form=form,
        entrada=None,
        titulo=_('Nueva Entrada'),
        today=date.today().isoformat(),
    )


# ---------------------------------------------------------------------------
# Edit
# ---------------------------------------------------------------------------

@entradas_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@technician_required
def editar(id):
    """Editar entrada existente."""
    entrada = Entrada.query.get_or_404(id)

    if entrada.anulado:
        flash(_('No se puede editar una entrada anulada.'), 'error')
        return redirect(url_for('entradas.ver', id=id))

    form = EntradaForm(obj=entrada)

    if form.validate_on_submit():
        entrada.codigo          = form.codigo.data
        entrada.lote            = form.lote.data or None
        entrada.nro_parte       = form.nro_parte.data or None
        entrada.fech_entrada    = form.fech_entrada.data or entrada.fech_entrada
        entrada.producto_id     = form.producto_id.data
        entrada.fabrica_id      = form.fabrica_id.data
        entrada.cliente_id      = form.cliente_id.data
        entrada.rama_id         = form.rama_id.data    if form.rama_id.data    and form.rama_id.data    > 0 else None
        entrada.pedido_id       = form.pedido_id.data  if form.pedido_id.data  and form.pedido_id.data  > 0 else None
        entrada.cantidad_recib  = form.cantidad_recib.data
        entrada.cantidad_muest  = form.cantidad_muest.data or None
        entrada.unidad_medida_id = form.unidad_medida_id.data if form.unidad_medida_id.data and form.unidad_medida_id.data > 0 else None
        entrada.fech_fab        = form.fech_fab.data
        entrada.fech_venc       = form.fech_venc.data
        entrada.fech_muestreo   = form.fech_muestreo.data
        entrada.observaciones   = form.observaciones.data or ''
        entrada.en_os           = form.en_os.data
        # Recalcular saldo después de cambios en cantidad_recib
        entrada.calcular_saldo()

        db.session.commit()

        flash(_('Entrada actualizada exitosamente.'), 'success')
        return redirect(url_for('entradas.ver', id=entrada.id))

    return render_template(
        'entradas/form_mejorado.html',
        form=form,
        entrada=entrada,
        titulo=_('Editar Entrada'),
        today=date.today().isoformat(),
    )


# ---------------------------------------------------------------------------
# Status change
# ---------------------------------------------------------------------------

@entradas_bp.route('/<int:id>/cambiar-estado', methods=['POST'])
@login_required
@technician_required
def cambiar_estado(id):
    """Cambiar estado de la entrada."""
    entrada     = Entrada.query.get_or_404(id)
    nuevo_estado = request.form.get('status')

    transiciones_validas = {
        EntradaStatus.RECIBIDO:   [EntradaStatus.EN_PROCESO, EntradaStatus.ANULADO],
        EntradaStatus.EN_PROCESO: [EntradaStatus.COMPLETADO, EntradaStatus.ANULADO],
        EntradaStatus.COMPLETADO: [EntradaStatus.ENTREGADO],
    }

    if nuevo_estado not in transiciones_validas.get(entrada.status, []):
        flash(_('Transición de estado no válida.'), 'error')
        return redirect(url_for('entradas.ver', id=id))

    entrada.status = nuevo_estado

    if nuevo_estado == EntradaStatus.ANULADO:
        entrada.anulado = True
    elif nuevo_estado == EntradaStatus.ENTREGADO:
        entrada.ent_entregada = True

    db.session.commit()
    flash(_('Estado actualizado exitosamente.'), 'success')
    return redirect(url_for('entradas.ver', id=id))


# ---------------------------------------------------------------------------
# Delivery registration
# ---------------------------------------------------------------------------

@entradas_bp.route('/<int:id>/registrar-entrega', methods=['POST'])
@login_required
@technician_required
def registrar_entrega(id):
    """Registrar entrega de muestra."""
    entrada  = Entrada.query.get_or_404(id)
    cantidad = request.form.get('cantidad', type=float)

    if cantidad is None or cantidad <= 0:
        flash(_('Cantidad de entrega inválida.'), 'error')
        return redirect(url_for('entradas.ver', id=id))

    nueva_cantidad = entrada.cantidad_entreg + Decimal(str(cantidad))

    if nueva_cantidad > entrada.cantidad_recib:
        flash(_('La cantidad entregada no puede exceder la recibida.'), 'error')
        return redirect(url_for('entradas.ver', id=id))

    entrada.cantidad_entreg = nueva_cantidad
    entrada.calcular_saldo()

    if entrada.saldo <= 0 and entrada.status == EntradaStatus.COMPLETADO:
        entrada.status        = EntradaStatus.ENTREGADO
        entrada.ent_entregada = True

    db.session.commit()
    flash(_('Entrega registrada exitosamente.'), 'success')
    return redirect(url_for('entradas.ver', id=id))


# ---------------------------------------------------------------------------
# Batch status
# ---------------------------------------------------------------------------

@entradas_bp.route('/batch-status', methods=['GET'])
@login_required
@technician_required
def batch_status():
    """Vista para actualización masiva de estados."""
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    return render_template('entradas/batch_status_update.html', clientes=clientes)
