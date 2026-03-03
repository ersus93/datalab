"""
App Factory - DataLab
Registra todos los features como blueprints.
La arquitectura hexagonal permite agregar/quitar features sin tocar el core.
"""
from flask import Flask
from flask_migrate import Migrate

from app.core.infrastructure.database import db

migrate = Migrate()


def create_app(config_name: str = "development") -> Flask:
    """Factory de la aplicación Flask."""
    app = Flask(__name__, template_folder="templates")

    # Configuración
    _configure_app(app, config_name)

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)

    # Registrar features (blueprints)
    _register_features(app)

    # Manejadores de error globales
    _register_error_handlers(app)

    return app


def _configure_app(app: Flask, config_name: str):
    configs = {
        "development": "app.config.DevelopmentConfig",
        "testing": "app.config.TestingConfig",
        "production": "app.config.ProductionConfig",
    }
    app.config.from_object(configs.get(config_name, configs["development"]))


def _register_features(app: Flask):
    """Registra cada feature como un blueprint independiente."""
    from app.features.clientes.infrastructure.web.routes import clientes_bp
    from app.features.muestras.infrastructure.web.routes import muestras_bp
    from app.features.ensayos.infrastructure.web.routes import ensayos_bp

    app.register_blueprint(clientes_bp)
    app.register_blueprint(muestras_bp)
    app.register_blueprint(ensayos_bp)


def _register_error_handlers(app: Flask):
    from flask import jsonify
    from app.core.domain.base import NotFoundError, ValidationError, DomainException

    @app.errorhandler(NotFoundError)
    def handle_not_found(e):
        return jsonify({"error": str(e)}), 404

    @app.errorhandler(ValidationError)
    def handle_validation(e):
        return jsonify({"error": str(e)}), 400

    @app.errorhandler(DomainException)
    def handle_domain(e):
        return jsonify({"error": str(e)}), 422
