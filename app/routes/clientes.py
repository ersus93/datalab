"""Rutas CRUD para gestión de clientes."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import _
from sqlalchemy import or_

from app import db
from app.database.models import Cliente, Organismo
from app.database.models.audit import AuditLog
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

    # Búsqueda por nombre o código
    if q:
        query = query.filter(
            or_(
                Cliente.nombre.ilike(f'%{q}%'),
                Cliente.codigo.ilike(f'%{q}%')
            )
        )

    # Filtros
    if organismo_id:
        query = query.filter_by(organismo_id=organismo_id)
    if estado:
        query = query.filter_by(activo=(estado == 'activo'))

    # Ordenamiento y paginación
    clientes = query.order_by(Cliente.nombre).paginate(
        page=page, per_page=25, error_out=False
    )

    organismos = Organismo.query.order_by(Organismo.nombre).all()

    return render_template('clientes/listar.html',
                           clientes=clientes,
                           organismos=organismos,
                           q=q)


@clientes_bp.route('/<int:id>')
@login_required
def ver(id):
    """Ver detalle de cliente."""
    cliente = Cliente.query.get_or_404(id)

    stats = {
        'total_fabricas': len(cliente.fabricas),
        'fabricas_activas': sum(1 for f in cliente.fabricas if f.activo),
    }

    # Últimas 10 entradas de auditoría para este cliente
    audit_entries = (
        AuditLog.query
        .filter_by(table_name='clientes', record_id=id)
        .order_by(AuditLog.created_at.desc())
        .limit(10)
        .all()
    )

    return render_template('clientes/ver.html',
                           cliente=cliente,
                           stats=stats,
                           audit_entries=audit_entries)


@clientes_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@laboratory_manager_required
def nuevo():
    """Crear nuevo cliente."""
    form = ClienteForm()

    if form.validate_on_submit():
        cliente = Cliente(
            codigo=form.codigo.data.strip().upper(),
            nombre=form.nombre.data,
            organismo_id=form.organismo_id.data,
            tipo_cliente=form.tipo_cliente.data,
            activo=form.activo.data
        )

        db.session.add(cliente)
        db.session.flush()  # Obtener ID antes del commit

        AuditLog.log_change(
            user_id=current_user.id,
            action='CREATE',
            table_name='clientes',
            record_id=cliente.id,
            new_values=cliente.to_dict(),
            ip_address=request.remote_addr
        )

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
        old_values = cliente.to_dict()

        cliente.codigo = form.codigo.data.strip().upper()
        cliente.nombre = form.nombre.data
        cliente.organismo_id = form.organismo_id.data
        cliente.tipo_cliente = form.tipo_cliente.data
        cliente.activo = form.activo.data

        AuditLog.log_change(
            user_id=current_user.id,
            action='UPDATE',
            table_name='clientes',
            record_id=cliente.id,
            old_values=old_values,
            new_values=cliente.to_dict(),
            ip_address=request.remote_addr
        )

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

    fabricas_activas = [f for f in cliente.fabricas if f.activo]
    if fabricas_activas:
        flash(_('No se puede desactivar: el cliente tiene fábricas activas.'), 'error')
        return redirect(url_for('clientes.ver', id=id))

    old_values = cliente.to_dict()
    cliente.activo = False

    AuditLog.log_change(
        user_id=current_user.id,
        action='DELETE',
        table_name='clientes',
        record_id=cliente.id,
        old_values=old_values,
        new_values={'activo': False},
        ip_address=request.remote_addr
    )

    db.session.commit()

    flash(_('Cliente desactivado exitosamente.'), 'success')
    return redirect(url_for('clientes.listar'))


@clientes_bp.route('/<int:id>/activar', methods=['POST'])
@login_required
@admin_required
def activar(id):
    """Reactivar cliente previamente desactivado."""
    cliente = Cliente.query.get_or_404(id)

    old_values = cliente.to_dict()
    cliente.activo = True

    AuditLog.log_change(
        user_id=current_user.id,
        action='UPDATE',
        table_name='clientes',
        record_id=cliente.id,
        old_values=old_values,
        new_values={'activo': True},
        ip_address=request.remote_addr
    )

    db.session.commit()

    flash(_('Cliente reactivado exitosamente.'), 'success')
    return redirect(url_for('clientes.ver', id=id))
