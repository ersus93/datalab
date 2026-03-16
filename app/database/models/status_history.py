"""Modelo StatusHistory - Auditoría de cambios de estado."""
from datetime import datetime

from app import db


class StatusHistory(db.Model):
    """
    Historial de cambios de estado para entradas.
    Registra quién, cuándo y por qué cambió el estado.
    """
    __tablename__ = 'status_history'

    id = db.Column(db.Integer, primary_key=True)
    entrada_id = db.Column(db.Integer, db.ForeignKey('entradas.id'), nullable=False)

    # Cambio de estado
    from_status = db.Column(db.String(20), nullable=False)
    to_status = db.Column(db.String(20), nullable=False)

    # Quién y cuándo
    changed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Por qué
    reason = db.Column(db.Text, nullable=True)
    meta_data = db.Column(db.JSON, nullable=True)  # Contexto adicional (metadata es reservado)

    # Relationships
    entrada = db.relationship('Entrada', back_populates='status_history')
    changed_by = db.relationship('User', backref='status_changes')

    def __repr__(self):
        return f'<StatusHistory {self.entrada_id}: {self.from_status} -> {self.to_status}>'

    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'from_status': self.from_status,
            'to_status': self.to_status,
            'changed_by': self.changed_by.nombre_completo if self.changed_by else None,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None,
            'reason': self.reason
        }
