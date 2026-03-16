#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests unitarios para el servicio EntradaService."""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.services.entrada_service import EntradaService


class TestCrearEntrada:
    """Tests para la creacion de entradas."""

    @patch('app.services.entrada_service.db')
    @patch('app.database.models.status_history.StatusHistory')
    @patch('app.database.models.entrada.Entrada')
    @patch('app.database.models.entrada.EntradaStatus')
    def test_crear_entrada_success(self, mock_status_class, mock_entrada_class,
                                    mock_history_class, mock_db):
        """Crear entrada con datos validos."""
        # Setup mocks
        mock_entrada_instance = MagicMock()
        mock_entrada_instance.id = 1
        mock_entrada_instance.to_dict.return_value = {'id': 1, 'codigo': 'ENT001'}
        mock_entrada_class.return_value = mock_entrada_instance

        mock_entrada_status = MagicMock()
        mock_entrada_status.RECIBIDO = 'RECIBIDO'
        mock_status_class.RECIBIDO = 'RECIBIDO'

        mock_db.session.add = MagicMock()
        mock_db.session.flush = MagicMock()
        mock_db.session.commit = MagicMock()

        data = {
            'codigo': 'ENT001',
            'lote': 'A-1234',
            'producto_id': 1,
            'fabrica_id': 1,
            'cliente_id': 1,
            'cantidad_recib': 100.0,
            'cantidad_entreg': 0,
            'fech_fab': date(2024, 1, 1),
            'fech_venc': date(2025, 1, 1)
        }

        result = EntradaService.crear_entrada(data, usuario_id=1)

        assert result is not None
        mock_db.session.add.assert_called()
        mock_db.session.commit.assert_called()

    def test_crear_entrada_invalid_lote(self):
        """Rechaza formato de lote invalido (no X-XXXX)."""
        data = {
            'codigo': 'ENT001',
            'lote': 'INVALIDO',
            'producto_id': 1,
            'fabrica_id': 1,
            'cliente_id': 1,
            'cantidad_recib': 100.0,
            'cantidad_entreg': 0
        }

        with pytest.raises(ValueError, match='Formato de lote'):
            EntradaService.crear_entrada(data, usuario_id=1)

    def test_crear_entrada_invalid_dates(self):
        """Rechaza cuando FechVenc <= FechFab."""
        data = {
            'codigo': 'ENT001',
            'lote': 'A-1234',
            'producto_id': 1,
            'fabrica_id': 1,
            'cliente_id': 1,
            'cantidad_recib': 100.0,
            'cantidad_entreg': 0,
            'fech_fab': date(2025, 1, 1),
            'fech_venc': date(2024, 1, 1)  # Anterior a fabricacion
        }

        with pytest.raises(ValueError, match='vencimiento'):
            EntradaService.crear_entrada(data, usuario_id=1)

    def test_crear_entrada_calculates_saldo(self):
        """Verifica calculo automatico del saldo."""
        saldo = EntradaService._calcular_saldo(
            Decimal('100'),
            Decimal('30')
        )
        assert saldo == Decimal('70')

    def test_calcular_saldo_no_negative(self):
        """El saldo nunca es negativo."""
        saldo = EntradaService._calcular_saldo(
            Decimal('50'),
            Decimal('100')
        )
        assert saldo == Decimal('0')


class TestActualizarEntrada:
    """Tests para actualizacion de entradas."""

    @patch('app.services.entrada_service.db')
    @patch('app.database.models.status_history.StatusHistory')
    @patch('app.database.models.entrada.Entrada')
    @patch('app.database.models.entrada.EntradaStatus')
    def test_actualizar_entrada_success(self, mock_status_class, mock_entrada_class,
                                         mock_history_class, mock_db):
        """Actualiza entrada correctamente."""
        mock_entrada = MagicMock()
        mock_entrada.anulado = False
        mock_entrada.lote = 'A-0001'
        mock_entrada.fech_fab = date(2024, 1, 1)
        mock_entrada.fech_venc = date(2025, 1, 1)
        mock_entrada.cantidad_recib = Decimal('100')
        mock_entrada.cantidad_entreg = Decimal('0')
        mock_entrada.status = 'RECIBIDO'

        mock_query = MagicMock()
        mock_query.get.return_value = mock_entrada
        mock_entrada_class.query = mock_query

        mock_db.session.commit = MagicMock()

        result = EntradaService.actualizar_entrada(
            1,
            {'observaciones': 'Nueva observacion'},
            usuario_id=1
        )

        assert result is not None
        mock_db.session.commit.assert_called()

    @patch('app.database.models.entrada.Entrada')
    def test_actualizar_entrada_anulado_fails(self, mock_entrada_class):
        """No se puede actualizar entrada ANULADA."""
        mock_entrada = MagicMock()
        mock_entrada.anulado = True

        mock_query = MagicMock()
        mock_query.get.return_value = mock_entrada
        mock_entrada_class.query = mock_query

        with pytest.raises(ValueError, match='anulada'):
            EntradaService.actualizar_entrada(1, {'observaciones': 'test'}, 1)


