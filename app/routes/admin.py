#!/usr/bin/env python3
"""Rutas de administración."""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_babel import lazy_gettext as _

from app import db
from app.database.models import User, UserRole, Cliente, AuditLog
from app.decorators import admin_required
from app.forms.user import UserForm, UserEditForm, PasswordResetForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/usuarios')
@login_required
@admin_required
def listar_usuarios():
    """Listar todos los usuarios con filtros."""
    page = request.args.get('page', 1, type=int)
    role = request.args.get('role')
    estado = request.args.get('estado')
    q = request.args.get('q', '')

    query = User.query

    if role:
        query = query.filter_by(role=UserRole(role))
    if estado:
        query = query.filter_by(activo=(estado == 'activo'))
    if q:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{q}%'),
                User.email.ilike(f'%{q}%'),
                User.nombre_completo.ilike(f'%{q}%')
            )
        )

    usuarios = query.order_by(User.creado_en.desc()).paginate(
        page=page, per_page=25, error_out=False
    )

    return render_template('admin/usuarios.html', usuarios=usuarios)


@admin_bp.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def crear_usuario():
    """Crear nuevo usuario."""
    form = UserForm()

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            nombre_completo=form.nombre_completo.data,
            role=UserRole(form.role.data),
            cliente_id=form.cliente_id.data if form.role.data == 'client' and form.cliente_id.data != 0 else None,
            activo=form.activo.data
        )
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        # Registrar en audit log
        AuditLog.log_change(
            user_id=current_user.id,
            action='CREATE',
            table_name='users',
            record_id=user.id,
            new_values=user.to_dict(),
            ip_address=request.remote_addr
        )
        db.session.commit()

        flash(_('Usuario creado exitosamente.'), 'success')
        return redirect(url_for('admin.listar_usuarios'))

    return render_template('admin/crear_usuario.html', form=form)


@admin_bp.route('/usuarios/<int:user_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_usuario(user_id):
    """Editar usuario existente."""
    user = User.query.get_or_404(user_id)

    # Evitar auto-desactivación
    if user.id == current_user.id:
        flash(_('No puede editar su propio usuario desde aquí.'), 'warning')
        return redirect(url_for('admin.listar_usuarios'))

    form = UserEditForm(user_id=user.id, obj=user)

    if form.validate_on_submit():
        old_values = user.to_dict()

        user.email = form.email.data
        user.nombre_completo = form.nombre_completo.data
        user.role = UserRole(form.role.data)
        user.activo = form.activo.data

        if form.role.data == 'client' and form.cliente_id.data != 0:
            user.cliente_id = form.cliente_id.data
        else:
            user.cliente_id = None

        db.session.commit()

        # Registrar en audit log
        AuditLog.log_change(
            user_id=current_user.id,
            action='UPDATE',
            table_name='users',
            record_id=user.id,
            old_values=old_values,
            new_values=user.to_dict(),
            ip_address=request.remote_addr
        )
        db.session.commit()

        flash(_('Usuario actualizado exitosamente.'), 'success')
        return redirect(url_for('admin.listar_usuarios'))

    return render_template('admin/editar_usuario.html', form=form, user=user)


@admin_bp.route('/usuarios/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_usuario(user_id):
    """Activar/desactivar usuario."""
    user = User.query.get_or_404(user_id)

    # Evitar auto-desactivación
    if user.id == current_user.id:
        flash(_('No puede desactivar su propia cuenta.'), 'error')
        return redirect(url_for('admin.listar_usuarios'))

    old_values = user.to_dict()
    user.activo = not user.activo
    db.session.commit()

    # Registrar en audit log
    AuditLog.log_change(
        user_id=current_user.id,
        action='UPDATE',
        table_name='users',
        record_id=user.id,
        old_values=old_values,
        new_values=user.to_dict(),
        ip_address=request.remote_addr
    )
    db.session.commit()

    if user.activo:
        flash(_('Usuario activado exitosamente.'), 'success')
    else:
        flash(_('Usuario desactivado exitosamente.'), 'success')

    return redirect(url_for('admin.listar_usuarios'))


@admin_bp.route('/usuarios/<int:user_id>/reset-password', methods=['GET', 'POST'])
@login_required
@admin_required
def reset_password(user_id):
    """Resetear contraseña de usuario por admin."""
    user = User.query.get_or_404(user_id)

    # Evitar auto-reset
    if user.id == current_user.id:
        flash(_('No puede cambiar su propia contraseña desde aquí.'), 'warning')
        return redirect(url_for('admin.listar_usuarios'))

    form = PasswordResetForm()

    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.clear_password_reset_token()
        db.session.commit()

        # Registrar en audit log
        AuditLog.log_change(
            user_id=current_user.id,
            action='UPDATE',
            table_name='users',
            record_id=user.id,
            ip_address=request.remote_addr
        )
        db.session.commit()

        flash(_('Contraseña actualizada exitosamente.'), 'success')
        return redirect(url_for('admin.listar_usuarios'))

    return render_template('admin/reset_password.html', form=form, user=user)
