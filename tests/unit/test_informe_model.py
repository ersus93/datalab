#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests unitarios para el modelo Informe."""

import pytest
from datetime import datetime, date
from sqlalchemy import UniqueConstraint, Index
from app.database.models.informe import (
    Informe, InformeStatus, TipoInforme, MedioEntrega, InformeEnsayo
)


class TestInformeModel:
    """Tests del modelo Informe."""

    def test_crear_informe_minimo(self):
        """Crear informe con campos mínimos obligatorios."""
        informe = Informe(
            nro_oficial="INF-2026-001",
            tipo_informe=TipoInforme.ANALISIS,
            entrada_id=1,
            cliente_id=2,
            resumen_resultados="Resultados del análisis",
        )

        assert informe.nro_oficial == "INF-2026-001"
        assert informe.tipo_informe == TipoInforme.ANALISIS
        assert informe.entrada_id == 1
        assert informe.cliente_id == 2
        assert informe.resumen_resultados == "Resultados del análisis"
        assert informe.conclusiones is None
        assert informe.observaciones is None
        assert informe.recomendaciones is None

    def test_estado_default_borrador(self):
        """El estado por defecto debe ser BORRADOR."""
        informe = Informe(
            nro_oficial="INF-2026-002",
            tipo_informe=TipoInforme.CERTIFICADO,
            entrada_id=1,
            cliente_id=2,
            resumen_resultados="Resumen",
        )
        # El default de SQLAlchemy se refleja en el Column
        estado_col = Informe.__table__.c.estado
        assert estado_col.default.arg == InformeStatus.BORRADOR

    def test_repr(self):
        """__repr__ debe incluir id, nro_oficial, tipo y estado."""
        informe = Informe(
            nro_oficial="INF-2026-003",
            tipo_informe=TipoInforme.ESPECIAL,
            entrada_id=5,
            cliente_id=10,
            resumen_resultados="Resumen de prueba",
        )
        informe.id = 42
        informe.estado = InformeStatus.EMITIDO

        texto = repr(informe)

        assert "42" in texto
        assert "INF-2026-003" in texto
        assert "ESPECIAL" in texto
        assert "EMITIDO" in texto

    def test_to_dict_contiene_campos(self):
        """to_dict() debe devolver todos los campos esperados."""
        informe = Informe(
            nro_oficial="INF-2026-004",
            tipo_informe=TipoInforme.ANALISIS,
            entrada_id=1,
            cliente_id=2,
            resumen_resultados="Resumen de resultados",
            conclusiones="Conclusiones del análisis",
            estado=InformeStatus.PENDIENTE_FIRMA,
        )
        informe.id = 10
        informe.fecha_generacion = datetime(2026, 1, 1, 10, 0, 0)
        informe.updated_at = datetime(2026, 1, 2, 10, 0, 0)

        resultado = informe.to_dict()

        campos_esperados = {
            'id', 'nro_oficial', 'tipo_informe',
            'entrada_id', 'entrada_codigo',
            'cliente_id', 'cliente_nombre',
            'estado',
            'fecha_generacion', 'fecha_emision', 'fecha_entrega', 'fecha_vencimiento',
            'emitido_por_id', 'emitido_por_nombre',
            'revisado_por_id', 'revisado_por_nombre',
            'aprobado_por_id', 'aprobado_por_nombre',
            'resumen_resultados', 'conclusiones', 'observaciones', 'recomendaciones',
            'numero_paginas', 'copias_entregadas', 'medio_entrega',
            'anulado', 'motivo_anulacion',
            'created_at', 'updated_at', 'ensayos_ids',
        }
        assert set(resultado.keys()) == campos_esperados
        assert resultado['id'] == 10
        assert resultado['nro_oficial'] == "INF-2026-004"
        assert resultado['tipo_informe'] == TipoInforme.ANALISIS
        assert resultado['entrada_id'] == 1
        assert resultado['cliente_id'] == 2
        assert resultado['estado'] == InformeStatus.PENDIENTE_FIRMA
        assert resultado['resumen_resultados'] == "Resumen de resultados"
        assert resultado['conclusiones'] == "Conclusiones del análisis"
        assert resultado['entrada_codigo'] is None
        assert resultado['cliente_nombre'] is None
        assert resultado['created_at'] is None
        assert resultado['updated_at'] == '2026-01-02T10:00:00'
        assert resultado['ensayos_ids'] == []


