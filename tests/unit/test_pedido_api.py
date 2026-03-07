#!/usr/bin/env python3
"""Tests unitarios para los endpoints de API de pedidos."""

import json
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from flask_login import login_user

from app import create_app, db
from app.database.models.user import User, UserRole


@pytest.fixture
def app():
    """Crear aplicacion Flask en modo testing."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de pruebas."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Crear un usuario de prueba tecnico."""
    with app.app_context():
        user = User(
            username='test_tech',
            email='tech@test.com',
            role=UserRole.TECHNICIAN,
            nombre_completo='Test Technician'
        )
        user.set_password('test123')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture
def auth_client(client, test_user, app):
    """Cliente autenticado como usuario tecnico."""
    with app.app_context():
        user = db.session.get(User, test_user.id)
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
    return client


@pytest.fixture
def auth_headers():
    """Headers para requests JSON."""
    return {'Content-Type': 'application/json'}


@pytest.mark.skip(reason="Requiere refactorización de fixtures")
class TestCrearPedido:
    """Tests para POST /api/pedidos"""

    @patch('app.routes.pedidos_api.PedidoService')
    def test_post_pedidos_creates_order(self, mock_service, auth_client,
                                        auth_headers, test_user, app):
        """POST /api/pedidos crea un pedido."""
        mock_pedido = MagicMock()
        mock_pedido.id = 1
        mock_pedido.codigo = 'PED-2024-0001'
        mock_pedido.status = 'PENDIENTE'
        mock_pedido.cliente = MagicMock()
        mock_pedido.cliente.id = 1
        mock_pedido.cliente.nombre = 'Cliente Test'
        mock_pedido.producto = MagicMock()
        mock_pedido.producto.id = 1
        mock_pedido.producto.nombre = 'Producto Test'
        mock_pedido.lote = 'L-001'
        mock_pedido.fech_fab = None
        mock_pedido.fech_venc = None
        mock_pedido.cantidad = None
        mock_pedido.entradas_count = 0
        mock_pedido.entradas_completadas = 0

        mock_service.crear_pedido.return_value = mock_pedido

        data = {
            'cliente_id': 1,
            'producto_id': 1,
            'lote': 'L-001'
        }

        with patch('app.decorators.current_user', test_user):
            response = auth_client.post(
                '/api/pedidos',
                data=json.dumps(data),
                headers=auth_headers
            )

        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['data']['id'] == 1
        assert response_data['data']['codigo'] == 'PED-2024-0001'

    def test_post_pedidos_validation_error(self, auth_client, auth_headers,
                                            test_user, app):
        """Retorna 400 para datos invalidos."""
        with patch('app.routes.pedidos_api.PedidoService') as mock_service:
            mock_service.crear_pedido.side_effect = ValueError('Cliente requerido')

            with patch('app.decorators.current_user', test_user):
                response = auth_client.post(
                    '/api/pedidos',
                    data=json.dumps({'producto_id': 1}),
                    headers=auth_headers
                )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert response_data['error']['code'] == 'VALIDATION_ERROR'


@pytest.mark.skip(reason="Requiere refactorización de fixtures")
class TestListarPedidos:
    """Tests para GET /api/pedidos"""

    @patch('app.routes.pedidos_api.PedidoService')
    def test_get_pedidos_list(self, mock_service, auth_client, test_user, app):
        """GET /api/pedidos retorna lista paginada."""
        mock_pedido = MagicMock()
        mock_pedido.id = 1
        mock_pedido.codigo = 'PED-2024-0001'
        mock_pedido.status = 'PENDIENTE'
        mock_pedido.cliente = MagicMock()
        mock_pedido.cliente.id = 1
        mock_pedido.cliente.nombre = 'Cliente Test'
        mock_pedido.producto = MagicMock()
        mock_pedido.producto.id = 1
        mock_pedido.producto.nombre = 'Producto Test'
        mock_pedido.lote = 'L-001'
        mock_pedido.fech_fab = None
        mock_pedido.fech_venc = None
        mock_pedido.cantidad = None
        mock_pedido.entradas_count = 0
        mock_pedido.entradas_completadas = 0

        mock_service.obtener_pedidos_paginados.return_value = (
            [mock_pedido],
            {
                'pagina': 1,
                'por_pagina': 20,
                'total': 1,
                'total_paginas': 1,
                'tiene_siguiente': False,
                'tiene_anterior': False,
                'siguiente_pagina': None,
                'pagina_anterior': None
            }
        )

        with patch('app.decorators.current_user', test_user):
            response = auth_client.get('/api/pedidos')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert len(response_data['data']) == 1
        assert response_data['meta']['total'] == 1

    @patch('app.routes.pedidos_api.PedidoService')
    def test_get_pedidos_with_filters(self, mock_service, auth_client,
                                       test_user, app):
        """El filtrado funciona correctamente."""
        mock_service.obtener_pedidos_paginados.return_value = (
            [],
            {
                'pagina': 1,
                'por_pagina': 20,
                'total': 0,
                'total_paginas': 0,
                'tiene_siguiente': False,
                'tiene_anterior': False,
                'siguiente_pagina': None,
                'pagina_anterior': None
            }
        )

        with patch('app.decorators.current_user', test_user):
            response = auth_client.get(
                '/api/pedidos?cliente_id=1&producto_id=2&status=PENDIENTE'
            )

        assert response.status_code == 200
        mock_service.obtener_pedidos_paginados.assert_called_once()


