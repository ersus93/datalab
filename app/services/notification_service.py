"""Servicio de notificaciones para DataLab.

Sistema de notificaciones que soporta:
- Notificaciones in-app (base de datos)
- Notificaciones por email (Flask-Mail)
- Preferencias de usuario
"""
import logging
from typing import Any, Dict, List, Optional

from flask import current_app, render_template
from flask_mail import Message

from app import db
from app.database.models.notification import Notification
from app.database.models.user import User


logger = logging.getLogger(__name__)


class NotificationService:
    """
    Servicio de notificaciones para DataLab.

    Provee métodos estáticos para enviar notificaciones por email
    y crear notificaciones in-app, respetando las preferencias del usuario.
    """

    # Tipos de notificación
    TYPE_STATUS_CHANGE = 'status_change'
    TYPE_DELIVERY_PENDING = 'delivery_pending'
    TYPE_TEST_COMPLETED = 'test_completed'
    TYPE_REPORT_READY = 'report_ready'
    TYPE_LOW_BALANCE = 'low_balance'
    TYPE_ENTRY_DELIVERED = 'entry_delivered'
    TYPE_ASSIGNED_TO_OT = 'assigned_to_ot'

    @staticmethod
    def _should_send_email(user: User, notification_type: str) -> bool:
        """
        Verificar si el usuario tiene habilitado el envío de email para un tipo.

        Args:
            user: Instancia del usuario
            notification_type: Tipo de notificación

        Returns:
            bool: True si debe enviarse email
        """
        # Si el usuario no tiene email, no enviar
        if not user or not user.email:
            return False

        # Verificar preferencias si existen
        if hasattr(user, 'notification_preferences'):
            prefs = user.notification_preferences
            if prefs:
                return getattr(prefs, f'email_{notification_type}', True)

        # Por defecto, enviar email
        return True

    @staticmethod
    def _should_send_in_app(user: User, notification_type: str) -> bool:
        """
        Verificar si el usuario tiene habilitadas notificaciones in-app.

        Args:
            user: Instancia del usuario
            notification_type: Tipo de notificación

        Returns:
            bool: True si debe crear notificación in-app
        """
        if not user:
            return False

        # Verificar preferencias si existen
        if hasattr(user, 'notification_preferences'):
            prefs = user.notification_preferences
            if prefs:
                return getattr(prefs, f'in_app_{notification_type}', True)

        # Por defecto, crear notificación
        return True

    @staticmethod
    def send_email_notification(
        user: User,
        template: str,
        context: Dict[str, Any],
        subject: Optional[str] = None
    ) -> bool:
        """
        Enviar notificación por email usando Flask-Mail.

        Args:
            user: Usuario destinatario
            template: Nombre del template (sin extensión)
            context: Diccionario con variables para el template
            subject: Asunto del email (opcional, puede estar en context)

        Returns:
            bool: True si se envió correctamente
        """
        try:
            if not user or not user.email:
                logger.warning("No se puede enviar email: usuario sin email")
                return False

            mail = current_app.extensions.get('mail')
            if not mail:
                logger.error("Flask-Mail no está configurado")
                return False

            # Obtener asunto del contexto o usar default
            email_subject = subject or context.get('subject', 'Notificación DataLab')

            # Renderizar templates HTML y texto
            try:
                html_body = render_template(f'emails/{template}.html', **context)
            except Exception as e:
                logger.warning(f"Template HTML no encontrado: {e}")
                html_body = None

            try:
                text_body = render_template(f'emails/{template}.txt', **context)
            except Exception as e:
                logger.warning(f"Template texto no encontrado: {e}")
                # Generar texto plano desde HTML si no hay template
                text_body = context.get('message', 'Notificación DataLab')

            # Crear mensaje
            msg = Message(
                subject=email_subject,
                recipients=[user.email],
                body=text_body,
                html=html_body
            )

            # Enviar email
            mail.send(msg)
            logger.info(f"Email enviado a {user.email}: {email_subject}")
            return True

        except Exception as e:
            logger.error(f"Error enviando email a {user.email if user else 'N/A'}: {e}")
            return False

    @staticmethod
    def send_in_app_notification(
        user_id: int,
        type: str,
        title: str,
        message: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None
    ) -> Optional[Notification]:
        """
        Crear una notificación in-app para un usuario.

        Args:
            user_id: ID del usuario destinatario
            type: Tipo de notificación
            title: Título de la notificación
            message: Mensaje/detalle
            entity_type: Tipo de entidad relacionada (opcional)
            entity_id: ID de la entidad relacionada (opcional)

        Returns:
            Notification: Instancia creada o None si falló
        """
        try:
            notification = Notification(
                user_id=user_id,
                type=type,
                title=title,
                message=message,
                entity_type=entity_type,
                entity_id=entity_id,
                read=False
            )

            db.session.add(notification)
            db.session.commit()

            logger.info(f"Notificación in-app creada para usuario {user_id}: {title}")
            return notification

        except Exception as e:
            logger.error(f"Error creando notificación para usuario {user_id}: {e}")
            db.session.rollback()
            return None

    @classmethod
    def notify_status_change(
        cls,
        entrada: Any,
        from_status: str,
        to_status: str
    ) -> Dict[str, Any]:
        """
        Notificar cambio de estado de una entrada.

        Envía notificación in-app y email según preferencias del usuario.

        Args:
            entrada: Instancia de Entrada
            from_status: Estado anterior
            to_status: Nuevo estado

        Returns:
            Dict: Resultado de las notificaciones enviadas
        """
        result = {'in_app': None, 'email': False}

        try:
            # Obtener usuario asociado a la entrada (cliente)
            user = None
            if entrada.cliente_id:
                # Buscar usuario con cliente_id asociado
                user = User.query.filter_by(cliente_id=entrada.cliente_id).first()

            if not user:
                logger.warning(f"No se encontró usuario para entrada {entrada.id}")
                return result

            # Preparar mensaje
            title = f"Cambio de estado: {entrada.codigo}"
            message = (
                f"La entrada {entrada.codigo} cambió de estado "
                f"de '{from_status}' a '{to_status}'"
            )

            # Crear notificación in-app si está habilitado
            if cls._should_send_in_app(user, cls.TYPE_STATUS_CHANGE):
                result['in_app'] = cls.send_in_app_notification(
                    user_id=user.id,
                    type=cls.TYPE_STATUS_CHANGE,
                    title=title,
                    message=message,
                    entity_type='entrada',
                    entity_id=entrada.id
                )

            # Enviar email si está habilitado
            if cls._should_send_email(user, cls.TYPE_STATUS_CHANGE):
                context = {
                    'subject': title,
                    'entrada': entrada,
                    'from_status': from_status,
                    'to_status': to_status,
                    'message': message,
                    'user': user
                }
                result['email'] = cls.send_email_notification(
                    user=user,
                    template='status_change',
                    context=context,
                    subject=title
                )

        except Exception as e:
            logger.error(f"Error en notify_status_change: {e}")

        return result

    @classmethod
    def notify_delivery_pending(cls, entrada: Any) -> Dict[str, Any]:
        """
        Notificar cuando el saldo de una entrada está bajo/pendiente.

        Args:
            entrada: Instancia de Entrada

        Returns:
            Dict: Resultado de las notificaciones enviadas
        """
        result = {'in_app': None, 'email': False}

        try:
            # Solo notificar si hay saldo pendiente pero es bajo
            if entrada.saldo <= 0:
                return result

            # Obtener usuario asociado
            user = None
            if entrada.cliente_id:
                user = User.query.filter_by(cliente_id=entrada.cliente_id).first()

            if not user:
                return result

            title = f"Saldo pendiente: {entrada.codigo}"
            message = (
                f"La entrada {entrada.codigo} tiene un saldo pendiente "
                f"de {entrada.saldo} unidades por entregar."
            )

            # Notificación in-app
            if cls._should_send_in_app(user, cls.TYPE_DELIVERY_PENDING):
                result['in_app'] = cls.send_in_app_notification(
                    user_id=user.id,
                    type=cls.TYPE_DELIVERY_PENDING,
                    title=title,
                    message=message,
                    entity_type='entrada',
                    entity_id=entrada.id
                )

            # Email
            if cls._should_send_email(user, cls.TYPE_DELIVERY_PENDING):
                context = {
                    'subject': title,
                    'entrada': entrada,
                    'saldo': entrada.saldo,
                    'message': message,
                    'user': user
                }
                result['email'] = cls.send_email_notification(
                    user=user,
                    template='delivery_pending',
                    context=context,
                    subject=title
                )

        except Exception as e:
            logger.error(f"Error en notify_delivery_pending: {e}")

        return result

    @classmethod
    def notify_assigned_to_ot(cls, entrada: Any) -> Dict[str, Any]:
        """
        Notificar cuando una entrada se asigna a una orden de trabajo.

        Envía notificación in-app y email según preferencias del usuario.

        Args:
            entrada: Instancia de Entrada

        Returns:
            Dict: Resultado de las notificaciones enviadas
        """
        result = {'in_app': None, 'email': False}

        try:
            user = None
            if entrada.cliente_id:
                user = User.query.filter_by(cliente_id=entrada.cliente_id).first()

            if not user:
                logger.warning(f"No se encontró usuario para entrada {entrada.id}")
                return result

            ot_info = ""
            if entrada.pedido and entrada.pedido.orden_trabajo:
                ot_info = f"OT #{entrada.pedido.orden_trabajo.codigo}"

            title = f"Muestra asignada a Orden de Trabajo: {entrada.codigo}"
            message = (
                f"La muestra {entrada.codigo} ha sido asignada a una orden de trabajo. "
                f"{ot_info}"
            )

            if cls._should_send_in_app(user, cls.TYPE_ASSIGNED_TO_OT):
                result['in_app'] = cls.send_in_app_notification(
                    user_id=user.id,
                    type=cls.TYPE_ASSIGNED_TO_OT,
                    title=title,
                    message=message,
                    entity_type='entrada',
                    entity_id=entrada.id
                )

            if cls._should_send_email(user, cls.TYPE_ASSIGNED_TO_OT):
                from flask import url_for
                sample_url = url_for('entradas.entrada_detail', id=entrada.id, _external=True)
                
                context = {
                    'subject': title,
                    'entrada': entrada,
                    'user': user,
                    'user_name': user.username,
                    'sample_code': entrada.codigo,
                    'producto': entrada.producto.nombre if entrada.producto else 'N/A',
                    'fabrica': entrada.fabrica.nombre if entrada.fabrica else 'N/A',
                    'ot_info': ot_info,
                    'sample_url': sample_url,
                    'assignment_date': entrada.updated_at.strftime('%d/%m/%Y %H:%M') if entrada.updated_at else '',
                    'message': message
                }
                result['email'] = cls.send_email_notification(
                    user=user,
                    template='assigned_to_ot',
                    context=context,
                    subject=title
                )

        except Exception as e:
            logger.error(f"Error en notify_assigned_to_ot: {e}")

        return result

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """
        Obtener cantidad de notificaciones no leídas de un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            int: Cantidad de notificaciones no leídas
        """
        try:
            return Notification.query.filter_by(
                user_id=user_id,
                read=False
            ).count()
        except Exception as e:
            logger.error(f"Error obteniendo conteo de notificaciones: {e}")
            return 0

    @staticmethod
    def get_user_notifications(
        user_id: int,
        page: int = 1,
        per_page: int = 20,
        unread_only: bool = False
    ) -> Dict[str, Any]:
        """
        Obtener notificaciones paginadas de un usuario.

        Args:
            user_id: ID del usuario
            page: Número de página (1-based)
            per_page: Cantidad por página
            unread_only: Si True, solo notificaciones no leídas

        Returns:
            Dict: Con items y metadata de paginación
        """
        try:
            query = Notification.query.filter_by(user_id=user_id)

            if unread_only:
                query = query.filter_by(read=False)

            # Ordenar por fecha descendente (más recientes primero)
            query = query.order_by(Notification.created_at.desc())

            # Paginar
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )

            return {
                'items': [n.to_dict() for n in pagination.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'total_pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev,
                    'next_page': pagination.next_num if pagination.has_next else None,
                    'prev_page': pagination.prev_num if pagination.has_prev else None
                }
            }

        except Exception as e:
            logger.error(f"Error obteniendo notificaciones: {e}")
            return {'items': [], 'pagination': {}}

    @staticmethod
    def mark_as_read(notification_id: int) -> bool:
        """
        Marcar una notificación como leída.

        Args:
            notification_id: ID de la notificación

        Returns:
            bool: True si se marcó correctamente
        """
        try:
            notification = Notification.query.get(notification_id)
            if not notification:
                logger.warning(f"Notificación {notification_id} no encontrada")
                return False

            if notification.read:
                return True  # Ya estaba leída

            notification.mark_read()
            db.session.commit()

            logger.info(f"Notificación {notification_id} marcada como leída")
            return True

        except Exception as e:
            logger.error(f"Error marcando notificación como leída: {e}")
            db.session.rollback()
            return False

    @staticmethod
    def mark_all_as_read(user_id: int) -> int:
        """
        Marcar todas las notificaciones de un usuario como leídas.

        Args:
            user_id: ID del usuario

        Returns:
            int: Cantidad de notificaciones marcadas
        """
        try:
            notifications = Notification.query.filter_by(
                user_id=user_id,
                read=False
            ).all()

            count = 0
            for notification in notifications:
                notification.mark_read()
                count += 1

            if count > 0:
                db.session.commit()
                logger.info(f"{count} notificaciones marcadas como leídas para usuario {user_id}")

            return count

        except Exception as e:
            logger.error(f"Error marcando notificaciones como leídas: {e}")
            db.session.rollback()
            return 0