class TestInformeStatusMachine:
    """Tests de la máquina de estados del Informe."""

    def test_transicion_borrador_a_pendiente_firma(self):
        """BORRADOR → PENDIENTE_FIRMA es válida."""
        assert Informe.can_transition('BORRADOR', 'PENDIENTE_FIRMA') is True

    def test_transicion_pendiente_firma_a_emitido(self):
        """PENDIENTE_FIRMA → EMITIDO es válida."""
        assert Informe.can_transition('PENDIENTE_FIRMA', 'EMITIDO') is True

    def test_transicion_emitido_a_entregado(self):
        """EMITIDO → ENTREGADO es válida."""
        assert Informe.can_transition('EMITIDO', 'ENTREGADO') is True

    def test_transicion_cualquiera_a_anulado(self):
        """Cualquier estado puede ir a ANULADO."""
        assert Informe.can_transition('BORRADOR', 'ANULADO') is True
        assert Informe.can_transition('PENDIENTE_FIRMA', 'ANULADO') is True
        assert Informe.can_transition('EMITIDO', 'ANULADO') is True
        assert Informe.can_transition('ENTREGADO', 'ANULADO') is True

    def test_transicion_invalida_borrador_a_entregado(self):
        """BORRADOR → ENTREGADO no es válida (salto de estados)."""
        assert Informe.can_transition('BORRADOR', 'ENTREGADO') is False

    def test_transicion_invalida_entregado_a_borrador(self):
        """ENTREGADO → BORRADOR no es válida."""
        assert Informe.can_transition('ENTREGADO', 'BORRADOR') is False

    def test_transicion_invalida_entregado_a_emitido(self):
        """ENTREGADO → EMITIDO no es válida."""
        assert Informe.can_transition('ENTREGADO', 'EMITIDO') is False

    def test_transicion_invalida_borrador_a_emitido(self):
        """BORRADOR → EMITIDO no es válida."""
        assert Informe.can_transition('BORRADOR', 'EMITIDO') is False

    def test_transicion_anulado_no_tiene_salida(self):
        """ANULADO no tiene transiciones posibles: cualquier destino es False."""
        assert Informe.can_transition('ANULADO', 'BORRADOR') is False
        assert Informe.can_transition('ANULADO', 'PENDIENTE_FIRMA') is False
        assert Informe.can_transition('ANULADO', 'EMITIDO') is False
        assert Informe.can_transition('ANULADO', 'ENTREGADO') is False

    def test_transicion_estado_desconocido(self):
        """Un estado desconocido retorna False."""
        assert Informe.can_transition('INEXISTENTE', 'BORRADOR') is False
        assert Informe.can_transition('BORRADOR', 'INEXISTENTE') is False

    def test_get_valid_transitions_borrador(self):
        """BORRADOR solo puede ir a ['PENDIENTE_FIRMA', 'ANULADO']."""
        transiciones = Informe.get_valid_transitions('BORRADOR')
        assert transiciones == ['PENDIENTE_FIRMA', 'ANULADO']

    def test_get_valid_transitions_pendiente_firma(self):
        """PENDIENTE_FIRMA puede ir a ['EMITIDO', 'BORRADOR', 'ANULADO']."""
        transiciones = Informe.get_valid_transitions('PENDIENTE_FIRMA')
        assert transiciones == ['EMITIDO', 'BORRADOR', 'ANULADO']

    def test_get_valid_transitions_emitido(self):
        """EMITIDO puede ir a ['ENTREGADO', 'ANULADO']."""
        transiciones = Informe.get_valid_transitions('EMITIDO')
        assert transiciones == ['ENTREGADO', 'ANULADO']

    def test_get_valid_transitions_entregado(self):
        """ENTREGADO solo puede ir a ['ANULADO']."""
        transiciones = Informe.get_valid_transitions('ENTREGADO')
        assert transiciones == ['ANULADO']

    def test_get_valid_transitions_anulado(self):
        """ANULADO no tiene transiciones posibles: lista vacía."""
        transiciones = Informe.get_valid_transitions('ANULADO')
        assert transiciones == []

    def test_get_valid_transitions_estado_desconocido(self):
        """Estado desconocido devuelve lista vacía."""
        transiciones = Informe.get_valid_transitions('INEXISTENTE')
        assert transiciones == []

    def test_valid_transitions_cubre_todos_los_estados(self):
        """VALID_TRANSITIONS define entradas para todos los estados del enum."""
        estados_enum = {s.value for s in InformeStatus}
        estados_mapa = set(Informe.VALID_TRANSITIONS.keys())
        assert estados_enum == estados_mapa


