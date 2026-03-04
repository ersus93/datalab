"""Servicio para gestionar workflow de estados."""
from typing import List

from flask_babel import _

from app import db
from app.database.models.entrada import Entrada, EntradaStatus
from app.database.models.status_history import StatusHistory
from app.database.models.notification import Notification


class StatusWorkflow:
    """Gestiona transiciones de estado para Entradas."""

    VALID_TRANSITIONS = {
        EntradaStatus.RECIBIDO: [EntradaStatus.EN_PROCESO, EntradaStatus.ANULADO],
        EntradaStatus.EN_PROCESO: [EntradaStatus.COMPLETADO, EntradaStatus.ANULADO],
        EntradaStatus.COMPLETADO: [EntradaStatus.ENTREGADO],
        EntradaStatus.ENTREGADO: [],  # Terminal
        EntradaStatus.ANULADO: []     # Terminal
    }

    STATUS_LABELS = {
        EntradaStatus.RECIBIDO: _('Recibido'),
        EntradaStatus.EN_PROCESO: _('En Proceso'),
        EntradaStatus.COMPLETADO: _('Completado'),
        EntradaStatus.ENTREGADO: _('Entregado'),
        EntradaStatus.ANULADO: _('Anulado')
    }

    STATUS_COLORS = {
        EntradaStatus.RECIBIDO: 'secondary',
        EntradaStatus.EN_PROCESO: 'primary',
        EntradaStatus.COMPLETADO: 'success',
        EntradaStatus.ENTREGADO: 'info',
        EntradaStatus.ANULADO: 'danger'
    }

    @classmethod
    def can_transition(cls, from_status: str, to_status: str) -> bool:
        """Verificar si una transición es válida."""
        return to_status in cls.VALID_TRANSITIONS.get(from_status, [])

    @classmethod
    def get_valid_transitions(cls, current_status: str) -> List[str]:
        """Obtener transiciones válidas desde un estado."""
        return cls.VALID_TRANSITIONS.get(current_status, [])

    @classmethod
    def transition(cls, entrada: Entrada, to_status: str,
                   changed_by_id: int, reason: str = None) -> bool:
        """
        Ejecutar transición de estado.

        Args:
            entrada: Entrada a modificar
            to_status: Nuevo estado
            changed_by_id: ID del usuario que hace el cambio
            reason: Razón del cambio (opcional)

        Returns:
            bool: True si la transición fue exitosa

        Raises:
            ValueError: Si la transición no es válida
        """
        from_status = entrada.status

        # Validar transición
        if not cls.can_transition(from_status, to_status):
            raise ValueError(
                _('Transición no válida: %(from_s)s -> %(to_s)s. '
                  'Transiciones válidas: %(valid)s',
                  from_s=from_status, to_s=to_status,
                  valid=', '.join(cls.get_valid_transitions(from_status)))
            )

        # Actualizar estado
        entrada.status = to_status

        # Actualizar flags según estado
        if to_status == EntradaStatus.ANULADO:
            entrada.anulado = True
        elif to_status == EntradaStatus.ENTREGADO:
            entrada.ent_entregada = True

        # Registrar en historial
        history = StatusHistory(
            entrada_id=entrada.id,
            from_status=from_status,
            to_status=to_status,
            changed_by_id=changed_by_id,
            reason=reason,
            meta_data={
                'ip_address': None,  # Se puede obtener de request
                'user_agent': None   # Se puede obtener de request
            }
        )
        db.session.add(history)

        # Enviar notificaciones
        cls._send_notifications(entrada, from_status, to_status)

        return True

    @classmethod
    def _send_notifications(cls, entrada: Entrada, from_status: str, to_status: str):
        """Enviar notificaciones según el cambio de estado."""
        # Notificar al cliente en completado/entregado
        if to_status in [EntradaStatus.COMPLETADO, EntradaStatus.ENTREGADO]:
            if entrada.cliente and entrada.cliente.usuarios:
                # Crear notificación para el primer usuario del cliente
                notif = Notification(
                    user_id=entrada.cliente.usuarios[0].id,
                    type='status_change',
                    title=_('Muestra %(codigo)s - %(status)s',
                            codigo=entrada.codigo,
                            status=cls.STATUS_LABELS[to_status]),
                    message=_('Su muestra ha cambiado de estado a: %(status)s',
                              status=cls.STATUS_LABELS[to_status]),
                    entity_type='entrada',
                    entity_id=entrada.id
                )
                db.session.add(notif)

    @classmethod
    def batch_transition(cls, entrada_ids: List[int], to_status: str,
                         changed_by_id: int, reason: str = None) -> dict:
        """
        Cambiar estado de múltiples entradas.

        Args:
            entrada_ids: Lista de IDs de entradas
            to_status: Nuevo estado
            changed_by_id: ID del usuario que hace el cambio
            reason: Razón del cambio (opcional)

        Returns:
            dict: Resultados con éxitos y fallos
        """
        results = {'success': [], 'failed': []}

        for entrada_id in entrada_ids:
            entrada = Entrada.query.get(entrada_id)
            if not entrada:
                results['failed'].append({
                    'id': entrada_id,
                    'error': _('Entrada no encontrada')
                })
                continue

            try:
                cls.transition(entrada, to_status, changed_by_id, reason)
                results['success'].append(entrada_id)
            except ValueError as e:
                results['failed'].append({
                    'id': entrada_id,
                    'error': str(e)
                })

        db.session.commit()
        return results
