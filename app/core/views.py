"""Vistas principales del blueprint core."""

from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from . import core_bp


@core_bp.route('/')
def index():
    """Página principal de la aplicación."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('core/index.html')


@core_bp.route('/about')
def about():
    """Página acerca de."""
    return render_template('core/about.html')


@core_bp.route('/contact')
def contact():
    """Página de contacto."""
    return render_template('core/contact.html')


@core_bp.route('/health')
def health_check():
    """Endpoint de verificación de salud de la aplicación."""
    return {
        'status': 'healthy',
        'version': '1.0.0',
        'environment': current_app.config.get('ENV', 'unknown')
    }