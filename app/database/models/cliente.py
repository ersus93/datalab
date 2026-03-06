#!/usr/bin/env python3
"""Modelo de Cliente para DataLab."""

from typing import TYPE_CHECKING, List
from datetime import datetime
from app import db
n# Relationship added for billing


if TYPE_CHECKING:
    from .fabrica import Fabrica


class Cliente(db.Model):
class Cliente(db.Model):
    """Modelo de Cliente."""
    """Modelo de Cliente."""


    __tablename__ = "clientes"
    __tablename__ = "clientes"
    __table_args__ = {"extend_existing": True}
    __table_args__ = {"extend_existing": True}
    
    
    id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False, index=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(200), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)
    direccion = db.Column(db.Text, nullable=True)
    direccion = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    
    
    # Relación con Organismo
    # Relación con Organismo
    organismo_id = db.Column(db.Integer, db.ForeignKey('organismos.id'), nullable=True)
    organismo_id = db.Column(db.Integer, db.ForeignKey('organismos.id'), nullable=True)
    organismo = db.relationship('Organismo', back_populates='clientes', lazy=True)
    organismo = db.relationship('Organismo', back_populates='clientes', lazy=True)
    
    
    # Tipo de cliente (para compatibilidad con Access)
    # Tipo de cliente (para compatibilidad con Access)
    tipo_cliente = db.Column(db.Integer, nullable=True)
    tipo_cliente = db.Column(db.Integer, nullable=True)
    
    
    # Timestamps
    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    
    # Relaciones
    # Relaciones
    fabricas = db.relationship(
    fabricas = db.relationship(
        'Fabrica',
        'Fabrica',
        back_populates='cliente',
        back_populates='cliente',
        lazy=True,
        lazy=True,
        cascade='all, delete-orphan'
        cascade='all, delete-orphan'
    )
    )
    ordenes_trabajo = db.relationship(
    ordenes_trabajo = db.relationship(
        'OrdenTrabajo',
        'OrdenTrabajo',
        back_populates='cliente',
        back_populates='cliente',
        lazy=True
        lazy=True
    )
    )
    pedidos = db.relationship(
    pedidos = db.relationship(
        'Pedido',
        'Pedido',
        back_populates='cliente',
        back_populates='cliente',
        lazy=True
        lazy=True
    )
    )
    
    
    def __repr__(self):
    def __repr__(self):
        return f'<Cliente {self.nombre}>'
        return f'<Cliente {self.nombre}>'
    
    
    @property
    @property
    def total_fabricas(self) -> int:
    def total_fabricas(self) -> int:
        """Contar total de fábricas del cliente."""
        """Contar total de fábricas del cliente."""
        try:
        try:
            return len(self.fabricas)  # type: ignore[arg-type]
            return len(self.fabricas)  # type: ignore[arg-type]
        except TypeError:
        except TypeError:
            return 0
            return 0


    @property
    @property
    def total_pedidos(self) -> int:
    def total_pedidos(self) -> int:
        """Contar total de pedidos del cliente."""
        """Contar total de pedidos del cliente."""
        try:
        try:
            pedidos = getattr(self, 'pedidos', None)  # type: ignore[var-returning]
            pedidos = getattr(self, 'pedidos', None)  # type: ignore[var-returning]
            if pedidos is not None:
            if pedidos is not None:
                return len(pedidos)  # type: ignore[arg-type]
                return len(pedidos)  # type: ignore[arg-type]
            return 0
            return 0
        except TypeError:
        except TypeError:
            return 0
            return 0
    
    
    def to_dict(self):
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