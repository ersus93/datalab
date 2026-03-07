"""Servicio de negocio para gestión de DetalleEnsayo."""
from datetime import datetime
from typing import Dict, List, Optional

from app import db


class DetalleEnsayoService:
    """
    Servicio de negocio para operaciones con DetalleEnsayo.

    Encapsula la lógica de negocio para asignación, transiciones de estado
    y consulta de detalles de ensayo asociados a entradas de muestras.
    """

    # -------------------------------------------------------------------------
    # Métodos de escritura / transición de estado
    # -------------------------------------------------------------------------

    @classmethod
    def asignar_ensayos(
        cls,
        entrada_id: int,
        ensayo_ids: List[int],
        cantidad: int = 1,
        usuario_id: Optional[int] = None,
    ) -> List:
        """
        Asignar en lote una lista de ensayos a una entrada.

        Omite duplicados: si el par (entrada_id, ensayo_id) ya existe no se
        crea un registro nuevo. Para cada registro creado se genera una
        entrada en AuditLog.

        Args:
            entrada_id: ID de la entrada (muestra) destino.
            ensayo_ids: Lista de IDs de ensayos a asignar.
            cantidad: Cantidad de réplicas por ensayo (default 1).
            usuario_id: ID del usuario que realiza la operación.

        Returns:
            List[DetalleEnsayo]: Lista de objetos DetalleEnsayo creados.

        Raises:
            ValueError: Si la entrada no existe.
        """
        from app.database.models.audit import AuditLog
        from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus
        from app.database.models.entrada import Entrada

        # Verificar que la entrada exista
        entrada = Entrada.query.get(entrada_id)
        if not entrada:
            raise ValueError(f'Entrada con id={entrada_id} no encontrada')

        # Obtener ensayo_ids ya existentes para esta entrada (evitar duplicados)
        existentes = {
            row[0]
            for row in db.session.query(DetalleEnsayo.ensayo_id).filter_by(
                entrada_id=entrada_id
            ).all()
        }

        creados = []
        ahora = datetime.utcnow()

        for ensayo_id in ensayo_ids:
            # Saltar duplicados
            if ensayo_id in existentes:
                continue

            detalle = DetalleEnsayo(
                entrada_id=entrada_id,
                ensayo_id=ensayo_id,
                cantidad=cantidad,
                estado=DetalleEnsayoStatus.PENDIENTE,
                created_at=ahora,
                updated_at=ahora,
            )
            db.session.add(detalle)
            db.session.flush()  # Obtener el ID antes del commit

            # Registrar en auditoría
            if usuario_id is not None:
                AuditLog.log_change(
                    user_id=usuario_id,
                    action='CREATE',
                    table_name='detalle_ensayos',
                    record_id=detalle.id,
                    old_values=None,
                    new_values={
                        'entrada_id': entrada_id,
                        'ensayo_id': ensayo_id,
                        'cantidad': cantidad,
                        'estado': DetalleEnsayoStatus.PENDIENTE,
                    },
                )

            existentes.add(ensayo_id)
            creados.append(detalle)

        db.session.commit()
        return creados

    @classmethod
    def asignar_tecnico(
        cls,
        detalle_id: int,
        tecnico_id: int,
        usuario_id: int,
    ):
        """
        Asignar un técnico a un detalle de ensayo.

        Realiza la transición de estado PENDIENTE → ASIGNADO, registra la
        fecha de asignación y el técnico responsable.

        Args:
            detalle_id: ID del DetalleEnsayo a modificar.
            tecnico_id: ID del usuario técnico asignado.
            usuario_id: ID del usuario que realiza la operación.

        Returns:
            DetalleEnsayo: Instancia actualizada.

        Raises:
            ValueError: Si el detalle no existe o la transición no es válida.
        """
        from app.database.models.audit import AuditLog
        from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus

        detalle = DetalleEnsayo.query.get(detalle_id)
        if not detalle:
            raise ValueError(f'DetalleEnsayo con id={detalle_id} no encontrado')

        # Validar transición mediante método del modelo
        if not detalle.can_transition(DetalleEnsayoStatus.ASIGNADO):
            raise ValueError(
                f'Transición no válida: {detalle.estado} → {DetalleEnsayoStatus.ASIGNADO}'
            )

        valores_anteriores = {
            'estado': detalle.estado,
            'tecnico_asignado_id': detalle.tecnico_asignado_id,
            'fecha_asignacion': (
                detalle.fecha_asignacion.isoformat() if detalle.fecha_asignacion else None
            ),
        }

        # Actualizar campos
        detalle.estado = DetalleEnsayoStatus.ASIGNADO
        detalle.tecnico_asignado_id = tecnico_id
        detalle.fecha_asignacion = datetime.utcnow()
        detalle.updated_at = datetime.utcnow()

        # Registrar en auditoría
        AuditLog.log_change(
            user_id=usuario_id,
            action='UPDATE',
            table_name='detalle_ensayos',
            record_id=detalle.id,
            old_values=valores_anteriores,
            new_values={
                'estado': detalle.estado,
                'tecnico_asignado_id': detalle.tecnico_asignado_id,
                'fecha_asignacion': detalle.fecha_asignacion.isoformat(),
            },
        )

        db.session.commit()
        return detalle

    @classmethod
    def iniciar_ensayo(cls, detalle_id: int, usuario_id: int):
        """
        Iniciar la ejecución de un ensayo.

        Realiza la transición ASIGNADO → EN_PROCESO y registra la fecha
        de inicio.

        Args:
            detalle_id: ID del DetalleEnsayo a modificar.
            usuario_id: ID del usuario que inicia el ensayo.

        Returns:
            DetalleEnsayo: Instancia actualizada.

        Raises:
            ValueError: Si el detalle no existe o la transición no es válida.
        """
        from app.database.models.audit import AuditLog
        from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus

        detalle = DetalleEnsayo.query.get(detalle_id)
        if not detalle:
            raise ValueError(f'DetalleEnsayo con id={detalle_id} no encontrado')

        if not detalle.can_transition(DetalleEnsayoStatus.EN_PROCESO):
            raise ValueError(
                f'Transición no válida: {detalle.estado} → {DetalleEnsayoStatus.EN_PROCESO}'
            )

        valores_anteriores = {
            'estado': detalle.estado,
            'fecha_inicio': (
                detalle.fecha_inicio.isoformat() if detalle.fecha_inicio else None
            ),
        }

        # Actualizar campos
        detalle.estado = DetalleEnsayoStatus.EN_PROCESO
        detalle.fecha_inicio = datetime.utcnow()
        detalle.updated_at = datetime.utcnow()

        # Registrar en auditoría
        AuditLog.log_change(
            user_id=usuario_id,
            action='UPDATE',
            table_name='detalle_ensayos',
            record_id=detalle.id,
            old_values=valores_anteriores,
            new_values={
                'estado': detalle.estado,
                'fecha_inicio': detalle.fecha_inicio.isoformat(),
            },
        )

        db.session.commit()
        return detalle

    @classmethod
    def completar_ensayo(
        cls,
        detalle_id: int,
        observaciones: Optional[str] = None,
        usuario_id: Optional[int] = None,
    ):
        """
        Marcar un ensayo como completado.

        Realiza la transición EN_PROCESO → COMPLETADO. Si todos los detalles
        de la entrada padre están en COMPLETADO o REPORTADO, auto-transiciona
        el estado de la Entrada usando StatusWorkflow.

        Args:
            detalle_id: ID del DetalleEnsayo a modificar.
            observaciones: Observaciones opcionales del resultado.
            usuario_id: ID del usuario que completa el ensayo.

        Returns:
            DetalleEnsayo: Instancia actualizada.

        Raises:
            ValueError: Si el detalle no existe o la transición no es válida.
        """
        from app.database.models.audit import AuditLog
        from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus
        from app.database.models.entrada import Entrada, EntradaStatus
        from app.services.status_workflow import StatusWorkflow

        detalle = DetalleEnsayo.query.get(detalle_id)
        if not detalle:
            raise ValueError(f'DetalleEnsayo con id={detalle_id} no encontrado')

        if not detalle.can_transition(DetalleEnsayoStatus.COMPLETADO):
            raise ValueError(
                f'Transición no válida: {detalle.estado} → {DetalleEnsayoStatus.COMPLETADO}'
            )

        valores_anteriores = {
            'estado': detalle.estado,
            'observaciones': detalle.observaciones,
            'fecha_completado': (
                detalle.fecha_completado.isoformat() if detalle.fecha_completado else None
            ),
        }

        # Actualizar campos
        detalle.estado = DetalleEnsayoStatus.COMPLETADO
        detalle.fecha_completado = datetime.utcnow()
        detalle.updated_at = datetime.utcnow()
        if observaciones is not None:
            detalle.observaciones = observaciones

        # Registrar en auditoría
        if usuario_id is not None:
            AuditLog.log_change(
                user_id=usuario_id,
                action='UPDATE',
                table_name='detalle_ensayos',
                record_id=detalle.id,
                old_values=valores_anteriores,
                new_values={
                    'estado': detalle.estado,
                    'observaciones': detalle.observaciones,
                    'fecha_completado': detalle.fecha_completado.isoformat(),
                },
            )

        # Verificar si todos los detalles de la entrada están finalizados
        estados_finales = {DetalleEnsayoStatus.COMPLETADO, DetalleEnsayoStatus.REPORTADO}
        detalles_entrada = DetalleEnsayo.query.filter_by(
            entrada_id=detalle.entrada_id
        ).all()

        todos_finalizados = all(d.estado in estados_finales for d in detalles_entrada)

        if todos_finalizados:
            entrada = Entrada.query.get(detalle.entrada_id)
            # Transicionar Entrada a COMPLETADO solo si aún no está en ese estado
            if entrada and entrada.status not in (
                EntradaStatus.COMPLETADO,
                EntradaStatus.ENTREGADO,
                EntradaStatus.ANULADO,
            ):
                try:
                    StatusWorkflow.transition(
                        entrada,
                        EntradaStatus.COMPLETADO,
                        changed_by_id=usuario_id,
                        reason='Todos los ensayos completados',
                    )
                except ValueError:
                    # Si la transición no es válida desde el estado actual, ignorar
                    pass

        db.session.commit()
        return detalle

    @classmethod
    def pausar_ensayo(cls, detalle_id: int, usuario_id: int):
        """
        Pausar un ensayo en proceso.

        Realiza la transición EN_PROCESO → PAUSADO. El ensayo puede ser
        reanudado posteriormente.

        Args:
            detalle_id: ID del DetalleEnsayo a pausar.
            usuario_id: ID del usuario que pausa el ensayo.

        Returns:
            DetalleEnsayo: Instancia actualizada.

        Raises:
            ValueError: Si el detalle no existe o la transición no es válida.
        """
        from app.database.models.audit import AuditLog
        from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus

        detalle = DetalleEnsayo.query.get(detalle_id)
        if not detalle:
            raise ValueError(f'DetalleEnsayo con id={detalle_id} no encontrado')

        if not detalle.can_transition(DetalleEnsayoStatus.PAUSADO):
            raise ValueError(
                f'Transición no válida: {detalle.estado} → {DetalleEnsayoStatus.PAUSADO}'
            )

        valores_anteriores = {'estado': detalle.estado}

        detalle.estado = DetalleEnsayoStatus.PAUSADO
        detalle.updated_at = datetime.utcnow()

        AuditLog.log_change(
            user_id=usuario_id,
            action='UPDATE',
            table_name='detalle_ensayos',
            record_id=detalle.id,
            old_values=valores_anteriores,
            new_values={'estado': detalle.estado},
        )

        db.session.commit()
        return detalle

    @classmethod
    def reanudar_ensayo(cls, detalle_id: int, usuario_id: int):
        """
        Reanudar un ensayo pausado.

        Realiza la transición PAUSADO → EN_PROCESO.

        Args:
            detalle_id: ID del DetalleEnsayo a reanudar.
            usuario_id: ID del usuario que reanuda el ensayo.

        Returns:
            DetalleEnsayo: Instancia actualizada.

        Raises:
            ValueError: Si el detalle no existe o la transición no es válida.
        """
        from app.database.models.audit import AuditLog
        from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus

        detalle = DetalleEnsayo.query.get(detalle_id)
        if not detalle:
            raise ValueError(f'DetalleEnsayo con id={detalle_id} no encontrado')

        if not detalle.can_transition(DetalleEnsayoStatus.EN_PROCESO):
            raise ValueError(
                f'Transición no válida: {detalle.estado} → {DetalleEnsayoStatus.EN_PROCESO}'
            )

        valores_anteriores = {'estado': detalle.estado}

        detalle.estado = DetalleEnsayoStatus.EN_PROCESO
        detalle.updated_at = datetime.utcnow()

        AuditLog.log_change(
            user_id=usuario_id,
            action='UPDATE',
            table_name='detalle_ensayos',
            record_id=detalle.id,
            old_values=valores_anteriores,
            new_values={'estado': detalle.estado},
        )

        db.session.commit()
        return detalle

    @classmethod
    def reportar_ensayo(cls, detalle_id: int, usuario_id: int):
        """
        Marcar un ensayo como reportado.

        Realiza la transición COMPLETADO → REPORTADO.

        Args:
            detalle_id: ID del DetalleEnsayo a modificar.
            usuario_id: ID del usuario que reporta el ensayo.

        Returns:
            DetalleEnsayo: Instancia actualizada.

        Raises:
            ValueError: Si el detalle no existe o la transición no es válida.
        """
        from app.database.models.audit import AuditLog
        from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus

        detalle = DetalleEnsayo.query.get(detalle_id)
        if not detalle:
            raise ValueError(f'DetalleEnsayo con id={detalle_id} no encontrado')

        if not detalle.can_transition(DetalleEnsayoStatus.REPORTADO):
            raise ValueError(
                f'Transición no válida: {detalle.estado} → {DetalleEnsayoStatus.REPORTADO}'
            )

        valores_anteriores = {'estado': detalle.estado}

        # Actualizar estado
        detalle.estado = DetalleEnsayoStatus.REPORTADO
        detalle.updated_at = datetime.utcnow()

        # Registrar en auditoría
        AuditLog.log_change(
            user_id=usuario_id,
            action='UPDATE',
            table_name='detalle_ensayos',
            record_id=detalle.id,
            old_values=valores_anteriores,
            new_values={'estado': detalle.estado},
        )

        db.session.commit()
        return detalle

    @classmethod
    def eliminar_detalle(cls, detalle_id: int, usuario_id: int) -> bool:
        """
        Eliminar un detalle de ensayo.

        Solo se permite la eliminación cuando el estado es PENDIENTE.

        Args:
            detalle_id: ID del DetalleEnsayo a eliminar.
            usuario_id: ID del usuario que realiza la operación.

        Returns:
            bool: True si la eliminación fue exitosa.

        Raises:
            ValueError: Si el detalle no existe o el estado no es PENDIENTE.
        """
        from app.database.models.audit import AuditLog
        from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus

        detalle = DetalleEnsayo.query.get(detalle_id)
        if not detalle:
            raise ValueError(f'DetalleEnsayo con id={detalle_id} no encontrado')

        if detalle.estado != DetalleEnsayoStatus.PENDIENTE:
            raise ValueError(
                f'Solo se pueden eliminar detalles en estado PENDIENTE. '
                f'Estado actual: {detalle.estado}'
            )

        valores_anteriores = {
            'entrada_id': detalle.entrada_id,
            'ensayo_id': detalle.ensayo_id,
            'estado': detalle.estado,
            'cantidad': detalle.cantidad,
        }

        # Registrar en auditoría antes de eliminar
        AuditLog.log_change(
            user_id=usuario_id,
            action='DELETE',
            table_name='detalle_ensayos',
            record_id=detalle.id,
            old_values=valores_anteriores,
            new_values=None,
        )

        db.session.delete(detalle)
        db.session.commit()
        return True

    # -------------------------------------------------------------------------
    # Métodos de consulta
    # -------------------------------------------------------------------------

    @classmethod
    def get_detalles_por_entrada(cls, entrada_id: int) -> List:
        """
        Obtener todos los detalles de ensayo para una entrada.

        Los resultados se ordenan por nombre del área y luego por nombre
        corto del ensayo.

        Args:
            entrada_id: ID de la entrada (muestra).

        Returns:
            List[DetalleEnsayo]: Lista ordenada de detalles.
        """
        from app.database.models.detalle_ensayo import DetalleEnsayo
        from app.database.models.ensayo import Ensayo
        from app.database.models.reference import Area

        return (
            DetalleEnsayo.query
            .join(Ensayo, DetalleEnsayo.ensayo_id == Ensayo.id)
            .join(Area, Ensayo.area_id == Area.id)
            .filter(DetalleEnsayo.entrada_id == entrada_id)
            .order_by(Area.nombre, Ensayo.nombre_corto)
            .all()
        )

    @classmethod
    def get_detalles_agrupados_por_area(cls, entrada_id: int) -> Dict[str, List]:
        """
        Obtener detalles de ensayo agrupados por área.

        Útil para renderizar la interfaz de usuario organizada por sección.

        Args:
            entrada_id: ID de la entrada (muestra).

        Returns:
            Dict[str, List[DetalleEnsayo]]: Diccionario donde cada clave es
            el nombre del área y el valor es la lista de detalles
            correspondientes.
        """
        detalles = cls.get_detalles_por_entrada(entrada_id)

        agrupados: Dict[str, List] = {}
        for detalle in detalles:
            # Acceder al nombre del área a través de la relación ensayo → area
            area_nombre = detalle.ensayo.area.nombre if (
                detalle.ensayo and detalle.ensayo.area
            ) else 'Sin Área'

            if area_nombre not in agrupados:
                agrupados[area_nombre] = []
            agrupados[area_nombre].append(detalle)

        return agrupados
