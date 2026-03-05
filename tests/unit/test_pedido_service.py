#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests unitarios para el servicio PedidoService."""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.services.pedido_service import PedidoService


class TestCrearPedido:
    """Tests para la creacion de pedidos."""

    @patch('app.services.pedido_service.db')
    @patch('app.database.models.pedido.Pedido')
    @patch('app.database.models.pedido.PedidoStatus')
    def test_crear_pedido_success(self, mock_status_class, mock_pedido_class,
                                   mock_db):
        """Crear pedido con datos validos."""
        # Setup mocks
        mock_pedido_instance = MagicMock()
        mock_pedido_instance.id = 1
        mock_pedido_instance.codigo = 'PED-2024-0001'
        mock_pedido_instance.status = 'PENDIENTE'
        mock_pedido_class.return_value = mock_pedido_instance

        mock_pedido_status = MagicMock()
        mock_pedido_status.PENDIENTE = 'PENDIENTE'
        mock_status_class.PENDIENTE = 'PENDIENTE'

        mock_db.session.add = MagicMock()
        mock_db.session.commit = MagicMock()

        data = {
            'codigo': 'PED-2024-0001',
            'cliente_id': 1,
            'producto_id': 1,
            'lote': 'L-1234',
            'fech_fab': date(2024, 1, 1),
            'fech_venc': date(2025, 1, 1),
            'cantidad': 100.0
        }

        result = PedidoService.crear_pedido(data, usuario_id=1)

        assert result is not None
        mock_db.session.add.assert_called()
        mock_db.session.commit.assert_called()

    def test_crear_pedido_invalid_dates(self):
        """Rechaza cuando FechVenc <= FechFab."""
        data = {
            'cliente_id': 1,
            'producto_id': 1,
            'fech_fab': date(2025, 1, 1),
            'fech_venc': date(2024, 1, 1)  # Anterior a fabricacion
        }

        with pytest.raises(ValueError, match='vencimiento'):
            PedidoService.crear_pedido(data, usuario_id=1)

    def test_crear_pedido_missing_required_fields(self):
        """Rechaza campos obligatorios faltantes (cliente_id o producto_id)."""
        # Sin cliente_id
        data_sin_cliente = {
            'producto_id': 1,
            'fech_fab': date(2024, 1, 1),
            'fech_venc': date(2025, 1, 1)
        }

        with pytest.raises(ValueError, match='cliente'):
            PedidoService.crear_pedido(data_sin_cliente, usuario_id=1)

        # Sin producto_id
        data_sin_producto = {
            'cliente_id': 1,
            'fech_fab': date(2024, 1, 1),
            'fech_venc': date(2025, 1, 1)
        }

        with pytest.raises(ValueError, match='producto'):
            PedidoService.crear_pedido(data_sin_producto, usuario_id=1)

    @patch('app.services.pedido_service.PedidoService._generar_codigo')
    @patch('app.services.pedido_service.db')
    @patch('app.database.models.pedido.Pedido')
    @patch('app.database.models.pedido.PedidoStatus')
    def test_crear_pedido_auto_generates_codigo(self, mock_status_class,
                                                 mock_pedido_class, mock_db,
                                                 mock_generar_codigo):
        """Verifica formato del codigo auto-generado."""
        # Setup mocks
        mock_pedido_instance = MagicMock()
        mock_pedido_instance.id = 1
        mock_pedido_instance.codigo = 'PED-2024-0001'
        mock_pedido_class.return_value = mock_pedido_instance

        mock_generar_codigo.return_value = 'PED-2024-0001'

        mock_pedido_status = MagicMock()
        mock_pedido_status.PENDIENTE = 'PENDIENTE'
        mock_status_class.PENDIENTE = 'PENDIENTE'

        mock_db.session.add = MagicMock()
        mock_db.session.commit = MagicMock()

        data = {
            'cliente_id': 1,
            'producto_id': 1
        }

        result = PedidoService.crear_pedido(data, usuario_id=1)

        # Verificar que se genero el codigo y sigue el formato
        assert result.codigo == 'PED-2024-0001'
        mock_generar_codigo.assert_called_once()


