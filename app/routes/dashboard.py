"""Rutas para dashboard principal."""
from flask import Blueprint, render_template
from flask_login import login_required

from app import db
from app.database.models import Cliente, Fabrica, Producto, Provincia, Rama

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard principal con resumen de datos maestros."""

    # Estadísticas principales
    stats = {
        'total_clientes': Cliente.query.filter_by(activo=True).count(),
        'total_fabricas': Fabrica.query.filter_by(activo=True).count(),
        'total_productos': Producto.query.filter_by(activo=True).count(),
        'total_provincias': Provincia.query.count(),
    }

    # Distribución por provincia (para gráfico)
    provincia_data = db.session.query(
        Provincia.nombre,
        Provincia.sigla,
        db.func.count(Fabrica.id).label('count')
    ).outerjoin(Fabrica).group_by(Provincia.id).all()

    # Top 10 clientes por cantidad de fábricas
    top_clientes = db.session.query(
        Cliente.id,
        Cliente.nombre,
        db.func.count(Fabrica.id).label('factory_count')
    ).join(Fabrica).group_by(Cliente.id).order_by(
        db.desc('factory_count')
    ).limit(10).all()

    # Distribución por sector (rama)
    sector_data = db.session.query(
        Rama.nombre,
        db.func.count(Producto.id).label('count')
    ).outerjoin(Producto).group_by(Rama.id).all()

    # Últimos registros agregados
    latest_clientes = Cliente.query.order_by(
        Cliente.fecha_creacion.desc()
    ).limit(5).all()

    latest_fabricas = Fabrica.query.order_by(
        Fabrica.creado_en.desc()
    ).limit(5).all()

    latest_productos = Producto.query.order_by(
        Producto.creado_en.desc()
    ).limit(5).all()

    return render_template('dashboard/index.html',
                           stats=stats,
                           provincia_data=provincia_data,
                           top_clientes=top_clientes,
                           sector_data=sector_data,
                           latest_clientes=latest_clientes,
                           latest_fabricas=latest_fabricas,
                           latest_productos=latest_productos)
