"""Modelo Entrada - Sistema de gestión de muestras."""
import re
from datetime import datetime
from decimal import Decimal
from sqlalchemy import event
from sqlalchemy.orm import validates
from flask_babel import _

from app import db


class EntradaStatus:
    """Estados posibles de una entrada."""
    RECIBIDO = 'RECIBIDO'
    EN_PROCESO = 'EN_PROCESO'
    COMPLETADO = 'COMPLETADO'
    ENTREGADO = 'ENTREGADO'
    ANULADO = 'ANULADO'


class Entrada(db.Model):
    """
    Entrada de muestra - TABLA CORE (109 registros).
    
    Representa muestras recibidas de clientes para análisis.
    Cálculo de saldo: cantidad_recib - cantidad_entreg = saldo
    Formato de lote: X-XXXX (letra-4dígitos)
    """
    __tablename__ = 'entradas'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    fabrica_id = db.Column(db.Integer, db.ForeignKey('fabricas.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    rama_id = db.Column(db.Integer, db.ForeignKey('ramas.id'), nullable=True)
    unidad_medida_id = db.Column(db.Integer, db.ForeignKey('unidades_medida.id'), nullable=True)
    
    # Core Fields
    codigo = db.Column(db.String(20), unique=True, nullable=False, index=True)
    lote = db.Column(db.String(10), nullable=True)  # Formato: X-XXXX
    nro_parte = db.Column(db.String(50), nullable=True)
    
    # Quantities - usando Numeric para precisión decimal
    cantidad_recib = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    cantidad_entreg = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    saldo = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    cantidad_muest = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Dates
    fech_fab = db.Column(db.Date, nullable=True)
    fech_venc = db.Column(db.Date, nullable=True)
    fech_muestreo = db.Column(db.Date, nullable=True)
    fech_entrada = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Status Flags
    status = db.Column(
        db.Enum(EntradaStatus.RECIBIDO, EntradaStatus.EN_PROCESO, 
                EntradaStatus.COMPLETADO, EntradaStatus.ENTREGADO,
                EntradaStatus.ANULADO, name='entrada_status'),
        default=EntradaStatus.RECIBIDO,
        nullable=False
    )
    en_os = db.Column(db.Boolean, default=False)  # En orden de servicio
    anulado = db.Column(db.Boolean, default=False)  # Cancelado
    ent_entregada = db.Column(db.Boolean, default=False)  # Entregada
    
    # Metadata
    observaciones = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pedido = db.relationship('Pedido', back_populates='entradas', lazy=True)
    producto = db.relationship('Producto', backref='entradas', lazy=True)
    fabrica = db.relationship('Fabrica', backref='entradas', lazy=True)
    cliente = db.relationship('Cliente', backref='entradas', lazy=True)
    rama = db.relationship('Rama', backref='entradas', lazy=True)
    unidad_medida = db.relationship('UnidadMedida', backref='entradas', lazy=True)
    status_history = db.relationship('StatusHistory', back_populates='entrada', lazy=True)
    
    def __repr__(self):
        return f'<Entrada {self.codigo}>'
    
    def calcular_saldo(self):
        """Calcular saldo actual."""
        self.saldo = self.cantidad_recib - self.cantidad_entreg
        return self.saldo
    
    @validates('lote')
    def validate_lote(self, key, lote):
        """Validar formato de lote X-XXXX."""
        if lote and not re.match(r'^[A-Z]-\d{4}$', lote):
            raise ValueError(_('Formato de lote debe ser X-XXXX (ej: A-1234)'))
        return lote
    
    @validates('fech_venc')
    def validate_fech_venc(self, key, fech_venc):
        """Validar que vencimiento > fabricación."""
        if fech_venc and self.fech_fab and fech_venc < self.fech_fab:
            raise ValueError(_('Fecha de vencimiento debe ser posterior a fabricación'))
        return fech_venc
    
    @validates('cantidad_recib', 'cantidad_entreg')
    def validate_cantidades(self, key, value):
        """Validar cantidades no negativas."""
        if value is not None and value < 0:
            raise ValueError(_('Las cantidades no pueden ser negativas'))
        return value
    
    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'codigo': self.codigo,
            'lote': self.lote,
            'producto': self.producto.nombre if self.producto else None,
            'cliente': self.cliente.nombre if self.cliente else None,
            'fabrica': self.fabrica.nombre if self.fabrica else None,
            'status': self.status,
            'cantidad_recib': str(self.cantidad_recib),
            'cantidad_entreg': str(self.cantidad_entreg),
            'saldo': str(self.saldo),
            'fech_entrada': self.fech_entrada.isoformat() if self.fech_entrada else None
        }


# Event listeners para cálculos automáticos
@event.listens_for(Entrada, 'before_insert')
@event.listens_for(Entrada, 'before_update')
def calculate_balance(mapper, connection, target):
    """Calcular saldo automáticamente antes de guardar."""
    target.calcular_saldo()
    
    # Actualizar flag ent_entregada
    target.ent_entregada = bool(target.saldo <= 0)
    
    # Auto-actualizar status si entregada completamente
    if target.ent_entregada and target.status == EntradaStatus.COMPLETADO:
        target.status = EntradaStatus.ENTREGADO
