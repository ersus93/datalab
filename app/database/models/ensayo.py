#!/usr/bin/env python3
"""Modelo de Ensayos físico-químicos para DataLab."""

from datetime import datetime
from app import db


class Ensayo(db.Model):
    """Ensayos físico-químicos para áreas FQ/MB/OS.

    Mapeo desde Access:
    - IdEns (INTEGER) -> id (PK)
    - NomOfic (VARCHAR) -> nombre_oficial
    - NomEns (VARCHAR) -> nombre_corto
    - IdArea (INTEGER) -> area_id (FK, típicamente 1 para FQ)
    - Precio (CURRENCY) -> precio (DECIMAL)
    - UM (VARCHAR) -> unidad_medida
    - Activo (BIT) -> activo
    - EsEnsayo (BIT) -> es_ensayo
    """

    __tablename__ = 'ensayos'

    id = db.Column(db.Integer, primary_key=True)
    nombre_oficial = db.Column(db.String(500), nullable=False)
    nombre_corto = db.Column(db.String(200), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=True)
    unidad_medida = db.Column(db.String(10), default='USD')
    activo = db.Column(db.Boolean, default=True, nullable=False)
    es_ensayo = db.Column(db.Boolean, default=True, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    area = db.relationship('Area', back_populates='ensayos')
    # detalles = relationship('DetalleEnsayo', back_populates='ensayo') - Phase 2
        utilizados = relationship('Utilizado', back_populates='ensayo') - Phase 2

    # Many-to-many con Producto (Phase 1 Issue #3)
    productos = db.relationship(
        'Producto',
        secondary='ensayos_x_productos',
        back_populates='ensayos',
        lazy='dynamic',
    )

    def __repr__(self):
        return f'<Ensayo {self.id}: {self.nombre_corto}>'

    def get_precio_formateado(self) -> str:
        """Devuelve el precio formateado con moneda."""
        if self.precio:
            return f"{self.unidad_medida} {self.precio:.2f}"
        return "N/A"

    @classmethod
    def get_activos_por_area(cls, area_id: int):
        """Obtiene los ensayos activos para un área específica."""
        return cls.query.filter_by(area_id=area_id, activo=True).all()

    def to_dict(self) -> dict:
        """Convierte el ensayo a diccionario para serialización JSON."""
        return {
            'id': self.id,
            'nombre_oficial': self.nombre_oficial,
            'nombre_corto': self.nombre_corto,
            'area_id': self.area_id,
            'precio': str(self.precio) if self.precio else None,
            'unidad_medida': self.unidad_medida,
            'activo': self.activo,
            'es_ensayo': self.es_ensayo,
        }
