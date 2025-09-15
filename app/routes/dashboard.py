#!/usr/bin/env python3
"""Rutas del dashboard de DataLab."""

from flask import Blueprint, render_template, request, jsonify

# Crear blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@dashboard_bp.route('/index')
def index():
    """Página principal del dashboard."""
    # Datos de ejemplo para el dashboard
    dashboard_data = {
        'total_users': 1234,
        'active_sessions': 89,
        'total_reports': 456,
        'system_health': 'good',
        'recent_activities': [
            {
                'type': 'user_registered',
                'description': 'Nuevo usuario registrado: María González',
                'time': 'Hace 5 minutos',
                'icon': 'user-plus'
            },
            {
                'type': 'report_generated',
                'description': 'Reporte mensual de ventas completado',
                'time': 'Hace 1 hora',
                'icon': 'file-text'
            },
            {
                'type': 'task_completed',
                'description': 'Backup automático de base de datos completado',
                'time': 'Hace 2 horas',
                'icon': 'clock'
            },
            {
                'type': 'system_update',
                'description': 'Sistema actualizado a la versión 2.1.4',
                'time': 'Hace 4 horas',
                'icon': 'check-circle'
            }
        ],
        'countries_stats': [
            {'name': 'España', 'flag': '🇪🇸', 'percentage': 45.2},
            {'name': 'México', 'flag': '🇲🇽', 'percentage': 23.1},
            {'name': 'Argentina', 'flag': '🇦🇷', 'percentage': 18.7},
            {'name': 'Colombia', 'flag': '🇨🇴', 'percentage': 13.0}
        ]
    }
    
    return render_template('pages/dashboard/dashboard.html', **dashboard_data)

@dashboard_bp.route('/api/stats')
def api_stats():
    """API endpoint para obtener estadísticas del dashboard."""
    stats = {
        'users': {
            'total': 1234,
            'active': 89,
            'new_today': 12
        },
        'reports': {
            'total': 456,
            'generated_today': 8,
            'pending': 3
        },
        'system': {
            'health': 'good',
            'uptime': '99.9%',
            'last_backup': '2 horas'
        }
    }
    
    return jsonify(stats)

@dashboard_bp.route('/api/activities')
def api_activities():
    """API endpoint para obtener actividades recientes."""
    activities = [
        {
            'id': 1,
            'type': 'user_registered',
            'title': 'Nuevo usuario registrado',
            'description': 'María González se ha registrado en la plataforma',
            'time': 'Hace 5 minutos',
            'icon': 'user-plus'
        },
        {
            'id': 2,
            'type': 'report_generated',
            'title': 'Reporte generado',
            'description': 'Reporte mensual de ventas completado',
            'time': 'Hace 1 hora',
            'icon': 'file-text'
        }
    ]
    
    return jsonify(activities)