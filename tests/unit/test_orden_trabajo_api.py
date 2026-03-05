#!/usr/bin/env python3
"""Tests unitarios para los endpoints de API de ordenes de trabajo."""

import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from flask_login import login_user

from app import create_app, db
from app.database.models.user import User, UserRole
from app.database.models.cliente import Cliente
from app.database.models.producto import Producto
from app.database.models.pedido import Pedido, PedidoStatus
from app.database.models.orden_trabajo import OrdenTrabajo, OTStatus


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
def test_cliente(app):
    """Crear un cliente de prueba."""
    with app.app_context():
        cliente = Cliente(
            codigo='CLI001',
            nombre='Cliente Test',
            email='test@cliente.com',
            activo=True
        )
        db.session.add(cliente)
        db.session.commit()
        db.session.refresh(cliente)
        return cliente


@pytest.fixture
def test_producto(app):
    """Crear un producto de prueba."""
    with app.app_context():
        producto = Producto(
            nombre='Producto Test',
            activo=True
        )
        db.session.add(producto)
        db.session.commit()
        db.session.refresh(producto)
        return producto


@pytest.fixture
def test_pedido(app, test_cliente, test_producto):
    """Crear un pedido de prueba."""
    with app.app_context():
        cliente = db.session.get(Cliente, test_cliente.id)
        producto = db.session.get(Producto, test_producto.id)
        pedido = Pedido(
            codigo='PED-2024-0001',
            cliente_id=cliente.id,
            producto_id=producto.id,
            lote='L-001',
            status=PedidoStatus.PENDIENTE
        )
        db.session.add(pedido)
        db.session.commit()
        db.session.refresh(pedido)
        return pedido


@pytest.fixture
def auth_headers():
    """Headers para requests JSON."""
    return {'Content-Type': 'application/json'}


