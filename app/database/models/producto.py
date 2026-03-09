#!/usr/bin/env python3
"""Modelo de Producto para DataLab.

Phase 2 Issue #3 — Product Catalog Module
Phase 1 Issue #3 — Test Catalog Models (relaciones ensayos)
"""

from datetime import datetime
from app import db


class Producto(db.Model):
    """Modelo de Producto.

    Representa los productos que se analizan en el laboratorio.
    Cada producto tiene un destino específico (CF, AC, ME, CD, DE)
    y pertenece a una rama / sector industrial.

    Access mapping:
      - IdProd      -> id
      - NomProd     -> nombre
      - IdDestino   -> destino_id
      - IdRama      -> rama_id   (Phase 2 Issue #3)
      - Activo      -> activo
    """

    __tablename__ = 'productos'

    id         = db.Column(db.Integer, primary_key=True)
    nombre     = db.Column(db.String(300), nullable=False, unique=True)
    destino_id = db.Column(db.Integer, db.ForeignKey('destinos.id'), nullable=True)
    rama_id    = db.Column(db.Integer, db.ForeignKey('ramas.id'),    nullable=True)
    activo     = db.Column(db.Boolean, default=True, nullable=False)
    creado_en  = db.Column(db.DateTime, default=datetime.utcnow)

    # -----------------------------------------------------------------------
    # Relationships
    # -----------------------------------------------------------------------

    destino = db.relationship('Destino', back_populates='productos', lazy=True)
    rama    = db.relationship('Rama',    back_populates='productos', lazy=True)
    pedidos = db.relationship('Pedido',  back_populates='producto',  lazy=True)

    # Many-to-many: ensayos FQ/MB/OS  (Phase 1 Issue #3)
    ensayos = db.relationship(
        'Ensayo',
        secondary='ensayos_x_productos',
        back_populates='productos',
        lazy='dynamic',
    )

    # Many-to-many: ensayos sensoriales ES  (Phase 1 Issue #3 + Phase 2 Issue #3)
    ensayos_es = db.relationship(
        'EnsayoES',
        secondary='ensayos_es_x_productos',
        back_populates='productos',
        lazy='dynamic',
        overlaps="ensayos_es_asociados,producto,ensayo_es,productos_asociados",
    )

    def __repr__(self):
        return f'<Producto {self.nombre}>'

    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id':         self.id,
            'nombre':     self.nombre,
            'destino_id': self.destino_id,
            'rama_id':    self.rama_id,
            'activo':     self.activo,
            'creado_en':  self.creado_en.isoformat() if self.creado_en else None,
        }
