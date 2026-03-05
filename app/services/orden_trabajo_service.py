"""Servicio de negocio para gestión de Ordenes de Trabajo."""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from flask_babel import _
from sqlalchemy import asc, desc, func

from app import db


class OrdenTrabajoService:
    """
    Servicio de negocio para operaciones con Ordenes de Trabajo.

    Encapsula la logica de negocio para creacion, actualizacion,
    eliminacion y consulta de ordenes de trabajo.
    """

    @staticmethod
    def _generar_codigo() -> str:
        """
        Generar codigo unico para la orden de trabajo.

        Formato: OT-YYYY-NNNN (ej: OT-2024-0001)

        Returns:
            str: Codigo generado
        """
        from app.database.models.orden_trabajo import OrdenTrabajo

        year = datetime.utcnow().year
        prefix = f"OT-{year}-"

        # Obtener el ultimo codigo del año actual
        ultimo = OrdenTrabajo.query.filter(
            OrdenTrabajo.codigo.like(f"{prefix}%")
        ).order_by(desc(OrdenTrabajo.id)).first()

        if ultimo:
            # Extraer numero del ultimo codigo
            try:
                numero = int(ultimo.codigo.split('-')[-1]) + 1
            except (ValueError, IndexError):
                numero = 1
        else:
            numero = 1

        return f"{prefix}{numero:04d}"

    @staticmethod
    def _validar_nro_ofic_unico(nro_ofic: str) -> None:
        """
        Validar que el numero oficial no exista.

        Args:
            nro_ofic: Numero oficial a validar

        Raises:
            ValueError: Si el numero oficial ya existe
        """
        from app.database.models.orden_trabajo import OrdenTrabajo

        existente = OrdenTrabajo.query.filter_by(nro_ofic=nro_ofic).first()
        if existente:
            raise ValueError(
                _('El numero oficial "%(nro)s" ya existe', nro=nro_ofic)
            )

    @classmethod
    def crear_orden_trabajo(cls, data: Dict[str, Any], usuario_id: int) -> Any:
        """
        Crear nueva orden de trabajo.

        Realiza validaciones de negocio, genera codigo automaticamente
        y establece el estado inicial como PENDIENTE.

        Args:
            data: Diccionario con datos de la orden de trabajo
            usuario_id: ID del usuario que crea la orden

        Returns:
            OrdenTrabajo: Instancia creada

        Raises:
            ValueError: Si fallan las validaciones de negocio
        """
        from app.database.models.orden_trabajo import OrdenTrabajo, OTStatus

        # Validar campos requeridos
        cliente_id = data.get('cliente_id')
        nro_ofic = data.get('nro_ofic')

        if not cliente_id:
            raise ValueError(_('El cliente es obligatorio'))
        if not nro_ofic:
            raise ValueError(_('El numero oficial es obligatorio'))

        # Validar que nro_ofic sea unico
        cls._validar_nro_ofic_unico(nro_ofic)

        # Generar codigo
        codigo = cls._generar_codigo()

        # Crear orden de trabajo
        orden = OrdenTrabajo(
            codigo=codigo,
            nro_ofic=nro_ofic,
            cliente_id=cliente_id,
            descripcion=data.get('descripcion'),
            observaciones=data.get('observaciones'),
            status=OTStatus.PENDIENTE,
            fech_creacion=datetime.utcnow()
        )

        db.session.add(orden)
        db.session.commit()

        return orden

    @classmethod
    def obtener_orden_por_id(cls, orden_id: int) -> Optional[Any]:
        """
        Obtener orden de trabajo por su ID.

        Args:
            orden_id: ID de la orden de trabajo

        Returns:
            OrdenTrabajo: Instancia encontrada o None
        """
        from app.database.models.orden_trabajo import OrdenTrabajo
        return OrdenTrabajo.query.get(orden_id)

    @classmethod
    def actualizar_orden(cls, orden_id: int, data: Dict[str, Any],
                         usuario_id: int) -> Any:
        """
        Actualizar orden de trabajo existente.

        Revalida datos modificados y actualiza el estado segun pedidos.

        Args:
            orden_id: ID de la orden a actualizar
            data: Diccionario con campos a actualizar
            usuario_id: ID del usuario que realiza la actualizacion

        Returns:
            OrdenTrabajo: Instancia actualizada

        Raises:
            ValueError: Si la orden no existe o fallan las validaciones
        """
        from app.database.models.orden_trabajo import OrdenTrabajo

        orden = OrdenTrabajo.query.get(orden_id)
        if not orden:
            raise ValueError(_('Orden de trabajo no encontrada'))

        # Validar nro_ofic si se esta cambiando
        if 'nro_ofic' in data and data['nro_ofic'] != orden.nro_ofic:
            cls._validar_nro_ofic_unico(data['nro_ofic'])
            orden.nro_ofic = data['nro_ofic']

        # Actualizar campos
        campos_actualizables = [
            'cliente_id', 'descripcion', 'observaciones'
        ]
        for campo in campos_actualizables:
            if campo in data:
                setattr(orden, campo, data[campo])

        # Recalcular estado basado en pedidos
        orden.actualizar_estado()

        db.session.commit()

        return orden

    @classmethod
    def eliminar_orden(cls, orden_id: int, usuario_id: int) -> Any:
        """
        Eliminar orden de trabajo (soft delete).

        Cambia el estado a ELIMINADA en lugar de borrar fisicamente.

        Args:
            orden_id: ID de la orden a eliminar
            usuario_id: ID del usuario que realiza la eliminacion

        Returns:
            OrdenTrabajo: Instancia marcada como eliminada

        Raises:
            ValueError: Si la orden no existe
        """
        from app.database.models.orden_trabajo import OrdenTrabajo

        orden = OrdenTrabajo.query.get(orden_id)
        if not orden:
            raise ValueError(_('Orden de trabajo no encontrada'))

        # Soft delete: cambiar estado a ELIMINADA
        orden.status = 'ELIMINADA'

        db.session.commit()

        return orden

    @classmethod
    def obtener_ordenes_paginadas(
        cls,
        filtros: Optional[Dict[str, Any]] = None,
        pagina: int = 1,
        por_pagina: int = 20,
        ordenar_por: str = 'fech_creacion',
        orden: str = 'desc'
    ) -> Tuple[List[Any], Dict[str, Any]]:
        """
        Obtener ordenes de trabajo paginadas con filtros.

        Args:
            filtros: Diccionario con filtros opcionales:
                    - cliente_id: Filtrar por cliente
                    - status: Filtrar por estado
                    - nro_ofic: Filtrar por numero oficial (busqueda parcial)
                    - fecha_desde: Fecha inicial (inclusive)
                    - fecha_hasta: Fecha final (inclusive)
            pagina: Numero de pagina (1-based)
            por_pagina: Cantidad de registros por pagina
            ordenar_por: Campo para ordenar
            orden: 'asc' o 'desc'

        Returns:
            Tuple: (lista_de_ordenes, metadata_de_paginacion)
        """
        from app.database.models.orden_trabajo import OrdenTrabajo

        filtros = filtros or {}
        query = OrdenTrabajo.query

        # Aplicar filtros
        if filtros.get('cliente_id'):
            query = query.filter(OrdenTrabajo.cliente_id == filtros['cliente_id'])

        if filtros.get('status'):
            query = query.filter(OrdenTrabajo.status == filtros['status'])

        if filtros.get('nro_ofic'):
            query = query.filter(
                OrdenTrabajo.nro_ofic.ilike(f"%{filtros['nro_ofic']}%")
            )

        if filtros.get('fecha_desde'):
            query = query.filter(OrdenTrabajo.fech_creacion >= filtros['fecha_desde'])

        if filtros.get('fecha_hasta'):
            query = query.filter(OrdenTrabajo.fech_creacion <= filtros['fecha_hasta'])

        # Aplicar ordenamiento
        columna_orden = getattr(OrdenTrabajo, ordenar_por, OrdenTrabajo.fech_creacion)
        if orden.lower() == 'desc':
            query = query.order_by(desc(columna_orden))
        else:
            query = query.order_by(asc(columna_orden))

        # Paginacion
        paginacion = query.paginate(
            page=pagina,
            per_page=por_pagina,
            error_out=False
        )

        # Metadata de paginacion
        meta = {
            'pagina': pagina,
            'por_pagina': por_pagina,
            'total': paginacion.total,
            'total_paginas': paginacion.pages,
            'tiene_siguiente': paginacion.has_next,
            'tiene_anterior': paginacion.has_prev,
            'siguiente_pagina': paginacion.next_num if paginacion.has_next else None,
            'pagina_anterior': paginacion.prev_num if paginacion.has_prev else None
        }

        return paginacion.items, meta

    @classmethod
    def asignar_pedido(cls, orden_id: int, pedido_id: int,
                       usuario_id: int) -> Any:
        """
        Asignar un pedido a una orden de trabajo.

        Args:
            orden_id: ID de la orden de trabajo
            pedido_id: ID del pedido a asignar
            usuario_id: ID del usuario que realiza la asignacion

        Returns:
            OrdenTrabajo: Instancia actualizada

        Raises:
            ValueError: Si la orden o el pedido no existen
        """
        from app.database.models.orden_trabajo import OrdenTrabajo
        from app.database.models.pedido import Pedido

        orden = OrdenTrabajo.query.get(orden_id)
        if not orden:
            raise ValueError(_('Orden de trabajo no encontrada'))

        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            raise ValueError(_('Pedido no encontrado'))

        # Asignar pedido a la orden
        pedido.orden_trabajo_id = orden_id

        # Actualizar estado de la orden
        orden.actualizar_estado()

        db.session.commit()

        return orden

    @classmethod
    def quitar_pedido(cls, orden_id: int, pedido_id: int,
                      usuario_id: int) -> Any:
        """
        Quitar un pedido de una orden de trabajo.

        Args:
            orden_id: ID de la orden de trabajo
            pedido_id: ID del pedido a quitar
            usuario_id: ID del usuario que realiza la operacion

        Returns:
            OrdenTrabajo: Instancia actualizada

        Raises:
            ValueError: Si la orden o el pedido no existen,
                       o si el pedido no pertenece a la orden
        """
        from app.database.models.orden_trabajo import OrdenTrabajo
        from app.database.models.pedido import Pedido

        orden = OrdenTrabajo.query.get(orden_id)
        if not orden:
            raise ValueError(_('Orden de trabajo no encontrada'))

        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            raise ValueError(_('Pedido no encontrado'))

        # Verificar que el pedido pertenezca a la orden
        if pedido.orden_trabajo_id != orden_id:
            raise ValueError(
                _('El pedido %(pedido)s no pertenece a esta orden de trabajo',
                  pedido=pedido.codigo)
            )

        # Quitar pedido de la orden
        pedido.orden_trabajo_id = None

        # Actualizar estado de la orden
        orden.actualizar_estado()

        db.session.commit()

        return orden

    @classmethod
    def buscar_por_nro_ofic(cls, nro_ofic: str) -> Optional[Any]:
        """
        Buscar orden de trabajo por numero oficial.

        Args:
            nro_ofic: Numero oficial a buscar

        Returns:
            OrdenTrabajo: Instancia encontrada o None
        """
        from app.database.models.orden_trabajo import OrdenTrabajo
        return OrdenTrabajo.query.filter_by(nro_ofic=nro_ofic).first()

    @classmethod
    def obtener_pedidos_de_orden(cls, orden_id: int) -> List[Dict[str, Any]]:
        """
        Obtener pedidos asignados a una orden de trabajo.

        Args:
            orden_id: ID de la orden de trabajo

        Returns:
            List[Dict]: Lista de pedidos con su informacion

        Raises:
            ValueError: Si la orden no existe
        """
        from app.database.models.orden_trabajo import OrdenTrabajo

        orden = OrdenTrabajo.query.get(orden_id)
        if not orden:
            raise ValueError(_('Orden de trabajo no encontrada'))

        pedidos = orden.pedidos.all()

        resultado = []
        for pedido in pedidos:
            resultado.append({
                'id': pedido.id,
                'codigo': pedido.codigo,
                'cliente': pedido.cliente.nombre if pedido.cliente else None,
                'producto': pedido.producto.nombre if pedido.producto else None,
                'lote': pedido.lote,
                'status': pedido.status,
                'entradas_count': pedido.entradas_count,
                'entradas_completadas': pedido.entradas_completadas,
                'fech_pedido': pedido.fech_pedido.isoformat() if pedido.fech_pedido else None
            })

        return resultado

    @classmethod
    def obtener_estadisticas(cls) -> Dict[str, Any]:
        """
        Obtener estadisticas de ordenes de trabajo para dashboard.

        Returns:
            Dict: Estadisticas incluyendo:
                - total: Total de ordenes
                - por_estado: Conteo por estado
                - promedio_pedidos: Promedio de pedidos por orden
                - ordenes_recientes: Ordenes creadas recientemente
                - completadas_este_mes: Ordenes completadas este mes
        """
        from app.database.models.orden_trabajo import OrdenTrabajo, OTStatus

        # Total de ordenes (excluyendo eliminadas)
        total = OrdenTrabajo.query.filter(
            OrdenTrabajo.status != 'ELIMINADA'
        ).count()

        # Conteo por estado
        por_estado = {}
        for status in [OTStatus.PENDIENTE, OTStatus.EN_PROGRESO, OTStatus.COMPLETADA]:
            por_estado[status] = OrdenTrabajo.query.filter_by(status=status).count()

        # Promedio de pedidos por orden
        ordenes_con_pedidos = OrdenTrabajo.query.all()
        total_pedidos = sum(o.pedidos_count for o in ordenes_con_pedidos)
        promedio_pedidos = (
            round(total_pedidos / len(ordenes_con_pedidos), 2)
            if ordenes_con_pedidos else 0
        )

        # Ordenes recientes (ultimas 5)
        ordenes_recientes = OrdenTrabajo.query.filter(
            OrdenTrabajo.status != 'ELIMINADA'
        ).order_by(desc(OrdenTrabajo.fech_creacion)).limit(5).all()

        # Completadas este mes
        hoy = datetime.utcnow()
        inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        completadas_este_mes = OrdenTrabajo.query.filter(
            OrdenTrabajo.status == OTStatus.COMPLETADA,
            OrdenTrabajo.fech_completado >= inicio_mes
        ).count()

        return {
            'total': total,
            'por_estado': por_estado,
            'promedio_pedidos': promedio_pedidos,
            'ordenes_recientes': [o.to_dict() for o in ordenes_recientes],
            'completadas_este_mes': completadas_este_mes
        }
