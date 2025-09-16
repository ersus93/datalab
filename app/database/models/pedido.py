#!/usr/bin/env python3
"""Modelo de Pedido para DataLab."""

from datetime import datetime
from app import db

class Pedido(db.Model):
    """Modelo de Pedido."""
    
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_pedido = db.Column(db.String(50), unique=True, nullable=False, index=True)
    descripcion = db.Column(db.Text, nullable=False)
    estado = db.Column(db.String(20), default='pendiente', nullable=False)
    
    # Relación con cliente
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    cliente = db.relationship('Cliente', backref=db.backref('pedidos', lazy=True))
    
    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Pedido {self.numero_pedido}>'
    
    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'numero_pedido': self.numero_pedido,
            'descripcion': self.descripcion,
            'estado': self.estado,
            'cliente_id': self.cliente_id,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }