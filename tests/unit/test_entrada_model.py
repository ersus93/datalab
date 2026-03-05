#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests unitarios para el modelo Entrada."""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.database.models.entrada import Entrada, EntradaStatus, calculate_balance


class TestEntradaCreation:
    """Tests de creacion basica de entradas."""

    def test_crear_entrada_minima(self):
        """Crear entrada con solo campos obligatorios."""
        entrada = Entrada(
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100')
        )

        assert entrada.codigo == 'ENT001'
        assert entrada.producto_id == 1
        assert entrada.fabrica_id == 1
        assert entrada.cliente_id == 1
        assert entrada.cantidad_recib == Decimal('100')
        # Los defaults de SQLAlchemy se aplican en la base de datos
        assert entrada.cantidad_entreg is None
        assert entrada.saldo is None
        assert entrada.status is None
        assert entrada.ent_entregada is None
        assert entrada.anulado is None
        assert entrada.en_os is None

    def test_crear_entrada_completa(self):
        """Crear entrada con todos los campos."""
        entrada = Entrada(
            codigo='ENT002',
            pedido_id=1,
            producto_id=2,
            fabrica_id=3,
            cliente_id=4,
            rama_id=1,
            unidad_medida_id=1,
            lote='A-1234',
            nro_parte='PART-001',
            cantidad_recib=Decimal('500'),
            cantidad_entreg=Decimal('100'),
            cantidad_muest=Decimal('50'),
            fech_fab=date(2024, 1, 15),
            fech_venc=date(2025, 1, 15),
            fech_muestreo=date(2024, 2, 1),
            observaciones='Observaciones de prueba'
        )

        assert entrada.codigo == 'ENT002'
        assert entrada.pedido_id == 1
        assert entrada.producto_id == 2
        assert entrada.fabrica_id == 3
        assert entrada.cliente_id == 4
        assert entrada.rama_id == 1
        assert entrada.unidad_medida_id == 1
        assert entrada.lote == 'A-1234'
        assert entrada.nro_parte == 'PART-001'
        assert entrada.cantidad_recib == Decimal('500')
        assert entrada.cantidad_entreg == Decimal('100')
        assert entrada.cantidad_muest == Decimal('50')
        assert entrada.fech_fab == date(2024, 1, 15)
        assert entrada.fech_venc == date(2025, 1, 15)
        assert entrada.fech_muestreo == date(2024, 2, 1)
        assert entrada.observaciones == 'Observaciones de prueba'

    @patch('app.database.models.entrada.db')
    def test_entrada_codigo_unique(self, mock_db):
        """Verificar que codigo sea unico en la base de datos."""
        from sqlalchemy import UniqueConstraint, Index

        tabla = Entrada.__table__

        constraints = [c for c in tabla.constraints if isinstance(c, UniqueConstraint)]
        unique_columns = []
        for constraint in constraints:
            unique_columns.extend([col.name for col in constraint.columns])

        indices = [i for i in tabla.indexes if i.unique]
        for idx in indices:
            unique_columns.extend([col.name for col in idx.columns])

        assert 'codigo' in unique_columns


