#!/usr/bin/env python3
"""Modelo InformeHistory - Historial de cambios de estado para informes."""

from datetime import datetime

from app import db


class InformeHistory(db.Model):
    """Historial de cambios de estado para informes.

    Registra quién, cuándo y por qué cambió el estado de un informe.
    Mantiene auditoría completa del ciclo de vida del informe.

    Attributes:
        id: Clave primaria.
        informe_id: FK al informe cuyo estado cambió.
        from_status: Estado anterior del informe.
        to_status: Nuevo estado del informe.
        changed_by_id: FK al usuario que realizó el cambio.
        changed_at: Timestamp del cambio de estado.
        reason: Razón o motivo del cambio de estado.
    """

    __tablename__ = "informe_history"

    id = db.Column(db.Integer, primary_key=True)

    informe_id = db.Column(
        db.Integer,
        db.ForeignKey("informes.id", ondelete="CASCADE"),
        nullable=False,
    )

    from_status = db.Column(db.String(20), nullable=False)
    to_status = db.Column(db.String(20), nullable=False)

    changed_by_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    reason = db.Column(db.Text, nullable=True)

    informe = db.relationship("Informe", backref="history", lazy=True)
    changed_by = db.relationship("User", backref="informe_status_changes", lazy=True)

    def __repr__(self):
        return f"<InformeHistory {self.informe_id}: {self.from_status} -> {self.to_status}>"

    def to_dict(self):
        """Serializa el registro de historial a diccionario.

        Returns:
            dict: Representación del registro con todos los campos.
        """
        return {
            "id": self.id,
            "informe_id": self.informe_id,
            "from_status": self.from_status,
            "to_status": self.to_status,
            "changed_by_id": self.changed_by_id,
            "changed_by_nombre": (
                self.changed_by.nombre_completo if self.changed_by else None
            ),
            "changed_at": self.changed_at.isoformat() if self.changed_at else None,
            "reason": self.reason,
        }
