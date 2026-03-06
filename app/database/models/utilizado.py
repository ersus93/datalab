"""
Modelo Utilizado - Tracking de uso y facturación de ensayos

Este modelo registra el uso de ensayos por entrada/producto para facturación.
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import ForeignKey, Numeric, Index
from sqlalchemy.orm import relationship
from app import db


class UtilizadoStatus(str, Enum):
    """Estados del registro de uso para facturación."""
    PENDIENTE = "PENDIENTE"
    FACTURADO = "FACTURADO"
    ANULADO = "ANULADO"


class Utilizado(db.Model):
    """
    Modelo para tracking de uso de ensayos y facturación.
    
    Relaciona las entradas con los ensayos ejecutados para permitir
    el seguimiento de uso y generación de facturas.
    """
    __tablename__ = 'utilizados'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    entrada_id = db.Column(db.Integer, ForeignKey('entradas.id'), nullable=False, index=True)
    detalle_ensayo_id = db.Column(db.Integer, ForeignKey('detalle_ensayos.id'), nullable=True, index=True)
    ensayo_id = db.Column(db.Integer, ForeignKey('ensayos.id'), nullable=False, index=True)
    factura_id = db.Column(db.Integer, ForeignKey('facturas.id'), nullable=True, index=True)
    
    # Campos financieros
    cantidad = db.Column(db.Numeric(10, 2), nullable=False, default=1)
    precio_unitario = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    importe = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    
    # Campos de tracking
    fecha_uso = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    mes_facturacion = db.Column(db.String(7), nullable=True)  # Format: YYYY-MM
    estado = db.Column(db.String(20), nullable=False, default=UtilizadoStatus.PENDIENTE.value)
    
    # Timestamps
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    entrada = relationship('Entrada', back_populates='utilizados')
    detalle_ensayo = relationship('DetalleEnsayo', back_populates='utilizados')
    ensayo = relationship('Ensayo', back_populates='utilizados')
    factura = relationship('Factura', back_populates='utilizados')
    
    def __repr__(self):
        return f'<Utilizado {self.id} - Ensayo {self.ensayo_id}>'
    
    def calcular_importe(self):
        """Calcula el importe: cantidad * precio_unitario"""
        self.importe = self.cantidad * self.precio_unitario
        return self.importe
    
    def to_dict(self):
        return {
            'id': self.id,
            'entrada_id': self.entrada_id,
            'detalle_ensayo_id': self.detalle_ensayo_id,
            'ensayo_id': self.ensayo_id,
            'factura_id': self.factura_id,
            'cantidad': float(self.cantidad) if self.cantidad else 0,
            'precio_unitario': float(self.precio_unitario) if self.precio_unitario else 0,
            'importe': float(self.importe) if self.importe else 0,
            'fecha_uso': self.fecha_uso.isoformat() if self.fecha_uso else None,
            'mes_facturacion': self.mes_facturacion,
            'estado': self.estado,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None
        }


class Factura(db.Model):
    """
    Modelo para facturas generadas a partir de usages.
    """
    __tablename__ = 'facturas'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, ForeignKey('clientes.id'), nullable=False, index=True)
    numero_factura = db.Column(db.String(50), unique=True, nullable=False)
    fecha_emision = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fecha_vencimiento = db.Column(db.DateTime, nullable=True)
    total = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    estado = db.Column(db.String(20), nullable=False, default='BORRADOR')  # BORRADOR, EMITIDA, PAGADA, ANULADA
    
    # Timestamps
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cliente = relationship('Cliente', back_populates='facturas')
    utilizados = relationship('Utilizado', back_populates='factura')
    
    def __repr__(self):
        return f'<Factura {self.numero_factura}>'
    
    def calcular_total(self):
        """Calcula el total de la factura sumando los importados."""
        self.total = sum(u.importe for u in self.utilizados if u.estado != 'ANULADO')
        return self.total
    
    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'numero_factura': self.numero_factura,
            'fecha_emision': self.fecha_emision.isoformat() if self.fecha_emision else None,
            'total': float(self.total) if self.total else 0,
            'estado': self.estado,
            'utilizados_count': len(self.utilizados)
        }


# Índices para optimización
Index('idx_utilizado_entrada_fecha', Utilizado.entrada_id, Utilizado.fecha_uso)
Index('idx_utilizado_estado_facturacion', Utilizado.estado, Utilizado.mes_facturacion)
Index('idx_utilizado_factura', Utilizado.factura_id)
