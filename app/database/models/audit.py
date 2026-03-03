#!/usr/bin/env python3
"""Modelo para registro de auditoría."""

from datetime import datetime

from app import db


class AuditLog(db.Model):
    """Registro de auditoría para cambios en datos."""

    __tablename__ = "audit_log"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # CREATE, UPDATE, DELETE
    table_name = db.Column(db.String(100), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    old_values = db.Column(db.JSON, nullable=True)
    new_values = db.Column(db.JSON, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="audit_logs")

    @classmethod
    def log_change(cls, user_id, action, table_name, record_id,
                   old_values=None, new_values=None, ip_address=None):
        """Crear entrada de auditoría."""
        log = cls(
            user_id=user_id,
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address
        )
        db.session.add(log)
        return log

    def to_dict(self):
        """Convertir a diccionario."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "action": self.action,
            "table_name": self.table_name,
            "record_id": self.record_id,
            "old_values": self.old_values,
            "new_values": self.new_values,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
