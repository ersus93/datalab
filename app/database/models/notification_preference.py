"""Modelo NotificationPreference - Preferencias de notificaciones de usuario."""
from datetime import datetime

from app import db


class NotificationPreference(db.Model):
    """Preferencias de notificaciones para cada usuario."""

    __tablename__ = "notification_preferences"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True,
        index=True
    )

    # Canales de notificación habilitados
    email_enabled = db.Column(db.Boolean, default=True, nullable=False)
    in_app_enabled = db.Column(db.Boolean, default=True, nullable=False)

    # Tipos de notificación por email
    status_change_email = db.Column(db.Boolean, default=True, nullable=False)
    delivery_email = db.Column(db.Boolean, default=True, nullable=False)
    pending_alert_email = db.Column(db.Boolean, default=True, nullable=False)

    # Timestamps
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relaciones
    user = db.relationship(
        "User",
        back_populates="notification_preferences",
        lazy=True
    )

    def __repr__(self):
        return f"<NotificationPreference user_id={self.user_id}>"

    def to_dict(self):
        """Convertir preferencias a diccionario."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "email_enabled": self.email_enabled,
            "in_app_enabled": self.in_app_enabled,
            "status_change_email": self.status_change_email,
            "delivery_email": self.delivery_email,
            "pending_alert_email": self.pending_alert_email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def should_send_email(self, notification_type):
        """Verificar si debe enviarse email según tipo de notificación.

        Args:
            notification_type: Tipo de notificación ('status_change', 'delivery', 'pending_alert', etc.)

        Returns:
            bool: True si debe enviarse email, False en caso contrario.
        """
        if not self.email_enabled:
            return False

        type_mapping = {
            "status_change": self.status_change_email,
            "delivery": self.delivery_email,
            "pending_alert": self.pending_alert_email,
        }

        return type_mapping.get(notification_type, True)

    def should_send_in_app(self, notification_type):
        """Verificar si debe enviarse notificación in-app.

        Args:
            notification_type: Tipo de notificación (ignorado en verificación básica).

        Returns:
            bool: True si debe enviarse notificación in-app, False en caso contrario.
        """
        return self.in_app_enabled

    @classmethod
    def get_or_create(cls, user_id):
        """Obtener preferencias existentes o crear nuevas con valores por defecto.

        Args:
            user_id: ID del usuario.

        Returns:
            NotificationPreference: Instancia de preferencias del usuario.
        """
        pref = cls.query.filter_by(user_id=user_id).first()
        if pref is None:
            pref = cls(user_id=user_id)
            db.session.add(pref)
            db.session.commit()
        return pref
