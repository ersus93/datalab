#!/usr/bin/env python3
"""Punto de entrada principal para ONIE DataLab."""

import os
from flask.cli import FlaskGroup
from app import create_app, db
from app.auth.models import User, Role
from app.core.models import SystemConfig

# Crear la aplicación
app = create_app(os.getenv('FLASK_ENV'))
cli = FlaskGroup(app)

@app.shell_context_processor
def make_shell_context():
    """Contexto del shell de Flask con objetos útiles."""
    return {
        'db': db,
        'User': User,
        'Role': Role,
        'SystemConfig': SystemConfig
    }

@app.cli.command()
def init_db():
    """Inicializar la base de datos con datos básicos."""
    print('Creando tablas de base de datos...')
    db.create_all()
    
    # Crear roles básicos
    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin', description='Administrador del sistema')
        db.session.add(admin_role)
    
    user_role = Role.query.filter_by(name='user').first()
    if not user_role:
        user_role = Role(name='user', description='Usuario estándar')
        db.session.add(user_role)
    
    # Crear usuario administrador por defecto
    admin_user = User.query.filter_by(email='admin@datalab.com').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@datalab.com',
            first_name='Staff',
            last_name='DataLab',
            is_active=True
        )
        admin_user.set_password('onie')  # Cambiar en producción
        admin_user.roles.append(admin_role)
        db.session.add(admin_user)
    
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
    print('Usuario administrador creado:')


if __name__ == '__main__':
    app.run(debug=os.getenv('DEBUG'), host=os.getenv('FLASK_HOST'), port=os.getenv('FLASK_PORT'))