class TestEntradaValidations:
    """Tests de validaciones del modelo."""

    def test_validar_lote_formato_valido(self):
        """Probar lotes con formato valido X-XXXX."""
        entrada = Entrada(
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100')
        )

        assert entrada.validate_lote('lote', 'A-1234') == 'A-1234'
        assert entrada.validate_lote('lote', 'B-9999') == 'B-9999'
        assert entrada.validate_lote('lote', 'Z-0001') == 'Z-0001'
        assert entrada.validate_lote('lote', 'M-5678') == 'M-5678'

    def test_validar_lote_formato_invalido(self):
        """Probar lotes con formato invalido."""
        entrada = Entrada(
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100')
        )

        with pytest.raises(ValueError, match='Formato de lote'):
            entrada.validate_lote('lote', '1234')

        with pytest.raises(ValueError, match='Formato de lote'):
            entrada.validate_lote('lote', 'A123')

        with pytest.raises(ValueError, match='Formato de lote'):
            entrada.validate_lote('lote', 'A-123')

        with pytest.raises(ValueError, match='Formato de lote'):
            entrada.validate_lote('lote', 'a-1234')

        with pytest.raises(ValueError, match='Formato de lote'):
            entrada.validate_lote('lote', 'AA-1234')

        with pytest.raises(ValueError, match='Formato de lote'):
            entrada.validate_lote('lote', 'A-12345')

    def test_validar_lote_none(self):
        """Permitir lote None."""
        entrada = Entrada(
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100')
        )

        assert entrada.validate_lote('lote', None) is None

    def test_validar_fech_venc_posterior(self):
        """fech_venc > fech_fab debe funcionar."""
        entrada = Entrada(
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100'),
            fech_fab=date(2024, 1, 1)
        )

        result = entrada.validate_fech_venc('fech_venc', date(2025, 1, 1))
        assert result == date(2025, 1, 1)

    def test_validar_fech_venc_anterior(self):
        """fech_venc < fech_fab debe lanzar ValueError."""
        entrada = Entrada(
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100'),
            fech_fab=date(2025, 1, 1)
        )

        with pytest.raises(ValueError, match='vencimiento'):
            entrada.validate_fech_venc('fech_venc', date(2024, 1, 1))

    def test_validar_fech_venc_igual(self):
        """fech_venc == fech_fab es permitido (solo < es rechazado)."""
        entrada = Entrada(
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100'),
            fech_fab=date(2024, 1, 1)
        )

        # Fechas iguales son permitidas (validacion solo rechaza <)
        result = entrada.validate_fech_venc('fech_venc', date(2024, 1, 1))
        assert result == date(2024, 1, 1)

    def test_validar_cantidad_recib_negativa(self):
        """cantidad_recib < 0 debe lanzar ValueError."""
        entrada = Entrada(
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100')
        )

        with pytest.raises(ValueError, match='negativas'):
            entrada.validate_cantidades('cantidad_recib', Decimal('-1'))

        with pytest.raises(ValueError, match='negativas'):
            entrada.validate_cantidades('cantidad_recib', Decimal('-100.50'))

    def test_validar_cantidad_entreg_negativa(self):
        """cantidad_entreg < 0 debe lanzar ValueError."""
        entrada = Entrada(
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100')
        )

        with pytest.raises(ValueError, match='negativas'):
            entrada.validate_cantidades('cantidad_entreg', Decimal('-1'))

        with pytest.raises(ValueError, match='negativas'):
            entrada.validate_cantidades('cantidad_entreg', Decimal('-50'))


class TestEntradaSaldoCalculation:
    """Tests de calculo de saldo."""

    def test_calcular_saldo_basico(self):
        """Calcular saldo: 100 - 30 = 70."""
        entrada = Entrada(
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100'),
            cantidad_entreg=Decimal('30')
        )

        saldo = entrada.calcular_saldo()

        assert saldo == Decimal('70')
        assert entrada.saldo == Decimal('70')

    def test_calcular_saldo_cero(self):
        """Calcular saldo: 100 - 100 = 0."""
        entrada = Entrada(
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100'),
            cantidad_entreg=Decimal('100')
        )

        saldo = entrada.calcular_saldo()

        assert saldo == Decimal('0')
        assert entrada.saldo == Decimal('0')

    def test_calcular_saldo_negativo(self):
        """Calcular saldo: 50 - 100 = -50 (permitido en calculo)."""
        entrada = Entrada(
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('50'),
            cantidad_entreg=Decimal('100')
        )

        saldo = entrada.calcular_saldo()

        assert saldo == Decimal('-50')
        assert entrada.saldo == Decimal('-50')

    def test_saldo_default(self):
        """Verificar default=None antes de commit (default=0 en DB)."""
        entrada = Entrada(
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100')
        )

        # Antes de flush, los defaults no se aplican
        assert entrada.saldo is None


class TestEntradaToDict:
    """Tests de serializacion a diccionario."""

    def test_to_dict_contiene_campos_esperados(self):
        """Verificar que to_dict incluye los campos esperados."""
        entrada = Entrada(
            id=1,
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100'),
            cantidad_entreg=Decimal('30'),
            saldo=Decimal('70'),
            status=EntradaStatus.RECIBIDO,
            fech_entrada=datetime(2024, 1, 15, 10, 30, 0)
        )

        result = entrada.to_dict()

        expected_keys = {
            'id', 'codigo', 'lote', 'producto', 'cliente',
            'fabrica', 'status', 'cantidad_recib', 'cantidad_entreg',
            'saldo', 'fech_entrada'
        }
        assert set(result.keys()) == expected_keys
        assert result['id'] == 1
        assert result['codigo'] == 'ENT001'
        assert result['status'] == EntradaStatus.RECIBIDO
        assert result['cantidad_recib'] == '100'
        assert result['cantidad_entreg'] == '30'
        assert result['saldo'] == '70'
        assert result['fech_entrada'] == '2024-01-15T10:30:00'

    def test_to_dict_con_relaciones(self):
        """Verificar que incluye nombres de relaciones."""
        entrada = Entrada(
            id=1,
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100'),
            status=EntradaStatus.RECIBIDO
        )

        mock_producto = MagicMock()
        mock_producto.nombre = 'Producto Test'
        entrada.producto = mock_producto

        mock_cliente = MagicMock()
        mock_cliente.nombre = 'Cliente Test'
        entrada.cliente = mock_cliente

        mock_fabrica = MagicMock()
        mock_fabrica.nombre = 'Fabrica Test'
        entrada.fabrica = mock_fabrica

        result = entrada.to_dict()

        assert result['producto'] == 'Producto Test'
        assert result['cliente'] == 'Cliente Test'
        assert result['fabrica'] == 'Fabrica Test'

    def test_to_dict_sin_relaciones(self):
        """Manejar cuando relaciones son None."""
        entrada = Entrada(
            id=1,
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100'),
            status=EntradaStatus.RECIBIDO,
            fech_entrada=None
        )

        result = entrada.to_dict()

        assert result['producto'] is None
        assert result['cliente'] is None
        assert result['fabrica'] is None
        assert result['lote'] is None
        assert result['fech_entrada'] is None


