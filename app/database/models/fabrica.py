#!/usr/bin/env python3
"""Modelo de Fábrica para DataLab."""

from datetime import datetime
from app import db


class Fabrica(db.Model):
    """Modelo de Fábrica.
    
    Representa las plantas o fábricas pertenecientes a un cliente.
    Cada cliente puede tener múltiples fábricas ubicadas en diferentes provincias.
    """
    
    __tablename__ = 'fabricas'
    __table_args__ = (
        db.UniqueConstraint('cliente_id', 'nombre', name='uix_fabrica_cliente_nombre'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    nombre = db.Column(db.String(300), nullable=False)
    provincia_id = db.Column(db.Integer, db.ForeignKey('provincias.id'))
    activo = db.Column(db.Boolean, default=True, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cliente = db.relationship('Cliente', back_populates='fabricas', lazy=True)
    provincia = db.relationship('Provincia', back_populates='fabricas', lazy=True)
    # entradas = relationship pendiente para Phase 2
    
    def __repr__(self):
        return f'<Fabrica {self.nombre}>'
    
    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'nombre': self.nombre,
            'provincia_id': self.provincia_id,
            'activo': self.activo,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None
        }
