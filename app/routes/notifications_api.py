"""API endpoints para gestión de notificaciones.

Endpoints para consultar, marcar como leídas y gestionar preferencias
de notificaciones del usuario autenticado.
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from app import db
from app.services.notification_service import NotificationService
from app.database.models.notification import Notification
from app.database.models.notification_preference import NotificationPreference

notifications_api_bp = Blueprint('notifications_api', __name__, url_prefix='/api/notifications')


@notifications_api_bp.route('', methods=['GET'])
@login_required
def get_notifications():
    """Obtener notificaciones paginadas del usuario actual.

    Query params:
        page (int): Número de página (default: 1)
        per_page (int): Cantidad por página (default: 20)
        unread_only (bool): Solo notificaciones no leídas

    Returns:
        JSON con lista de notificaciones, metadatos de paginación y conteo de no leídas.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'

        # Validar parámetros de paginación
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20

        result = NotificationService.get_user_notifications(
            user_id=current_user.id,
            page=page,
            per_page=per_page,
            unread_only=unread_only
        )

        unread_count = NotificationService.get_unread_count(current_user.id)

        return jsonify({
            'success': True,
            'notifications': result.get('items', []),
            'pagination': result.get('pagination', {}),
            'unread_count': unread_count
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e),
                'details': {}
            }
        }), 500


@notifications_api_bp.route('/unread-count', methods=['GET'])
@login_required
def get_unread_count():
    """Obtener cantidad de notificaciones no leídas del usuario actual.

    Returns:
        JSON con el conteo de notificaciones no leídas.
    """
    try:
        count = NotificationService.get_unread_count(current_user.id)
        return jsonify({
            'success': True,
            'count': count
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e),
                'details': {}
            }
        }), 500


@notifications_api_bp.route('/<int:id>/read', methods=['POST'])
@login_required
def mark_notification_read(id):
    """Marcar una notificación como leída.

    Args:
        id (int): ID de la notificación.

    Returns:
        JSON con la notificación actualizada o error 404.
    """
    try:
        # Verificar que la notificación existe y pertenece al usuario
        notification = Notification.query.filter_by(
            id=id,
            user_id=current_user.id
        ).first()

        if not notification:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Notificación no encontrada',
                    'details': {}
                }
            }), 404

        success = NotificationService.mark_as_read(id)

        if not success:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': 'No se pudo marcar la notificación como leída',
                    'details': {}
                }
            }), 500

        # Refrescar la notificación para obtener datos actualizados
        notification = Notification.query.get(id)

        return jsonify({
            'success': True,
            'notification': notification.to_dict()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e),
                'details': {}
            }
        }), 500


@notifications_api_bp.route('/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Marcar todas las notificaciones del usuario como leídas.

    Returns:
        JSON con la cantidad de notificaciones marcadas.
    """
    try:
        marked_count = NotificationService.mark_all_as_read(current_user.id)

        return jsonify({
            'success': True,
            'marked_count': marked_count
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e),
                'details': {}
            }
        }), 500


@notifications_api_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_notification(id):
    """Eliminar una notificación.

    Args:
        id (int): ID de la notificación.

    Returns:
        204 No Content en éxito, 404 si no existe o no pertenece al usuario.
    """
    try:
        # Verificar que la notificación existe y pertenece al usuario
        notification = Notification.query.filter_by(
            id=id,
            user_id=current_user.id
        ).first()

        if not notification:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'Notificación no encontrada',
                    'details': {}
                }
            }), 404

        db.session.delete(notification)
        db.session.commit()

        return '', 204

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e),
                'details': {}
            }
        }), 500


@notifications_api_bp.route('/preferences', methods=['GET'])
@login_required
def get_preferences():
    """Obtener preferencias de notificación del usuario.

    Returns:
        JSON con las preferencias del usuario.
    """
    try:
        preferences = NotificationPreference.get_or_create(current_user.id)

        return jsonify({
            'success': True,
            'preferences': preferences.to_dict()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e),
                'details': {}
            }
        }), 500


@notifications_api_bp.route('/preferences', methods=['PUT'])
@login_required
def update_preferences():
    """Actualizar preferencias de notificación del usuario.

    Body:
        JSON con campos de preferencia a actualizar.

    Returns:
        JSON con las preferencias actualizadas.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Se requiere un cuerpo JSON válido',
                    'details': {}
                }
            }), 400

        preferences = NotificationPreference.get_or_create(current_user.id)

        # Campos permitidos para actualización
        allowed_fields = [
            'email_enabled',
            'in_app_enabled',
            'status_change_email',
            'delivery_email',
            'pending_alert_email'
        ]

        updated = False
        for field in allowed_fields:
            if field in data:
                value = data[field]
                if isinstance(value, bool):
                    setattr(preferences, field, value)
                    updated = True

        if updated:
            db.session.commit()

        return jsonify({
            'success': True,
            'preferences': preferences.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': str(e),
                'details': {}
            }
        }), 500
