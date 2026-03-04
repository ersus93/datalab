"""Rutas CRUD para pedidos."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_babel import _

from app import db
from app.database.models.pedido import Pedido, PedidoStatus
from app.database.models import Cliente, Producto, OrdenTrabajo
from app.forms.pedido import PedidoForm
from app.decorators import laboratory_manager_required

pedidos_bp = Blueprint('pedidos', __name__, url_prefix='/pedidos')

@pedidos_bp.route('/')
@login_required
def listar():
    """Listar pedidos con filtros."""
    page = request.args.get('page', 1, type=int)
    cliente_id = request.args.get('cliente', type=int)
    producto_id = request.args.get('producto', type=int)
    status = request.args.get('status')
    q = request.args.get('q', '')
    
    query = Pedido.query
    
    if cliente_id:
        query = query.filter_by(cliente_id=cliente_id)
    if producto_id:
        query = query.filter_by(producto_id=producto_id)
    if status:
        query = query.filter_by(status=status)
    if q:
        query = query.filter(Pedido.codigo.ilike(f'%{q}%'))
    
    pedidos = query.order_by(Pedido.fech_pedido.desc()).paginate(
        page=page, per_page=25, error_out=False
    )
    
    clientes = Cliente.query.filter_by(activo=True).all()
    productos = Producto.query.filter_by(activo=True).all()
    
    return render_template('pedidos/listar.html',
                         pedidos=pedidos,
                         clientes=clientes,
                         productos=productos)

@pedidos_bp.route('/<int:id>')
@login_required
def ver(id):
    """Ver detalle de pedido."""
    pedido = Pedido.query.get_or_404(id)
    entradas = pedido.entradas.all()
    
    return render_template('pedidos/ver.html',
                         pedido=pedido,
                         entradas=entradas)

@pedidos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@laboratory_manager_required
def nuevo():
    """Crear nuevo pedido."""
    form = PedidoForm()
    
    if form.validate_on_submit():
        pedido = Pedido(
            codigo=form.codigo.data,
            cliente_id=form.cliente_id.data,
            producto_id=form.producto_id.data,
            orden_trabajo_id=form.orden_trabajo_id.data or None,
            lote=form.lote.data,
            cantidad=form.cantidad.data,
            unidad_medida_id=form.unidad_medida_id.data or None,
            fech_fab=form.fech_fab.data,
            fech_venc=form.fech_venc.data,
            observaciones=form.observaciones.data,
            status=PedidoStatus.PENDIENTE
        )
        
        db.session.add(pedido)
        db.session.commit()
        
        flash(_('Pedido creado exitosamente.'), 'success')
        return redirect(url_for('pedidos.ver', id=pedido.id))
    
    return render_template('pedidos/form.html', form=form, titulo=_('Nuevo Pedido'))

@pedidos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@laboratory_manager_required
def editar(id):
    """Editar pedido."""
    pedido = Pedido.query.get_or_404(id)
    form = PedidoForm(obj=pedido)
    
    if form.validate_on_submit():
        pedido.codigo = form.codigo.data
        pedido.cliente_id = form.cliente_id.data
        pedido.producto_id = form.producto_id.data
        pedido.orden_trabajo_id = form.orden_trabajo_id.data or None
        pedido.lote = form.lote.data
        pedido.cantidad = form.cantidad.data
        pedido.unidad_medida_id = form.unidad_medida_id.data or None
        pedido.fech_fab = form.fech_fab.data
        pedido.fech_venc = form.fech_venc.data
        pedido.observaciones = form.observaciones.data
        
        db.session.commit()
        
        flash(_('Pedido actualizado exitosamente.'), 'success')
        return redirect(url_for('pedidos.ver', id=pedido.id))
    
    return render_template('pedidos/form.html',
                         form=form,
                         pedido=pedido,
                         titulo=_('Editar Pedido'))
