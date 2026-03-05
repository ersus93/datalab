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
    from .dashboard_api import dashboard_api_bp
    from .entradas import entradas_bp
    from .ordenes_trabajo import ordenes_trabajo_bp
    from .ordenes_trabajo_api import ordenes_trabajo_api_bp, clientes_ordenes_api_bp
    from .pedidos import pedidos_bp
    from .reference import reference_bp
    from .status_api import status_api_bp
    from .entradas_api import entradas_api_bp
    from .pedidos_api import pedidos_api_bp, clientes_pedidos_api_bp
    from .notifications_api import notifications_api_bp

    # Registrar rutas legacy
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(reference_bp)
    app.register_blueprint(entradas_bp)
    app.register_blueprint(ordenes_trabajo_bp)
    app.register_blueprint(ordenes_trabajo_api_bp)
    app.register_blueprint(clientes_ordenes_api_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(status_api_bp)
    app.register_blueprint(entradas_api_bp)
    app.register_blueprint(pedidos_api_bp)
    app.register_blueprint(clientes_pedidos_api_bp)
    app.register_blueprint(notifications_api_bp, url_prefix='/api/notifications')
    app.register_blueprint(dashboard_api_bp, url_prefix='/api/dashboard')

    @app.route("/")
    def index():
        from flask import redirect, url_for

        return redirect(url_for("dashboard.index"))