class TestInformeConstraints:
    """Tests de constraints de base de datos."""

    def test_unique_constraint_nro_oficial(self):
        """Debe existir UniqueConstraint sobre nro_oficial."""
        tabla = Informe.__table__
        constraints = [
            c for c in tabla.constraints
            if isinstance(c, UniqueConstraint)
        ]
        nombres_columnas = set()
        for constraint in constraints:
            nombres_columnas.update(col.name for col in constraint.columns)

        assert 'nro_oficial' in nombres_columnas

    def test_unique_constraint_nombre(self):
        """El UniqueConstraint tiene el nombre esperado."""
        tabla = Informe.__table__
        nombres = {c.name for c in tabla.constraints if isinstance(c, UniqueConstraint)}
        assert 'uq_informe_nro_oficial' in nombres

    def test_index_on_nro_oficial_estado_fecha_emision(self):
        """Debe existir un índice compuesto sobre (nro_oficial, estado, fecha_emision)."""
        tabla = Informe.__table__
        indices = list(tabla.indexes)
        columnas_por_indice = [
            {col.name for col in idx.columns}
            for idx in indices
        ]
        assert {'nro_oficial', 'estado', 'fecha_emision'} in columnas_por_indice

    def test_index_nro_oficial_estado_fecha_nombre(self):
        """El índice compuesto tiene el nombre esperado."""
        tabla = Informe.__table__
        nombres = {idx.name for idx in tabla.indexes}
        assert 'ix_informe_nro_oficial_estado_fecha' in nombres

    def test_entrada_id_nullable_false(self):
        """entrada_id no puede ser nulo."""
        col = Informe.__table__.c.entrada_id
        assert col.nullable is False

    def test_entrada_id_cascade_delete(self):
        """entrada_id tiene CASCADE en ondelete."""
        col = Informe.__table__.c.entrada_id
        fk = list(col.foreign_keys)[0]
        assert str(fk.ondelete) == 'CASCADE'

    def test_cliente_id_nullable_false(self):
        """cliente_id no puede ser nulo."""
        col = Informe.__table__.c.cliente_id
        assert col.nullable is False

    def test_cliente_id_protect(self):
        """cliente_id tiene PROTECT en ondelete."""
        col = Informe.__table__.c.cliente_id
        fk = list(col.foreign_keys)[0]
        assert str(fk.ondelete) == 'PROTECT'

    def test_nro_oficial_unique_true(self):
        """nro_oficial debe ser único."""
        col = Informe.__table__.c.nro_oficial
        assert col.unique is True

    def test_estado_nullable_false(self):
        """estado no puede ser nulo."""
        col = Informe.__table__.c.estado
        assert col.nullable is False

    def test_fecha_generacion_nullable_false(self):
        """fecha_generacion no puede ser nulo."""
        col = Informe.__table__.c.fecha_generacion
        assert col.nullable is False
