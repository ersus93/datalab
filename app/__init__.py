"""
App Factory - DataLab
Registra todos los features como blueprints.
La arquitectura hexagonal permite agregar/quitar features sin tocar el core.
"""
from flask import Flask, request
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_babel import Babel

from app.core.infrastructure.database import db

# Inicializar extensiones
login_manager = LoginManager()
migrate = Migrate()
babel = Babel()

# Exportar db para compatibilidad
__all__ = ['create_app', 'db', 'login_manager']


def _register_template_context_processors(app):
    """Registra context processors para templates."""
    from app.utils.flash_messages import flash_message_component

    @app.context_processor
    def inject_globals():
        return {"flash_message_component": flash_message_component}


def create_app(config_name: str = "development") -> Flask:
    """Factory de la aplicación Flask."""
    app = Flask(__name__, template_folder="templates")

    # Configuración
    _configure_app(app, config_name)

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    babel.init_app(app, locale_selector=_get_locale)

    # Configurar Flask-Login
    _configure_login_manager(app)

    # Registrar context processors para templates
    _register_template_context_processors(app)

    # Registrar rutas (lazy import para evitar ciclos)
    from app.routes import register_routes
    register_routes(app)

    # Manejadores de error globales
    _register_error_handlers(app)

    # Registrar comandos CLI personalizados
    from app.cli import register_cli_commands
    register_cli_commands(app)

    return app


def _configure_login_manager(app: Flask):
    """Configura el LoginManager de Flask-Login."""
    login_manager.login_view = app.config.get("LOGIN_VIEW", "auth.login")
    login_manager.login_message = app.config.get(
        "LOGIN_MESSAGE", "Por favor inicie sesión para acceder a esta página."
    )
    login_manager.login_message_category = app.config.get(
        "LOGIN_MESSAGE_CATEGORY", "warning"
    )

    @login_manager.user_loader
    def load_user(user_id: str):
        """Carga el usuario por su ID."""
        from app.database.models.user import User
        return User.query.get(int(user_id))


def _configure_app(app: Flask, config_name: str):
    configs = {
        "development": "app.config.DevelopmentConfig",
        "testing": "app.config.TestingConfig",
        "production": "app.config.ProductionConfig",
    }
    app.config.from_object(configs.get(config_name, configs["development"]))


def _get_locale():
    """Determina el idioma preferido del usuario."""
    return request.accept_languages.best_match(['es', 'en']) or 'es'


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
