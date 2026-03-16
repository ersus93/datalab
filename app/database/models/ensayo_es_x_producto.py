#!/usr/bin/env python3
"""Tabla de unión EnsayoES-Producto para relación many-to-many.

Phase 1 Issue #3 — Test Catalog Models
Phase 2 Issue #3 — Product Catalog Module

Asocia los 29 ensayos de evaluación sensorial (ES) a los 160 productos del catálogo.
"""

from datetime import datetime
from app import db


class EnsayoESXProducto(db.Model):
    """Tabla de unión para relación many-to-many entre EnsayosES y Productos.

    Permite asociar múltiples ensayos sensoriales a múltiples productos,
    análogo a EnsayoXProducto pero para el área ES.
    """

    __tablename__ = 'ensayos_es_x_productos'

    producto_id = db.Column(
        db.Integer,
        db.ForeignKey('productos.id'),
        primary_key=True,
    )
    ensayo_es_id = db.Column(
        db.Integer,
        db.ForeignKey('ensayos_es.id'),
        primary_key=True,
    )
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    producto  = db.relationship('Producto',  backref=db.backref('ensayos_es_asociados', lazy='dynamic', overlaps="ensayos_es,productos"), overlaps="ensayos_es,productos")
    ensayo_es = db.relationship('EnsayoES',  backref=db.backref('productos_asociados',  lazy='dynamic', overlaps="ensayos_es,productos"), overlaps="ensayos_es,productos")

    __table_args__ = (
        db.Index('ix_ensayos_es_x_productos_producto_id',  'producto_id'),
        db.Index('ix_ensayos_es_x_productos_ensayo_es_id', 'ensayo_es_id'),
    )

    def __repr__(self):
        return f'<EnsayoESXProducto producto={self.producto_id} ensayo_es={self.ensayo_es_id}>'

    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'producto_id':  self.producto_id,
            'ensayo_es_id': self.ensayo_es_id,
            'creado_en':    self.creado_en.isoformat() if self.creado_en else None,
        }
