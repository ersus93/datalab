"""Vistas de autenticación."""

from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app import db
from . import auth_bp
from .models import User, Role
from .forms import LoginForm, RegistrationForm, ProfileForm


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.username.data)
        ).first()
        
        if user and user.check_password(form.password.data) and user.is_active:
            login_user(user, remember=form.remember_me.data)
            user.update_last_login()
            
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('dashboard.index')
            
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(next_page)
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión."""
    logout_user()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('core.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Verificar si el usuario ya existe
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data)
        ).first()
        
        if existing_user:
            flash('El usuario o email ya existe.', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Crear nuevo usuario
        user = User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        
        # Asignar rol por defecto
        default_role = Role.query.filter_by(name='user').first()
        if default_role:
            user.add_role(default_role)
            db.session.commit()
        
        flash('Registro exitoso. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Página de perfil del usuario."""
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        
        if form.password.data:
            current_user.set_password(form.password.data)
        
        db.session.commit()
        flash('Perfil actualizado correctamente.', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html', form=form)


@auth_bp.route('/settings')
@login_required
def settings():
    """Página de configuración del usuario."""
    return render_template('auth/settings.html')


@auth_bp.route('/users')
@login_required
def users():
    """Lista de usuarios (solo para administradores)."""
    if not current_user.has_role('admin'):
        flash('No tienes permisos para acceder a esta página.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(
        page=page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    
    return render_template('auth/users.html', users=users)