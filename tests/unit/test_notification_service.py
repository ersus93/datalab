#!/usr/bin/env python3
"""Tests unitarios para NotificationService.

Part of Issue #45 - Sistema de notificaciones.
"""
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.services.notification_service import NotificationService


class TestSendEmailNotification:
    """Tests para envío de notificaciones por email."""

    @patch('app.services.notification_service.current_app')
    def test_send_email_notification_success(self, mock_current_app):
        """Email enviado correctamente con Flask-Mail."""
        # Mock de Flask-Mail
        mock_mail = MagicMock()
        mock_current_app.extensions = {'mail': mock_mail}

        # Mock de render_template
        with patch('app.services.notification_service.render_template') as mock_render:
            mock_render.return_value = '<html>Test</html>'

            # Mock del usuario
            mock_user = MagicMock()
            mock_user.email = 'test@example.com'

            result = NotificationService.send_email_notification(
                user=mock_user,
                template='test_template',
                context={'subject': 'Test Subject', 'message': 'Test message'},
                subject='Test Subject'
            )

        assert result is True
        mock_mail.send.assert_called_once()
        # Verificar que el mensaje fue creado con los parámetros correctos
        call_args = mock_mail.send.call_args[0][0]
        assert call_args.subject == 'Test Subject'
        assert call_args.recipients == ['test@example.com']

    @patch('app.services.notification_service.current_app')
    def test_send_email_notification_no_user(self, mock_current_app):
        """No envía email si no hay usuario."""
        result = NotificationService.send_email_notification(
            user=None,
            template='test_template',
            context={'message': 'Test'}
        )

        assert result is False

    @patch('app.services.notification_service.current_app')
    def test_send_email_notification_no_email(self, mock_current_app):
        """No envía email si el usuario no tiene email."""
        mock_user = MagicMock()
        mock_user.email = None

        result = NotificationService.send_email_notification(
            user=mock_user,
            template='test_template',
            context={'message': 'Test'}
        )

        assert result is False

    @patch('app.services.notification_service.current_app')
    def test_send_email_notification_no_mail_extension(self, mock_current_app):
        """No envía email si Flask-Mail no está configurado."""
        mock_current_app.extensions = {}

        mock_user = MagicMock()
        mock_user.email = 'test@example.com'

        result = NotificationService.send_email_notification(
            user=mock_user,
            template='test_template',
            context={'message': 'Test'}
        )

        assert result is False

    @patch('app.services.notification_service.current_app')
    def test_send_email_notification_handles_exception(self, mock_current_app):
        """Maneja excepciones al enviar email."""
        mock_mail = MagicMock()
        mock_mail.send.side_effect = Exception('SMTP Error')
        mock_current_app.extensions = {'mail': mock_mail}

        mock_user = MagicMock()
        mock_user.email = 'test@example.com'

        with patch('app.services.notification_service.render_template'):
            result = NotificationService.send_email_notification(
                user=mock_user,
                template='test_template',
                context={'message': 'Test'}
            )

        assert result is False


class TestSendInAppNotification:
    """Tests para creación de notificaciones in-app."""

    @patch('app.services.notification_service.db')
    def test_send_in_app_notification_success(self, mock_db):
        """Crea notificación in-app correctamente."""
        mock_notification = MagicMock()
        mock_notification.id = 1
        mock_notification.to_dict.return_value = {'id': 1, 'title': 'Test'}

        with patch('app.services.notification_service.Notification') as mock_notification_class:
            mock_notification_class.return_value = mock_notification

            result = NotificationService.send_in_app_notification(
                user_id=1,
                type='status_change',
                title='Test Title',
                message='Test message',
                entity_type='entrada',
                entity_id=42
            )

        assert result is not None
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()

    @patch('app.services.notification_service.db')
    def test_send_in_app_notification_no_entity(self, mock_db):
        """Crea notificación sin entidad relacionada."""
        mock_notification = MagicMock()

        with patch('app.services.notification_service.Notification') as mock_notification_class:
            mock_notification_class.return_value = mock_notification

            result = NotificationService.send_in_app_notification(
                user_id=1,
                type='test',
                title='Test',
                message='Message'
            )

        assert result is not None
        mock_db.session.add.assert_called_once()

    @patch('app.services.notification_service.db')
    def test_send_in_app_notification_rollback_on_error(self, mock_db):
        """Hace rollback si hay error al crear notificación."""
        mock_db.session.add.side_effect = Exception('DB Error')

        with patch('app.services.notification_service.Notification') as mock_notification_class:
            mock_notification_class.return_value = MagicMock()

            result = NotificationService.send_in_app_notification(
                user_id=1,
                type='test',
                title='Test',
                message='Message'
            )

        assert result is None
        mock_db.session.rollback.assert_called_once()