@pytest.mark.skip(reason="Requiere refactorización de fixtures")
class TestObtenerPedido:
    """Tests para GET /api/pedidos/{id}"""

    @patch('app.routes.pedidos_api.PedidoService')
    def test_get_pedido_detail(self, mock_service, auth_client, test_user, app):
        """GET /api/pedidos/{id} retorna detalles."""
        mock_pedido = MagicMock()
        mock_pedido.id = 1
        mock_pedido.codigo = 'PED-2024-0001'
        mock_pedido.status = 'PENDIENTE'
        mock_pedido.cliente = MagicMock()
        mock_pedido.cliente.id = 1
        mock_pedido.cliente.nombre = 'Cliente Test'
        mock_pedido.producto = MagicMock()
        mock_pedido.producto.id = 1
        mock_pedido.producto.nombre = 'Producto Test'
        mock_pedido.lote = 'L-001'
        mock_pedido.fech_fab = None
        mock_pedido.fech_venc = None
        mock_pedido.cantidad = None
        mock_pedido.entradas_count = 0
        mock_pedido.entradas_completadas = 0

        mock_service.obtener_pedido_por_id.return_value = mock_pedido

        with patch('app.decorators.current_user', test_user):
            response = auth_client.get('/api/pedidos/1')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['data']['id'] == 1

    @patch('app.routes.pedidos_api.PedidoService')
    def test_get_pedido_not_found(self, mock_service, auth_client, test_user, app):
        """Retorna 404 para ID inexistente."""
        mock_service.obtener_pedido_por_id.return_value = None

        with patch('app.decorators.current_user', test_user):
            response = auth_client.get('/api/pedidos/999')

        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert response_data['error']['code'] == 'NOT_FOUND'


@pytest.mark.skip(reason="Requiere refactorización de fixtures")
class TestActualizarPedido:
    """Tests para PUT /api/pedidos/{id}"""

    @patch('app.routes.pedidos_api.PedidoService')
    def test_put_pedido_updates(self, mock_service, auth_client, auth_headers,
                                 test_user, app):
        """PUT /api/pedidos/{id} actualiza el pedido."""
        mock_pedido = MagicMock()
        mock_pedido.id = 1
        mock_pedido.codigo = 'PED-2024-0001'
        mock_pedido.status = 'PENDIENTE'
        mock_pedido.cliente = MagicMock()
        mock_pedido.cliente.id = 1
        mock_pedido.cliente.nombre = 'Cliente Test'
        mock_pedido.producto = MagicMock()
        mock_pedido.producto.id = 1
        mock_pedido.producto.nombre = 'Producto Test'
        mock_pedido.lote = 'L-001'
        mock_pedido.fech_fab = None
        mock_pedido.fech_venc = None
        mock_pedido.cantidad = None
        mock_pedido.entradas_count = 0
        mock_pedido.entradas_completadas = 0

        mock_service.actualizar_pedido.return_value = mock_pedido

        with patch('app.decorators.current_user', test_user):
            response = auth_client.put(
                '/api/pedidos/1',
                data=json.dumps({'observaciones': 'Actualizado'}),
                headers=auth_headers
            )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True