class TestActualizarPedido:
    """Tests para actualizacion de pedidos."""

    @patch('app.services.pedido_service.db')
    @patch('app.database.models.pedido.Pedido')
    def test_actualizar_pedido_success(self, mock_pedido_class, mock_db):
        """Actualiza pedido correctamente."""
        mock_pedido = MagicMock()
        mock_pedido.id = 1
        mock_pedido.fech_fab = date(2024, 1, 1)
        mock_pedido.fech_venc = date(2025, 1, 1)
        mock_pedido.cantidad = Decimal('100')
        mock_pedido.entradas_count = 0

        mock_query = MagicMock()
        mock_query.get.return_value = mock_pedido
        mock_pedido_class.query = mock_query

        mock_db.session.commit = MagicMock()

        result = PedidoService.actualizar_pedido(
            1,
            {'observaciones': 'Nueva observacion'},
            usuario_id=1
        )

        assert result is not None
        mock_db.session.commit.assert_called()

    @patch('app.database.models.pedido.Pedido')
    def test_actualizar_pedido_revalidates_dates(self, mock_pedido_class):
        """Re-valida fechas al actualizar."""
        mock_pedido = MagicMock()
        mock_pedido.id = 1
        mock_pedido.fech_fab = date(2024, 1, 1)
        mock_pedido.fech_venc = date(2025, 1, 1)

        mock_query = MagicMock()
        mock_query.get.return_value = mock_pedido
        mock_pedido_class.query = mock_query

        # Intentar actualizar con fechas invalidas
        with pytest.raises(ValueError, match='vencimiento'):
            PedidoService.actualizar_pedido(
                1,
                {
                    'fech_fab': date(2025, 1, 1),
                    'fech_venc': date(2024, 1, 1)
                },
                usuario_id=1
            )


class TestEliminarPedido:
    """Tests para eliminacion (soft delete) de pedidos."""

    @patch('app.services.pedido_service.db')
    @patch('app.database.models.pedido.Pedido')
    def test_eliminar_pedido_soft_delete(self, mock_pedido_class, mock_db):
        """Realiza soft delete verificando que no tenga entradas."""
        mock_pedido = MagicMock()
        mock_pedido.id = 1
        mock_pedido.status = 'PENDIENTE'
        mock_pedido.entradas_count = 0

        mock_query = MagicMock()
        mock_query.get.return_value = mock_pedido
        mock_pedido_class.query = mock_query

        mock_db.session.commit = MagicMock()

        result = PedidoService.eliminar_pedido(1, usuario_id=1)

        assert result.status == 'ELIMINADO'
        mock_db.session.commit.assert_called()

    @patch('app.database.models.pedido.Pedido')
    def test_eliminar_pedido_with_entradas_fails(self, mock_pedido_class):
        """No permite eliminar si tiene entradas relacionadas."""
        mock_pedido = MagicMock()
        mock_pedido.id = 1
        mock_pedido.entradas_count = 3  # Tiene 3 entradas

        mock_query = MagicMock()
        mock_query.get.return_value = mock_pedido
        mock_pedido_class.query = mock_query

        with pytest.raises(ValueError, match='entrada'):
            PedidoService.eliminar_pedido(1, usuario_id=1)


