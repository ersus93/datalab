"""Rutas CRUD para entradas de muestras."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_babel import _
from decimal import Decimal

from app import db
from app.database.models.entrada import Entrada, EntradaStatus
from app.database.models import Cliente, Fabrica, Producto, Pedido
from app.forms.entrada import EntradaForm
from app.decorators import laboratory_manager_required, technician_required

entradas_bp = Blueprint('entradas', __name__, url_prefix='/entradas')


@entradas_bp.route('/')
@login_required
def listar():
    """Listar entradas con filtros avanzados."""
    page = request.args.get('page', 1, type=int)
    cliente_id = request.args.get('cliente', type=int)
    producto_id = request.args.get('producto', type=int)
    status = request.args.get('status')
    desde = request.args.get('desde')
    hasta = request.args.get('hasta')
    q = request.args.get('q', '')
    
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
                Entrada.lote.ilike(f'%{q}%')
            )
        )
    
    entradas = query.order_by(Entrada.fech_entrada.desc()).paginate(
        page=page, per_page=25, error_out=False
    )
    
    # Datos para filtros
    clientes = Cliente.query.filter_by(activo=True).all()
    productos = Producto.query.filter_by(activo=True).all()
    
    return render_template('entradas/listar.html',
                         entradas=entradas,
                         clientes=clientes,
                         productos=productos,
                         q=q)


@entradas_bp.route('/<int:id>')
@login_required
def ver(id):
    """Ver detalle de entrada."""
    entrada = Entrada.query.get_or_404(id)
    
    return render_template('entradas/ver.html',
                         entrada=entrada)


@entradas_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
@technician_required
def nueva():
    """Crear nueva entrada."""
    form = EntradaForm()
    
    if form.validate_on_submit():
        entrada = Entrada(
            codigo=form.codigo.data,
            lote=form.lote.data,
            nro_parte=form.nro_parte.data,
            producto_id=form.producto_id.data,
            fabrica_id=form.fabrica_id.data,
            cliente_id=form.cliente_id.data,
            rama_id=form.rama_id.data if form.rama_id.data and form.rama_id.data > 0 else None,
            pedido_id=form.pedido_id.data if form.pedido_id.data and form.pedido_id.data > 0 else None,
            cantidad_recib=form.cantidad_recib.data,
            cantidad_entreg=Decimal('0'),
            cantidad_muest=form.cantidad_muest.data,
            unidad_medida_id=form.unidad_medida_id.data if form.unidad_medida_id.data and form.unidad_medida_id.data > 0 else None,
            fech_fab=form.fech_fab.data,
            fech_venc=form.fech_venc.data,
            fech_muestreo=form.fech_muestreo.data,
            observaciones=form.observaciones.data,
            status=EntradaStatus.RECIBIDO
        )
        
        db.session.add(entrada)
        db.session.commit()
        
        flash(_('Entrada creada exitosamente.'), 'success')
        return redirect(url_for('entradas.ver', id=entrada.id))
    
    return render_template('entradas/form.html', form=form, titulo=_('Nueva Entrada'))


@entradas_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@technician_required
def editar(id):
    """Editar entrada existente."""
    entrada = Entrada.query.get_or_404(id)
    
    # No permitir editar entradas anuladas o entregadas
    if entrada.anulado:
        flash(_('No se puede editar una entrada anulada.'), 'error')
        return redirect(url_for('entradas.ver', id=id))
    
    form = EntradaForm(obj=entrada)
    
    if form.validate_on_submit():
        entrada.codigo = form.codigo.data
        entrada.lote = form.lote.data
        entrada.nro_parte = form.nro_parte.data
        entrada.producto_id = form.producto_id.data
        entrada.fabrica_id = form.fabrica_id.data
        entrada.cliente_id = form.cliente_id.data
        entrada.rama_id = form.rama_id.data if form.rama_id.data and form.rama_id.data > 0 else None
        entrada.pedido_id = form.pedido_id.data if form.pedido_id.data and form.pedido_id.data > 0 else None
        entrada.cantidad_recib = form.cantidad_recib.data
        entrada.cantidad_muest = form.cantidad_muest.data
        entrada.unidad_medida_id = form.unidad_medida_id.data if form.unidad_medida_id.data and form.unidad_medida_id.data > 0 else None
        entrada.fech_fab = form.fech_fab.data
        entrada.fech_venc = form.fech_venc.data
        entrada.fech_muestreo = form.fech_muestreo.data
        entrada.observaciones = form.observaciones.data
        
        db.session.commit()
        
        flash(_('Entrada actualizada exitosamente.'), 'success')
        return redirect(url_for('entradas.ver', id=entrada.id))
    
    return render_template('entradas/form.html',
                         form=form,
                         entrada=entrada,
                         titulo=_('Editar Entrada'))


@entradas_bp.route('/<int:id>/cambiar-estado', methods=['POST'])
@login_required
@technician_required
def cambiar_estado(id):
    """Cambiar estado de la entrada."""
    entrada = Entrada.query.get_or_404(id)
    nuevo_estado = request.form.get('status')
    razon = request.form.get('razon', '')
    
    # Validar transición (simplificado, se expande en #27)
    transiciones_validas = {
        EntradaStatus.RECIBIDO: [EntradaStatus.EN_PROCESO, EntradaStatus.ANULADO],
        EntradaStatus.EN_PROCESO: [EntradaStatus.COMPLETADO, EntradaStatus.ANULADO],
        EntradaStatus.COMPLETADO: [EntradaStatus.ENTREGADO]
    }
    
    if nuevo_estado not in transiciones_validas.get(entrada.status, []):
        flash(_('Transición de estado no válida.'), 'error')
        return redirect(url_for('entradas.ver', id=id))
    
    entrada.status = nuevo_estado
    
    # Actualizar flags según estado
    if nuevo_estado == EntradaStatus.ANULADO:
        entrada.anulado = True
    elif nuevo_estado == EntradaStatus.ENTREGADO:
        entrada.ent_entregada = True
    
    db.session.commit()
    
    # TODO: Registrar en StatusHistory (issue #27)
    # TODO: Enviar notificaciones (issue #27)
    
    flash(_('Estado actualizado exitosamente.'), 'success')
    return redirect(url_for('entradas.ver', id=id))


@entradas_bp.route('/<int:id>/registrar-entrega', methods=['POST'])
@login_required
@technician_required
def registrar_entrega(id):
    """Registrar entrega de muestra."""
    entrada = Entrada.query.get_or_404(id)
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
    
    # Auto-actualizar estado si saldo llega a 0
    if entrada.saldo <= 0 and entrada.status == EntradaStatus.COMPLETADO:
        entrada.status = EntradaStatus.ENTREGADO
        entrada.ent_entregada = True
    
    db.session.commit()
    
    flash(_('Entrega registrada exitosamente.'), 'success')
    return redirect(url_for('entradas.ver', id=id))


@entradas_bp.route('/batch-status', methods=['GET'])
@login_required
@technician_required
def batch_status():
    """Vista para actualización masiva de estados."""
    # Obtener clientes para el filtro
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    return render_template('entradas/batch_status_update.html', clientes=clientes)
