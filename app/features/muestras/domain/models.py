"""
Feature: Muestras (Entradas)
Capa: Domain
Entidades puras de Python. Workflow: Recibida → En análisis → Completada.
"""
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional

from app.core.domain.base import AuditMixin, Entity, ValidationError


class EstadoMuestra(str, Enum):
    RECIBIDA = "RECIBIDA"
    EN_ANALISIS = "EN_ANALISIS"
    COMPLETADA = "COMPLETADA"
    RECHAZADA = "RECHAZADA"


@dataclass
class Muestra(Entity, AuditMixin):
    """Entidad de dominio: Muestra de laboratorio."""
    numero_entrada: str = ""
    cliente_id: int = 0
    descripcion: str = ""
    fecha_recepcion: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    estado: EstadoMuestra = EstadoMuestra.RECIBIDA
    observaciones: Optional[str] = None
    codigo_producto: Optional[str] = None
    lote: Optional[str] = None

    def __post_init__(self):
        self._validar()

    def _validar(self):
        if not self.numero_entrada:
            raise ValidationError("El número de entrada es obligatorio.")
        if not self.cliente_id:
            raise ValidationError("La muestra debe estar asociada a un cliente.")
        if not self.descripcion:
            raise ValidationError("La descripción de la muestra es obligatoria.")

    def iniciar_analisis(self):
        if self.estado != EstadoMuestra.RECIBIDA:
            raise ValidationError(
                f"No se puede iniciar análisis desde el estado '{self.estado}'."
            )
        self.estado = EstadoMuestra.EN_ANALISIS

    def completar(self):
        if self.estado != EstadoMuestra.EN_ANALISIS:
            raise ValidationError(
                f"No se puede completar desde el estado '{self.estado}'."
            )
        self.estado = EstadoMuestra.COMPLETADA

    def rechazar(self, motivo: str):
        self.estado = EstadoMuestra.RECHAZADA
        self.observaciones = f"RECHAZADA: {motivo}"

    @property
    def esta_vencida(self) -> bool:
        if self.fecha_vencimiento is None:
            return False
        return date.today() > self.fecha_vencimiento
