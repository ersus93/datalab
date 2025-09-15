#!/usr/bin/env python3
"""Punto de entrada principal para ONIE DataLab."""

import os
from flask.cli import FlaskGroup
from app import create_app, db
from app.core.models import SystemConfig

# Crear la aplicación
app = create_app(os.getenv('FLASK_ENV'))
cli = FlaskGroup(app)

@app.shell_context_processor
def make_shell_context():
    """Contexto del shell de Flask con objetos útiles."""
    return {
        'db': db,
        'SystemConfig': SystemConfig
    }

@app.cli.command()
def init_db():
    """Inicializar la base de datos con datos básicos."""
    print('Creando tablas de base de datos...')
    db.create_all()
    
    # Configuración inicial del sistema
    system_config = SystemConfig.query.filter_by(key='app_initialized').first()
    if not system_config:
        system_config = SystemConfig(
            key='app_initialized',
            value='true',
            description='Indica si la aplicación ha sido inicializada'
        )
        db.session.add(system_config)
    
    db.session.commit()
    print('Base de datos inicializada correctamente.')
    print('Aplicación DataLab lista para usar.')


if __name__ == '__main__':
    app.run(debug=os.getenv('DEBUG'), host=os.getenv('FLASK_HOST'), port=os.getenv('FLASK_PORT'))