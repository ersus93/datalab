"""Script para crear/resetear usuario administrador en DataLab."""
import os
from dotenv import load_dotenv
load_dotenv()  # Carga el .env ANTES de crear la app - mismo DB que usa la web
os.environ.setdefault('FLASK_ENV', 'development')

from app import create_app, db
from app.database.models.user import User, UserRole

app = create_app(os.getenv('FLASK_ENV'))

with app.app_context():
    existing = User.query.filter_by(username='admin').first()
    if existing:
        print(f"Usuario 'admin' ya existe (email: {existing.email})")
        print("Actualizando contrasena...")
        existing.set_password('admin1234')
        db.session.commit()
        print("OK - Contrasena actualizada.")
    else:
        user = User(
            username='admin',
            email='admin@datalab.com',
            nombre_completo='Administrador',
            role=UserRole.ADMIN,
            activo=True,
        )
        user.set_password('admin1234')
        db.session.add(user)
        db.session.commit()
        print("OK - Usuario administrador creado.")

    print("----------------------------")
    print("  Usuario:  admin")
    print("  Password: admin1234")
    print("  Rol:      ADMIN")
    print("----------------------------")
