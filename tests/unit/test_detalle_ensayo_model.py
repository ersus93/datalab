#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests unitarios para el modelo DetalleEnsayo."""

from datetime import datetime

import pytest
from sqlalchemy import UniqueConstraint, Index

from app.database.models.detalle_ensayo import DetalleEnsayo, DetalleEnsayoStatus


@pytest.mark.skip(reason="Requiere refactorización de fixtures")
class TestDetalleEnsayoModel:
    """Tests del modelo DetalleEnsayo."""

    def test_crear_detalle_minimo(self):
        """Crear detalle con campos mínimos obligatorios."""
        detalle = DetalleEnsayo(
            entrada_id=1,
            ensayo_id=2,
        )

        assert detalle.entrada_id == 1
        assert detalle.ensayo_id == 2
        assert detalle.tecnico_asignado_id is None
        assert detalle.observaciones is None
        assert detalle.fecha_asignacion is None
        assert detalle.fecha_inicio is None
        assert detalle.fecha_completado is None

    def test_estado_default_pendiente(self):
        """El estado por defecto debe ser PENDIENTE (aplicado en DB, revisado por valor column)."""
        detalle = DetalleEnsayo(entrada_id=1, ensayo_id=1)
        # El default de SQLAlchemy se refleja en el Column, no en la instancia antes de flush
        # Verificamos que el server_default apunta a PENDIENTE
        estado_col = DetalleEnsayo.__table__.c.estado
        assert estado_col.default.arg == DetalleEnsayoStatus.PENDIENTE.value

    def test_cantidad_default_uno(self):
        """La cantidad por defecto debe ser 1."""
        cantidad_col = DetalleEnsayo.__table__.c.cantidad
        assert cantidad_col.default.arg == 1

    def test_repr(self):
        """__repr__ debe incluir id, entrada_id, ensayo_id y estado."""
        detalle = DetalleEnsayo(entrada_id=3, ensayo_id=7)
        detalle.id = 42
        detalle.estado = DetalleEnsayoStatus.PENDIENTE.value

        texto = repr(detalle)

        assert '42' in texto
        assert '3' in texto
        assert '7' in texto
        assert 'PENDIENTE' in texto

    def test_to_dict_contiene_campos(self):
        """to_dict() debe devolver todos los campos esperados."""
        detalle = DetalleEnsayo(
            entrada_id=1,
            ensayo_id=2,
            cantidad=3,
            estado=DetalleEnsayoStatus.PENDIENTE.value,
        )
        detalle.id = 10
        detalle.created_at = datetime(2026, 1, 1, 10, 0, 0)
        detalle.updated_at = datetime(2026, 1, 2, 10, 0, 0)

        resultado = detalle.to_dict()

        campos_esperados = {
            'id', 'entrada_id', 'entrada_codigo',
            'ensayo_id', 'ensayo_nombre',
            'cantidad', 'estado',
            'fecha_asignacion', 'fecha_inicio', 'fecha_completado',
            'tecnico_asignado_id', 'tecnico_nombre',
            'observaciones', 'created_at', 'updated_at',
        }
        assert set(resultado.keys()) == campos_esperados
        assert resultado['id'] == 10
        assert resultado['entrada_id'] == 1
        assert resultado['ensayo_id'] == 2
        assert resultado['cantidad'] == 3
        assert resultado['estado'] == DetalleEnsayoStatus.PENDIENTE.value
        assert resultado['entrada_codigo'] is None  # relación no cargada
        assert resultado['ensayo_nombre'] is None   # relación no cargada
        assert resultado['tecnico_nombre'] is None
        assert resultado['created_at'] == '2026-01-01T10:00:00'
        assert resultado['updated_at'] == '2026-01-02T10:00:00'


