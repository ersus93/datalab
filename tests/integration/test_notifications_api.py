#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests de integración para los endpoints de API de notificaciones.

Este módulo prueba el flujo completo de notificaciones incluyendo
paginación, filtrado, marcado como leídas, eliminación y gestión
de preferencias del usuario autenticado.
"""

import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app import create_app, db
from app.database.models.user import User, UserRole
from app.database.models.notification import Notification
from app.database.models.notification_preference import NotificationPreference


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def app():
    """Crear aplicación Flask en modo testing."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de pruebas no autenticado."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Crear un usuario de prueba."""
    with app.app_context():
        user = User(
            username='test_user',
            email='test@example.com',
            role=UserRole.TECHNICIAN,
            nombre_completo='Test User'
        )
        user.set_password('test123')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def test_user_2(app):
    """Crear un segundo usuario de prueba para tests de autorización."""
    with app.app_context():
        user = User(
            username='test_user_2',
            email='test2@example.com',
            role=UserRole.TECHNICIAN,
            nombre_completo='Test User 2'
        )
        user.set_password('test123')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def auth_client(client, test_user, app):
    """Cliente autenticado como usuario de prueba."""
    with app.app_context():
        user = db.session.get(User, test_user.id)
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
    return client


@pytest.fixture
def auth_headers():
    """Headers para requests JSON."""
    return {'Content-Type': 'application/json'}


@pytest.fixture
def sample_notifications(app, test_user):
    """Crear notificaciones de prueba para el usuario."""
    with app.app_context():
        notifications = []
        for i in range(1, 6):
            notification = Notification(
                user_id=test_user.id,
                type='status_change',
                title=f'Notificación {i}',
                message=f'Mensaje de prueba {i}',
                entity_type='entrada',
                entity_id=i,
                read=(i > 3)  # Las primeras 3 no leídas, las demás sí
            )
            db.session.add(notification)
            notifications.append(notification)
        db.session.commit()
        return notifications


@pytest.fixture
def other_user_notifications(app, test_user_2):
    """Crear notificaciones para otro usuario (para tests de autorización)."""
    with app.app_context():
        notifications = []
        for i in range(1, 4):
            notification = Notification(
                user_id=test_user_2.id,
                type='delivery',
                title=f'Notificación Otro {i}',
                message=f'Mensaje de otro usuario {i}',
                entity_type='entrada',
                entity_id=i,
                read=False
            )
            db.session.add(notification)
            notifications.append(notification)
        db.session.commit()
        return notifications


# =============================================================================
# TestObtenerNotificaciones
# =============================================================================

class TestObtenerNotificaciones:
    """Tests para GET /api/notifications - Obtener notificaciones paginadas."""

    @patch('app.routes.notifications_api.NotificationService')
    def test_get_notifications_success(self, mock_service, auth_client, test_user, app):
        """GET /api/notifications retorna lista paginada de notificaciones."""
        mock_notification = {
            'id': 1,
            'type': 'status_change',
            'title': 'Cambio de estado',
            'message': 'La entrada cambió de estado',
            'entity_type': 'entrada',
            'entity_id': 1,
            'read': False,
            'created_at': datetime.utcnow().isoformat()
        }

        mock_service.get_user_notifications.return_value = {
            'items': [mock_notification],
            'pagination': {
                'page': 1,
                'per_page': 20,
                'total': 1,
                'total_pages': 1,
                'has_next': False,
                'has_prev': False,
                'next_page': None,
                'prev_page': None
            }
        }
        mock_service.get_unread_count.return_value = 3

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.get('/api/notifications')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert len(response_data['notifications']) == 1
        assert response_data['notifications'][0]['title'] == 'Cambio de estado'
        assert response_data['unread_count'] == 3
        assert response_data['pagination']['total'] == 1

    @patch('app.routes.notifications_api.NotificationService')
    def test_get_notifications_with_pagination(self, mock_service, auth_client,
                                                test_user, app):
        """La paginación funciona correctamente con page y per_page."""
        mock_notifications = [
            {
                'id': i,
                'type': 'status_change',
                'title': f'Notificación {i}',
                'message': f'Mensaje {i}',
                'read': False,
                'created_at': datetime.utcnow().isoformat()
            }
            for i in range(1, 11)
        ]

        mock_service.get_user_notifications.return_value = {
            'items': mock_notifications,
            'pagination': {
                'page': 2,
                'per_page': 10,
                'total': 25,
                'total_pages': 3,
                'has_next': True,
                'has_prev': True,
                'next_page': 3,
                'prev_page': 1
            }
        }
        mock_service.get_unread_count.return_value = 15

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.get('/api/notifications?page=2&per_page=10')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert len(response_data['notifications']) == 10
        assert response_data['pagination']['page'] == 2
        assert response_data['pagination']['total_pages'] == 3
        assert response_data['pagination']['has_next'] is True

    @patch('app.routes.notifications_api.NotificationService')
    def test_get_notifications_unread_only(self, mock_service, auth_client,
                                           test_user, app):
        """Filtrar por notificaciones no leídas con unread_only=true."""
        mock_notifications = [
            {
                'id': 1,
                'type': 'status_change',
                'title': 'No leída 1',
                'message': 'Mensaje',
                'read': False,
                'created_at': datetime.utcnow().isoformat()
            }
        ]

        mock_service.get_user_notifications.return_value = {
            'items': mock_notifications,
            'pagination': {
                'page': 1,
                'per_page': 20,
                'total': 1,
                'total_pages': 1,
                'has_next': False,
                'has_prev': False
            }
        }
        mock_service.get_unread_count.return_value = 1

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.get('/api/notifications?unread_only=true')

        assert response.status_code == 200
        mock_service.get_user_notifications.assert_called_once_with(
            user_id=test_user.id,
            page=1,
            per_page=20,
            unread_only=True
        )

    @patch('app.routes.notifications_api.NotificationService')
    def test_get_notifications_empty_list(self, mock_service, auth_client,
                                          test_user, app):
        """Retorna lista vacía cuando no hay notificaciones."""
        mock_service.get_user_notifications.return_value = {
            'items': [],
            'pagination': {
                'page': 1,
                'per_page': 20,
                'total': 0,
                'total_pages': 0,
                'has_next': False,
                'has_prev': False
            }
        }
        mock_service.get_unread_count.return_value = 0

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.get('/api/notifications')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert len(response_data['notifications']) == 0
        assert response_data['unread_count'] == 0


# =============================================================================
# TestUnreadCount
# =============================================================================

class TestUnreadCount:
    """Tests para GET /api/notifications/unread-count."""

    @patch('app.routes.notifications_api.NotificationService')
    def test_get_unread_count_success(self, mock_service, auth_client,
                                      test_user, app):
        """GET /api/notifications/unread-count retorna conteo exacto."""
        mock_service.get_unread_count.return_value = 5

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.get('/api/notifications/unread-count')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['count'] == 5

    @patch('app.routes.notifications_api.NotificationService')
    def test_get_unread_count_zero(self, mock_service, auth_client, test_user, app):
        """Retorna 0 cuando no hay notificaciones no leídas."""
        mock_service.get_unread_count.return_value = 0

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.get('/api/notifications/unread-count')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['count'] == 0


# =============================================================================
# TestMarcarComoLeida
# =============================================================================

class TestMarcarComoLeida:
    """Tests para POST /api/notifications/<id>/read."""

    @patch('app.routes.notifications_api.NotificationService')
    @patch('app.routes.notifications_api.Notification')
    def test_mark_notification_read_success(self, mock_notification_class,
                                            mock_service, auth_client,
                                            test_user, app):
        """POST marca la notificación como leída exitosamente."""
        mock_notification = MagicMock()
        mock_notification.id = 1
        mock_notification.to_dict.return_value = {
            'id': 1,
            'type': 'status_change',
            'title': 'Test',
            'message': 'Test message',
            'read': True,
            'created_at': datetime.utcnow().isoformat()
        }

        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_notification
        mock_notification_class.query = mock_query

        mock_service.mark_as_read.return_value = True

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.post('/api/notifications/1/read')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        mock_service.mark_as_read.assert_called_once_with(1)

    @patch('app.routes.notifications_api.Notification')
    def test_mark_notification_read_not_found(self, mock_notification_class,
                                              auth_client, test_user, app):
        """Retorna 404 si la notificación no existe o no pertenece al usuario."""
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_notification_class.query = mock_query

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.post('/api/notifications/999/read')

        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert response_data['error']['code'] == 'NOT_FOUND'

    @patch('app.routes.notifications_api.NotificationService')
    @patch('app.routes.notifications_api.Notification')
    def test_mark_notification_read_service_error(self, mock_notification_class,
                                                  mock_service, auth_client,
                                                  test_user, app):
        """Retorna 500 si el servicio falla al marcar como leída."""
        mock_notification = MagicMock()
        mock_notification.id = 1

        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_notification
        mock_notification_class.query = mock_query

        mock_service.mark_as_read.return_value = False

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.post('/api/notifications/1/read')

        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data['success'] is False


# =============================================================================
# TestMarcarTodasLeidas
# =============================================================================

class TestMarcarTodasLeidas:
    """Tests para POST /api/notifications/mark-all-read."""

    @patch('app.routes.notifications_api.NotificationService')
    def test_mark_all_notifications_read_success(self, mock_service, auth_client,
                                                 test_user, app):
        """POST marca todas las notificaciones como leídas."""
        mock_service.mark_all_as_read.return_value = 5

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.post('/api/notifications/mark-all-read')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['marked_count'] == 5
        mock_service.mark_all_as_read.assert_called_once_with(test_user.id)

    @patch('app.routes.notifications_api.NotificationService')
    def test_mark_all_notifications_read_zero(self, mock_service, auth_client,
                                              test_user, app):
        """Retorna 0 cuando no hay notificaciones para marcar."""
        mock_service.mark_all_as_read.return_value = 0

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.post('/api/notifications/mark-all-read')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['marked_count'] == 0


# =============================================================================
# TestEliminarNotificacion
# =============================================================================

class TestEliminarNotificacion:
    """Tests para DELETE /api/notifications/<id>."""

    @patch('app.routes.notifications_api.db')
    @patch('app.routes.notifications_api.Notification')
    def test_delete_notification_success(self, mock_notification_class,
                                         mock_db, auth_client, test_user, app):
        """DELETE elimina la notificación exitosamente (204)."""
        mock_notification = MagicMock()
        mock_notification.id = 1

        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_notification
        mock_notification_class.query = mock_query

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.delete('/api/notifications/1')

        assert response.status_code == 204
        mock_db.session.delete.assert_called_once_with(mock_notification)
        mock_db.session.commit.assert_called_once()

    @patch('app.routes.notifications_api.Notification')
    def test_delete_notification_not_found(self, mock_notification_class,
                                          auth_client, test_user, app):
        """Retorna 404 si la notificación no existe o no pertenece al usuario."""
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_notification_class.query = mock_query

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.delete('/api/notifications/999')

        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert response_data['error']['code'] == 'NOT_FOUND'

    @patch('app.routes.notifications_api.db')
    @patch('app.routes.notifications_api.Notification')
    def test_delete_notification_db_error(self, mock_notification_class,
                                          mock_db, auth_client, test_user, app):
        """Maneja errores de base de datos correctamente (500)."""
        mock_notification = MagicMock()

        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_notification
        mock_notification_class.query = mock_query

        mock_db.session.commit.side_effect = Exception('DB Error')

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.delete('/api/notifications/1')

        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        mock_db.session.rollback.assert_called_once()


# =============================================================================
# TestPreferencias
# =============================================================================

class TestPreferencias:
    """Tests para GET y PUT /api/notifications/preferences."""

    @patch('app.routes.notifications_api.NotificationPreference')
    def test_get_preferences_success(self, mock_pref_class, auth_client,
                                     test_user, app):
        """GET /api/notifications/preferences retorna preferencias del usuario."""
        mock_preferences = MagicMock()
        mock_preferences.to_dict.return_value = {
            'id': 1,
            'user_id': test_user.id,
            'email_enabled': True,
            'in_app_enabled': True,
            'status_change_email': True,
            'delivery_email': False,
            'pending_alert_email': True
        }
        mock_pref_class.get_or_create.return_value = mock_preferences

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.get('/api/notifications/preferences')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['preferences']['email_enabled'] is True
        assert response_data['preferences']['delivery_email'] is False

    @patch('app.routes.notifications_api.NotificationPreference')
    def test_update_preferences_success(self, mock_pref_class, auth_client,
                                        test_user, app, auth_headers):
        """PUT /api/notifications/preferences actualiza preferencias."""
        mock_preferences = MagicMock()
        mock_preferences.email_enabled = True
        mock_preferences.in_app_enabled = True
        mock_preferences.status_change_email = False
        mock_preferences.delivery_email = True
        mock_preferences.pending_alert_email = False
        mock_preferences.to_dict.return_value = {
            'id': 1,
            'user_id': test_user.id,
            'email_enabled': True,
            'in_app_enabled': True,
            'status_change_email': False,
            'delivery_email': True,
            'pending_alert_email': False
        }
        mock_pref_class.get_or_create.return_value = mock_preferences

        update_data = {
            'status_change_email': False,
            'delivery_email': True,
            'pending_alert_email': False
        }

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.put(
                '/api/notifications/preferences',
                data=json.dumps(update_data),
                headers=auth_headers
            )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['preferences']['status_change_email'] is False
        assert response_data['preferences']['delivery_email'] is True

    @patch('app.routes.notifications_api.NotificationPreference')
    def test_update_preferences_invalid_data(self, mock_pref_class, auth_client,
                                             test_user, app, auth_headers):
        """Retorna 400 si no se proporciona cuerpo JSON válido."""
        mock_preferences = MagicMock()
        mock_pref_class.get_or_create.return_value = mock_preferences

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.put(
                '/api/notifications/preferences',
                data=json.dumps({}),
                headers=auth_headers
            )

        assert response.status_code == 200  # Acepta body vacío, no actualiza nada

        # Sin body debe retornar 400
        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.put(
                '/api/notifications/preferences',
                data='',
                headers=auth_headers
            )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert response_data['error']['code'] == 'VALIDATION_ERROR'


# =============================================================================
# TestAutenticacionAutorizacion
# =============================================================================

class TestAutenticacionAutorizacion:
    """Tests de autenticación y autorización."""

    def test_unauthorized_access_get_notifications(self, client):
        """Acceso sin autenticación a GET /api/notifications retorna 401/302."""
        response = client.get('/api/notifications')
        assert response.status_code in [302, 401, 403]

    def test_unauthorized_access_get_unread_count(self, client):
        """Acceso sin autenticación a unread-count retorna 401/302."""
        response = client.get('/api/notifications/unread-count')
        assert response.status_code in [302, 401, 403]

    def test_unauthorized_access_mark_read(self, client):
        """Acceso sin autenticación a mark-read retorna 401/302."""
        response = client.post('/api/notifications/1/read')
        assert response.status_code in [302, 401, 403]

    def test_unauthorized_access_mark_all_read(self, client):
        """Acceso sin autenticación a mark-all-read retorna 401/302."""
        response = client.post('/api/notifications/mark-all-read')
        assert response.status_code in [302, 401, 403]

    def test_unauthorized_access_delete(self, client):
        """Acceso sin autenticación a DELETE retorna 401/302."""
        response = client.delete('/api/notifications/1')
        assert response.status_code in [302, 401, 403]

    def test_unauthorized_access_preferences_get(self, client):
        """Acceso sin autenticación a GET preferences retorna 401/302."""
        response = client.get('/api/notifications/preferences')
        assert response.status_code in [302, 401, 403]

    def test_unauthorized_access_preferences_put(self, client):
        """Acceso sin autenticación a PUT preferences retorna 401/302."""
        response = client.put('/api/notifications/preferences')
        assert response.status_code in [302, 401, 403]

    @patch('app.routes.notifications_api.Notification')
    def test_cannot_access_other_user_notification(self, mock_notification_class,
                                                   auth_client, test_user,
                                                   test_user_2, app):
        """No se puede marcar como leída una notificación de otro usuario."""
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_notification_class.query = mock_query

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.post('/api/notifications/1/read')

        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['success'] is False

    @patch('app.routes.notifications_api.Notification')
    def test_cannot_delete_other_user_notification(self, mock_notification_class,
                                                   auth_client, test_user,
                                                   test_user_2, app):
        """No se puede eliminar una notificación de otro usuario."""
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_notification_class.query = mock_query

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.delete('/api/notifications/1')

        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['success'] is False


# =============================================================================
# TestErroresYValidaciones
# =============================================================================

class TestErroresYValidaciones:
    """Tests para casos de error y validación."""

    @patch('app.routes.notifications_api.NotificationService')
    def test_pagination_params_validation(self, mock_service, auth_client,
                                          test_user, app):
        """Los parámetros de paginación negativos se corrigen a valores válidos."""
        mock_service.get_user_notifications.return_value = {
            'items': [],
            'pagination': {'page': 1, 'per_page': 20, 'total': 0}
        }
        mock_service.get_unread_count.return_value = 0

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.get('/api/notifications?page=-1&per_page=200')

        assert response.status_code == 200

    @patch('app.routes.notifications_api.NotificationService')
    def test_internal_error_handling(self, mock_service, auth_client,
                                     test_user, app):
        """Manejo de errores internos del servidor (500)."""
        mock_service.get_user_notifications.side_effect = Exception('DB Error')

        with patch('app.routes.notifications_api.current_user', test_user):
            response = auth_client.get('/api/notifications')

        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert response_data['error']['code'] == 'INTERNAL_ERROR'
