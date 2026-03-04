"""Rutas CRUD para órdenes de trabajo."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required

from app import db
from app.database.models.orden_trabajo import OrdenTrabajo, OTStatus
from app.database.models import Cliente, Pedido
from app.forms.orden_trabajo import OrdenTrabajoForm
from app.decorators import laboratory_manager_required

ordenes_trabajo_bp = Blueprint('ordenes_trabajo', __name__, url_prefix='/ordenes-trabajo')


@ordenes_trabajo_bp.route('/')
@login_required
def listar():
    """Listar órdenes de trabajo con filtros."""
    page = request.args.get('page', 1, type=int)
    cliente_id = request.args.get('cliente', type=int)
    status = request.args.get('status')
    q = request.args.get('q', '')
    
    query = OrdenTrabajo.query
    
    if cliente_id:
        query = query.filter_by(cliente_id=cliente_id)
    if status:
        query = query.filter_by(status=status)
    if q:
        query = query.filter(
            db.or_(
                OrdenTrabajo.nro_ofic.ilike(f'%{q}%'),
                OrdenTrabajo.codigo.ilike(f'%{q}%')
            )
        )
    
    ordenes = query.order_by(OrdenTrabajo.fech_creacion.desc()).paginate(
        page=page, per_page=25, error_out=False
    )
    
    clientes = Cliente.query.filter_by(activo=True).all()
    
    return render_template('ordenes_trabajo/listar.html',
                         ordenes=ordenes,
                         clientes=clientes)


@ordenes_trabajo_bp.route('/<int:id>')
@login_required
def ver(id):
    """Ver detalle de orden de trabajo."""
    orden = OrdenTrabajo.query.get_or_404(id)
    pedidos = orden.pedidos.all()
    
    # Pedidos disponibles para asignar (del mismo cliente, sin OT)
    pedidos_disponibles = Pedido.query.filter_by(
        cliente_id=orden.cliente_id,
        orden_trabajo_id=None
    ).all()
    
    return render_template('ordenes_trabajo/ver.html',
                         orden=orden,
                         pedidos=pedidos,
                         pedidos_disponibles=pedidos_disponibles)


@ordenes_trabajo_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
@laboratory_manager_required
def nueva():
    """Crear nueva orden de trabajo."""
    form = OrdenTrabajoForm()
    
    if form.validate_on_submit():
        # Generar código automático si no se proporciona
        codigo = form.codigo.data or generar_codigo_ot()
        
        orden = OrdenTrabajo(
            nro_ofic=form.nro_ofic.data,
            codigo=codigo,
            cliente_id=form.cliente_id.data,
            descripcion=form.descripcion.data,
            observaciones=form.observaciones.data,
            status=OTStatus.PENDIENTE
        )
        
        db.session.add(orden)
        db.session.commit()
        
        flash(_('Orden de trabajo creada exitosamente.'), 'success')
        return redirect(url_for('ordenes_trabajo.ver', id=orden.id))
    
    return render_template('ordenes_trabajo/form.html', form=form, titulo=_('Nueva Orden de Trabajo'))


@ordenes_trabajo_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@laboratory_manager_required
def editar(id):
    """Editar orden de trabajo."""
    orden = OrdenTrabajo.query.get_or_404(id)
    form = OrdenTrabajoForm(obj=orden)
    
    if form.validate_on_submit():
        orden.nro_ofic = form.nro_ofic.data
        orden.codigo = form.codigo.data
        orden.cliente_id = form.cliente_id.data
        orden.descripcion = form.descripcion.data
        orden.observaciones = form.observaciones.data
        
        db.session.commit()
        
        flash(_('Orden de trabajo actualizada exitosamente.'), 'success')
        return redirect(url_for('ordenes_trabajo.ver', id=orden.id))
    
    return render_template('ordenes_trabajo/form.html',
                         form=form,
                         orden=orden,
                         titulo=_('Editar Orden de Trabajo'))


@ordenes_trabajo_bp.route('/<int:id>/asignar-pedido', methods=['POST'])
@login_required
@laboratory_manager_required
def asignar_pedido(id):
    """Asignar pedido a orden de trabajo."""
    orden = OrdenTrabajo.query.get_or_404(id)
    pedido_id = request.form.get('pedido_id', type=int)
    
    if not pedido_id:
        flash(_('Debe seleccionar un pedido.'), 'error')
        return redirect(url_for('ordenes_trabajo.ver', id=id))
    
    pedido = Pedido.query.get_or_404(pedido_id)
    
    # Verificar que el pedido sea del mismo cliente
    if pedido.cliente_id != orden.cliente_id:
        flash(_('El pedido debe ser del mismo cliente.'), 'error')
        return redirect(url_for('ordenes_trabajo.ver', id=id))
    
    pedido.orden_trabajo_id = orden.id
    db.session.commit()
    
    # Actualizar estado de la OT
    orden.actualizar_estado()
    db.session.commit()
    
    flash(_('Pedido asignado exitosamente.'), 'success')
    return redirect(url_for('ordenes_trabajo.ver', id=id))


@ordenes_trabajo_bp.route('/<int:orden_id>/quitar-pedido/<int:pedido_id>', methods=['POST'])
@login_required
@laboratory_manager_required
def quitar_pedido(orden_id, pedido_id):
    """Quitar pedido de orden de trabajo."""
    orden = OrdenTrabajo.query.get_or_404(orden_id)
    pedido = Pedido.query.get_or_404(pedido_id)
    
    if pedido.orden_trabajo_id != orden.id:
        flash(_('El pedido no pertenece a esta orden de trabajo.'), 'error')
        return redirect(url_for('ordenes_trabajo.ver', id=orden_id))
    
    pedido.orden_trabajo_id = None
    db.session.commit()
    
    # Actualizar estado de la OT
    orden.actualizar_estado()
    db.session.commit()
    
    flash(_('Pedido removido exitosamente.'), 'success')
    return redirect(url_for('ordenes_trabajo.ver', id=orden_id))


@ordenes_trabajo_bp.route('/buscar')
@login_required
def buscar():
    """Buscar órdenes de trabajo por número oficial."""
    nro_ofic = request.args.get('nro_ofic', '').strip()
    
    if not nro_ofic:
        return jsonify({'error': 'NroOfic requerido'}), 400
    
    # Búsqueda parcial
    ordenes = OrdenTrabajo.query.filter(
        OrdenTrabajo.nro_ofic.ilike(f'%{nro_ofic}%')
    ).all()
    
    return jsonify({
        'results': [ot.to_dict() for ot in ordenes],
        'count': len(ordenes)
    })


def generar_codigo_ot():
    """Generar código único para orden de trabajo."""
    ultima = OrdenTrabajo.query.order_by(OrdenTrabajo.id.desc()).first()
    siguiente_id = (ultima.id + 1) if ultima else 1
    return f'OT-{siguiente_id:04d}'