class TestEliminarEntrada:
    """Tests para eliminacion (soft delete) de entradas."""

    @patch('app.services.entrada_service.db')
    @patch('app.database.models.status_history.StatusHistory')
    @patch('app.database.models.entrada.Entrada')
    @patch('app.database.models.entrada.EntradaStatus')
    def test_eliminar_entrada_soft_delete(self, mock_status_class, mock_entrada_class,
                                           mock_history_class, mock_db):
        """Marca como anulado y cambia el estado."""
        mock_entrada = MagicMock()
        mock_entrada.anulado = False
        mock_entrada.status = 'RECIBIDO'

        mock_query = MagicMock()
        mock_query.get.return_value = mock_entrada
        mock_entrada_class.query = mock_query

        mock_entrada_status = MagicMock()
        mock_entrada_status.ANULADO = 'ANULADO'
        mock_status_class.ANULADO = 'ANULADO'

        mock_db.session.commit = MagicMock()

        result = EntradaService.eliminar_entrada(1, usuario_id=1)

        assert result.anulado is True
        assert result.status == 'ANULADO'
        mock_db.session.commit.assert_called()


class TestRegistrarEntrega:
    """Tests para registro de entregas."""

    @patch('app.services.entrada_service.db')
    @patch('app.database.models.status_history.StatusHistory')
    @patch('app.database.models.entrada.Entrada')
    @patch('app.database.models.entrada.EntradaStatus')
    def test_registrar_entrega_updates_balance(self, mock_status_class, mock_entrada_class,
                                                mock_history_class, mock_db):
        """La entrega actualiza cantidad_entreg y saldo."""
        mock_entrada = MagicMock()
        mock_entrada.anulado = False
        mock_entrada.cantidad_recib = Decimal('100')
        mock_entrada.cantidad_entreg = Decimal('20')
        mock_entrada.saldo = Decimal('80')
        mock_entrada.status = 'COMPLETADO'

        mock_query = MagicMock()
        mock_query.get.return_value = mock_entrada
        mock_entrada_class.query = mock_query

        mock_entrada_status = MagicMock()
        mock_entrada_status.ENTREGADO = 'ENTREGADO'
        mock_entrada_status.COMPLETADO = 'COMPLETADO'
        mock_status_class.ENTREGADO = 'ENTREGADO'
        mock_status_class.COMPLETADO = 'COMPLETADO'

        mock_db.session.commit = MagicMock()
        mock_db.session.add = MagicMock()

        result = EntradaService.registrar_entrega(
            1,
            Decimal('30'),
            usuario_id=1
        )

        assert result.cantidad_entreg == Decimal('50')  # 20 + 30

    @patch('app.database.models.entrada.Entrada')
    def test_registrar_entrega_negative_balance_fails(self, mock_entrada_class):
        """Previene saldo negativo."""
        mock_entrada = MagicMock()
        mock_entrada.anulado = False
        mock_entrada.cantidad_recib = Decimal('100')
        mock_entrada.cantidad_entreg = Decimal('80')
        mock_entrada.saldo = Decimal('20')

        mock_query = MagicMock()
        mock_query.get.return_value = mock_entrada
        mock_entrada_class.query = mock_query

        with pytest.raises(ValueError, match='entregar'):
            EntradaService.registrar_entrega(1, Decimal('50'), 1)  # Intenta entregar 50 cuando solo quedan 20


