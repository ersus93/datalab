#!/usr/bin/env python3
"""Modelo Informe - Informes técnicos y certificados de análisis."""

from datetime import datetime, date
from enum import Enum
from typing import ClassVar

from sqlalchemy import UniqueConstraint, Index

from app import db


class InformeStatus(Enum):
    """Estados posibles de un informe.

    Flujo de trabajo:
        BORRADOR → PENDIENTE_FIRMA → EMITIDO → ENTREGADO
        Cualquier estado puede pasar a ANULADO.
    """

    BORRADOR = "BORRADOR"
    PENDIENTE_FIRMA = "PENDIENTE_FIRMA"
    EMITIDO = "EMITIDO"
    ENTREGADO = "ENTREGADO"
    ANULADO = "ANULADO"


class TipoInforme(Enum):
    """Tipos de informe según su propósito."""

    ANALISIS = "ANALISIS"
    CERTIFICADO = "CERTIFICADO"
    CONSULTA = "CONSULTA"
    ESPECIAL = "ESPECIAL"


class MedioEntrega(Enum):
    """Medio de entrega del informe al cliente."""

    FISICO = "FISICO"
    DIGITAL = "DIGITAL"
    AMBOS = "AMBOS"


class Informe(db.Model):
    """Informe técnico o certificado de análisis.

    Representa un documento oficial generado a partir de los ensayos
    realizados a una muestra de entrada. Puede ser un análisis completo,
    un certificado de conformidad, una consulta técnica o un informe especial.

    Flujo de estados:
        BORRADOR → PENDIENTE_FIRMA → EMITIDO → ENTREGADO
        (cualquier estado) → ANULADO

    Attributes:
        id: Clave primaria.
        nro_oficial: Número oficial único del informe, indexado.
        tipo_informe: Tipo de informe según TipoInforme.
        entrada_id: FK a entradas, no nula, CASCADE.
        cliente_id: FK a clientes, no nula, PROTECT.
        estado: Estado actual del informe según InformeStatus.
        fecha_generacion: Momento de creación del informe.
        fecha_emision: Momento en que se emitió el informe.
        fecha_entrega: Momento en que se entregó al cliente.
        fecha_vencimiento: Fecha de vigencia del informe.
        emitido_por_id: FK al usuario que emitió el informe.
        revisado_por_id: FK al usuario que revisó el informe.
        aprobado_por_id: FK al usuario que aprobó el informe.
        resumen_resultados: Resumen de los resultados del análisis.
        conclusiones: Conclusiones del informe.
        observaciones: Observaciones adicionales.
        recomendaciones: Recomendaciones técnicas.
        numero_paginas: Número de páginas del documento.
        copias_entregadas: Cantidad de copias entregadas.
        medio_entrega: Medio de entrega según MedioEntrega.
        anulado: Flag de anulación.
        motivo_anulacion: Razón de la anulación.
        created_at: Timestamp de creación del registro.
        updated_at: Timestamp de última modificación.
    """

    __tablename__ = "informes"

    __table_args__ = (
        UniqueConstraint("nro_oficial", name="uq_informe_nro_oficial"),
        Index("ix_informe_nro_oficial_estado_fecha", "nro_oficial", "estado", "fecha_emision"),
    )

    id = db.Column(db.Integer, primary_key=True)

    nro_oficial = db.Column(db.String(50), unique=True, nullable=False, index=True)

    tipo_informe = db.Column(
        db.Enum(
            TipoInforme,
            name="tipo_informe",
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )

    entrada_id = db.Column(
        db.Integer,
        db.ForeignKey("entradas.id", ondelete="CASCADE"),
        nullable=False,
    )

    cliente_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id", ondelete="PROTECT"),
        nullable=False,
    )

    estado = db.Column(
        db.Enum(
            InformeStatus,
            name="informe_status",
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        default=InformeStatus.BORRADOR,
        nullable=False,
    )

    fecha_generacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_emision = db.Column(db.DateTime, nullable=True)
    fecha_entrega = db.Column(db.DateTime, nullable=True)
    fecha_vencimiento = db.Column(db.Date, nullable=True)

    emitido_por_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
    )

    revisado_por_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
    )

    aprobado_por_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
    )

    resumen_resultados = db.Column(db.Text, nullable=False)
    conclusiones = db.Column(db.Text, nullable=True, default="")
    observaciones = db.Column(db.Text, nullable=True, default="")
    recomendaciones = db.Column(db.Text, nullable=True, default="")

    numero_paginas = db.Column(db.Integer, default=1, nullable=False)
    copias_entregadas = db.Column(db.Integer, default=1, nullable=False)

    medio_entrega = db.Column(
        db.Enum(
            MedioEntrega,
            name="medio_entrega",
            native_enum=False,
            values_callable=lambda x: [e.value for e in x],
        ),
        default=MedioEntrega.FISICO,
        nullable=False,
    )

    anulado = db.Column(db.Boolean, default=False, nullable=False)
    motivo_anulacion = db.Column(db.Text, nullable=True, default="")

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    entrada = db.relationship("Entrada", backref="informes", lazy=True)
    cliente = db.relationship("Cliente", backref="informes", lazy=True)

    emitidos_por = db.relationship(
        "User",
        foreign_keys=[emitido_por_id],
        backref="informes_emitidos",
        lazy=True,
    )

    revisados_por = db.relationship(
        "User",
        foreign_keys=[revisado_por_id],
        backref="informes_revisados",
        lazy=True,
    )

    aprobados_por = db.relationship(
        "User",
        foreign_keys=[aprobado_por_id],
        backref="informes_aprobados",
        lazy=True,
    )

    ensayos = db.relationship(
        "DetalleEnsayo",
        secondary="informes_ensayos",
        backref="informes",
        lazy="dynamic",
    )

    VALID_TRANSITIONS: ClassVar[dict[str, list[str]]] = {
        InformeStatus.BORRADOR.value: [
            InformeStatus.PENDIENTE_FIRMA.value,
            InformeStatus.ANULADO.value,
        ],
        InformeStatus.PENDIENTE_FIRMA.value: [
            InformeStatus.EMITIDO.value,
            InformeStatus.BORRADOR.value,
            InformeStatus.ANULADO.value,
        ],
        InformeStatus.EMITIDO.value: [
            InformeStatus.ENTREGADO.value,
            InformeStatus.ANULADO.value,
        ],
        InformeStatus.ENTREGADO.value: [
            InformeStatus.ANULADO.value,
        ],
        InformeStatus.ANULADO.value: [],
    }

    def __repr__(self) -> str:
        return (
            f"<Informe id={self.id} "
            f"nro_oficial={self.nro_oficial} "
            f"tipo={self.tipo_informe} "
            f"estado={self.estado}>"
        )

    def to_dict(self) -> dict:
        """Serializa el informe a diccionario.

        Returns:
            dict: Representación del registro con todos los campos y
                  nombres de entidades relacionadas donde estén cargadas.
        """
        return {
            "id": self.id,
            "nro_oficial": self.nro_oficial,
            "tipo_informe": self.tipo_informe,
            "entrada_id": self.entrada_id,
            "entrada_codigo": self.entrada.codigo if self.entrada else None,
            "cliente_id": self.cliente_id,
            "cliente_nombre": self.cliente.nombre if self.cliente else None,
            "estado": self.estado,
            "fecha_generacion": (
                self.fecha_generacion.isoformat() if self.fecha_generacion else None
            ),
            "fecha_emision": (
                self.fecha_emision.isoformat() if self.fecha_emision else None
            ),
            "fecha_entrega": (
                self.fecha_entrega.isoformat() if self.fecha_entrega else None
            ),
            "fecha_vencimiento": (
                self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None
            ),
            "emitido_por_id": self.emitido_por_id,
            "emitido_por_nombre": (
                self.emitidos_por.nombre_completo if self.emitidos_por else None
            ),
            "revisado_por_id": self.revisado_por_id,
            "revisado_por_nombre": (
                self.revisados_por.nombre_completo if self.revisados_por else None
            ),
            "aprobado_por_id": self.aprobado_por_id,
            "aprobado_por_nombre": (
                self.aprobados_por.nombre_completo if self.aprobados_por else None
            ),
            "resumen_resultados": self.resumen_resultados,
            "conclusiones": self.conclusiones,
            "observaciones": self.observaciones,
            "recomendaciones": self.recomendaciones,
            "numero_paginas": self.numero_paginas,
            "copias_entregadas": self.copias_entregadas,
            "medio_entrega": self.medio_entrega,
            "anulado": self.anulado,
            "motivo_anulacion": self.motivo_anulacion,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "ensayos_ids": [e.id for e in self.ensayos] if self.ensayos else [],
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
            >>> Informe.can_transition("BORRADOR", "PENDIENTE_FIRMA")
            True
            >>> Informe.can_transition("BORRADOR", "ENTREGADO")
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
            >>> Informe.get_valid_transitions("BORRADOR")
            ['PENDIENTE_FIRMA', 'ANULADO']
            >>> Informe.get_valid_transitions("ANULADO")
            []
        """
        return cls.VALID_TRANSITIONS.get(current_status, [])


class InformeEnsayo(db.Model):
    """Tabla de unión para relación many-to-many entre Informes y DetalleEnsayo.

    Permite asociar múltiples ensayos (detalles) a múltiples informes.
    """

    __tablename__ = "informes_ensayos"

    informe_id = db.Column(
        db.Integer,
        db.ForeignKey("informes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    detalle_ensayo_id = db.Column(
        db.Integer,
        db.ForeignKey("detalles_ensayo.id", ondelete="CASCADE"),
        primary_key=True,
    )
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<InformeEnsayo informe={self.informe_id} detalle_ensayo={self.detalle_ensayo_id}>"

    def to_dict(self) -> dict:
        """Serializa la relación a diccionario."""
        return {
            "informe_id": self.informe_id,
            "detalle_ensayo_id": self.detalle_ensayo_id,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
        }
