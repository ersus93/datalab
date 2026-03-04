#!/usr/bin/env python3
"""Modelo de Producto para DataLab."""

from datetime import datetime
from app import db


class Producto(db.Model):
    """Modelo de Producto.
    
    Representa los productos que se analizan en el laboratorio.
    Cada producto tiene un destino específico (CF, AC, ME, CD, DE).
    """
    
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(300), nullable=False, unique=True)
    destino_id = db.Column(db.Integer, db.ForeignKey('destinos.id'))
    activo = db.Column(db.Boolean, default=True, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    destino = db.relationship('Destino', back_populates='productos', lazy=True)
    pedidos = db.relationship('Pedido', back_populates='producto', lazy=True)
    # ensayos = many-to-many via EnsayoXProducto (Phase 2)
    
    def __repr__(self):
        return f'<Producto {self.nombre}>'
    
    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'destino_id': self.destino_id,
            'activo': self.activo,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None
        }
