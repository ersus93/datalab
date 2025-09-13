"""Vistas de analytics."""

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from . import analytics_bp


@analytics_bp.route('/')
@login_required
def index():
    """Página principal de analytics."""
    return render_template('analytics/index.html')


@analytics_bp.route('/charts')
@login_required
def charts():
    """Página de gráficos y visualizaciones."""
    return render_template('analytics/charts.html')


@analytics_bp.route('/data')
@login_required
def data():
    """Página de análisis de datos."""
    return render_template('analytics/data.html')


@analytics_bp.route('/api/chart-data')
@login_required
def api_chart_data():
    """API endpoint para datos de gráficos."""
    # Datos de ejemplo para gráficos
    chart_data = {
        'labels': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio'],
        'datasets': [{
            'label': 'Ventas',
            'data': [12, 19, 3, 5, 2, 3],
            'backgroundColor': 'rgba(59, 130, 246, 0.5)',
            'borderColor': 'rgba(59, 130, 246, 1)'
        }]
    }
    return jsonify(chart_data)