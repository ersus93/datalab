"""Vistas del dashboard."""

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from . import dashboard_bp


@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard principal."""
    return render_template('dashboard/index.html')


@dashboard_bp.route('/overview')
@login_required
def overview():
    """Vista general del dashboard."""
    # Aquí se pueden agregar métricas y estadísticas
    stats = {
        'total_users': 0,
        'active_sessions': 0,
        'data_processed': 0,
        'reports_generated': 0
    }
    return render_template('dashboard/overview.html', stats=stats)


@dashboard_bp.route('/widgets')
@login_required
def widgets():
    """Página de widgets del dashboard."""
    return render_template('dashboard/widgets.html')


@dashboard_bp.route('/api/stats')
@login_required
def api_stats():
    """API endpoint para estadísticas del dashboard."""
    stats = {
        'users': {
            'total': 0,
            'active': 0,
            'new_today': 0
        },
        'data': {
            'processed_today': 0,
            'total_records': 0,
            'storage_used': '0 MB'
        },
        'performance': {
            'avg_response_time': '0ms',
            'uptime': '99.9%',
            'cpu_usage': '0%'
        }
    }
    return jsonify(stats)