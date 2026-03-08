import os
os.environ.setdefault('FLASK_ENV', 'development')
from app import create_app, db
from app.database.models.user import User

app = create_app(os.getenv('FLASK_ENV'))

with app.app_context():
    user = User.query.filter_by(username='admin').first()
    if user:
        print(f"username: {user.username}")
        print(f"email:    {user.email}")
        print(f"activo:   {user.activo}")
        print(f"role:     {user.role}")
        print(f"hash:     {user.password_hash[:40]}...")
        # Probar la contrasena directamente
        ok = user.check_password('admin1234')
        print(f"check_password('admin1234'): {ok}")
    else:
        print("ERROR: usuario admin no encontrado")
