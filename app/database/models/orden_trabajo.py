"""Modelo OrdenTrabajo - Órdenes de trabajo."""
from datetime import datetime
from app import db


class OTStatus:
    """Estados de orden de trabajo."""
    PENDIENTE = 'PENDIENTE'
    EN_PROGRESO = 'EN_PROGRESO'
    COMPLETADA = 'COMPLETADA'


class OrdenTrabajo(db.Model):
    """
    Órdenes de trabajo para organizar solicitudes de clientes (37 registros).
    
    Las OT agrupan múltiples pedidos y sirven como unidad primaria
    para facturación y seguimiento de entregas.
    Número oficial (NroOfic) se usa para referencia externa.
    """
    __tablename__ = 'ordenes_trabajo'
    __table_args__ = {"extend_existing": True}
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    
    # Identification
    nro_ofic = db.Column(db.String(30), unique=True, nullable=False)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    
    # Content
    descripcion = db.Column(db.Text, nullable=True)
    observaciones = db.Column(db.Text, nullable=True)
    
    # Status
    status = db.Column(
        db.Enum(OTStatus.PENDIENTE, OTStatus.EN_PROGRESO, OTStatus.COMPLETADA, name='ot_status'),
        default=OTStatus.PENDIENTE,
        nullable=False
    )
    
    # Dates
    fech_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fech_completado = db.Column(db.DateTime, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    cliente = db.relationship('Cliente', back_populates='ordenes_trabajo')
    pedidos = db.relationship('Pedido', back_populates='orden_trabajo', lazy='dynamic')
    
    def __repr__(self):
        return f'<OrdenTrabajo {self.nro_ofic}>'
    
    @property
    def pedidos_count(self):
        """Contar pedidos relacionados."""
        return self.pedidos.count()
    
    @property
    def entradas_count(self):
        """Contar total de entradas en todos los pedidos."""
        return sum(p.entradas_count for p in self.pedidos)
    
    @property
    def progreso(self):
        """Calcular porcentaje de completitud."""
        if self.pedidos_count == 0:
            return 0
        from app.database.models.pedido import PedidoStatus
        completados = sum(1 for p in self.pedidos if p.status == PedidoStatus.COMPLETADO)
        return int((completados / self.pedidos_count) * 100)
    
    def actualizar_estado(self):
        """Auto-actualizar estado basado en pedidos."""
        from app.database.models.pedido import PedidoStatus
        
        if self.pedidos_count == 0:
            self.status = OTStatus.PENDIENTE
            self.fech_completado = None
        elif all(p.status == PedidoStatus.COMPLETADO for p in self.pedidos):
            self.status = OTStatus.COMPLETADA
            if not self.fech_completado:
                self.fech_completado = datetime.utcnow()
        else:
            self.status = OTStatus.EN_PROGRESO
            self.fech_completado = None
    
    def to_dict(self):
        """Convertir a diccionario."""
        return {
            'id': self.id,
            'nro_ofic': self.nro_ofic,
            'codigo': self.codigo,
            'cliente': self.cliente.nombre if self.cliente else None,
            'descripcion': self.descripcion,
            'status': self.status,
            'progreso': self.progreso,
            'pedidos_count': self.pedidos_count,
            'entradas_count': self.entradas_count,
            'fech_creacion': self.fech_creacion.isoformat() if self.fech_creacion else None,
            'fech_completado': self.fech_completado.isoformat() if self.fech_completado else None
        }
