"""Servicio de negocio para gestión de Entradas de muestras."""
import re
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from flask_babel import _
from sqlalchemy import asc, desc

from app import db
from app.services.status_workflow import StatusWorkflow


class EntradaService:
    """
    Servicio de negocio para operaciones con Entradas.

    Encapsula la lógica de negocio para creación, actualización,
    eliminación y consulta de entradas de muestras.
    """

    # Expresión regular para formato de lote: A-1234
    LOTE_PATTERN = re.compile(r'^[A-Z]-\d{4}$')

    @staticmethod
    def _validar_lote(lote: str) -> None:
        """
        Validar formato de lote.

        Args:
            lote: Código de lote a validar

        Raises:
            ValueError: Si el formato no es válido (debe ser X-XXXX)
        """
        if lote and not EntradaService.LOTE_PATTERN.match(lote):
            raise ValueError(_('Formato de lote inválido. Debe ser X-XXXX (ej: A-1234)'))

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
    def _calcular_saldo(cantidad_recib: Decimal, cantidad_entreg: Decimal) -> Decimal:
        """
        Calcular saldo de cantidades.

        Args:
            cantidad_recib: Cantidad recibida
            cantidad_entreg: Cantidad entregada

        Returns:
            Decimal: Saldo calculado (siempre >= 0)
        """
        saldo = cantidad_recib - cantidad_entreg
        return max(Decimal('0'), saldo)

    @staticmethod
    def _validar_no_anulado(entrada: Any) -> None:
        """
        Verificar que una entrada no esté anulada.

        Args:
            entrada: Instancia de Entrada

        Raises:
            ValueError: Si la entrada está anulada
        """
        if entrada.anulado:
            raise ValueError(_('No se puede modificar una entrada anulada'))

    @classmethod
    def crear_entrada(cls, data: Dict[str, Any], usuario_id: int) -> Any:
        """
        Crear nueva entrada de muestra.

        Realiza validaciones de negocio, calcula saldo inicial
        y registra el estado inicial en el historial.

        Args:
            data: Diccionario con datos de la entrada
            usuario_id: ID del usuario que crea la entrada

        Returns:
            Entrada: Instancia creada

        Raises:
            ValueError: Si fallan las validaciones de negocio
        """
        from app.database.models.entrada import Entrada, EntradaStatus
        from app.database.models.status_history import StatusHistory

        # Extraer datos
        lote = data.get('lote')
        fech_fab = data.get('fech_fab')
        fech_venc = data.get('fech_venc')
        cantidad_recib = Decimal(str(data.get('cantidad_recib', 0)))
        cantidad_entreg = Decimal(str(data.get('cantidad_entreg', 0)))

        # Validaciones
        cls._validar_lote(lote)
        cls._validar_fechas(fech_fab, fech_venc)

        # Calcular saldo
        saldo = cls._calcular_saldo(cantidad_recib, cantidad_entreg)

        # Crear entrada
        entrada = Entrada(
            codigo=data['codigo'],
            lote=lote,
            producto_id=data['producto_id'],
            fabrica_id=data['fabrica_id'],
            cliente_id=data['cliente_id'],
            rama_id=data.get('rama_id'),
            unidad_medida_id=data.get('unidad_medida_id'),
            pedido_id=data.get('pedido_id'),
            nro_parte=data.get('nro_parte'),
            cantidad_recib=cantidad_recib,
            cantidad_entreg=cantidad_entreg,
            saldo=saldo,
            cantidad_muest=data.get('cantidad_muest'),
            fech_fab=fech_fab,
            fech_venc=fech_venc,
            fech_muestreo=data.get('fech_muestreo'),
            status=EntradaStatus.RECIBIDO,
            observaciones=data.get('observaciones')
        )

        db.session.add(entrada)
        db.session.flush()  # Para obtener el ID

        # Registrar en historial de estados
        history = StatusHistory(
            entrada_id=entrada.id,
            from_status=EntradaStatus.RECIBIDO,
            to_status=EntradaStatus.RECIBIDO,
            changed_by_id=usuario_id,
            reason=_('Creación de entrada'),
            meta_data={'action': 'create'}
        )
        db.session.add(history)
        db.session.commit()

        return entrada

    @classmethod
    def actualizar_entrada(cls, entrada_id: int, data: Dict[str, Any],
                           usuario_id: int) -> Any:
        """
        Actualizar entrada existente.

        Revalida datos modificados y recalcula saldo si cambian cantidades.

        Args:
            entrada_id: ID de la entrada a actualizar
            data: Diccionario con campos a actualizar
            usuario_id: ID del usuario que realiza la actualización

        Returns:
            Entrada: Instancia actualizada

        Raises:
            ValueError: Si la entrada no existe, está anulada o fallan validaciones
        """
        from app.database.models.entrada import Entrada, EntradaStatus
        from app.database.models.status_history import StatusHistory

        entrada = Entrada.query.get(entrada_id)
        if not entrada:
            raise ValueError(_('Entrada no encontrada'))

        cls._validar_no_anulado(entrada)

        # Validar y actualizar lote si cambió
        if 'lote' in data and data['lote'] != entrada.lote:
            cls._validar_lote(data['lote'])
            entrada.lote = data['lote']

        # Validar y actualizar fechas si cambiaron
        fech_fab = data.get('fech_fab', entrada.fech_fab)
        fech_venc = data.get('fech_venc', entrada.fech_venc)
        if ('fech_fab' in data or 'fech_venc' in data):
            cls._validar_fechas(fech_fab, fech_venc)
        entrada.fech_fab = fech_fab
        entrada.fech_venc = fech_venc

        # Actualizar cantidades y recalcular saldo
        cantidad_recib = Decimal(str(data['cantidad_recib'])) \
            if 'cantidad_recib' in data else entrada.cantidad_recib
        cantidad_entreg = Decimal(str(data['cantidad_entreg'])) \
            if 'cantidad_entreg' in data else entrada.cantidad_entreg

        if 'cantidad_recib' in data or 'cantidad_entreg' in data:
            entrada.saldo = cls._calcular_saldo(cantidad_recib, cantidad_entreg)
            entrada.cantidad_recib = cantidad_recib
            entrada.cantidad_entreg = cantidad_entreg

        # Actualizar campos opcionales
        campos_actualizables = [
            'producto_id', 'fabrica_id', 'cliente_id', 'rama_id',
            'unidad_medida_id', 'pedido_id', 'nro_parte',
            'cantidad_muest', 'fech_muestreo', 'observaciones'
        ]
        for campo in campos_actualizables:
            if campo in data:
                setattr(entrada, campo, data[campo])

        # Registrar en historial
        history = StatusHistory(
            entrada_id=entrada.id,
            from_status=entrada.status,
            to_status=entrada.status,
            changed_by_id=usuario_id,
            reason=_('Actualización de datos'),
            meta_data={'action': 'update', 'updated_fields': list(data.keys())}
        )
        db.session.add(history)
        db.session.commit()

        return entrada

    @classmethod
    def eliminar_entrada(cls, entrada_id: int, usuario_id: int) -> Any:
        """
        Eliminar entrada (soft delete - anulación).

        Marca la entrada como anulada y registra el cambio en historial.

        Args:
            entrada_id: ID de la entrada a anular
            usuario_id: ID del usuario que realiza la anulación

        Returns:
            Entrada: Instancia anulada

        Raises:
            ValueError: Si la entrada no existe o ya está anulada
        """
        from app.database.models.entrada import Entrada, EntradaStatus
        from app.database.models.status_history import StatusHistory

        entrada = Entrada.query.get(entrada_id)
        if not entrada:
            raise ValueError(_('Entrada no encontrada'))

        if entrada.anulado:
            raise ValueError(_('La entrada ya está anulada'))

        from_status = entrada.status

        # Anular entrada
        entrada.anulado = True
        entrada.status = EntradaStatus.ANULADO

        # Registrar en historial
        history = StatusHistory(
            entrada_id=entrada.id,
            from_status=from_status,
            to_status=EntradaStatus.ANULADO,
            changed_by_id=usuario_id,
            reason=_('Anulación de entrada'),
            meta_data={'action': 'delete'}
        )
        db.session.add(history)
        db.session.commit()

        return entrada

    @classmethod
    def registrar_entrega(cls, entrada_id: int, cantidad: Decimal,
                          usuario_id: int) -> Any:
        """
        Registrar entrega de cantidad.

        Actualiza cantidad_entreg, recalcula saldo y cambia estado
        automáticamente si el saldo llega a cero.

        Args:
            entrada_id: ID de la entrada
            cantidad: Cantidad a entregar (se suma a cantidad_entreg)
            usuario_id: ID del usuario que registra la entrega

        Returns:
            Entrada: Instancia actualizada

        Raises:
            ValueError: Si la entrada no existe, está anulada,
                       o si resultaría en saldo negativo
        """
        from app.database.models.entrada import Entrada, EntradaStatus
        from app.database.models.status_history import StatusHistory

        entrada = Entrada.query.get(entrada_id)
        if not entrada:
            raise ValueError(_('Entrada no encontrada'))

        cls._validar_no_anulado(entrada)

        cantidad = Decimal(str(cantidad))
        if cantidad <= 0:
            raise ValueError(_('La cantidad a entregar debe ser mayor a cero'))

        # Calcular nueva cantidad entregada
        nueva_cantidad_entreg = entrada.cantidad_entreg + cantidad

        # Verificar que no exceda lo recibido
        if nueva_cantidad_entreg > entrada.cantidad_recib:
            raise ValueError(
                _('No se puede entregar más de lo recibido. '
                  'Recibido: %(recib)s, Ya entregado: %(entreg)s, '
                  'Intentando entregar: %(cant)s',
                  recib=entrada.cantidad_recib,
                  entreg=entrada.cantidad_entreg,
                  cant=cantidad)
            )

        # Actualizar cantidades
        entrada.cantidad_entreg = nueva_cantidad_entreg
        entrada.saldo = cls._calcular_saldo(
            entrada.cantidad_recib,
            nueva_cantidad_entreg
        )

        # Verificar si se completó la entrega
        old_status = entrada.status
        if entrada.saldo == 0 and entrada.status == EntradaStatus.COMPLETADO:
            entrada.status = EntradaStatus.ENTREGADO
            entrada.ent_entregada = True

            # Registrar cambio de estado
            history = StatusHistory(
                entrada_id=entrada.id,
                from_status=old_status,
                to_status=EntradaStatus.ENTREGADO,
                changed_by_id=usuario_id,
                reason=_('Entrega completa - saldo cero'),
                meta_data={'action': 'delivery_complete'}
            )
            db.session.add(history)
        else:
            # Registrar entrega parcial
            history = StatusHistory(
                entrada_id=entrada.id,
                from_status=entrada.status,
                to_status=entrada.status,
                changed_by_id=usuario_id,
                reason=_('Registro de entrega parcial'),
                meta_data={
                    'action': 'partial_delivery',
                    'cantidad_entregada': str(cantidad),
                    'saldo_restante': str(entrada.saldo)
                }
            )
            db.session.add(history)

        db.session.commit()
        return entrada

    @classmethod
    def cambiar_estado(cls, entrada_id: int, nuevo_estado: str,
                       usuario_id: int, razon: Optional[str] = None) -> Any:
        """
        Cambiar estado de una entrada.

        Utiliza StatusWorkflow para validar transiciones válidas.

        Args:
            entrada_id: ID de la entrada
            nuevo_estado: Nuevo estado a asignar
            usuario_id: ID del usuario que realiza el cambio
            razon: Razón opcional del cambio

        Returns:
            Entrada: Instancia actualizada

        Raises:
            ValueError: Si la entrada no existe o la transición no es válida
        """
        from app.database.models.entrada import Entrada

        entrada = Entrada.query.get(entrada_id)
        if not entrada:
            raise ValueError(_('Entrada no encontrada'))

        # StatusWorkflow.transition valida y ejecuta la transición
        StatusWorkflow.transition(entrada, nuevo_estado, usuario_id, razon)

        db.session.commit()
        return entrada

    @classmethod
    def obtener_entradas_paginadas(
        cls,
        filtros: Optional[Dict[str, Any]] = None,
        pagina: int = 1,
        por_pagina: int = 20,
        ordenar_por: str = 'fech_entrada',
        orden: str = 'desc'
    ) -> Tuple[List[Any], Dict[str, Any]]:
        """
        Obtener entradas paginadas con filtros.

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
            Tuple: (lista_de_entradas, metadata_de_paginacion)
        """
        from app.database.models.entrada import Entrada

        filtros = filtros or {}
        query = Entrada.query

        # Aplicar filtros
        if filtros.get('cliente_id'):
            query = query.filter(Entrada.cliente_id == filtros['cliente_id'])

        if filtros.get('producto_id'):
            query = query.filter(Entrada.producto_id == filtros['producto_id'])

        if filtros.get('status'):
            query = query.filter(Entrada.status == filtros['status'])

        if filtros.get('fecha_desde'):
            query = query.filter(Entrada.fech_entrada >= filtros['fecha_desde'])

        if filtros.get('fecha_hasta'):
            query = query.filter(Entrada.fech_entrada <= filtros['fecha_hasta'])

        # Aplicar ordenamiento
        columna_orden = getattr(Entrada, ordenar_por, Entrada.fech_entrada)
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
    def obtener_entrada_por_id(cls, entrada_id: int) -> Optional[Any]:
        """
        Obtener entrada por su ID.

        Args:
            entrada_id: ID de la entrada

        Returns:
            Entrada: Instancia encontrada o None
        """
        from app.database.models.entrada import Entrada
        return Entrada.query.get(entrada_id)