class TestCambiarEstado:
    """Tests para cambio de estado."""

    @patch('app.services.entrada_service.StatusWorkflow')
    @patch('app.services.entrada_service.db')
    @patch('app.database.models.entrada.Entrada')
    def test_cambiar_estado_valid_transition(self, mock_entrada_class, mock_db, mock_workflow):
        """Transicion de estado valida ejecuta sin error."""
        mock_entrada = MagicMock()
        mock_entrada.status = 'RECIBIDO'

        mock_query = MagicMock()
        mock_query.get.return_value = mock_entrada
        mock_entrada_class.query = mock_query

        mock_db.session.commit = MagicMock()
        mock_workflow.transition.return_value = True

        # Solo verificar que no hay excepcion y el resultado es correcto
        result = EntradaService.cambiar_estado(1, 'EN_PROCESO', 1, 'Iniciar proceso')

        assert result is not None
        assert result == mock_entrada

    @patch('app.services.entrada_service.StatusWorkflow')
    @patch('app.database.models.entrada.Entrada')
    def test_cambiar_estado_invalid_transition_fails(self, mock_entrada_class, mock_workflow):
        """Transicion invalida lanza error."""
        mock_entrada = MagicMock()

        mock_query = MagicMock()
        mock_query.get.return_value = mock_entrada
        mock_entrada_class.query = mock_query

        mock_workflow.transition.side_effect = ValueError('Transicion no valida')

        with pytest.raises(ValueError, match='Transicion no valida'):
            EntradaService.cambiar_estado(1, 'INVALIDO', 1)


class TestObtenerEntradas:
    """Tests para consulta de entradas."""

    @patch('app.services.entrada_service.desc')
    @patch('app.database.models.entrada.Entrada')
    def test_obtener_entradas_paginadas(self, mock_entrada_class, mock_desc):
        """Paginacion funciona con filtros."""
        mock_entrada1 = MagicMock()
        mock_entrada2 = MagicMock()

        mock_pagination = MagicMock()
        mock_pagination.items = [mock_entrada1, mock_entrada2]
        mock_pagination.total = 2
        mock_pagination.pages = 1
        mock_pagination.has_next = False
        mock_pagination.has_prev = False
        mock_pagination.next_num = None
        mock_pagination.prev_num = None

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.paginate.return_value = mock_pagination
        mock_entrada_class.query = mock_query
        mock_entrada_class.fech_entrada = MagicMock()

        entradas, meta = EntradaService.obtener_entradas_paginadas(
            filtros={'cliente_id': 1},
            pagina=1,
            por_pagina=20
        )

        assert len(entradas) == 2
        assert meta['total'] == 2
        assert meta['pagina'] == 1

    @patch('app.database.models.entrada.Entrada')
    def test_obtener_entrada_por_id_found(self, mock_entrada_class):
        """Retorna entrada existente."""
        mock_entrada = MagicMock()
        mock_entrada.id = 1

        mock_query = MagicMock()
        mock_query.get.return_value = mock_entrada
        mock_entrada_class.query = mock_query

        result = EntradaService.obtener_entrada_por_id(1)

        assert result is not None
        assert result.id == 1

    @patch('app.database.models.entrada.Entrada')
    def test_obtener_entrada_por_id_not_found(self, mock_entrada_class):
        """Retorna None para ID inexistente."""
        mock_query = MagicMock()
        mock_query.get.return_value = None
        mock_entrada_class.query = mock_query

        result = EntradaService.obtener_entrada_por_id(999)

        assert result is None


class TestValidaciones:
    """Tests para metodos de validacion privados."""

    def test_validar_lote_valido(self):
        """Acepta lote con formato X-XXXX."""
        EntradaService._validar_lote('A-1234')  # No debe lanzar error
        EntradaService._validar_lote('Z-9999')  # No debe lanzar error

    def test_validar_lote_invalido(self):
        """Rechaza lote con formato incorrecto."""
        with pytest.raises(ValueError, match='Formato de lote'):
            EntradaService._validar_lote('1234')
        with pytest.raises(ValueError, match='Formato de lote'):
            EntradaService._validar_lote('AA-1234')
        with pytest.raises(ValueError, match='Formato de lote'):
            EntradaService._validar_lote('A-123')

    def test_validar_fechas_validas(self):
        """Acepta cuando vencimiento > fabricacion."""
        EntradaService._validar_fechas(
            date(2024, 1, 1),
            date(2025, 1, 1)
        )  # No debe lanzar error

    def test_validar_fechas_invalidas(self):
        """Rechaza cuando vencimiento <= fabricacion."""
        with pytest.raises(ValueError, match='vencimiento'):
            EntradaService._validar_fechas(
                date(2025, 1, 1),
                date(2024, 1, 1)
            )

    def test_validar_no_anulado(self):
        """Lanza error si entrada esta anulada."""
        mock_entrada = MagicMock()
        mock_entrada.anulado = True

        with pytest.raises(ValueError, match='anulada'):
            EntradaService._validar_no_anulado(mock_entrada)

    def test_validar_no_anulado_valido(self):
        """No lanza error si entrada no esta anulada."""
        mock_entrada = MagicMock()
        mock_entrada.anulado = False

        EntradaService._validar_no_anulado(mock_entrada)  # No debe lanzar error
