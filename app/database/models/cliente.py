#!/usr/bin/env python3
"""Modelo de Cliente para DataLab."""

from typing import TYPE_CHECKING, List
from datetime import datetime
from app import db

if TYPE_CHECKING:
    from .fabrica import Fabrica


class Cliente(db.Model):
    """Modelo de Cliente."""

    __tablename__ = "clientes"
    __table_args__ = {"extend_existing": True}
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    direccion = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relación con Organismo
    organismo_id = db.Column(db.Integer, db.ForeignKey('organismos.id'), nullable=True)
    organismo = db.relationship('Organismo', back_populates='clientes', lazy=True)
    
    # Tipo de cliente (para compatibilidad con Access)
    tipo_cliente = db.Column(db.Integer, nullable=True)
    
    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    fabricas = db.relationship(
        'Fabrica',
        back_populates='cliente',
        lazy=True,
        cascade='all, delete-orphan'
    )
    ordenes_trabajo = db.relationship(
        'OrdenTrabajo',
        back_populates='cliente',
        lazy=True
    )
    pedidos = db.relationship(
        'Pedido',
        back_populates='cliente',
        lazy=True
    )
    
    def __repr__(self):
        return f'<Cliente {self.nombre}>'
    
    @property
    def total_fabricas(self) -> int:
        """Contar total de fábricas del cliente."""
        try:
            return len(self.fabricas)  # type: ignore[arg-type]
        except TypeError:
            return 0

    @property
    def total_pedidos(self) -> int:
        """Contar total de pedidos del cliente."""
        try:
            pedidos = getattr(self, 'pedidos', None)  # type: ignore[var-returning]
            if pedidos is not None:
                return len(pedidos)  # type: ignore[arg-type]
            return 0
        except TypeError:
            return 0
    
    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'email': self.email,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'activo': self.activo,
            'organismo_id': self.organismo_id,
            'tipo_cliente': self.tipo_cliente,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'total_fabricas': self.total_fabricas,
            'total_pedidos': self.total_pedidos
        }