class TestNotifyStatusChange:
    """Tests para notificación de cambio de estado."""

    @patch('app.services.notification_service.NotificationService._should_send_in_app')
    @patch('app.services.notification_service.NotificationService._should_send_email')
    @patch('app.services.notification_service.User')
    def test_notify_status_change_success(self, mock_user_class, mock_should_email, mock_should_in_app):
        """Notifica cambio de estado correctamente."""
        # Mock del usuario
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user_class.query.filter_by.return_value.first.return_value = mock_user
        mock_should_in_app.return_value = True
        mock_should_email.return_value = True

        # Mock de la entrada
        mock_entrada = MagicMock()
        mock_entrada.id = 42
        mock_entrada.codigo = 'ENT001'
        mock_entrada.cliente_id = 1

        with patch.object(NotificationService, 'send_in_app_notification') as mock_send_in_app:
            with patch.object(NotificationService, 'send_email_notification') as mock_send_email:
                mock_send_in_app.return_value = MagicMock(id=1)
                mock_send_email.return_value = True

                result = NotificationService.notify_status_change(
                    entrada=mock_entrada,
                    from_status='RECIBIDO',
                    to_status='EN_PROCESO'
                )

        assert result['in_app'] is not None
        assert result['email'] is True
        mock_send_in_app.assert_called_once()

    @patch('app.services.notification_service.User')
    def test_notify_status_change_no_user(self, mock_user_class):
        """No notifica si no encuentra usuario asociado."""
        mock_user_class.query.filter_by.return_value.first.return_value = None

        mock_entrada = MagicMock()
        mock_entrada.id = 42
        mock_entrada.cliente_id = 999

        result = NotificationService.notify_status_change(
            entrada=mock_entrada,
            from_status='RECIBIDO',
            to_status='EN_PROCESO'
        )

        assert result['in_app'] is None
        assert result['email'] is False


class TestNotifyDeliveryPending:
    """Tests para notificación de saldo pendiente."""

    @patch('app.services.notification_service.NotificationService._should_send_in_app')
    @patch('app.services.notification_service.NotificationService._should_send_email')
    @patch('app.services.notification_service.User')
    def test_notify_delivery_pending_success(self, mock_user_class, mock_should_email, mock_should_in_app):
        """Notifica saldo pendiente correctamente."""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user_class.query.filter_by.return_value.first.return_value = mock_user
        mock_should_in_app.return_value = True
        mock_should_email.return_value = True

        mock_entrada = MagicMock()
        mock_entrada.id = 42
        mock_entrada.codigo = 'ENT001'
        mock_entrada.cliente_id = 1
        mock_entrada.saldo = Decimal('10.5')

        with patch.object(NotificationService, 'send_in_app_notification') as mock_send_in_app:
            with patch.object(NotificationService, 'send_email_notification') as mock_send_email:
                mock_send_in_app.return_value = MagicMock(id=1)
                mock_send_email.return_value = True

                result = NotificationService.notify_delivery_pending(mock_entrada)

        assert result['in_app'] is not None
        assert result['email'] is True

    def test_notify_delivery_pending_no_saldo(self):
        """No notifica si no hay saldo pendiente."""
        mock_entrada = MagicMock()
        mock_entrada.saldo = Decimal('0')

        result = NotificationService.notify_delivery_pending(mock_entrada)

        assert result['in_app'] is None
        assert result['email'] is False

    def test_notify_delivery_pending_negative_saldo(self):
        """No notifica si el saldo es negativo."""
        mock_entrada = MagicMock()
        mock_entrada.saldo = Decimal('-5')

        result = NotificationService.notify_delivery_pending(mock_entrada)

        assert result['in_app'] is None
        assert result['email'] is False


class TestGetUnreadCount:
    """Tests para conteo de notificaciones no leídas."""

    @patch('app.services.notification_service.Notification')
    def test_get_unread_count_success(self, mock_notification_class):
        """Retorna conteo correcto de no leídas."""
        mock_query = MagicMock()
        mock_query.filter_by.return_value.count.return_value = 5
        mock_notification_class.query = mock_query

        result = NotificationService.get_unread_count(user_id=1)

        assert result == 5

    @patch('app.services.notification_service.Notification')
    def test_get_unread_count_zero(self, mock_notification_class):
        """Retorna 0 si no hay notificaciones."""
        mock_query = MagicMock()
        mock_query.filter_by.return_value.count.return_value = 0
        mock_notification_class.query = mock_query

        result = NotificationService.get_unread_count(user_id=1)

        assert result == 0

    @patch('app.services.notification_service.Notification')
    def test_get_unread_count_handles_error(self, mock_notification_class):
        """Retorna 0 si hay error en la consulta."""
        mock_query = MagicMock()
        mock_query.filter_by.side_effect = Exception('DB Error')
        mock_notification_class.query = mock_query

        result = NotificationService.get_unread_count(user_id=1)

        assert result == 0


