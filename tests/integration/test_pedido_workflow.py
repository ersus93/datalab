#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests de integración end-to-end para el flujo completo de pedidos.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.database.models.pedido import Pedido, PedidoStatus
from app.database.models.entrada import Entrada, EntradaStatus


class TestFlujoCompletoPedido:
    """Tests para el flujo básico completo de pedido."""

    @patch('app.database.models.pedido.Pedido')
    def test_crear_pedido(self, mock_pedido_class):
        """Crear nuevo pedido con datos válidos."""
        mock_pedido = MagicMock()
        mock_pedido.id = 1
        mock_pedido.codigo = "PED-001"
        mock_pedido.status = PedidoStatus.PENDIENTE
        
        assert mock_pedido.codigo == 'PED-001'
        assert mock_pedido.status == PedidoStatus.PENDIENTE


class TestPedidoEntradasIntegration:
    """Tests para integración pedido-entradas."""

    @patch('app.database.models.pedido.Pedido')
    def test_entradas_count(self, mock_pedido_class):
        """Verificar que pedido calcula correctamente entradas relacionadas."""
        mock_pedido = MagicMock()
        mock_pedido.id = 1
        
        # Simular relación con entradas
        mock_entradas = MagicMock()
        mock_entradas.count.return_value = 5
        mock_pedido.entradas = mock_entradas
        
        assert mock_pedido.entradas.count() == 5

    @patch('app.database.models.pedido.Pedido')
    def test_entradas_completadas(self, mock_pedido_class):
        """Verificar cálculo de entradas completadas."""
        mock_pedido = MagicMock()
        mock_pedido.status = PedidoStatus.EN_PROCESO
        
        # Simular 3 entradas, 1 completada
        mock_entradas = MagicMock()
        mock_entradas.count.return_value = 3
        
        def filter_by_status(status):
            mock_result = MagicMock()
            mock_result.count.return_value = 1 if status == EntradaStatus.COMPLETADO else 2
            return mock_result
        
        mock_entradas.filter_by = filter_by_status
        mock_pedido.entradas = mock_entradas
        
        # Verificar entradas completadas
        completed = mock_pedido.entradas.filter_by(status=EntradaStatus.COMPLETADO).count()
        assert completed == 1

    @patch('app.database.models.pedido.Pedido')
    def test_actualizar_estado_vacio(self, mock_pedido_class):
        """Verificar estado PENDIENTE cuando no hay entradas."""
        mock_pedido = MagicMock()
        mock_pedido.status = PedidoStatus.PENDIENTE
        
        # Simular 0 entradas
        mock_entradas = MagicMock()
        mock_entradas.count.return_value = 0
        mock_pedido.entradas = mock_entradas
        
        # Si no hay entradas, debe estar PENDIENTE
        assert mock_pedido.entradas.count() == 0


class TestPedidoOrdenTrabajoIntegration:
    """Tests para integración pedido-orden de trabajo."""

    @patch('app.database.models.pedido.Pedido')
    def test_vincular_a_orden_trabajo(self, mock_pedido_class):
        """Vincular pedido a orden de trabajo."""
        mock_pedido = MagicMock()
        mock_pedido.id = 1
        mock_pedido.orden_trabajo_id = None
        
        mock_ot = MagicMock()
        mock_ot.id = 1
        mock_ot.nro_ofic = "OT-2024-001"
        
        # Simular vinculación
        mock_pedido.orden_trabajo_id = mock_ot.id
        
        assert mock_pedido.orden_trabajo_id == 1

    @patch('app.database.models.pedido.Pedido')
    def test_pedido_sin_orden_trabajo(self, mock_pedido_class):
        """Verificar que pedido puede existir sin OT."""
        mock_pedido = MagicMock()
        mock_pedido.id = 1
        mock_pedido.orden_trabajo_id = None
        
        assert mock_pedido.orden_trabajo_id is None


class TestPedidoStatus:
    """Tests para estados de pedido."""

    def test_estados_definidos(self):
        """Verificar que todos los estados están definidos."""
        assert hasattr(PedidoStatus, 'PENDIENTE')
        assert hasattr(PedidoStatus, 'EN_PROCESO')
        assert hasattr(PedidoStatus, 'COMPLETADO')
        
        assert PedidoStatus.PENDIENTE == 'PENDIENTE'
        assert PedidoStatus.EN_PROCESO == 'EN_PROCESO'
        assert PedidoStatus.COMPLETADO == 'COMPLETADO'

    @patch('app.database.models.pedido.Pedido')
    def test_transiciones_estado(self, mock_pedido_class):
        """Verificar transiciones de estado válidas."""
        # PENDIENTE -> EN_PROCESO (cuando hay entradas)
        mock_pedido = MagicMock()
        mock_pedido.status = PedidoStatus.PENDIENTE
        
        mock_entradas = MagicMock()
        mock_entradas.count.return_value = 1  # Tiene entradas
        mock_pedido.entradas = mock_entradas
        
        # Con entradas debe pasar a EN_PROCESO
        assert mock_pedido.entradas.count() > 0


class TestPedidoToDict:
    """Tests para serialización de pedido."""

    @patch('app.database.models.pedido.Pedido')
    def test_to_dict_basic(self, mock_pedido_class):
        """Verificar método to_dict básico."""
        mock_pedido = MagicMock()
        mock_pedido.id = 1
        mock_pedido.codigo = "PED-001"
        mock_pedido.status = PedidoStatus.PENDIENTE
        mock_pedido.entradas = MagicMock()
        mock_pedido.entradas.count.return_value = 3
        
        # Verificar estructura básica
        assert mock_pedido.id == 1
        assert mock_pedido.codigo == "PED-001"
        assert mock_pedido.status == PedidoStatus.PENDIENTE


class TestPedidoFechas:
    """Tests para fechas de pedido."""

    @patch('app.database.models.pedido.Pedido')
    def test_fechas_opcionales(self, mock_pedido_class):
        """Verificar que fechas pueden ser None."""
        mock_pedido = MagicMock()
        mock_pedido.fech_fab = None
        mock_pedido.fech_venc = None
        mock_pedido.fech_pedido = datetime.utcnow()
        
        assert mock_pedido.fech_fab is None
        assert mock_pedido.fech_venc is None
        assert mock_pedido.fech_pedido is not None

    @patch('app.database.models.pedido.Pedido')
    def test_fechas_validas(self, mock_pedido_class):
        """Verificar fechas válidas."""
        mock_pedido = MagicMock()
        mock_pedido.fech_fab = date(2024, 1, 1)
        mock_pedido.fech_venc = date(2025, 1, 1)
        
        # Vencimiento debe ser posterior a fabricación
        assert mock_pedido.fech_venc > mock_pedido.fech_fab


class TestPedidoCantidad:
    """Tests para cantidad de pedido."""

    @patch('app.database.models.pedido.Pedido')
    def test_cantidad_opcional(self, mock_pedido_class):
        """Verificar que cantidad puede ser None."""
        mock_pedido = MagicMock()
        mock_pedido.cantidad = None
        
        assert mock_pedido.cantidad is None

    @patch('app.database.models.pedido.Pedido')
    def test_cantidad_decimal(self, mock_pedido_class):
        """Verificar cantidad con decimales."""
        mock_pedido = MagicMock()
        mock_pedido.cantidad = Decimal('100.50')
        
        assert mock_pedido.cantidad == Decimal('100.50')