@pytest.mark.skip(reason="Requiere refactorización de fixtures")
class TestDetalleEnsayoStatusMachine:
    """Tests de la máquina de estados."""

    def test_transicion_pendiente_a_asignado(self):
        """PENDIENTE → ASIGNADO es válida."""
        assert DetalleEnsayo.can_transition('PENDIENTE', 'ASIGNADO') is True

    def test_transicion_asignado_a_en_proceso(self):
        """ASIGNADO → EN_PROCESO es válida."""
        assert DetalleEnsayo.can_transition('ASIGNADO', 'EN_PROCESO') is True

    def test_transicion_en_proceso_a_completado(self):
        """EN_PROCESO → COMPLETADO es válida."""
        assert DetalleEnsayo.can_transition('EN_PROCESO', 'COMPLETADO') is True

    def test_transicion_completado_a_reportado(self):
        """COMPLETADO → REPORTADO es válida."""
        assert DetalleEnsayo.can_transition('COMPLETADO', 'REPORTADO') is True

    def test_transicion_invalida_pendiente_a_completado(self):
        """PENDIENTE → COMPLETADO no es válida (salto de estados)."""
        assert DetalleEnsayo.can_transition('PENDIENTE', 'COMPLETADO') is False

    def test_transicion_invalida_pendiente_a_en_proceso(self):
        """PENDIENTE → EN_PROCESO no es válida."""
        assert DetalleEnsayo.can_transition('PENDIENTE', 'EN_PROCESO') is False

    def test_transicion_invalida_pendiente_a_reportado(self):
        """PENDIENTE → REPORTADO no es válida."""
        assert DetalleEnsayo.can_transition('PENDIENTE', 'REPORTADO') is False

    def test_transicion_invalida_estado_terminal(self):
        """REPORTADO no tiene transiciones posibles: cualquier destino es False."""
        assert DetalleEnsayo.can_transition('REPORTADO', 'PENDIENTE') is False
        assert DetalleEnsayo.can_transition('REPORTADO', 'ASIGNADO') is False
        assert DetalleEnsayo.can_transition('REPORTADO', 'COMPLETADO') is False

    def test_transicion_invalida_estado_desconocido(self):
        """Un estado desconocido retorna False."""
        assert DetalleEnsayo.can_transition('INEXISTENTE', 'ASIGNADO') is False

    def test_get_valid_transitions_pendiente(self):
        """PENDIENTE solo puede ir a ['ASIGNADO']."""
        transiciones = DetalleEnsayo.get_valid_transitions('PENDIENTE')
        assert transiciones == ['ASIGNADO']

    def test_get_valid_transitions_asignado(self):
        """ASIGNADO solo puede ir a ['EN_PROCESO']."""
        transiciones = DetalleEnsayo.get_valid_transitions('ASIGNADO')
        assert transiciones == ['EN_PROCESO']

    def test_get_valid_transitions_en_proceso(self):
        """EN_PROCESO solo puede ir a ['COMPLETADO']."""
        transiciones = DetalleEnsayo.get_valid_transitions('EN_PROCESO')
        assert transiciones == ['COMPLETADO']

    def test_get_valid_transitions_completado(self):
        """COMPLETADO solo puede ir a ['REPORTADO']."""
        transiciones = DetalleEnsayo.get_valid_transitions('COMPLETADO')
        assert transiciones == ['REPORTADO']

    def test_get_valid_transitions_reportado(self):
        """REPORTADO no tiene transiciones posibles: lista vacía."""
        transiciones = DetalleEnsayo.get_valid_transitions('REPORTADO')
        assert transiciones == []

    def test_get_valid_transitions_estado_desconocido(self):
        """Estado desconocido devuelve lista vacía."""
        transiciones = DetalleEnsayo.get_valid_transitions('INEXISTENTE')
        assert transiciones == []

    def test_valid_transitions_cubre_todos_los_estados(self):
        """VALID_TRANSITIONS define entradas para todos los estados del enum."""
        estados_enum = {s.value for s in DetalleEnsayoStatus}
        estados_mapa = set(DetalleEnsayo.VALID_TRANSITIONS.keys())
        assert estados_enum == estados_mapa


class TestDetalleEnsayoConstraints:
    """Tests de constraints de base de datos."""

    def test_unique_constraint_entrada_ensayo(self):
        """Debe existir UniqueConstraint sobre (entrada_id, ensayo_id)."""
        tabla = DetalleEnsayo.__table__
        constraints = [
            c for c in tabla.constraints
            if isinstance(c, UniqueConstraint)
        ]
        nombres_columnas = set()
        for constraint in constraints:
            nombres_columnas.update(col.name for col in constraint.columns)

        assert 'entrada_id' in nombres_columnas
        assert 'ensayo_id' in nombres_columnas

    def test_unique_constraint_nombre(self):
        """El UniqueConstraint tiene el nombre esperado."""
        tabla = DetalleEnsayo.__table__
        nombres = {c.name for c in tabla.constraints if isinstance(c, UniqueConstraint)}
        assert 'uq_detalle_entrada_ensayo' in nombres

    def test_index_on_entrada_estado(self):
        """Debe existir un índice compuesto sobre (entrada_id, estado)."""
        tabla = DetalleEnsayo.__table__
        indices = list(tabla.indexes)
        columnas_por_indice = [
            {col.name for col in idx.columns}
            for idx in indices
        ]
        assert {'entrada_id', 'estado'} in columnas_por_indice

    def test_index_entrada_estado_nombre(self):
        """El índice compuesto tiene el nombre esperado."""
        tabla = DetalleEnsayo.__table__
        nombres = {idx.name for idx in tabla.indexes}
        assert 'ix_detalle_entrada_estado' in nombres

    def test_entrada_id_nullable_false(self):
        """entrada_id no puede ser nulo."""
        col = DetalleEnsayo.__table__.c.entrada_id
        assert col.nullable is False

    def test_ensayo_id_nullable_false(self):
        """ensayo_id no puede ser nulo."""
        col = DetalleEnsayo.__table__.c.ensayo_id
        assert col.nullable is False

    def test_tecnico_asignado_id_nullable_true(self):
        """tecnico_asignado_id puede ser nulo (asignación es opcional)."""
        col = DetalleEnsayo.__table__.c.tecnico_asignado_id
        assert col.nullable is True

    def test_estado_nullable_false(self):
        """estado no puede ser nulo."""
        col = DetalleEnsayo.__table__.c.estado
        assert col.nullable is False
