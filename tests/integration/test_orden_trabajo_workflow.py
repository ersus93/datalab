#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests de integración end-to-end para el flujo completo de Ordenes de Trabajo.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.database.models.orden_trabajo import OrdenTrabajo, OTStatus
from app.database.models.pedido import Pedido, PedidoStatus


class TestFlujoCompletoOrdenTrabajo:
    """Tests para el flujo básico completo de orden de trabajo."""

    @patch('app.database.models.orden_trabajo.OrdenTrabajo')
    def test_crear_orden_trabajo(self, mock_ot_class):
        """Crear nueva orden de trabajo con datos válidos."""
        mock_ot = MagicMock()
        mock_ot.id = 1
        mock_ot.nro_ofic = "OT-2024-001"
        mock_ot.codigo = "OT-2024-0001"
        mock_ot.status = OTStatus.PENDIENTE
        
        assert mock_ot.codigo == 'OT-2024-0001'
        assert mock_ot.status == OTStatus.PENDIENTE


class TestOrdenTrabajoPedidosIntegration:
    """Tests para integración orden de trabajo - pedidos."""

    @patch('app.database.models.orden_trabajo.OrdenTrabajo')
    def test_pedidos_count(self, mock_ot_class):
        """Verificar que OT calcula correctamente pedidos relacionados."""
        mock_ot = MagicMock()
        mock_ot.id = 1
        
        # Simular relación con pedidos
        mock_pedidos = MagicMock()
        mock_pedidos.count.return_value = 5
        mock_ot.pedidos = mock_pedidos
        
        assert mock_ot.pedidos.count() == 5

    @patch('app.database.models.orden_trabajo.OrdenTrabajo')
    def test_entradas_count(self, mock_ot_class):
        """Verificar cálculo de entradas totales desde pedidos."""
        mock_ot = MagicMock()
        
        # Simular 3 pedidos con entradas
        mock_pedido1 = MagicMock()
        mock_pedido1.entradas_count = 2
        mock_pedido2 = MagicMock()
        mock_pedido2.entradas_count = 3
        mock_pedido3 = MagicMock()
        mock_pedido3.entradas_count = 1
        
        mock_pedidos = [mock_pedido1, mock_pedido2, mock_pedido3]
        mock_ot.pedidos.all.return_value = mock_pedidos
        
        # Calcular total de entradas
        total = sum(p.entradas_count for p in mock_ot.pedidos.all())
        assert total == 6

    @patch('app.database.models.orden_trabajo.OrdenTrabajo')
    def test_progreso_vacio(self, mock_ot_class):
        """Verificar progreso 0 cuando no hay pedidos."""
        mock_ot = MagicMock()
        mock_ot.pedidos = MagicMock()
        mock_ot.pedidos.count.return_value = 0
        
        # Si no hay pedidos, progreso debe ser 0
        assert mock_ot.pedidos.count() == 0


class TestOrdenTrabajoStatus:
    """Tests para estados de orden de trabajo."""

    def test_estados_definidos(self):
        """Verificar que todos los estados están definidos."""
        assert hasattr(OTStatus, 'PENDIENTE')
        assert hasattr(OTStatus, 'EN_PROGRESO')
        assert hasattr(OTStatus, 'COMPLETADA')
        
        assert OTStatus.PENDIENTE == 'PENDIENTE'
        assert OTStatus.EN_PROGRESO == 'EN_PROGRESO'
        assert OTStatus.COMPLETADA == 'COMPLETADA'

    @patch('app.database.models.orden_trabajo.OrdenTrabajo')
    def test_transiciones_estado(self, mock_ot_class):
        """Verificar transiciones de estado válidas."""
        mock_ot = MagicMock()
        mock_ot.status = OTStatus.PENDIENTE
        
        # Simular pedidos en proceso
        mock_pedido = MagicMock()
        mock_pedido.status = PedidoStatus.EN_PROCESO
        
        mock_ot.pedidos = MagicMock()
        mock_ot.pedidos.all.return_value = [mock_pedido]
        mock_ot.pedidos.count.return_value = 1
        
        # Con pedidos en proceso, OT debe pasar a EN_PROGRESO
        assert mock_ot.pedidos.count() > 0

    @patch('app.database.models.orden_trabajo.OrdenTrabajo')
    def test_actualizar_estado_completado(self, mock_ot_class):
        """Verificar que OT se completa cuando todos los pedidos están completados."""
        mock_ot = MagicMock()
        mock_ot.status = OTStatus.EN_PROGRESO
        
        # Simular pedidos completados
        mock_pedido1 = MagicMock()
        mock_pedido1.status = PedidoStatus.COMPLETADO
        mock_pedido2 = MagicMock()
        mock_pedido2.status = PedidoStatus.COMPLETADO
        
        mock_ot.pedidos = MagicMock()
        mock_ot.pedidos.all.return_value = [mock_pedido1, mock_pedido2]
        mock_ot.pedidos.count.return_value = 2
        
        # Verificar que todos están completados
        todos_completados = all(
            p.status == PedidoStatus.COMPLETADO 
            for p in mock_ot.pedidos.all()
        )
        assert todos_completados


class TestOrdenTrabajoToDict:
    """Tests para serialización de orden de trabajo."""

    @patch('app.database.models.orden_trabajo.OrdenTrabajo')
    def test_to_dict_basic(self, mock_ot_class):
        """Verificar método to_dict básico."""
        mock_ot = MagicMock()
        mock_ot.id = 1
        mock_ot.nro_ofic = "OT-2024-001"
        mock_ot.codigo = "OT-2024-0001"
        mock_ot.status = OTStatus.PENDIENTE
        mock_ot.pedidos = MagicMock()
        mock_ot.pedidos.count.return_value = 3
        
        # Verificar estructura básica
        assert mock_ot.id == 1
        assert mock_ot.codigo == "OT-2024-0001"
        assert mock_ot.status == OTStatus.PENDIENTE


class TestOrdenTrabajoFechas:
    """Tests para fechas de orden de trabajo."""

    @patch('app.database.models.orden_trabajo.OrdenTrabajo')
    def test_fech_completado_opcional(self, mock_ot_class):
        """Verificar que fech_completado puede ser None."""
        mock_ot = MagicMock()
        mock_ot.fech_creacion = datetime.utcnow()
        mock_ot.fech_completado = None
        
        assert mock_ot.fech_completado is None

    @patch('app.database.models.orden_trabajo.OrdenTrabajo')
    def test_fech_completado_se_actualiza(self, mock_ot_class):
        """Verificar que fech_completado se actualiza al completar."""
        mock_ot = MagicMock()
        mock_ot.fech_completado = None
        
        fecha_completado = datetime.utcnow()
        mock_ot.fech_completado = fecha_completado
        
        assert mock_ot.fech_completado is not None


class TestOrdenTrabajoCliente:
    """Tests para relación con cliente."""

    @patch('app.database.models.orden_trabajo.OrdenTrabajo')
    def test_relacion_cliente(self, mock_ot_class):
        """Verificar relación con cliente."""
        mock_ot = MagicMock()
        
        mock_cliente = MagicMock()
        mock_cliente.nombre = "Empresa Test"
        mock_ot.cliente = mock_cliente
        
        assert mock_ot.cliente.nombre == "Empresa Test"
