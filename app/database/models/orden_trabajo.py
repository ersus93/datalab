#!/usr/bin/env python3
"""Modelo de Orden de Trabajo para DataLab."""

from datetime import datetime
from app import db

class OrdenTrabajo(db.Model):
    """Modelo de Orden de Trabajo."""
    
    __tablename__ = 'ordenes_trabajo'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False, index=True)
    descripcion = db.Column(db.Text, nullable=False)
    tipo_analisis = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(20), default='pendiente', nullable=False)
    prioridad = db.Column(db.String(10), default='normal', nullable=False)  # alta, normal, baja
    
    # Relación con pedido
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    pedido = db.relationship('Pedido', backref=db.backref('ordenes_trabajo', lazy=True))
    
    # Fechas importantes
    fecha_inicio = db.Column(db.DateTime, nullable=True)
    fecha_fin_estimada = db.Column(db.DateTime, nullable=True)
    fecha_fin_real = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<OrdenTrabajo {self.numero}>'
    
    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'numero': self.numero,
            'descripcion': self.descripcion,
            'tipo_analisis': self.tipo_analisis,
            'estado': self.estado,
            'prioridad': self.prioridad,
            'pedido_id': self.pedido_id,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin_estimada': self.fecha_fin_estimada.isoformat() if self.fecha_fin_estimada else None,
            'fecha_fin_real': self.fecha_fin_real.isoformat() if self.fecha_fin_real else None,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }