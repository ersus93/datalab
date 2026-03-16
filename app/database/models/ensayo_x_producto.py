#!/usr/bin/env python3
"""Tabla de unión Ensayo-Producto para relación many-to-many."""

from datetime import datetime
from app import db


class EnsayoXProducto(db.Model):
    """Tabla de unión para relación many-to-many entre Ensayos y Productos.
    
    Permite asociar múltiples ensayos a múltiples productos.
    """
    
    __tablename__ = 'ensayos_x_productos'
    
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), primary_key=True)
    ensayo_id = db.Column(db.Integer, db.ForeignKey('ensayos.id'), primary_key=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EnsayoXProducto producto={self.producto_id} ensayo={self.ensayo_id}>'
    
    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'producto_id': self.producto_id,
            'ensayo_id': self.ensayo_id,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None
        }