class TestOrdenesTrabajoAPI:
    """Tests para la API REST de Ordenes de Trabajo."""

    # List Tests
    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_list_ordenes_trabajo_success(self, mock_service, auth_client, test_user, app):
        """GET /api/ordenes-trabajo retorna lista paginada."""
        mock_cliente = MagicMock()
        mock_cliente.id = 1
        mock_cliente.nombre = 'Cliente Test'

        mock_orden = MagicMock()
        mock_orden.id = 1
        mock_orden.nro_ofic = 'OT-001'
        mock_orden.codigo = 'OT-2024-0001'
        mock_orden.cliente = mock_cliente
        mock_orden.descripcion = 'Descripcion test'
        mock_orden.observaciones = None
        mock_orden.status = OTStatus.PENDIENTE
        mock_orden.progreso = 0
        mock_orden.pedidos_count = 0
        mock_orden.entradas_count = 0
        mock_orden.fech_creacion = datetime.utcnow()
        mock_orden.fech_completado = None
        mock_orden.pedidos = MagicMock()
        mock_orden.pedidos.all.return_value = []

        mock_service.obtener_ordenes_paginadas.return_value = (
            [mock_orden],
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
            response = auth_client.get('/api/ordenes-trabajo')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert len(response_data['data']) == 1
        assert response_data['data'][0]['id'] == 1
        assert response_data['meta']['total'] == 1

    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_list_ordenes_trabajo_with_filters(self, mock_service, auth_client, test_user, app):
        """El filtrado funciona correctamente."""
        mock_service.obtener_ordenes_paginadas.return_value = (
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
                '/api/ordenes-trabajo?cliente_id=1&status=PENDIENTE&q=OT-001'
            )

        assert response.status_code == 200
        mock_service.obtener_ordenes_paginadas.assert_called_once()

    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_list_ordenes_trabajo_pagination(self, mock_service, auth_client, test_user, app):
        """La paginacion funciona correctamente."""
        mock_service.obtener_ordenes_paginadas.return_value = (
            [],
            {
                'pagina': 2,
                'por_pagina': 10,
                'total': 25,
                'total_paginas': 3,
                'tiene_siguiente': True,
                'tiene_anterior': True,
                'siguiente_pagina': 3,
                'pagina_anterior': 1
            }
        )

        with patch('app.decorators.current_user', test_user):
            response = auth_client.get('/api/ordenes-trabajo?page=2&per_page=10')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['meta']['page'] == 2
        assert response_data['meta']['per_page'] == 10
        assert response_data['meta']['total'] == 25
        assert response_data['meta']['total_pages'] == 3

    def test_list_ordenes_trabajo_unauthorized(self, client):
        """Acceso sin autenticacion retorna 401/302."""
        response = client.get('/api/ordenes-trabajo')
        assert response.status_code in [302, 401, 403]

    # Create Tests
    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_create_orden_trabajo_success(self, mock_service, auth_client, test_user, app, test_cliente):
        """POST /api/ordenes-trabajo crea una orden de trabajo."""
        mock_cliente = MagicMock()
        mock_cliente.id = test_cliente.id
        mock_cliente.nombre = 'Cliente Test'

        mock_orden = MagicMock()
        mock_orden.id = 1
        mock_orden.nro_ofic = 'OT-001'
        mock_orden.codigo = 'OT-2024-0001'
        mock_orden.cliente = mock_cliente
        mock_orden.descripcion = 'Descripcion test'
        mock_orden.observaciones = None
        mock_orden.status = OTStatus.PENDIENTE
        mock_orden.progreso = 0
        mock_orden.pedidos_count = 0
        mock_orden.entradas_count = 0
        mock_orden.fech_creacion = datetime.utcnow()
        mock_orden.fech_completado = None
        mock_orden.pedidos = MagicMock()
        mock_orden.pedidos.all.return_value = []

        mock_service.crear_orden_trabajo.return_value = mock_orden

        data = {
            'cliente_id': test_cliente.id,
            'nro_ofic': 'OT-001',
            'descripcion': 'Descripcion test'
        }

        with patch('app.decorators.current_user', test_user):
            response = auth_client.post(
                '/api/ordenes-trabajo',
                data=json.dumps(data),
                headers={'Content-Type': 'application/json'}
            )

        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['data']['id'] == 1
        assert response_data['data']['nro_ofic'] == 'OT-001'

    def test_create_orden_trabajo_validation_error(self, auth_client, test_user):
        """Retorna 400 para datos invalidos."""
        with patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService') as mock_service:
            mock_service.crear_orden_trabajo.side_effect = ValueError('El cliente es obligatorio')

            with patch('app.decorators.current_user', test_user):
                response = auth_client.post(
                    '/api/ordenes-trabajo',
                    data=json.dumps({'nro_ofic': 'OT-001'}),
                    headers={'Content-Type': 'application/json'}
                )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert response_data['error']['code'] == 'VALIDATION_ERROR'

    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_create_orden_trabajo_duplicate_nro_ofic(self, mock_service, auth_client, test_user, app, test_cliente):
        """Retorna 400 si el nro_ofic ya existe."""
        mock_service.crear_orden_trabajo.side_effect = ValueError('El numero oficial "OT-001" ya existe')

        data = {
            'cliente_id': test_cliente.id,
            'nro_ofic': 'OT-001',
            'descripcion': 'Descripcion test'
        }

        with patch('app.decorators.current_user', test_user):
            response = auth_client.post(
                '/api/ordenes-trabajo',
                data=json.dumps(data),
                headers={'Content-Type': 'application/json'}
            )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert response_data['error']['code'] == 'VALIDATION_ERROR'

    def test_create_orden_trabajo_unauthorized(self, client, test_user):
        """Creacion sin autenticacion retorna 401/302."""
        data = {
            'cliente_id': 1,
            'nro_ofic': 'OT-001',
            'descripcion': 'Descripcion test'
        }
        response = client.post(
            '/api/ordenes-trabajo',
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code in [302, 401, 403]

    # Get Tests
    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_get_orden_trabajo_success(self, mock_service, auth_client, test_user, app, test_cliente):
        """GET /api/ordenes-trabajo/{id} retorna detalles."""
        mock_cliente = MagicMock()
        mock_cliente.id = test_cliente.id
        mock_cliente.nombre = 'Cliente Test'

        mock_orden = MagicMock()
        mock_orden.id = 1
        mock_orden.nro_ofic = 'OT-001'
        mock_orden.codigo = 'OT-2024-0001'
        mock_orden.cliente = mock_cliente
        mock_orden.descripcion = 'Descripcion test'
        mock_orden.observaciones = None
        mock_orden.status = OTStatus.PENDIENTE
        mock_orden.progreso = 0
        mock_orden.pedidos_count = 0
        mock_orden.entradas_count = 0
        mock_orden.fech_creacion = datetime.utcnow()
        mock_orden.fech_completado = None
        mock_orden.pedidos = MagicMock()
        mock_orden.pedidos.all.return_value = []

        mock_service.obtener_orden_por_id.return_value = mock_orden

        with patch('app.decorators.current_user', test_user):
            response = auth_client.get('/api/ordenes-trabajo/1')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['data']['id'] == 1
        assert response_data['data']['nro_ofic'] == 'OT-001'

    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_get_orden_trabajo_not_found(self, mock_service, auth_client, test_user):
        """Retorna 404 para ID inexistente."""
        mock_service.obtener_orden_por_id.return_value = None

        with patch('app.decorators.current_user', test_user):
            response = auth_client.get('/api/ordenes-trabajo/999')

        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert response_data['error']['code'] == 'NOT_FOUND'

    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_get_orden_trabajo_includes_pedidos(self, mock_service, auth_client, test_user, app, test_cliente, test_pedido):
        """GET incluye los pedidos relacionados."""
        mock_cliente = MagicMock()
        mock_cliente.id = test_cliente.id
        mock_cliente.nombre = 'Cliente Test'

        mock_producto = MagicMock()
        mock_producto.id = 1
        mock_producto.nombre = 'Producto Test'

        mock_pedido = MagicMock()
        mock_pedido.id = test_pedido.id
        mock_pedido.codigo = 'PED-2024-0001'
        mock_pedido.cliente = mock_cliente
        mock_pedido.producto = mock_producto
        mock_pedido.lote = 'L-001'
        mock_pedido.fech_fab = None
        mock_pedido.fech_venc = None
        mock_pedido.cantidad = None
        mock_pedido.status = PedidoStatus.PENDIENTE
        mock_pedido.entradas_count = 0
        mock_pedido.entradas_completadas = 0

        mock_orden = MagicMock()
        mock_orden.id = 1
        mock_orden.nro_ofic = 'OT-001'
        mock_orden.codigo = 'OT-2024-0001'
        mock_orden.cliente = mock_cliente
        mock_orden.descripcion = 'Descripcion test'
        mock_orden.observaciones = None
        mock_orden.status = OTStatus.PENDIENTE
        mock_orden.progreso = 0
        mock_orden.pedidos_count = 1
        mock_orden.entradas_count = 0
        mock_orden.fech_creacion = datetime.utcnow()
        mock_orden.fech_completado = None
        mock_orden.pedidos = MagicMock()
        mock_orden.pedidos.all.return_value = [mock_pedido]

        mock_service.obtener_orden_por_id.return_value = mock_orden

        with patch('app.decorators.current_user', test_user):
            response = auth_client.get('/api/ordenes-trabajo/1')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert len(response_data['data']['pedidos']) == 1
        assert response_data['data']['pedidos'][0]['codigo'] == 'PED-2024-0001'

    # Update Tests
    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_update_orden_trabajo_success(self, mock_service, auth_client, test_user, app, test_cliente):
        """PUT /api/ordenes-trabajo/{id} actualiza la orden."""
        mock_cliente = MagicMock()
        mock_cliente.id = test_cliente.id
        mock_cliente.nombre = 'Cliente Test'

        mock_orden = MagicMock()
        mock_orden.id = 1
        mock_orden.nro_ofic = 'OT-001-UPDATED'
        mock_orden.codigo = 'OT-2024-0001'
        mock_orden.cliente = mock_cliente
        mock_orden.descripcion = 'Descripcion actualizada'
        mock_orden.observaciones = 'Observaciones actualizadas'
        mock_orden.status = OTStatus.PENDIENTE
        mock_orden.progreso = 0
        mock_orden.pedidos_count = 0
        mock_orden.entradas_count = 0
        mock_orden.fech_creacion = datetime.utcnow()
        mock_orden.fech_completado = None
        mock_orden.pedidos = MagicMock()
        mock_orden.pedidos.all.return_value = []

        mock_service.actualizar_orden.return_value = mock_orden

        with patch('app.decorators.current_user', test_user):
            response = auth_client.put(
                '/api/ordenes-trabajo/1',
                data=json.dumps({
                    'descripcion': 'Descripcion actualizada',
                    'observaciones': 'Observaciones actualizadas'
                }),
                headers={'Content-Type': 'application/json'}
            )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['data']['descripcion'] == 'Descripcion actualizada'

    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_update_orden_trabajo_not_found(self, mock_service, auth_client, test_user):
        """Retorna error si la orden no existe."""
        mock_service.actualizar_orden.side_effect = ValueError('Orden de trabajo no encontrada')

        with patch('app.decorators.current_user', test_user):
            response = auth_client.put(
                '/api/ordenes-trabajo/999',
                data=json.dumps({'descripcion': 'Actualizado'}),
                headers={'Content-Type': 'application/json'}
            )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert response_data['error']['code'] == 'VALIDATION_ERROR'

    def test_update_orden_trabajo_unauthorized(self, client, test_user):
        """Actualizacion sin autenticacion retorna 401/302."""
        response = client.put(
            '/api/ordenes-trabajo/1',
            data=json.dumps({'descripcion': 'Actualizado'}),
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code in [302, 401, 403]

    # Delete Tests
    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_delete_orden_trabajo_success(self, mock_service, auth_client, test_user, app, test_cliente):
        """DELETE realiza soft delete."""
        mock_cliente = MagicMock()
        mock_cliente.id = test_cliente.id
        mock_cliente.nombre = 'Cliente Test'

        mock_orden = MagicMock()
        mock_orden.id = 1
        mock_orden.nro_ofic = 'OT-001'
        mock_orden.codigo = 'OT-2024-0001'
        mock_orden.cliente = mock_cliente
        mock_orden.descripcion = 'Descripcion test'
        mock_orden.observaciones = None
        mock_orden.status = 'ELIMINADA'
        mock_orden.progreso = 0
        mock_orden.pedidos_count = 0
        mock_orden.entradas_count = 0
        mock_orden.fech_creacion = datetime.utcnow()
        mock_orden.fech_completado = None
        mock_orden.pedidos = MagicMock()
        mock_orden.pedidos.all.return_value = []

        mock_service.eliminar_orden.return_value = mock_orden

        with patch('app.decorators.current_user', test_user):
            response = auth_client.delete('/api/ordenes-trabajo/1')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['data']['status'] == 'ELIMINADA'

    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_delete_orden_trabajo_not_found(self, mock_service, auth_client, test_user):
        """Retorna error si la orden no existe."""
        mock_service.eliminar_orden.side_effect = ValueError('Orden de trabajo no encontrada')

        with patch('app.decorators.current_user', test_user):
            response = auth_client.delete('/api/ordenes-trabajo/999')

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert response_data['error']['code'] == 'VALIDATION_ERROR'

    def test_delete_orden_trabajo_unauthorized(self, client, test_user):
        """Eliminacion sin autenticacion retorna 401/302."""
        response = client.delete('/api/ordenes-trabajo/1')
        assert response.status_code in [302, 401, 403]

    # Assignment Tests
    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_asignar_pedido_success(self, mock_service, auth_client, test_user, app, test_cliente, test_pedido):
        """POST /asignar-pedido asigna un pedido a la orden."""
        mock_cliente = MagicMock()
        mock_cliente.id = test_cliente.id
        mock_cliente.nombre = 'Cliente Test'

        mock_producto = MagicMock()
        mock_producto.id = 1
        mock_producto.nombre = 'Producto Test'

        mock_pedido = MagicMock()
        mock_pedido.id = test_pedido.id
        mock_pedido.codigo = 'PED-2024-0001'
        mock_pedido.cliente = mock_cliente
        mock_pedido.producto = mock_producto
        mock_pedido.lote = 'L-001'
        mock_pedido.fech_fab = None
        mock_pedido.fech_venc = None
        mock_pedido.cantidad = None
        mock_pedido.status = PedidoStatus.PENDIENTE
        mock_pedido.entradas_count = 0
        mock_pedido.entradas_completadas = 0

        mock_orden = MagicMock()
        mock_orden.id = 1
        mock_orden.nro_ofic = 'OT-001'
        mock_orden.codigo = 'OT-2024-0001'
        mock_orden.cliente = mock_cliente
        mock_orden.descripcion = 'Descripcion test'
        mock_orden.observaciones = None
        mock_orden.status = OTStatus.EN_PROGRESO
        mock_orden.progreso = 0
        mock_orden.pedidos_count = 1
        mock_orden.entradas_count = 0
        mock_orden.fech_creacion = datetime.utcnow()
        mock_orden.fech_completado = None
        mock_orden.pedidos = MagicMock()
        mock_orden.pedidos.all.return_value = [mock_pedido]

        mock_service.asignar_pedido.return_value = mock_orden

        with patch('app.decorators.current_user', test_user):
            response = auth_client.post(
                '/api/ordenes-trabajo/1/asignar-pedido',
                data=json.dumps({'pedido_id': test_pedido.id}),
                headers={'Content-Type': 'application/json'}
            )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['data']['pedidos_count'] == 1

    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_asignar_pedido_different_cliente_error(self, mock_service, auth_client, test_user, app, test_cliente):
        """Retorna error si el pedido pertenece a otro cliente."""
        mock_service.asignar_pedido.side_effect = ValueError(
            'El pedido pertenece a otro cliente'
        )

        with patch('app.decorators.current_user', test_user):
            response = auth_client.post(
                '/api/ordenes-trabajo/1/asignar-pedido',
                data=json.dumps({'pedido_id': 999}),
                headers={'Content-Type': 'application/json'}
            )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert response_data['error']['code'] == 'VALIDATION_ERROR'

    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_asignar_pedido_not_found(self, mock_service, auth_client, test_user):
        """Retorna error si el pedido no existe."""
        mock_service.asignar_pedido.side_effect = ValueError('Pedido no encontrado')

        with patch('app.decorators.current_user', test_user):
            response = auth_client.post(
                '/api/ordenes-trabajo/1/asignar-pedido',
                data=json.dumps({'pedido_id': 999}),
                headers={'Content-Type': 'application/json'}
            )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False

    def test_asignar_pedido_missing_pedido_id(self, auth_client, test_user):
        """Retorna 400 si no se proporciona pedido_id."""
        with patch('app.decorators.current_user', test_user):
            response = auth_client.post(
                '/api/ordenes-trabajo/1/asignar-pedido',
                data=json.dumps({}),
                headers={'Content-Type': 'application/json'}
            )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert response_data['error']['code'] == 'VALIDATION_ERROR'

    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_quitar_pedido_success(self, mock_service, auth_client, test_user, app, test_cliente, test_pedido):
        """POST /quitar-pedido quita un pedido de la orden."""
        mock_cliente = MagicMock()
        mock_cliente.id = test_cliente.id
        mock_cliente.nombre = 'Cliente Test'

        mock_orden = MagicMock()
        mock_orden.id = 1
        mock_orden.nro_ofic = 'OT-001'
        mock_orden.codigo = 'OT-2024-0001'
        mock_orden.cliente = mock_cliente
        mock_orden.descripcion = 'Descripcion test'
        mock_orden.observaciones = None
        mock_orden.status = OTStatus.PENDIENTE
        mock_orden.progreso = 0
        mock_orden.pedidos_count = 0
        mock_orden.entradas_count = 0
        mock_orden.fech_creacion = datetime.utcnow()
        mock_orden.fech_completado = None
        mock_orden.pedidos = MagicMock()
        mock_orden.pedidos.all.return_value = []

        mock_service.quitar_pedido.return_value = mock_orden

        with patch('app.decorators.current_user', test_user):
            response = auth_client.post(
                '/api/ordenes-trabajo/1/quitar-pedido',
                data=json.dumps({'pedido_id': test_pedido.id}),
                headers={'Content-Type': 'application/json'}
            )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['message'] == 'Pedido quitado exitosamente'

    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_quitar_pedido_not_assigned(self, mock_service, auth_client, test_user, app, test_cliente):
        """Retorna error si el pedido no esta asignado a la orden."""
        mock_service.quitar_pedido.side_effect = ValueError(
            'El pedido PED-2024-0001 no pertenece a esta orden de trabajo'
        )

        with patch('app.decorators.current_user', test_user):
            response = auth_client.post(
                '/api/ordenes-trabajo/1/quitar-pedido',
                data=json.dumps({'pedido_id': 999}),
                headers={'Content-Type': 'application/json'}
            )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert response_data['error']['code'] == 'VALIDATION_ERROR'

    # Search Tests
    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_buscar_por_nro_ofic_success(self, mock_service, auth_client, test_user, app, test_cliente):
        """GET /buscar encuentra orden por nro_ofic exacto."""
        mock_cliente = MagicMock()
        mock_cliente.id = test_cliente.id
        mock_cliente.nombre = 'Cliente Test'

        mock_orden = MagicMock()
        mock_orden.id = 1
        mock_orden.nro_ofic = 'OT-001'
        mock_orden.codigo = 'OT-2024-0001'
        mock_orden.cliente = mock_cliente
        mock_orden.descripcion = 'Descripcion test'
        mock_orden.observaciones = None
        mock_orden.status = OTStatus.PENDIENTE
        mock_orden.progreso = 0
        mock_orden.pedidos_count = 0
        mock_orden.entradas_count = 0
        mock_orden.fech_creacion = datetime.utcnow()
        mock_orden.fech_completado = None
        mock_orden.pedidos = MagicMock()
        mock_orden.pedidos.all.return_value = []

        mock_service.buscar_por_nro_ofic.return_value = mock_orden

        with patch('app.decorators.current_user', test_user):
            response = auth_client.get('/api/ordenes-trabajo/buscar?nro_ofic=OT-001')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['data']['nro_ofic'] == 'OT-001'

    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_buscar_por_nro_ofic_partial_match(self, mock_service, auth_client, test_user, app, test_cliente):
        """La busqueda funciona con coincidencias parciales."""
        mock_cliente = MagicMock()
        mock_cliente.id = test_cliente.id
        mock_cliente.nombre = 'Cliente Test'

        mock_orden = MagicMock()
        mock_orden.id = 1
        mock_orden.nro_ofic = 'OT-001-ABC'
        mock_orden.codigo = 'OT-2024-0001'
        mock_orden.cliente = mock_cliente
        mock_orden.descripcion = 'Descripcion test'
        mock_orden.observaciones = None
        mock_orden.status = OTStatus.PENDIENTE
        mock_orden.progreso = 0
        mock_orden.pedidos_count = 0
        mock_orden.entradas_count = 0
        mock_orden.fech_creacion = datetime.utcnow()
        mock_orden.fech_completado = None
        mock_orden.pedidos = MagicMock()
        mock_orden.pedidos.all.return_value = []

        mock_service.buscar_por_nro_ofic.return_value = mock_orden

        with patch('app.decorators.current_user', test_user):
            response = auth_client.get('/api/ordenes-trabajo/buscar?nro_ofic=OT-001')

        assert response.status_code == 200
        mock_service.buscar_por_nro_ofic.assert_called_once_with('OT-001')

    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_buscar_por_nro_ofic_not_found(self, mock_service, auth_client, test_user):
        """Retorna 404 si no se encuentra la orden."""
        mock_service.buscar_por_nro_ofic.return_value = None

        with patch('app.decorators.current_user', test_user):
            response = auth_client.get('/api/ordenes-trabajo/buscar?nro_ofic=OT-NOEXISTE')

        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert response_data['error']['code'] == 'NOT_FOUND'

    def test_buscar_por_nro_ofic_empty_query(self, auth_client, test_user):
        """Retorna 400 si no se proporciona nro_ofic."""
        with patch('app.decorators.current_user', test_user):
            response = auth_client.get('/api/ordenes-trabajo/buscar')

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert response_data['error']['code'] == 'VALIDATION_ERROR'

    # Client Orders Tests
    @patch('app.routes.ordenes_trabajo_api.OrdenTrabajoService')
    def test_get_ordenes_por_cliente_success(self, mock_service, auth_client, test_user, app, test_cliente):
        """GET /api/clientes/{id}/ordenes-trabajo retorna ordenes del cliente."""
        mock_cliente = MagicMock()
        mock_cliente.id = test_cliente.id
        mock_cliente.nombre = 'Cliente Test'

        mock_orden = MagicMock()
        mock_orden.id = 1
        mock_orden.nro_ofic = 'OT-001'
        mock_orden.codigo = 'OT-2024-0001'
        mock_orden.cliente = mock_cliente
        mock_orden.descripcion = 'Descripcion test'
        mock_orden.observaciones = None
        mock_orden.status = OTStatus.PENDIENTE
        mock_orden.progreso = 0
        mock_orden.pedidos_count = 0
        mock_orden.entradas_count = 0
        mock_orden.fech_creacion = datetime.utcnow()
        mock_orden.fech_completado = None
        mock_orden.pedidos = MagicMock()
        mock_orden.pedidos.all.return_value = []

        mock_service.obtener_ordenes_paginadas.return_value = (
            [mock_orden],
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
            response = auth_client.get(f'/api/clientes/{test_cliente.id}/ordenes-trabajo')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert len(response_data['data']) == 1
        assert response_data['data'][0]['cliente']['id'] == test_cliente.id
        mock_service.obtener_ordenes_paginadas.assert_called_once()