class TestGetUserNotifications:
    """Tests para obtención de notificaciones paginadas."""

    @patch('app.services.notification_service.Notification')
    def test_get_user_notifications_paginated(self, mock_notification_class):
        """Retorna notificaciones paginadas correctamente."""
        # Mock de notificaciones
        mock_notification1 = MagicMock()
        mock_notification1.to_dict.return_value = {'id': 1, 'title': 'Notif 1'}
        mock_notification2 = MagicMock()
        mock_notification2.to_dict.return_value = {'id': 2, 'title': 'Notif 2'}

        # Mock de paginación
        mock_pagination = MagicMock()
        mock_pagination.items = [mock_notification1, mock_notification2]
        mock_pagination.total = 2
        mock_pagination.pages = 1
        mock_pagination.has_next = False
        mock_pagination.has_prev = False
        mock_pagination.next_num = None
        mock_pagination.prev_num = None

        mock_query = MagicMock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.paginate.return_value = mock_pagination
        mock_notification_class.query = mock_query
        mock_notification_class.created_at = MagicMock()

        result = NotificationService.get_user_notifications(
            user_id=1,
            page=1,
            per_page=20
        )

        assert len(result['items']) == 2
        assert result['pagination']['total'] == 2
        assert result['pagination']['page'] == 1

    @patch('app.services.notification_service.Notification')
    def test_get_user_notifications_unread_only(self, mock_notification_class):
        """Filtra solo notificaciones no leídas."""
        mock_pagination = MagicMock()
        mock_pagination.items = []
        mock_pagination.total = 0
        mock_pagination.pages = 1
        mock_pagination.has_next = False
        mock_pagination.has_prev = False
        mock_pagination.next_num = None
        mock_pagination.prev_num = None

        mock_query = MagicMock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.paginate.return_value = mock_pagination
        mock_notification_class.query = mock_query
        mock_notification_class.created_at = MagicMock()

        result = NotificationService.get_user_notifications(
            user_id=1,
            unread_only=True
        )

        # Verificar que se llamó filter_by dos veces (user_id y read=False)
        assert mock_query.filter_by.call_count >= 1

    @patch('app.services.notification_service.Notification')
    def test_get_user_notifications_handles_error(self, mock_notification_class):
        """Retorna lista vacía si hay error."""
        mock_query = MagicMock()
        mock_query.filter_by.side_effect = Exception('DB Error')
        mock_notification_class.query = mock_query

        result = NotificationService.get_user_notifications(user_id=1)

        assert result['items'] == []


class TestMarkAsRead:
    """Tests para marcar notificaciones como leídas."""

    @patch('app.services.notification_service.db')
    @patch('app.services.notification_service.Notification')
    def test_mark_as_read_success(self, mock_notification_class, mock_db):
        """Marca notificación como leída correctamente."""
        mock_notification = MagicMock()
        mock_notification.read = False

        mock_query = MagicMock()
        mock_query.get.return_value = mock_notification
        mock_notification_class.query = mock_query

        result = NotificationService.mark_as_read(notification_id=1)

        assert result is True
        mock_notification.mark_read.assert_called_once()
        mock_db.session.commit.assert_called_once()

    @patch('app.services.notification_service.Notification')
    def test_mark_as_read_not_found(self, mock_notification_class):
        """Retorna False si la notificación no existe."""
        mock_query = MagicMock()
        mock_query.get.return_value = None
        mock_notification_class.query = mock_query

        result = NotificationService.mark_as_read(notification_id=999)

        assert result is False

    @patch('app.services.notification_service.db')
    @patch('app.services.notification_service.Notification')
    def test_mark_as_read_already_read(self, mock_notification_class, mock_db):
        """Retorna True si ya estaba leída sin hacer commit."""
        mock_notification = MagicMock()
        mock_notification.read = True

        mock_query = MagicMock()
        mock_query.get.return_value = mock_notification
        mock_notification_class.query = mock_query

        result = NotificationService.mark_as_read(notification_id=1)

        assert result is True
        mock_notification.mark_read.assert_not_called()
        mock_db.session.commit.assert_not_called()


