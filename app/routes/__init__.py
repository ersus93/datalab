from flask import Blueprint, render_template


def register_routes(app):
    # Importar analytics
    from app.routes.analytics_api import analytics_api_bp
    from app.routes.analytics import analytics_bp
    # Importar features PRIMERO (registran sus propios modelos ORM)
    from app.features.clientes.infrastructure.web.routes import clientes_bp
    from app.features.ensayos.infrastructure.web.routes import ensayos_bp
    from app.features.muestras.infrastructure.web.routes import muestras_bp
    from app.features.reportes import reportes_bp

    # Registrar features
    app.register_blueprint(clientes_bp)
    app.register_blueprint(muestras_bp)
    app.register_blueprint(ensayos_bp)
    app.register_blueprint(reportes_bp)

    # Importar User DESPUÉS de los features (para evitar conflictos de tabla)
    from app.database.models.user import User

    # Importar rutas legacy
    from .auth import auth_bp
    from .dashboard import dashboard_bp
    from .dashboard_api import dashboard_api_bp
    from .entradas import entradas_bp
    from .fabricas import fabricas_bp
    from .fabricas_api import fabricas_api_bp
    from .ordenes_trabajo import ordenes_trabajo_bp
    from .ordenes_trabajo_api import ordenes_trabajo_api_bp, clientes_ordenes_api_bp
    from .pedidos import pedidos_bp
    from .productos import productos_bp
    from .productos_api import productos_api_bp
    from .reference import reference_bp
    from .status_api import status_api_bp
    from .entradas_api import entradas_api_bp
    from .pedidos_api import pedidos_api_bp, clientes_pedidos_api_bp
    from .notifications_api import notifications_api_bp
    from .detalle_ensayo_api import detalle_ensayo_api_bp, ensayos_catalog_bp
    from .detalle_ensayo import detalle_ensayo_bp
    from .lab import lab_bp
    from .billing_api import billing_bp
    from .tecnico import tecnico_bp
    from .admin import admin_bp
    from .informes import informes_bp

    # Registrar rutas legacy
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(reference_bp)
    app.register_blueprint(fabricas_bp)
    app.register_blueprint(fabricas_api_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(productos_api_bp)
    app.register_blueprint(entradas_bp)
    app.register_blueprint(ordenes_trabajo_bp)
    app.register_blueprint(ordenes_trabajo_api_bp)
    app.register_blueprint(clientes_ordenes_api_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(status_api_bp)
    app.register_blueprint(entradas_api_bp)
    app.register_blueprint(pedidos_api_bp)
    app.register_blueprint(clientes_pedidos_api_bp)
    app.register_blueprint(detalle_ensayo_api_bp)
    app.register_blueprint(ensayos_catalog_bp)
    app.register_blueprint(detalle_ensayo_bp)
    app.register_blueprint(lab_bp)
    app.register_blueprint(tecnico_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(informes_bp)
    app.register_blueprint(notifications_api_bp, url_prefix='/api/notifications')
    app.register_blueprint(dashboard_api_bp, url_prefix='/api/dashboard')
    app.register_blueprint(analytics_api_bp, url_prefix='/api/analytics')
    app.register_blueprint(analytics_bp)

    @app.route("/")
    def index():
        from flask import redirect, url_for

        return redirect(url_for("dashboard.index"))
