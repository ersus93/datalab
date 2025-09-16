#!/usr/bin/env python3
"""Inicialización de la aplicación Flask DataLab."""

import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config.config import Config

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    """Factory para crear la aplicación Flask."""
    app = Flask(__name__)
    
    # Configuración
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app.config.from_object(Config)
    
    # Inicializar extensiones con la app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Importar modelos después de inicializar db para evitar importación circular
    from app.database.models import Cliente, Pedido, OrdenTrabajo
    
    # Registrar blueprints
    from app.routes import register_routes, search
    register_routes(app)
    app.register_blueprint(search.bp)
    
    # Registrar funciones helper para templates
    from app.utils.flash_messages import flash_message_component
    app.jinja_env.globals['flash_message_component'] = flash_message_component
    
    
    
    return app