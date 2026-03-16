"""Modelo Notification - Sistema de notificaciones."""
from datetime import datetime

from app import db


class Notification(db.Model):
    """Notificaciones para usuarios."""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Contenido
    type = db.Column(db.String(50), nullable=False)  # 'status_change', 'delivery', etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)

    # Link a entidad relacionada
    entity_type = db.Column(db.String(50), nullable=True)  # 'entrada', 'pedido', etc.
    entity_id = db.Column(db.Integer, nullable=True)

    # Estado
    read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def mark_read(self):
        """Marcar como leída."""
        self.read = True
        self.read_at = datetime.utcnow()

    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'read': self.read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
