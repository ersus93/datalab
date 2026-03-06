#!/usr/bin/env python3
"""Modelo DetalleEnsayo - Asignación de ensayos a entradas de muestras."""

from datetime import datetime
from enum import Enum
from typing import ClassVar

from sqlalchemy import UniqueConstraint, Index

from app import db


class DetalleEnsayoStatus(Enum):
    """Estados posibles de un detalle de ensayo.

    Flujo de trabajo:
        PENDIENTE → ASIGNADO → EN_PROCESO → COMPLETADO → REPORTADO
    """

    PENDIENTE = "PENDIENTE"
    ASIGNADO = "ASIGNADO"
    EN_PROCESO = "EN_PROCESO"
    COMPLETADO = "COMPLETADO"
    REPORTADO = "REPORTADO"


class DetalleEnsayo(db.Model):
    """Detalle de ensayo asignado a una entrada de muestra.

    Representa la asociación entre una entrada (muestra) y un ensayo
    (análisis físico-químico), con seguimiento de estado, técnico
    asignado y fechas de cada etapa del proceso.

    Flujo de estados:
        PENDIENTE → ASIGNADO → EN_PROCESO → COMPLETADO → REPORTADO

    Attributes:
        id: Clave primaria.
        entrada_id: FK a entradas, no nula, indexada junto a estado.
        ensayo_id: FK a ensayos, no nula.
        cantidad: Número de réplicas del ensayo, por defecto 1.
        estado: Estado actual del ensayo según DetalleEnsayoStatus.
        fecha_asignacion: Momento en que se asignó el técnico.
        fecha_inicio: Momento en que el técnico inició el análisis.
        fecha_completado: Momento en que se completó el análisis.
        tecnico_asignado_id: FK al usuario técnico responsable, nullable.
        observaciones: Notas adicionales sobre el ensayo.
        created_at: Timestamp de creación del registro.
        updated_at: Timestamp de última modificación.
    """

    __tablename__ = "detalles_ensayo"

    # Restricciones de tabla: unicidad y rendimiento
    __table_args__ = (
        # Evitar duplicados: una entrada no puede tener el mismo ensayo dos veces
        UniqueConstraint("entrada_id", "ensayo_id", name="uq_detalle_entrada_ensayo"),
        # Índice compuesto para consultas por entrada filtradas por estado
        Index("ix_detalle_entrada_estado", "entrada_id", "estado"),
    )

    # Clave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Claves foráneas
    entrada_id = db.Column(
        db.Integer,
        db.ForeignKey("entradas.id"),
        nullable=False,
        index=True,
    )
    ensayo_id = db.Column(
        db.Integer,
        db.ForeignKey("ensayos.id"),
        nullable=False,
    )
    tecnico_asignado_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
    )

    # Campos principales
    cantidad = db.Column(db.Integer, default=1, nullable=False)
    estado = db.Column(
        db.Enum(
            DetalleEnsayoStatus.PENDIENTE.value,
            DetalleEnsayoStatus.ASIGNADO.value,
            DetalleEnsayoStatus.EN_PROCESO.value,
            DetalleEnsayoStatus.COMPLETADO.value,
            DetalleEnsayoStatus.REPORTADO.value,
            name="detalle_ensayo_status",
        ),
        default=DetalleEnsayoStatus.PENDIENTE.value,
        nullable=False,
    )
    observaciones = db.Column(db.Text, nullable=True)

    # Fechas de seguimiento del flujo de trabajo
    fecha_asignacion = db.Column(db.DateTime, nullable=True)
    fecha_inicio = db.Column(db.DateTime, nullable=True)
    fecha_completado = db.Column(db.DateTime, nullable=True)

    # Timestamps de auditoría
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relaciones
    entrada = db.relationship("Entrada", backref="detalles_ensayo", lazy=True)
    ensayo = db.relationship("Ensayo", backref="detalles_ensayo", lazy=True)
    tecnico_asignado = db.relationship("User", backref="ensayos_asignados", lazy=True)

    # Mapa de transiciones válidas del estado del ensayo
    VALID_TRANSITIONS: ClassVar[dict[str, list[str]]] = {
        DetalleEnsayoStatus.PENDIENTE.value: [DetalleEnsayoStatus.ASIGNADO.value],
        DetalleEnsayoStatus.ASIGNADO.value: [DetalleEnsayoStatus.EN_PROCESO.value],
        DetalleEnsayoStatus.EN_PROCESO.value: [DetalleEnsayoStatus.COMPLETADO.value],
        DetalleEnsayoStatus.COMPLETADO.value: [DetalleEnsayoStatus.REPORTADO.value],
        DetalleEnsayoStatus.REPORTADO.value: [],
    }

    def __repr__(self) -> str:
        return (
            f"<DetalleEnsayo id={self.id} "
            f"entrada={self.entrada_id} "
            f"ensayo={self.ensayo_id} "
            f"estado={self.estado}>"
        )

    def to_dict(self) -> dict:
        """Serializa el detalle de ensayo a diccionario.

        Returns:
            dict: Representación del registro con todos los campos y
                  nombres de entidades relacionadas donde estén cargadas.
        """
        return {
            "id": self.id,
            "entrada_id": self.entrada_id,
            # Código de entrada si la relación está cargada
            "entrada_codigo": self.entrada.codigo if self.entrada else None,
            "ensayo_id": self.ensayo_id,
            # Nombre corto del ensayo si la relación está cargada
            "ensayo_nombre": self.ensayo.nombre_corto if self.ensayo else None,
            "cantidad": self.cantidad,
            "estado": self.estado,
            "fecha_asignacion": (
                self.fecha_asignacion.isoformat() if self.fecha_asignacion else None
            ),
            "fecha_inicio": (
                self.fecha_inicio.isoformat() if self.fecha_inicio else None
            ),
            "fecha_completado": (
                self.fecha_completado.isoformat() if self.fecha_completado else None
            ),
            "tecnico_asignado_id": self.tecnico_asignado_id,
            # Nombre completo del técnico si la relación está cargada
            "tecnico_nombre": (
                self.tecnico_asignado.nombre_completo
                if self.tecnico_asignado
                else None
            ),
            "observaciones": self.observaciones,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def can_transition(cls, from_status: str, to_status: str) -> bool:
        """Verifica si la transición de estado es válida según la máquina de estados.

        Args:
            from_status: Estado actual (valor de cadena).
            to_status: Estado destino (valor de cadena).

        Returns:
            bool: True si la transición está permitida, False en caso contrario.

        Example:
            >>> DetalleEnsayo.can_transition("PENDIENTE", "ASIGNADO")
            True
            >>> DetalleEnsayo.can_transition("PENDIENTE", "COMPLETADO")
            False
        """
        transiciones_validas = cls.VALID_TRANSITIONS.get(from_status, [])
        return to_status in transiciones_validas

    @classmethod
    def get_valid_transitions(cls, current_status: str) -> list[str]:
        """Devuelve la lista de estados a los que se puede transicionar desde el actual.

        Args:
            current_status: Estado actual (valor de cadena).

        Returns:
            list[str]: Lista de estados destino válidos. Lista vacía si no hay
                       transiciones posibles o el estado no existe en el mapa.

        Example:
            >>> DetalleEnsayo.get_valid_transitions("PENDIENTE")
            ['ASIGNADO']
            >>> DetalleEnsayo.get_valid_transitions("REPORTADO")
            []
        """
        return cls.VALID_TRANSITIONS.get(current_status, [])