class TestCambiarEstado:
    """Tests para cambio de estado de pedidos."""

    @patch('app.services.pedido_service.db')
    @patch('app.database.models.pedido.Pedido')
    @patch('app.database.models.pedido.PedidoStatus')
    def test_cambiar_estado_valid_transition(self, mock_status_class,
                                              mock_pedido_class, mock_db):
        """Transicion de estado valida ejecuta sin error."""
        mock_pedido = MagicMock()
        mock_pedido.id = 1
        mock_pedido.status = 'PENDIENTE'

        mock_query = MagicMock()
        mock_query.get.return_value = mock_pedido
        mock_pedido_class.query = mock_query

        mock_pedido_status = MagicMock()
        mock_pedido_status.PENDIENTE = 'PENDIENTE'
        mock_pedido_status.EN_PROCESO = 'EN_PROCESO'
        mock_pedido_status.COMPLETADO = 'COMPLETADO'
        mock_status_class.PENDIENTE = 'PENDIENTE'
        mock_status_class.EN_PROCESO = 'EN_PROCESO'
        mock_status_class.COMPLETADO = 'COMPLETADO'

        mock_db.session.commit = MagicMock()

        # PENDIENTE -> EN_PROCESO es valido
        result = PedidoService.cambiar_estado(1, 'EN_PROCESO', usuario_id=1)

        assert result is not None
        assert result == mock_pedido

    @patch('app.database.models.pedido.Pedido')
    @patch('app.database.models.pedido.PedidoStatus')
    def test_cambiar_estado_invalid_transition(self, mock_status_class,
                                                mock_pedido_class):
        """Transicion invalida lanza error."""
        mock_pedido = MagicMock()
        mock_pedido.id = 1
        mock_pedido.status = 'PENDIENTE'

        mock_query = MagicMock()
        mock_query.get.return_value = mock_pedido
        mock_pedido_class.query = mock_query

        mock_pedido_status = MagicMock()
        mock_pedido_status.PENDIENTE = 'PENDIENTE'
        mock_pedido_status.EN_PROCESO = 'EN_PROCESO'
        mock_pedido_status.COMPLETADO = 'COMPLETADO'
        mock_pedido_status.ELIMINADO = 'ELIMINADO'
        mock_status_class.PENDIENTE = 'PENDIENTE'
        mock_status_class.EN_PROCESO = 'EN_PROCESO'
        mock_status_class.COMPLETADO = 'COMPLETADO'

        # PENDIENTE -> INVALID_STATUS no es una transicion valida
        with pytest.raises(ValueError):
            PedidoService.cambiar_estado(1, 'INVALIDO', usuario_id=1)


class TestObtenerPedidos:
    """Tests para consulta de pedidos."""

    @patch('app.services.pedido_service.desc')
    @patch('app.services.pedido_service.asc')
    @patch('app.database.models.pedido.Pedido')
    def test_obtener_pedidos_paginados(self, mock_pedido_class, mock_asc,
                                        mock_desc):
        """Paginacion funciona correctamente."""
        mock_pedido1 = MagicMock()
        mock_pedido2 = MagicMock()

        mock_pagination = MagicMock()
        mock_pagination.items = [mock_pedido1, mock_pedido2]
        mock_pagination.total = 2
        mock_pagination.pages = 1
        mock_pagination.has_next = False
        mock_pagination.has_prev = False
        mock_pagination.next_num = None
        mock_pagination.prev_num = None

        mock_query = MagicMock()
        mock_query.order_by.return_value = mock_query
        mock_query.paginate.return_value = mock_pagination
        mock_pedido_class.query = mock_query
        mock_pedido_class.fech_pedido = MagicMock()

        pedidos, meta = PedidoService.obtener_pedidos_paginados(
            pagina=1,
            por_pagina=20
        )

        assert len(pedidos) == 2
        assert meta['total'] == 2
        assert meta['pagina'] == 1

    @patch('app.services.pedido_service.desc')
    @patch('app.services.pedido_service.asc')
    @patch('app.database.models.pedido.Pedido')
    def test_obtener_pedidos_paginados_with_filters(self, mock_pedido_class,
                                                     mock_asc, mock_desc):
        """Filtros por cliente, producto y estado funcionan."""
        mock_pedido = MagicMock()

        mock_pagination = MagicMock()
        mock_pagination.items = [mock_pedido]
        mock_pagination.total = 1
        mock_pagination.pages = 1
        mock_pagination.has_next = False
        mock_pagination.has_prev = False

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.paginate.return_value = mock_pagination
        mock_pedido_class.query = mock_query
        mock_pedido_class.fech_pedido = MagicMock()
        mock_pedido_class.cliente_id = MagicMock()
        mock_pedido_class.producto_id = MagicMock()
        mock_pedido_class.status = MagicMock()

        filtros = {
            'cliente_id': 1,
            'producto_id': 2,
            'status': 'PENDIENTE'
        }

        pedidos, meta = PedidoService.obtener_pedidos_paginados(
            filtros=filtros,
            pagina=1,
            por_pagina=20
        )

        assert len(pedidos) == 1
        assert meta['total'] == 1
        mock_query.filter.assert_called()

    @patch('app.database.models.pedido.Pedido')
    def test_obtener_pedido_por_id_found(self, mock_pedido_class):
        """Retorna pedido existente."""
        mock_pedido = MagicMock()
        mock_pedido.id = 1
        mock_pedido.codigo = 'PED-2024-0001'

        mock_query = MagicMock()
        mock_query.get.return_value = mock_pedido
        mock_pedido_class.query = mock_query

        result = PedidoService.obtener_pedido_por_id(1)

        assert result is not None
        assert result.id == 1

    @patch('app.database.models.pedido.Pedido')
    def test_obtener_pedido_por_id_not_found(self, mock_pedido_class):
        """Retorna None para ID inexistente."""
        mock_query = MagicMock()
        mock_query.get.return_value = None
        mock_pedido_class.query = mock_query

        result = PedidoService.obtener_pedido_por_id(999)

        assert result is None


