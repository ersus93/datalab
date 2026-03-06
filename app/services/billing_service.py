"""
Billing Service - Servicio para gestión de uso y facturación
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import func
from app import db
from app.database.models.utilizado import Utilizado, UtilizadoStatus, Factura
from app.database.models.ensayo import Ensayo
from app.database.models.entrada import Entrada


class BillingService:
    """Servicio para tracking de uso y generación de facturas."""
    
    @staticmethod
    def crear_utilizado(
        entrada_id: int,
        ensayo_id: int,
        cantidad: float = 1,
        precio_unitario: float = 0,
        detalle_ensayo_id: Optional[int] = None
    ) -> Utilizado:
        """Crea un registro de uso para un ensayo en una entrada."""
        utilizado = Utilizado(
            entrada_id=entrada_id,
            ensayo_id=ensayo_id,
            detalle_ensayo_id=detalle_ensayo_id,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            fecha_uso=datetime.utcnow()
        )
        utilizado.calcular_importe()
        
        # Determinar mes de facturación
        if utilizado.fecha_uso:
            utilizado.mes_facturacion = utilizado.fecha_uso.strftime('%Y-%m')
        
        db.session.add(utilizado)
        db.session.commit()
        return utilizado
    
    @staticmethod
    def crear_desde_detalle_ensayo(detalle_ensayo_id: int, precio_unitario: float = 0) -> Utilizado:
        """Crea un registro de uso desde un DetalleEnsayo completado."""
        from app.database.models.detalle_ensayo import DetalleEnsayo
        
        detalle = DetalleEnsayo.query.get(detalle_ensayo_id)
        if not detalle:
            raise ValueError(f"DetalleEnsayo {detalle_ensayo_id} no encontrado")
        
        if detalle.estado != 'COMPLETADO':
            raise ValueError(f"El ensayo debe estar COMPLETADO para facturar")
        
        return BillingService.crear_utilizado(
            entrada_id=detalle.entrada_id,
            ensayo_id=detalle.ensayo_id,
            cantidad=1,
            precio_unitario=precio_unitario,
            detalle_ensayo_id=detalle_ensayo_id
        )
    
    @staticmethod
    def get_utilizados_por_cliente(
        cliente_id: int,
        estado: Optional[str] = None,
        mes_facturacion: Optional[str] = None
    ) -> List[Utilizado]:
        """Obtiene los registros de uso de un cliente."""
        query = Utilizado.query.join(Entrada).filter(Entrada.cliente_id == cliente_id)
        
        if estado:
            query = query.filter(Utilizado.estado == estado)
        if mes_facturacion:
            query = query.filter(Utilizado.mes_facturacion == mes_facturacion)
        
        return query.all()
    
    @staticmethod
    def get_utilizados_pendientes_facturacion(
        cliente_id: Optional[int] = None,
        mes_facturacion: Optional[str] = None
    ) -> List[Utilizado]:
        """Obtiene los registros pendientes de facturación."""
        query = Utilizado.query.filter(Utilizado.estado == UtilizadoStatus.PENDIENTE.value)
        
        if cliente_id:
            query = query.join(Entrada).filter(Entrada.cliente_id == cliente_id)
        if mes_facturacion:
            query = query.filter(Utilizado.mes_facturacion == mes_facturacion)
        
        return query.all()
    
    @staticmethod
    def generar_factura(
        cliente_id: int,
        utilizado_ids: List[int],
        numero_factura: str,
        fecha_vencimiento: Optional[datetime] = None
    ) -> Factura:
        """Genera una factura a partir de registros de uso."""
        # Verificar que todos los utilizados pertenecen al cliente y están pendientes
        utilizados = Utilizado.query.filter(
            Utilizado.id.in_(utilizado_ids),
            Utilizado.estado == UtilizadoStatus.PENDIENTE.value
        ).all()
        
        if not utilizados:
            raise ValueError("No hay registros pendientes para facturar")
        
        # Verificar que todos pertenecen al mismo cliente
        for u in utilizados:
            if u.entrada.cliente_id != cliente_id:
                raise ValueError(f"El registro {u.id} no pertenece al cliente {cliente_id}")
        
        # Crear factura
        factura = Factura(
            cliente_id=cliente_id,
            numero_factura=numero_factura,
            fecha_emision=datetime.utcnow(),
            fecha_vencimiento=fecha_vencimiento
        )
        db.session.add(factura)
        db.session.flush()  # Obtener el ID
        
        # Vincular utilizados a la factura
        total = 0
        for u in utilizados:
            u.factura_id = factura.id
            u.estado = UtilizadoStatus.FACTURADO.value
            total += float(u.importe)
        
        factura.total = total
        db.session.commit()
        
        return factura
    
    @staticmethod
    def get_resumen_por_tipo_ensayo(
        cliente_id: Optional[int] = None,
        mes_facturacion: Optional[str] = None
    ) -> dict:
        """Obtiene resumen de usage por tipo de ensayo."""
        query = db.session.query(
            Ensayo.nombre_corto,
            Ensayo.area_id,
            func.count(Utilizado.id).label('cantidad'),
            func.sum(Utilizado.importe).label('total')
        ).join(Utilizado, Utilizado.ensayo_id == Ensayo.id)
        
        if cliente_id:
            query = query.join(Entrada).filter(Entrada.cliente_id == cliente_id)
        if mes_facturacion:
            query = query.filter(Utilizado.mes_facturacion == mes_facturacion)
        
        results = query.group_by(Ensayo.id).all()
        
        return {
            'items': [
                {
                    'ensayo': r[0],
                    'area_id': r[1],
                    'cantidad': r[2],
                    'total': float(r[3]) if r[3] else 0
                }
                for r in results
            ]
        }
    
    @staticmethod
    def get_reporte_facturacion(
        cliente_id: Optional[int] = None,
        fecha_inicio: Optional[datetime] = None,
        fecha_fin: Optional[datetime] = None
    ) -> dict:
        """Genera reporte de facturación."""
        query = Factura.query
        
        if cliente_id:
            query = query.filter(Factura.cliente_id == cliente_id)
        if fecha_inicio:
            query = query.filter(Factura.fecha_emision >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Factura.fecha_emision <= fecha_fin)
        
        facturas = query.all()
        
        return {
            'facturas': [f.to_dict() for f in facturas],
            'total_facturado': sum(float(f.total) for f in facturas),
            'cantidad': len(facturas)
        }
