"""API endpoints para Analytics Dashboard de DataLab."""
from flask import Blueprint, jsonify, request
from flask_login import login_required

from app.services.analytics_service import AnalyticsService

analytics_api_bp = Blueprint('analytics_api', __name__, url_prefix='/api/analytics')


@analytics_api_bp.route('/es-pending', methods=['GET'])
@login_required
def get_es_pending():
    """Obtener ensayos sensoriales pendientes por área.

    Returns:
        JSON con lista de áreas y conteo de ES pendientes.
    """
    try:
        data = AnalyticsService.get_es_pending()
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'INTERNAL_ERROR', 'message': str(e)}
        }), 500


@analytics_api_bp.route('/fq-pending', methods=['GET'])
@login_required
def get_fq_pending():
    """Obtener ensayos físico-químicos pendientes.

    Returns:
        JSON con lista de ensayos FQ pendientes.
    """
    try:
        data = AnalyticsService.get_fq_pending()
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'INTERNAL_ERROR', 'message': str(e)}
        }), 500


@analytics_api_bp.route('/mb-pending-by-tech', methods=['GET'])
@login_required
def get_mb_pending_by_tech():
    """Obtener ensayos de microbiología pendientes por técnico.

    Returns:
        JSON con lista de técnicos y conteo de MB pendientes.
    """
    try:
        data = AnalyticsService.get_mb_pending_by_tech()
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'INTERNAL_ERROR', 'message': str(e)}
        }), 500


@analytics_api_bp.route('/completed-timeline', methods=['GET'])
@login_required
def get_completed_timeline():
    """Obtener timeline de determinaciones completadas por mes.

    Query params:
        months: Número de meses hacia atrás (default: 12)

    Returns:
        JSON con lista de meses y conteo de completados.
    """
    try:
        months = request.args.get('months', 12, type=int)
        if months < 1 or months > 36:
            months = 12

        data = AnalyticsService.get_completed_timeline(months)
        return jsonify({
            'success': True,
            'data': data,
            'months': months
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'INTERNAL_ERROR', 'message': str(e)}
        }), 500


@analytics_api_bp.route('/lotes-by-type-client', methods=['GET'])
@login_required
def get_lotes_by_type_client():
    """Obtener lotes analizados agrupados por tipo de muestra y cliente.

    Returns:
        JSON con lista de tipos de muestra por cliente.
    """
    try:
        data = AnalyticsService.get_lotes_by_type_client()
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'INTERNAL_ERROR', 'message': str(e)}
        }), 500


@analytics_api_bp.route('/muestreos-by-client-type', methods=['GET'])
@login_required
def get_muestreos_by_client_type():
    """Obtener muestreos agrupados por tipo de cliente.

    Returns:
        JSON con datos para pie chart y area chart.
    """
    try:
        data = AnalyticsService.get_muestreos_by_client_type()
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'INTERNAL_ERROR', 'message': str(e)}
        }), 500


@analytics_api_bp.route('/kpis', methods=['GET'])
@login_required
def get_analytics_kpis():
    """Obtener KPIs generales del laboratorio.

    Returns:
        JSON con contadores de KPIs.
    """
    try:
        data = AnalyticsService.get_analytics_kpis()
        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'INTERNAL_ERROR', 'message': str(e)}
        }), 500


@analytics_api_bp.route('/full', methods=['GET'])
@login_required
def get_full_analytics():
    """Obtener todos los datos de analytics en una llamada.

    Query params:
        days: Período en días para los reportes (optional)

    Returns:
        JSON con todos los datos de analytics.
    """
    try:
        period_days = request.args.get('days', type=int)
        data = AnalyticsService.get_full_analytics(period_days)

        return jsonify({
            'success': True,
            'data': data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'INTERNAL_ERROR', 'message': str(e)}
        }), 500


@analytics_api_bp.route('/invalidate-cache', methods=['POST'])
@login_required
def invalidate_cache():
    """Invalidar toda la caché de analytics.

    Returns:
        JSON con número de claves eliminadas.
    """
    try:
        count = AnalyticsService.invalidate_cache()
        return jsonify({
            'success': True,
            'data': {'cleared_keys': count},
            'message': f'Se eliminaron {count} claves de caché'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'INTERNAL_ERROR', 'message': str(e)}
        }), 500