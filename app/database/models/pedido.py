"""Modelo Pedido - Órdenes de cliente."""
from datetime import datetime
from sqlalchemy import event
from app import db


class PedidoStatus:
    """Estados posibles de un pedido."""
    PENDIENTE = 'PENDIENTE'
    EN_PROCESO = 'EN_PROCESO'
    COMPLETADO = 'COMPLETADO'


class Pedido(db.Model):
    """
    Pedidos de clientes (49 registros).
    
    Vincula clientes con sus solicitudes de análisis.
    Un pedido puede tener múltiples entradas de muestra.
    """
    __tablename__ = 'pedidos'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    orden_trabajo_id = db.Column(db.Integer, db.ForeignKey('ordenes_trabajo.id'), nullable=True)
    unidad_medida_id = db.Column(db.Integer, db.ForeignKey('unidades_medida.id'), nullable=True)
    
    # Order Information
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    lote = db.Column(db.String(20), nullable=True)
    
    # Dates
    fech_fab = db.Column(db.Date, nullable=True)
    fech_venc = db.Column(db.Date, nullable=True)
    fech_pedido = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Quantity
    cantidad = db.Column(db.Numeric(10, 2), nullable=True)
    
    # Status
    status = db.Column(
        db.Enum(PedidoStatus.PENDIENTE, PedidoStatus.EN_PROCESO, 
                PedidoStatus.COMPLETADO, name='pedido_status'),
        default=PedidoStatus.PENDIENTE,
        nullable=False
    )
    
    # Metadata
    observaciones = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    cliente = db.relationship('Cliente', back_populates='pedidos')
    producto = db.relationship('Producto', back_populates='pedidos')
    orden_trabajo = db.relationship('OrdenTrabajo', back_populates='pedidos')
    unidad_medida = db.relationship('UnidadMedida', back_populates='pedidos')
    entradas = db.relationship('Entrada', back_populates='pedido', lazy='dynamic')
    
    def __repr__(self):
        return f'<Pedido {self.codigo}>'
    
    @property
    def entradas_count(self):
        """Contar entradas relacionadas."""
        return self.entradas.count()
    
    @property
    def entradas_completadas(self):
        """Contar entradas completadas."""
        from app.database.models.entrada import EntradaStatus
        return self.entradas.filter_by(status=EntradaStatus.COMPLETADO).count()
    
    def actualizar_estado(self):
        """Auto-actualizar estado basado en entradas."""
        if self.entradas_count == 0:
            self.status = PedidoStatus.PENDIENTE
        elif self.entradas_completadas == self.entradas_count:
            self.status = PedidoStatus.COMPLETADO
        else:
            self.status = PedidoStatus.EN_PROCESO
    
    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'codigo': self.codigo,
            'cliente': self.cliente.nombre if self.cliente else None,
            'producto': self.producto.nombre if self.producto else None,
            'lote': self.lote,
            'status': self.status,
            'entradas_count': self.entradas_count,
            'entradas_completadas': self.entradas_completadas,
            'fech_pedido': self.fech_pedido.isoformat() if self.fech_pedido else None
        }


# Event listener para auto-actualizar estado desde entradas
@event.listens_for(Pedido, 'before_update')
def check_status_update(mapper, connection, target):
    """Verificar si necesita actualizar estado."""
    target.actualizar_estado()