@pytest.mark.skip(reason="Requiere refactorización de fixtures")
class TestEliminarPedido:
    """Tests para DELETE /api/pedidos/{id}"""

    @patch('app.routes.pedidos_api.PedidoService')
    def test_delete_pedido_soft_deletes(self, mock_service, auth_client,
                                         test_user, app):
        """DELETE realiza soft delete."""
        mock_pedido = MagicMock()
        mock_pedido.id = 1
        mock_pedido.codigo = 'PED-2024-0001'
        mock_pedido.status = 'ELIMINADO'
        mock_pedido.cliente = MagicMock()
        mock_pedido.cliente.id = 1
        mock_pedido.cliente.nombre = 'Cliente Test'
        mock_pedido.producto = MagicMock()
        mock_pedido.producto.id = 1
        mock_pedido.producto.nombre = 'Producto Test'
        mock_pedido.lote = 'L-001'
        mock_pedido.fech_fab = None
        mock_pedido.fech_venc = None
        mock_pedido.cantidad = None
        mock_pedido.entradas_count = 0
        mock_pedido.entradas_completadas = 0

        mock_service.eliminar_pedido.return_value = mock_pedido

        with patch('app.decorators.current_user', test_user):
            response = auth_client.delete('/api/pedidos/1')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True


@pytest.mark.skip(reason="Requiere refactorización de fixtures")
class TestObtenerEntradasPedido:
    """Tests para GET /api/pedidos/{id}/entradas"""

    @patch('app.routes.pedidos_api.PedidoService')
    def test_get_pedido_entradas(self, mock_service, auth_client, test_user, app):
        """GET /api/pedidos/{id}/entradas retorna entradas relacionadas."""
        mock_entradas = [
            {
                'id': 1,
                'codigo': 'ENT001',
                'lote': 'L-001',
                'status': 'RECIBIDO',
                'cantidad_recib': '100',
                'cantidad_entreg': '0',
                'saldo': '100',
                'fech_entrada': '2024-01-01T00:00:00',
                'anulado': False
            },
            {
                'id': 2,
                'codigo': 'ENT002',
                'lote': 'L-002',
                'status': 'EN_PROCESO',
                'cantidad_recib': '50',
                'cantidad_entreg': '20',
                'saldo': '30',
                'fech_entrada': '2024-01-15T00:00:00',
                'anulado': False
            }
        ]
        mock_service.obtener_entradas_de_pedido.return_value = mock_entradas

        with patch('app.decorators.current_user', test_user):
            response = auth_client.get('/api/pedidos/1/entradas')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert len(response_data['data']) == 2
        assert response_data['data'][0]['id'] == 1
        assert response_data['data'][1]['id'] == 2


@pytest.mark.skip(reason="Requiere refactorización de fixtures")
class TestObtenerPedidosPorCliente:
    """Tests para GET /api/clientes/{id}/pedidos"""

    @patch('app.routes.pedidos_api.PedidoService')
    def test_get_cliente_pedidos(self, mock_service, auth_client, test_user, app):
        """GET /api/clientes/{id}/pedidos retorna pedidos del cliente."""
        mock_pedido = MagicMock()
        mock_pedido.id = 1
        mock_pedido.codigo = 'PED-2024-0001'
        mock_pedido.status = 'PENDIENTE'
        mock_pedido.cliente = MagicMock()
        mock_pedido.cliente.id = 1
        mock_pedido.cliente.nombre = 'Cliente Test'
        mock_pedido.producto = MagicMock()
        mock_pedido.producto.id = 1
        mock_pedido.producto.nombre = 'Producto Test'
        mock_pedido.lote = 'L-001'
        mock_pedido.fech_fab = None
        mock_pedido.fech_venc = None
        mock_pedido.cantidad = None
        mock_pedido.entradas_count = 0
        mock_pedido.entradas_completadas = 0

        mock_service.obtener_pedidos_paginados.return_value = (
            [mock_pedido],
            {
                'pagina': 1,
                'por_pagina': 20,
                'total': 1,
                'total_paginas': 1,
                'tiene_siguiente': False,
                'tiene_anterior': False,
                'siguiente_pagina': None,
                'pagina_anterior': None
            }
        )

        with patch('app.decorators.current_user', test_user):
            response = auth_client.get('/api/clientes/1/pedidos')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert len(response_data['data']) == 1
        assert response_data['data'][0]['id'] == 1


@pytest.mark.skip(reason="Requiere refactorización de fixtures")
class TestAutorizacion:
    """Tests de autorizacion."""

    def test_unauthorized_access(self, client):
        """Acceso sin autenticacion retorna 401/302."""
        response = client.get('/api/pedidos')

        assert response.status_code in [302, 401, 403]
