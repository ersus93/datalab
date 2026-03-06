#!/usr/bin/env python3
"""Modelo de Ensayos de Evaluación Sensorial para DataLab."""

from datetime import datetime
from app import db


class EnsayoES(db.Model):
    """Ensayos de evaluación sensorial para área ES.

    Mapeo desde Access:
    - IdEnsES (INTEGER) -> id (PK)
    - NomOfic (VARCHAR) -> nombre_oficial
    - NomEnsES (VARCHAR) -> nombre_corto
    - IdArea (INTEGER) -> area_id (FK, =3 para ES)
    - IdTipoES (BYTE) -> tipo_es_id (FK)
    - Precio (CURRENCY) -> precio (DECIMAL)
    - UM (VARCHAR) -> unidad_medida
    - Activo (BIT) -> activo
    """

    __tablename__ = 'ensayos_es'

    id = db.Column(db.Integer, primary_key=True)
    nombre_oficial = db.Column(db.String(500), nullable=False)
    nombre_corto = db.Column(db.String(200), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'), nullable=False, default=3)
    tipo_es_id = db.Column(db.Integer, db.ForeignKey('tipos_es.id'))
    precio = db.Column(db.Numeric(10, 2), nullable=True)
    unidad_medida = db.Column(db.String(10), default='USD')
    activo = db.Column(db.Boolean, default=True, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    area     = db.relationship('Area',   back_populates='ensayos_es')
    tipo_es  = db.relationship('TipoES', back_populates='ensayos_es')

    # Many-to-many con Producto (Phase 1 Issue #3 + Phase 2 Issue #3)
    productos = db.relationship(
        'Producto',
        secondary='ensayos_es_x_productos',
        back_populates='ensayos_es',
        lazy='dynamic',
    )

    def __repr__(self):
        return f'<EnsayoES {self.id}: {self.nombre_corto}>'

    def to_dict(self) -> dict:
        """Convierte el ensayo ES a diccionario para serialización JSON."""
        return {
            'id': self.id,
            'nombre_oficial': self.nombre_oficial,
            'nombre_corto': self.nombre_corto,
            'area_id': self.area_id,
            'tipo_es_id': self.tipo_es_id,
            'precio': str(self.precio) if self.precio else None,
            'unidad_medida': self.unidad_medida,
            'activo': self.activo,
        }
