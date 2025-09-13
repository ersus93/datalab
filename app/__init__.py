from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
import os

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
cors = CORS()

def create_app(config_name='default'):
    """Factory function para crear la aplicación Flask."""
    
    app = Flask(__name__)
    
    # Cargar configuración
    from config.config import config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Inicializar extensiones con la app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    
    # Configurar Login Manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.auth.models import User
        return User.query.get(int(user_id))
    
    # Registrar blueprints
    from app.core.views import core_bp
    from app.auth.views import auth_bp
    from app.dashboard.views import dashboard_bp
    from app.analytics.views import analytics_bp
    from app.reports.views import reports_bp
    
    app.register_blueprint(core_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    # Configurar logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('ONIE DataLab startup')
    
    # Context processors globales
    @app.context_processor
    def inject_global_vars():
        return {
            'brand_name': app.config.get('BRAND_NAME', 'ONIE DataLab'),
            'brand_description': app.config.get('BRAND_DESCRIPTION', ''),
            'theme': app.config.get('THEME', 'light')
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app