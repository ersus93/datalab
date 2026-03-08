"""
Billing Service - Servicio para gestión de uso y facturación
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict
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

    # ─── NUEVOS MÉTODOS ──────────────────────────────────────────────────────

    @staticmethod
    def get_reporte_mensual(anio: int, mes: int) -> Dict:
        """Reporte de uso para un mes específico.

        Args:
            anio: Año (ej. 2025)
            mes: Mes 1-12

        Returns:
            dict con totales del mes.
        """
        fecha_inicio = date(anio, mes, 1)
        if mes == 12:
            fecha_fin = date(anio + 1, 1, 1) - timedelta(days=1)
        else:
            fecha_fin = date(anio, mes + 1, 1) - timedelta(days=1)

        mes_str = fecha_inicio.strftime('%Y-%m')
        utilizados = Utilizado.query.filter(
            Utilizado.mes_facturacion == mes_str
        ).all()

        clientes_unicos = {u.entrada.cliente_id for u in utilizados if u.entrada and u.entrada.cliente_id}

        return {
            'anio': anio,
            'mes': mes,
            'mes_str': mes_str,
            'total_utilizados': len(utilizados),
            'total_facturado': sum(float(u.importe) for u in utilizados),
            'clientes_unicos': len(clientes_unicos),
            'pendientes': sum(1 for u in utilizados if u.estado == UtilizadoStatus.PENDIENTE.value),
            'facturados': sum(1 for u in utilizados if u.estado == UtilizadoStatus.FACTURADO.value),
        }

    @staticmethod
    def get_comparativo_mensual(anio: int) -> List[Dict]:
        """Comparativo de los 12 meses de un año.

        Args:
            anio: Año a analizar.

        Returns:
            Lista de 12 dicts con datos por mes.
        """
        resultados = []
        nombres_mes = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                       'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        for mes in range(1, 13):
            datos = BillingService.get_reporte_mensual(anio, mes)
            datos['nombre_mes'] = nombres_mes[mes]
            resultados.append(datos)
        return resultados

    @staticmethod
    def get_ranking_ensayos(
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        top_n: int = 20,
        cliente_id: Optional[int] = None,
    ) -> List[Dict]:
        """Top-N ensayos más utilizados en un período.

        Args:
            fecha_inicio: Fecha de inicio del filtro.
            fecha_fin: Fecha de fin del filtro.
            top_n: Máximo de resultados (default 20).
            cliente_id: Filtrar por cliente específico.

        Returns:
            Lista ordenada por cantidad descendente.
        """
        query = db.session.query(
            Ensayo.id,
            Ensayo.nombre_corto,
            Ensayo.area_id,
            func.count(Utilizado.id).label('cantidad'),
            func.sum(Utilizado.importe).label('total_importe'),
        ).join(Utilizado, Utilizado.ensayo_id == Ensayo.id)

        if cliente_id:
            query = query.join(Entrada, Utilizado.entrada_id == Entrada.id).filter(
                Entrada.cliente_id == cliente_id
            )
        if fecha_inicio:
            query = query.filter(Utilizado.fecha_uso >= datetime.combine(fecha_inicio, datetime.min.time()))
        if fecha_fin:
            query = query.filter(Utilizado.fecha_uso <= datetime.combine(fecha_fin, datetime.max.time()))

        resultados = query.group_by(Ensayo.id, Ensayo.nombre_corto, Ensayo.area_id) \
                         .order_by(func.count(Utilizado.id).desc()) \
                         .limit(top_n).all()

        return [
            {
                'ensayo_id': r.id,
                'ensayo': r.nombre_corto,
                'area_id': r.area_id,
                'cantidad': r.cantidad,
                'total_importe': float(r.total_importe) if r.total_importe else 0.0,
            }
            for r in resultados
        ]

    @staticmethod
    def verificar_precios_factura(factura_id: int) -> List[Dict]:
        """Compara precios facturados vs precio actual del catálogo.

        Args:
            factura_id: ID de la factura a verificar.

        Returns:
            Lista de discrepancias (vacía si todo coincide).
        """
        utilizados = Utilizado.query.filter_by(factura_id=factura_id).all()
        discrepancias = []
        for u in utilizados:
            if not u.ensayo:
                continue
            precio_actual = float(u.ensayo.precio_referencia) if hasattr(u.ensayo, 'precio_referencia') and u.ensayo.precio_referencia else 0.0
            precio_facturado = float(u.precio_unitario) if u.precio_unitario else 0.0
            if abs(precio_facturado - precio_actual) > 0.01:
                discrepancias.append({
                    'utilizado_id': u.id,
                    'ensayo': u.ensayo.nombre_corto,
                    'precio_facturado': precio_facturado,
                    'precio_actual': precio_actual,
                    'diferencia': precio_facturado - precio_actual,
                })
        return discrepancias

    @staticmethod
    def verificar_utilizados_sin_facturar(
        cliente_id: Optional[int] = None,
        mes_facturacion: Optional[str] = None,
    ) -> Dict:
        """Detecta ensayos completados que aún no han sido facturados.

        Returns:
            dict con lista de utilizados pendientes y totales.
        """
        query = Utilizado.query.filter(Utilizado.estado == UtilizadoStatus.PENDIENTE.value)
        if cliente_id:
            query = query.join(Entrada).filter(Entrada.cliente_id == cliente_id)
        if mes_facturacion:
            query = query.filter(Utilizado.mes_facturacion == mes_facturacion)

        pendientes = query.all()
        return {
            'cantidad': len(pendientes),
            'total_importe': sum(float(u.importe) for u in pendientes),
            'items': [u.to_dict() for u in pendientes],
        }

    @staticmethod
    def conciliar_factura(factura_id: int) -> Dict:
        """Verifica que el total de la factura coincida con la suma de sus ítems.

        Returns:
            dict con resultado de la conciliación.
        """
        factura = Factura.query.get(factura_id)
        if not factura:
            return {'error': f'Factura {factura_id} no encontrada'}

        utilizados = Utilizado.query.filter_by(factura_id=factura_id).all()
        suma_items = sum(float(u.importe) for u in utilizados if u.estado != UtilizadoStatus.ANULADO.value)
        total_factura = float(factura.total) if factura.total else 0.0
        diferencia = total_factura - suma_items

        return {
            'factura_id': factura_id,
            'numero_factura': factura.numero_factura,
            'total_factura': total_factura,
            'suma_items': suma_items,
            'diferencia': diferencia,
            'ok': abs(diferencia) < 0.01,
        }
