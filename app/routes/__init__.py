#!/usr/bin/env python3
"""Registro de rutas de la aplicación DataLab."""

from flask import render_template

def register_routes(app):
    """Registrar todas las rutas de la aplicación."""
    
    # Importar blueprints
    from app.routes.dashboard import dashboard_bp
    
    # Registrar blueprints
    app.register_blueprint(dashboard_bp)
    
    # Ruta principal - redirigir al dashboard
    @app.route('/')
    def index():
        """Página principal - redirige al dashboard."""
        from flask import redirect, url_for
        return redirect(url_for('dashboard.index'))