class TestObtenerEntradasDePedido:
    """Tests para obtener entradas relacionadas a un pedido."""

    @patch('app.database.models.pedido.Pedido')
    def test_obtener_entradas_de_pedido(self, mock_pedido_class):
        """Retorna entradas relacionadas al pedido."""
        mock_entrada1 = MagicMock()
        mock_entrada1.id = 1
        mock_entrada1.codigo = 'ENT001'
        mock_entrada1.lote = 'L-001'
        mock_entrada1.status = 'RECIBIDO'
        mock_entrada1.cantidad_recib = Decimal('100')
        mock_entrada1.cantidad_entreg = Decimal('0')
        mock_entrada1.saldo = Decimal('100')
        mock_entrada1.fech_entrada = datetime(2024, 1, 1)
        mock_entrada1.anulado = False

        mock_entrada2 = MagicMock()
        mock_entrada2.id = 2
        mock_entrada2.codigo = 'ENT002'
        mock_entrada2.lote = 'L-002'
        mock_entrada2.status = 'EN_PROCESO'
        mock_entrada2.cantidad_recib = Decimal('50')
        mock_entrada2.cantidad_entreg = Decimal('20')
        mock_entrada2.saldo = Decimal('30')
        mock_entrada2.fech_entrada = datetime(2024, 1, 15)
        mock_entrada2.anulado = False

        mock_pedido = MagicMock()
        mock_pedido.id = 1
        mock_pedido.entradas.all.return_value = [mock_entrada1, mock_entrada2]

        mock_query = MagicMock()
        mock_query.get.return_value = mock_pedido
        mock_pedido_class.query = mock_query

        result = PedidoService.obtener_entradas_de_pedido(1)

        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[0]['codigo'] == 'ENT001'
        assert result[1]['id'] == 2
        assert result[1]['codigo'] == 'ENT002'

    @patch('app.database.models.pedido.Pedido')
    def test_obtener_entradas_pedido_not_found(self, mock_pedido_class):
        """Lanza error si el pedido no existe."""
        mock_query = MagicMock()
        mock_query.get.return_value = None
        mock_pedido_class.query = mock_query

        with pytest.raises(ValueError, match='Pedido no encontrado'):
            PedidoService.obtener_entradas_de_pedido(999)