class TestEntradaStatus:
    """Tests de estados de entrada."""

    def test_status_default_recibido(self):
        """Verificar default=None antes de commit (default=RECIBIDO en DB)."""
        entrada = Entrada(
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100')
        )

        # Antes de flush, los defaults no se aplican
        assert entrada.status is None

    def test_status_posibles_valores(self):
        """Probar todos los estados validos."""
        estados = [
            EntradaStatus.RECIBIDO,
            EntradaStatus.EN_PROCESO,
            EntradaStatus.COMPLETADO,
            EntradaStatus.ENTREGADO,
            EntradaStatus.ANULADO
        ]

        expected = ['RECIBIDO', 'EN_PROCESO', 'COMPLETADO', 'ENTREGADO', 'ANULADO']

        for estado, expected_value in zip(estados, expected):
            assert estado == expected_value


class TestEntradaEventListeners:
    """Tests de event listeners."""

    def test_event_listener_calcula_saldo(self):
        """Verificar que before_insert calcula saldo."""
        entrada = Entrada(
            id=1,
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100'),
            cantidad_entreg=Decimal('30'),
            status=EntradaStatus.RECIBIDO
        )

        mock_connection = MagicMock()
        mock_mapper = MagicMock()

        calculate_balance(mock_mapper, mock_connection, entrada)

        assert entrada.saldo == Decimal('70')

    def test_event_listener_actualiza_entregada(self):
        """Verificar que actualiza ent_entregada cuando saldo <= 0."""
        entrada = Entrada(
            id=1,
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100'),
            cantidad_entreg=Decimal('100'),
            status=EntradaStatus.RECIBIDO
        )

        mock_connection = MagicMock()
        mock_mapper = MagicMock()

        calculate_balance(mock_mapper, mock_connection, entrada)

        assert entrada.ent_entregada is True

    def test_event_listener_cambia_status_entregado(self):
        """Verificar cambio a ENTREGADO cuando completado y entregada."""
        entrada = Entrada(
            id=1,
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100'),
            cantidad_entreg=Decimal('100'),
            status=EntradaStatus.COMPLETADO
        )

        mock_connection = MagicMock()
        mock_mapper = MagicMock()

        calculate_balance(mock_mapper, mock_connection, entrada)

        assert entrada.status == EntradaStatus.ENTREGADO
        assert entrada.ent_entregada is True

    def test_event_listener_no_cambia_status_si_no_completado(self):
        """No cambiar status si no esta en COMPLETADO."""
        entrada = Entrada(
            id=1,
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100'),
            cantidad_entreg=Decimal('100'),
            status=EntradaStatus.RECIBIDO
        )

        mock_connection = MagicMock()
        mock_mapper = MagicMock()

        calculate_balance(mock_mapper, mock_connection, entrada)

        assert entrada.status == EntradaStatus.RECIBIDO
        assert entrada.ent_entregada is True

    def test_event_listener_saldo_positivo_no_entregada(self):
        """Saldo positivo no marca como entregada."""
        entrada = Entrada(
            id=1,
            codigo='ENT001',
            producto_id=1,
            fabrica_id=1,
            cliente_id=1,
            cantidad_recib=Decimal('100'),
            cantidad_entreg=Decimal('30'),
            status=EntradaStatus.COMPLETADO
        )

        mock_connection = MagicMock()
        mock_mapper = MagicMock()

        calculate_balance(mock_mapper, mock_connection, entrada)

        assert entrada.ent_entregada is False
        assert entrada.status == EntradaStatus.COMPLETADO

    def test_repr(self):
        """Verificar representacion string del modelo."""
        entrada = Entrada(codigo='ENT001')

        assert repr(entrada) == '<Entrada ENT001>'
