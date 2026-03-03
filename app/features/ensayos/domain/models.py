"""
Feature: Ensayos
Capa: Domain
Modelos para Ensayos FQ (Físico-Químico), MB (Microbiológico), ES (Especiales).
"""
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional

from app.core.domain.base import AuditMixin, Entity, ValidationError


class TipoEnsayo(str, Enum):
    FISICO_QUIMICO = "FQ"
    MICROBIOLOGICO = "MB"
    ESPECIAL = "ES"


class EstadoEnsayo(str, Enum):
    PENDIENTE = "PENDIENTE"
    EN_PROCESO = "EN_PROCESO"
    COMPLETADO = "COMPLETADO"
    ANULADO = "ANULADO"


@dataclass
class ResultadoParametro:
    """Value Object: Resultado de un parámetro de ensayo."""
    parametro: str
    valor_obtenido: str
    unidad: Optional[str]
    valor_referencia: Optional[str]
    conforme: Optional[bool]

    def __post_init__(self):
        if not self.parametro:
            raise ValidationError("El nombre del parámetro es obligatorio.")


@dataclass
class Ensayo(Entity, AuditMixin):
    """Entidad de dominio: Ensayo de laboratorio."""
    muestra_id: int = 0
    tipo: TipoEnsayo = TipoEnsayo.FISICO_QUIMICO
    estado: EstadoEnsayo = EstadoEnsayo.PENDIENTE
    metodo: Optional[str] = None
    analist_responsable: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    resultados: List[ResultadoParametro] = field(default_factory=list)
    observaciones: Optional[str] = None

    def __post_init__(self):
        if not self.muestra_id:
            raise ValidationError("El ensayo debe estar asociado a una muestra.")

    def iniciar(self, analista: str):
        if self.estado != EstadoEnsayo.PENDIENTE:
            raise ValidationError("Solo se puede iniciar un ensayo PENDIENTE.")
        self.estado = EstadoEnsayo.EN_PROCESO
        self.analist_responsable = analista
        self.fecha_inicio = date.today()

    def registrar_resultado(self, resultado: ResultadoParametro):
        if self.estado != EstadoEnsayo.EN_PROCESO:
            raise ValidationError("Solo se pueden registrar resultados en ensayos EN_PROCESO.")
        self.resultados.append(resultado)

    def completar(self):
        if self.estado != EstadoEnsayo.EN_PROCESO:
            raise ValidationError("Solo se puede completar un ensayo EN_PROCESO.")
        if not self.resultados:
            raise ValidationError("Debe haber al menos un resultado registrado para completar.")
        self.estado = EstadoEnsayo.COMPLETADO
        self.fecha_fin = date.today()

    def anular(self, motivo: str):
        self.estado = EstadoEnsayo.ANULADO
        self.observaciones = f"ANULADO: {motivo}"

    @property
    def es_conforme(self) -> Optional[bool]:
        """Retorna True si todos los resultados son conformes."""
        if not self.resultados:
            return None
        conformes = [r.conforme for r in self.resultados if r.conforme is not None]
        if not conformes:
            return None
        return all(conformes)