class TestMarkAllAsRead:
    """Tests para marcar todas las notificaciones como leídas."""

    @patch('app.services.notification_service.db')
    @patch('app.services.notification_service.Notification')
    def test_mark_all_as_read_success(self, mock_notification_class, mock_db):
        """Marca todas las notificaciones como leídas."""
        mock_notification1 = MagicMock()
        mock_notification2 = MagicMock()

        mock_query = MagicMock()
        mock_query.filter_by.return_value.all.return_value = [mock_notification1, mock_notification2]
        mock_notification_class.query = mock_query

        result = NotificationService.mark_all_as_read(user_id=1)

        assert result == 2
        mock_notification1.mark_read.assert_called_once()
        mock_notification2.mark_read.assert_called_once()
        mock_db.session.commit.assert_called_once()

    @patch('app.services.notification_service.db')
    @patch('app.services.notification_service.Notification')
    def test_mark_all_as_read_none_unread(self, mock_notification_class, mock_db):
        """No hace commit si no hay notificaciones por leer."""
        mock_query = MagicMock()
        mock_query.filter_by.return_value.all.return_value = []
        mock_notification_class.query = mock_query

        result = NotificationService.mark_all_as_read(user_id=1)

        assert result == 0
        mock_db.session.commit.assert_not_called()

    @patch('app.services.notification_service.db')
    @patch('app.services.notification_service.Notification')
    def test_mark_all_as_read_rollback_on_error(self, mock_notification_class, mock_db):
        """Hace rollback si hay error."""
        mock_query = MagicMock()
        mock_query.filter_by.side_effect = Exception('DB Error')
        mock_notification_class.query = mock_query

        result = NotificationService.mark_all_as_read(user_id=1)

        assert result == 0


class TestShouldSendPreferences:
    """Tests para verificación de preferencias de notificación."""

    def test_should_send_email_with_preferences(self):
        """Verifica preferencias de email del usuario."""
        mock_user = MagicMock()
        mock_user.email = 'test@example.com'
        mock_prefs = MagicMock()
        mock_prefs.email_status_change = True
        mock_user.notification_preferences = mock_prefs

        result = NotificationService._should_send_email(mock_user, 'status_change')

        assert result is True

    def test_should_send_email_disabled(self):
        """No envía si las preferencias están deshabilitadas."""
        mock_user = MagicMock()
        mock_user.email = 'test@example.com'
        mock_prefs = MagicMock()
        mock_prefs.email_status_change = False
        mock_user.notification_preferences = mock_prefs

        result = NotificationService._should_send_email(mock_user, 'status_change')

        assert result is False

    def test_should_send_email_no_user(self):
        """No envía si no hay usuario."""
        result = NotificationService._should_send_email(None, 'status_change')
        assert result is False

    def test_should_send_email_no_email(self):
        """No envía si el usuario no tiene email."""
        mock_user = MagicMock()
        mock_user.email = None

        result = NotificationService._should_send_email(mock_user, 'status_change')
        assert result is False

    def test_should_send_email_default_true(self):
        """Por defecto envía email si no hay preferencias."""
        mock_user = MagicMock()
        mock_user.email = 'test@example.com'

        result = NotificationService._should_send_email(mock_user, 'status_change')
        assert result is True

    def test_should_send_in_app_with_preferences(self):
        """Verifica preferencias in-app del usuario."""
        mock_user = MagicMock()
        mock_prefs = MagicMock()
        mock_prefs.in_app_status_change = True
        mock_user.notification_preferences = mock_prefs

        result = NotificationService._should_send_in_app(mock_user, 'status_change')

        assert result is True

    def test_should_send_in_app_disabled(self):
        """No envía in-app si las preferencias están deshabilitadas."""
        mock_user = MagicMock()
        mock_prefs = MagicMock()
        mock_prefs.in_app_status_change = False
        mock_user.notification_preferences = mock_prefs

        result = NotificationService._should_send_in_app(mock_user, 'status_change')

        assert result is False

    def test_should_send_in_app_no_user(self):
        """No envía in-app si no hay usuario."""
        result = NotificationService._should_send_in_app(None, 'status_change')
        assert result is False

    def test_should_send_in_app_default_true(self):
        """Por defecto envía in-app si no hay preferencias."""
        mock_user = MagicMock()

        result = NotificationService._should_send_in_app(mock_user, 'status_change')
        assert result is True
