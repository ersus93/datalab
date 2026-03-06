"""
App Factory - DataLab
Registra todos los features como blueprints.
La arquitectura hexagonal permite agregar/quitar features sin tocar el core.
"""
from flask import Flask, request
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_babel import Babel
from flask_mail import Mail

from app.core.infrastructure.database import db

# Inicializar extensiones
login_manager = LoginManager()
migrate = Migrate()
babel = Babel()
mail = Mail()

# Exportar db para compatibilidad
__all__ = ['create_app', 'db', 'login_manager']


def _register_template_context_processors(app):
    """Registra context processors para templates."""
    from app.utils.flash_messages import flash_message_component

    @app.context_processor
    def inject_globals():
        return {"flash_message_component": flash_message_component}

    # ------------------------------------------------------------------
    # Template filters para status de Entradas
    # ------------------------------------------------------------------
    _STATUS_COLORS = {
        'RECIBIDO':   'blue',
        'EN_PROCESO': 'yellow',
        'COMPLETADO': 'purple',
        'ENTREGADO':  'green',
        'ANULADO':    'red',
    }
    _STATUS_LABELS = {
        'RECIBIDO':   'Recibido',
        'EN_PROCESO': 'En Proceso',
        'COMPLETADO': 'Completado',
        'ENTREGADO':  'Entregado',
        'ANULADO':    'Anulado',
    }

    @app.template_filter('status_color')
    def status_color_filter(status):
        """Devuelve el color Tailwind correspondiente al status."""
        return _STATUS_COLORS.get(str(status), 'gray')

    @app.template_filter('status_label')
    def status_label_filter(status):
        """Devuelve la etiqueta legible correspondiente al status."""
        return _STATUS_LABELS.get(str(status), str(status))


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
    mail.init_app(app)

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
    """Determina el idioma preferido del usuario.
    
    Prioridad:
    1. Parámetro ?lang= en la URL (permite cambio manual)
    2. Accept-Languages del navegador
    3. Español como fallback
    """
    supported = ['es', 'en']
    lang = request.args.get('lang')
    if lang and lang in supported:
        return lang
    return request.accept_languages.best_match(supported) or 'es'


def _register_error_handlers(app: Flask):
    from flask import jsonify, render_template
    from app.core.domain.base import NotFoundError, ValidationError, DomainException

    def _wants_json():
        """Determina si el cliente prefiere respuesta JSON."""
        return request.path.startswith('/api/') or \
               request.accept_mimetypes.best == 'application/json'

    @app.errorhandler(NotFoundError)
    def handle_not_found(e):
        if _wants_json():
            return jsonify({"error": str(e)}), 404
        return render_template('errors/404.html', message=str(e)), 404

    @app.errorhandler(ValidationError)
    def handle_validation(e):
        if _wants_json():
            return jsonify({"error": str(e)}), 400
        return render_template('errors/400.html', message=str(e)), 400

    @app.errorhandler(DomainException)
    def handle_domain(e):
        if _wants_json():
            return jsonify({"error": str(e)}), 422
        return render_template('errors/422.html', message=str(e)), 422

    @app.errorhandler(403)
    def handle_403(e):
        if _wants_json():
            return jsonify({"error": "Acceso prohibido"}), 403
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def handle_404(e):
        if _wants_json():
            return jsonify({"error": "Recurso no encontrado"}), 404
        return render_template('errors/404.html'), 404
