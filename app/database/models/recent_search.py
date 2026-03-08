#!/usr/bin/env python3
"""Modelo de Búsquedas Recientes por Usuario."""

from datetime import datetime

from app import db


class RecentSearch(db.Model):
    """Modelo de búsquedas recientes realizadas por usuarios."""

    __tablename__ = "recent_searches"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    query = db.Column(db.String(200), nullable=False)

    # Timestamps
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con usuario
    user = db.relationship("User", backref=db.backref("recent_searches", lazy="dynamic", cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<RecentSearch user_id={self.user_id} query="{self.query}">'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'query': self.query,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None
        }
