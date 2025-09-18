from flask import Blueprint, render_template

from .dashboard import dashboard_bp
from .pedidos import bp as pedidos_bp
from .search import bp as search_bp
from .clientes import clientes_bp

def register_routes(app):
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(clientes_bp)

    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('dashboard.index'))