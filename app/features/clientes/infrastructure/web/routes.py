"""
Feature: Clientes
Capa: Infrastructure - Web (Adapter Flask)

Adaptador que expone las rutas legacy de clientes bajo la nueva
estructura hexagonal. Pendiente: migrar completamente a la arquitectura
hexagonal con servicios de aplicación.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_babel import _

from app import db
from app.database.models import Cliente, Organismo
from app.forms.cliente import ClienteForm
from app.decorators import admin_required, laboratory_manager_required

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')


@clientes_bp.route('/')
@login_required
def listar():
    """Listar clientes con paginación, búsqueda y filtros."""
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '')
    organismo_id = request.args.get('organismo', type=int)
    estado = request.args.get('estado')
    
    query = Cliente.query
    
    # Búsqueda
    if q:
        query = query.filter(Cliente.nombre.ilike(f'%{q}%'))
    
    # Filtros
    if organismo_id:
        query = query.filter_by(organismo_id=organismo_id)
    if estado:
        query = query.filter_by(activo=(estado == 'activo'))
    
    # Ordenamiento y paginación
    clientes = query.order_by(Cliente.nombre).paginate(
        page=page, per_page=25, error_out=False
    )
    
    organismos = Organismo.query.all()
    
    return render_template('clientes/listar.html',
                         clientes=clientes,
                         organismos=organismos,
                         q=q)


@clientes_bp.route('/<int:id>')
@login_required
def ver(id):
    """Ver detalle de cliente."""
    cliente = Cliente.query.get_or_404(id)
    
    # Estadísticas
    stats = {
        'total_fabricas': len(cliente.fabricas),
        'fabricas_activas': sum(1 for f in cliente.fabricas if f.activo),
    }
    
    return render_template('clientes/ver.html',
                         cliente=cliente,
                         stats=stats)


@clientes_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@laboratory_manager_required
def nuevo():
    """Crear nuevo cliente."""
    form = ClienteForm()
    
    if form.validate_on_submit():
        cliente = Cliente(
            nombre=form.nombre.data,
            organismo_id=form.organismo_id.data,
            tipo_cliente=form.tipo_cliente.data,
            activo=form.activo.data
        )
        
        db.session.add(cliente)
        db.session.commit()
        
        flash(_('Cliente creado exitosamente.'), 'success')
        return redirect(url_for('clientes.ver', id=cliente.id))
    
    return render_template('clientes/form.html', form=form, titulo=_('Nuevo Cliente'))


@clientes_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@laboratory_manager_required
def editar(id):
    """Editar cliente existente."""
    cliente = Cliente.query.get_or_404(id)
    form = ClienteForm(obj=cliente)
    
    if form.validate_on_submit():
        cliente.nombre = form.nombre.data
        cliente.organismo_id = form.organismo_id.data
        cliente.tipo_cliente = form.tipo_cliente.data
        cliente.activo = form.activo.data
        
        db.session.commit()
        
        flash(_('Cliente actualizado exitosamente.'), 'success')
        return redirect(url_for('clientes.ver', id=cliente.id))
    
    return render_template('clientes/form.html', 
                         form=form, 
                         cliente=cliente,
                         titulo=_('Editar Cliente'))


@clientes_bp.route('/<int:id>/desactivar', methods=['POST'])
@login_required
@admin_required
def desactivar(id):
    """Desactivar cliente (soft delete)."""
    cliente = Cliente.query.get_or_404(id)
    
    # Verificar si tiene fábricas activas
    fabricas_activas = [f for f in cliente.fabricas if f.activo]
    if fabricas_activas:
        flash(_('No se puede desactivar: el cliente tiene fábricas activas.'), 'error')
        return redirect(url_for('clientes.ver', id=id))
    
    cliente.activo = False
    db.session.commit()
    
    flash(_('Cliente desactivado exitosamente.'), 'success')
    return redirect(url_for('clientes.listar'))
