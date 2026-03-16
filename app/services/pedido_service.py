"""Servicio de negocio para gestión de Pedidos."""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from flask_babel import _
from sqlalchemy import asc, desc, func

from app import db


class PedidoService:
    """
    Servicio de negocio para operaciones con Pedidos.

    Encapsula la lógica de negocio para creación, actualización,
    eliminación y consulta de pedidos de clientes.
    """

    @staticmethod
    def _validar_fechas(fech_fab: Any, fech_venc: Any) -> None:
        """
        Validar que fecha de vencimiento sea posterior a fabricación.

        Args:
            fech_fab: Fecha de fabricación
            fech_venc: Fecha de vencimiento

        Raises:
            ValueError: Si fech_venc <= fech_fab
        """
        if fech_fab and fech_venc and fech_venc <= fech_fab:
            raise ValueError(_('Fecha de vencimiento debe ser posterior a fecha de fabricación'))

    @staticmethod
    def _generar_codigo() -> str:
        """
        Generar código único para el pedido.

        Formato: PED-YYYY-NNNN (ej: PED-2024-0001)

        Returns:
            str: Código generado
        """
        from app.database.models.pedido import Pedido

        year = datetime.utcnow().year
        prefix = f"PED-{year}-"

        # Obtener el último código del año actual
        ultimo = Pedido.query.filter(
            Pedido.codigo.like(f"{prefix}%")
        ).order_by(desc(Pedido.id)).first()

        if ultimo:
            # Extraer número del último código
            try:
                numero = int(ultimo.codigo.split('-')[-1]) + 1
            except (ValueError, IndexError):
                numero = 1
        else:
            numero = 1

        return f"{prefix}{numero:04d}"

    @staticmethod
    def _validar_estado_transicion(estado_actual: str, nuevo_estado: str) -> None:
        """
        Validar transición de estados válida.

        Transiciones válidas:
        - PENDIENTE → EN_PROCESO → COMPLETADO

        Args:
            estado_actual: Estado actual del pedido
            nuevo_estado: Nuevo estado deseado

        Raises:
            ValueError: Si la transición no es válida
        """
        from app.database.models.pedido import PedidoStatus

        # Transiciones válidas
        transiciones = {
            PedidoStatus.PENDIENTE: [PedidoStatus.EN_PROCESO, PedidoStatus.COMPLETADO],
            PedidoStatus.EN_PROCESO: [PedidoStatus.COMPLETADO, PedidoStatus.PENDIENTE],
            PedidoStatus.COMPLETADO: [PedidoStatus.EN_PROCESO, PedidoStatus.PENDIENTE]
        }

        validos = transiciones.get(estado_actual, [])
        if nuevo_estado not in validos:
            raise ValueError(
                _('Transición no válida: %(actual)s → %(nuevo)s',
                  actual=estado_actual, nuevo=nuevo_estado)
            )

    @classmethod
    def crear_pedido(cls, data: Dict[str, Any], usuario_id: int) -> Any:
        """
        Crear nuevo pedido.

        Realiza validaciones de negocio, genera código automáticamente
        y establece el estado inicial como PENDIENTE.

        Args:
            data: Diccionario con datos del pedido
            usuario_id: ID del usuario que crea el pedido

        Returns:
            Pedido: Instancia creada

        Raises:
            ValueError: Si fallan las validaciones de negocio
        """
        from app.database.models.pedido import Pedido, PedidoStatus

        # Validar campos requeridos
        cliente_id = data.get('cliente_id')
        producto_id = data.get('producto_id')

        if not cliente_id:
            raise ValueError(_('El cliente es obligatorio'))
        if not producto_id:
            raise ValueError(_('El producto es obligatorio'))

        # Extraer y validar fechas
        fech_fab = data.get('fech_fab')
        fech_venc = data.get('fech_venc')
        cls._validar_fechas(fech_fab, fech_venc)

        # Generar o usar código proporcionado
        codigo = data.get('codigo')
        if not codigo:
            codigo = cls._generar_codigo()

        # Crear pedido
        pedido = Pedido(
            codigo=codigo,
            cliente_id=cliente_id,
            producto_id=producto_id,
            orden_trabajo_id=data.get('orden_trabajo_id'),
            unidad_medida_id=data.get('unidad_medida_id'),
            lote=data.get('lote'),
            fech_fab=fech_fab,
            fech_venc=fech_venc,
            cantidad=data.get('cantidad'),
            status=PedidoStatus.PENDIENTE,
            observaciones=data.get('observaciones')
        )

        db.session.add(pedido)
        db.session.commit()

        return pedido

    @classmethod
    def actualizar_pedido(cls, pedido_id: int, data: Dict[str, Any],
                          usuario_id: int) -> Any:
        """
        Actualizar pedido existente.

        Revalida datos modificados y recalcula el estado basado en entradas.

        Args:
            pedido_id: ID del pedido a actualizar
            data: Diccionario con campos a actualizar
            usuario_id: ID del usuario que realiza la actualización

        Returns:
            Pedido: Instancia actualizada

        Raises:
            ValueError: Si el pedido no existe o fallan las validaciones
        """
        from app.database.models.pedido import Pedido

        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            raise ValueError(_('Pedido no encontrado'))

        # Validar y actualizar fechas si cambiaron
        fech_fab = data.get('fech_fab', pedido.fech_fab)
        fech_venc = data.get('fech_venc', pedido.fech_venc)
        if 'fech_fab' in data or 'fech_venc' in data:
            cls._validar_fechas(fech_fab, fech_venc)
        pedido.fech_fab = fech_fab
        pedido.fech_venc = fech_venc

        # Actualizar campos
        campos_actualizables = [
            'cliente_id', 'producto_id', 'orden_trabajo_id',
            'unidad_medida_id', 'lote', 'cantidad', 'observaciones'
        ]
        for campo in campos_actualizables:
            if campo in data:
                setattr(pedido, campo, data[campo])

        # Recalcular estado basado en entradas
        pedido.actualizar_estado()

        db.session.commit()

        return pedido

    @classmethod
    def eliminar_pedido(cls, pedido_id: int, usuario_id: int) -> Any:
        """
        Eliminar pedido (soft delete).

        Verifica que el pedido no tenga entradas relacionadas antes
        de permitir la eliminación.

        Args:
            pedido_id: ID del pedido a eliminar
            usuario_id: ID del usuario que realiza la eliminación

        Returns:
            Pedido: Instancia marcada como eliminada

        Raises:
            ValueError: Si el pedido no existe o tiene entradas relacionadas
        """
        from app.database.models.pedido import Pedido

        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            raise ValueError(_('Pedido no encontrado'))

        # Verificar si tiene entradas
        if pedido.entradas_count > 0:
            raise ValueError(
                _('No se puede eliminar el pedido porque tiene %(count)s entrada(s) relacionada(s)',
                  count=pedido.entradas_count)
            )

        # Soft delete: cambiar estado a un valor especial
        pedido.status = 'ELIMINADO'

        db.session.commit()

        return pedido

    @classmethod
    def cambiar_estado(cls, pedido_id: int, nuevo_estado: str,
                       usuario_id: int) -> Any:
        """
        Cambiar estado de un pedido.

        Valida que la transición sea válida según el flujo:
        PENDIENTE → EN_PROCESO → COMPLETADO

        Args:
            pedido_id: ID del pedido
            nuevo_estado: Nuevo estado a asignar
            usuario_id: ID del usuario que realiza el cambio

        Returns:
            Pedido: Instancia actualizada

        Raises:
            ValueError: Si el pedido no existe o la transición no es válida
        """
        from app.database.models.pedido import Pedido

        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            raise ValueError(_('Pedido no encontrado'))

        # Validar transición
        cls._validar_estado_transicion(pedido.status, nuevo_estado)

        pedido.status = nuevo_estado
        db.session.commit()

        return pedido

    @classmethod
    def obtener_pedidos_paginados(
        cls,
        filtros: Optional[Dict[str, Any]] = None,
        pagina: int = 1,
        por_pagina: int = 20,
        ordenar_por: str = 'fech_pedido',
        orden: str = 'desc'
    ) -> Tuple[List[Any], Dict[str, Any]]:
        """
        Obtener pedidos paginados con filtros.

        Args:
            filtros: Diccionario con filtros opcionales:
                    - cliente_id: Filtrar por cliente
                    - producto_id: Filtrar por producto
                    - status: Filtrar por estado
                    - fecha_desde: Fecha inicial (inclusive)
                    - fecha_hasta: Fecha final (inclusive)
            pagina: Número de página (1-based)
            por_pagina: Cantidad de registros por página
            ordenar_por: Campo para ordenar
            orden: 'asc' o 'desc'

        Returns:
            Tuple: (lista_de_pedidos, metadata_de_paginacion)
        """
        from app.database.models.pedido import Pedido

        filtros = filtros or {}
        query = Pedido.query

        # Aplicar filtros
        if filtros.get('cliente_id'):
            query = query.filter(Pedido.cliente_id == filtros['cliente_id'])

        if filtros.get('producto_id'):
            query = query.filter(Pedido.producto_id == filtros['producto_id'])

        if filtros.get('status'):
            query = query.filter(Pedido.status == filtros['status'])

        if filtros.get('fecha_desde'):
            query = query.filter(Pedido.fech_pedido >= filtros['fecha_desde'])

        if filtros.get('fecha_hasta'):
            query = query.filter(Pedido.fech_pedido <= filtros['fecha_hasta'])

        # Aplicar ordenamiento
        columna_orden = getattr(Pedido, ordenar_por, Pedido.fech_pedido)
        if orden.lower() == 'desc':
            query = query.order_by(desc(columna_orden))
        else:
            query = query.order_by(asc(columna_orden))

        # Paginación
        paginacion = query.paginate(
            page=pagina,
            per_page=por_pagina,
            error_out=False
        )

        # Metadata de paginación
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
    def obtener_pedido_por_id(cls, pedido_id: int) -> Optional[Any]:
        """
        Obtener pedido por su ID.

        Args:
            pedido_id: ID del pedido

        Returns:
            Pedido: Instancia encontrada o None
        """
        from app.database.models.pedido import Pedido
        return Pedido.query.get(pedido_id)

    @classmethod
    def obtener_entradas_de_pedido(cls, pedido_id: int) -> List[Dict[str, Any]]:
        """
        Obtener entradas relacionadas a un pedido.

        Args:
            pedido_id: ID del pedido

        Returns:
            List[Dict]: Lista de entradas con su información de estado
        """
        from app.database.models.pedido import Pedido
        from app.database.models.entrada import Entrada

        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            raise ValueError(_('Pedido no encontrado'))

        entradas = pedido.entradas.all()

        resultado = []
        for entrada in entradas:
            resultado.append({
                'id': entrada.id,
                'codigo': entrada.codigo,
                'lote': entrada.lote,
                'status': entrada.status,
                'cantidad_recib': str(entrada.cantidad_recib),
                'cantidad_entreg': str(entrada.cantidad_entreg),
                'saldo': str(entrada.saldo),
                'fech_entrada': entrada.fech_entrada.isoformat() if entrada.fech_entrada else None,
                'anulado': entrada.anulado
            })

        return resultado
