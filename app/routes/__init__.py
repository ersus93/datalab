from flask import Blueprint, render_template


def register_routes(app):
    # Importar features PRIMERO (registran sus propios modelos ORM)
    from app.features.clientes.infrastructure.web.routes import clientes_bp
    from app.features.ensayos.infrastructure.web.routes import ensayos_bp
    from app.features.muestras.infrastructure.web.routes import muestras_bp

    # Registrar features
    app.register_blueprint(clientes_bp)
    app.register_blueprint(muestras_bp)
    app.register_blueprint(ensayos_bp)

    # Importar User DESPUÉS de los features (para evitar conflictos de tabla)
    from app.database.models.user import User

    # Importar rutas legacy
    from .auth import auth_bp
    from .dashboard import dashboard_bp

    # Registrar rutas legacy
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)

    @app.route("/")
    def index():
        from flask import redirect, url_for

        return redirect(url_for("dashboard.index"))
