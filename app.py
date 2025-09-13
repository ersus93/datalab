#!/usr/bin/env python3
"""Punto de entrada principal para ONIE DataLab."""

import os
from flask.cli import FlaskGroup
from app import create_app, db
from app.auth.models import User, Role
from app.core.models import SystemConfig

# Crear la aplicación
app = create_app(os.getenv('FLASK_ENV', 'development'))
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
    
    analyst_role = Role.query.filter_by(name='analyst').first()
    if not analyst_role:
        analyst_role = Role(name='analyst', description='Analista de datos')
        db.session.add(analyst_role)
    
    # Crear usuario administrador por defecto
    admin_user = User.query.filter_by(email='admin@datalab.com').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@datalab.com',
            first_name='Administrador',
            last_name='Sistema',
            is_active=True
        )
        admin_user.set_password('admin123')  # Cambiar en producción
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
    print('  Email: admin@datalab.com')
    print('  Password: admin123')
    print('¡IMPORTANTE: Cambia la contraseña del administrador en producción!')

@app.cli.command()
def create_sample_data():
    """Crear datos de ejemplo para desarrollo."""
    print('Creando datos de ejemplo...')
    
    # Crear usuarios de ejemplo
    users_data = [
        {
            'username': 'analista1',
            'email': 'analista1@datalab.com',
            'first_name': 'Ana',
            'last_name': 'García',
            'role': 'analyst'
        },
        {
            'username': 'usuario1',
            'email': 'usuario1@datalab.com',
            'first_name': 'Carlos',
            'last_name': 'López',
            'role': 'user'
        }
    ]
    
    for user_data in users_data:
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if not existing_user:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                is_active=True
            )
            user.set_password('password123')
            
            role = Role.query.filter_by(name=user_data['role']).first()
            if role:
                user.roles.append(role)
            
            db.session.add(user)
    
    db.session.commit()
    print('Datos de ejemplo creados correctamente.')

@app.cli.command()
def reset_db():
    """Resetear la base de datos (¡CUIDADO: Elimina todos los datos!)."""
    if input('¿Estás seguro de que quieres resetear la base de datos? (y/N): ').lower() == 'y':
        print('Eliminando todas las tablas...')
        db.drop_all()
        print('Recreando tablas...')
        db.create_all()
        print('Base de datos reseteada correctamente.')
    else:
        print('Operación cancelada.')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)