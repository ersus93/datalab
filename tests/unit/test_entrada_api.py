#!/usr/bin/env python3
"""Tests unitarios para los endpoints de API de entradas."""

import json
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from flask_login import login_user

from app import create_app, db
from app.database.models.user import User, UserRole


@pytest.fixture
def app():
    """Crear aplicación Flask en modo testing."""
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
    """Crear un usuario de prueba técnico."""
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
        # Refrescar para obtener el ID asignado
        db.session.refresh(user)
        return user


@pytest.fixture
def auth_client(client, test_user, app):
    """Cliente autenticado como usuario técnico."""
    with app.app_context():
        # Refrescar el usuario en este contexto
        user = db.session.get(User, test_user.id)
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True
    return client


@pytest.fixture
def auth_headers():
    """Headers para requests JSON."""
    return {'Content-Type': 'application/json'}


class TestCrearEntrada:
    """Tests para POST /api/entradas"""

    @patch('app.routes.entradas_api.EntradaService')
    def test_post_entradas_creates_entry(self, mock_service, auth_client, auth_headers, test_user, app):
        """POST /api/entradas crea una entrada."""
        mock_entrada = MagicMock()
        mock_entrada.to_dict.return_value = {
            'id': 1,
            'codigo': 'ENT001',
            'status': 'RECIBIDO'
        }
        mock_service.crear_entrada.return_value = mock_entrada

        data = {
            'codigo': 'ENT001',
            'lote': 'A-1234',
            'producto_id': 1,
            'fabrica_id': 1,
            'cliente_id': 1,
            'cantidad_recib': 100.0
        }

        with patch('app.decorators.current_user', test_user):
            response = auth_client.post(
                '/api/entradas',
                data=json.dumps(data),
                headers=auth_headers
            )

        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['data']['id'] == 1

    def test_post_entradas_validation_error(self, auth_client, auth_headers, test_user, app):
        """Retorna 400 para datos inválidos."""
        with patch('app.routes.entradas_api.EntradaService') as mock_service:
            mock_service.crear_entrada.side_effect = ValueError('Lote inválido')

            with patch('app.decorators.current_user', test_user):
                response = auth_client.post(
                    '/api/entradas',
                    data=json.dumps({'codigo': 'ENT001'}),
                    headers=auth_headers
                )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert response_data['error']['code'] == 'VALIDATION_ERROR'


class TestListarEntradas:
    """Tests para GET /api/entradas"""

    @patch('app.routes.entradas_api.EntradaService')
    def test_get_entradas_list(self, mock_service, auth_client, test_user, app):
        """GET /api/entradas retorna lista paginada."""
        mock_entrada = MagicMock()
        mock_entrada.to_dict.return_value = {
            'id': 1,
            'codigo': 'ENT001',
            'status': 'RECIBIDO'
        }

        mock_service.obtener_entradas_paginadas.return_value = (
            [mock_entrada],
            {
                'pagina': 1,
                'por_pagina': 20,
                'total': 1,
                'total_paginas': 1,
                'tiene_siguiente': False,
                'tiene_anterior': False
            }
        )

        with patch('app.decorators.current_user', test_user):
            response = auth_client.get('/api/entradas')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert len(response_data['data']['entradas']) == 1
        assert response_data['data']['pagination']['total'] == 1

    @patch('app.routes.entradas_api.EntradaService')
    def test_get_entradas_with_filters(self, mock_service, auth_client, test_user, app):
        """El filtrado funciona correctamente."""
        mock_service.obtener_entradas_paginadas.return_value = (
            [],
            {'pagina': 1, 'por_pagina': 20, 'total': 0, 'total_paginas': 0}
        )

        with patch('app.decorators.current_user', test_user):
            response = auth_client.get('/api/entradas?cliente_id=1&status=RECIBIDO')

        assert response.status_code == 200
        mock_service.obtener_entradas_paginadas.assert_called_once()


class TestObtenerEntrada:
    """Tests para GET /api/entradas/{id}"""

    @patch('app.routes.entradas_api.EntradaService')
    def test_get_entrada_detail(self, mock_service, auth_client, test_user, app):
        """GET /api/entradas/{id} retorna detalles."""
        mock_entrada = MagicMock()
        mock_entrada.to_dict.return_value = {
            'id': 1,
            'codigo': 'ENT001',
            'status': 'RECIBIDO',
            'saldo': '100.00'
        }
        mock_service.obtener_entrada_por_id.return_value = mock_entrada

        with patch('app.decorators.current_user', test_user):
            response = auth_client.get('/api/entradas/1')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['data']['id'] == 1

    @patch('app.routes.entradas_api.EntradaService')
    def test_get_entrada_not_found(self, mock_service, auth_client, test_user, app):
        """Retorna 404 para ID inexistente."""
        mock_service.obtener_entrada_por_id.return_value = None

        with patch('app.decorators.current_user', test_user):
            response = auth_client.get('/api/entradas/999')

        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert response_data['error']['code'] == 'NOT_FOUND'


class TestActualizarEntrada:
    """Tests para PUT /api/entradas/{id}"""

    @patch('app.routes.entradas_api.EntradaService')
    def test_put_entrada_updates(self, mock_service, auth_client, auth_headers, test_user, app):
        """PUT /api/entradas/{id} actualiza la entrada."""
        mock_entrada = MagicMock()
        mock_entrada.to_dict.return_value = {'id': 1, 'codigo': 'ENT001'}
        mock_service.actualizar_entrada.return_value = mock_entrada

        with patch('app.decorators.current_user', test_user):
            response = auth_client.put(
                '/api/entradas/1',
                data=json.dumps({'observaciones': 'Actualizado'}),
                headers=auth_headers
            )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True


class TestEliminarEntrada:
    """Tests para DELETE /api/entradas/{id}"""

    @patch('app.routes.entradas_api.EntradaService')
    def test_delete_entrada_soft_deletes(self, mock_service, auth_client, test_user, app):
        """DELETE realiza soft delete."""
        mock_entrada = MagicMock()
        mock_entrada.to_dict.return_value = {'id': 1, 'status': 'ANULADO'}
        mock_service.eliminar_entrada.return_value = mock_entrada

        with patch('app.decorators.current_user', test_user):
            response = auth_client.delete('/api/entradas/1')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True


class TestCambiarEstado:
    """Tests para POST /api/entradas/{id}/cambiar-estado"""

    @patch('app.routes.entradas_api.EntradaService')
    def test_post_cambiar_estado(self, mock_service, auth_client, auth_headers, test_user, app):
        """El endpoint de cambio de estado funciona."""
        mock_entrada = MagicMock()
        mock_entrada.to_dict.return_value = {'id': 1, 'status': 'EN_PROCESO'}
        mock_service.cambiar_estado.return_value = mock_entrada

        with patch('app.decorators.current_user', test_user):
            response = auth_client.post(
                '/api/entradas/1/cambiar-estado',
                data=json.dumps({'status': 'EN_PROCESO', 'reason': 'Iniciar'}),
                headers=auth_headers
            )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True


class TestRegistrarEntrega:
    """Tests para POST /api/entradas/{id}/entregar"""

    @patch('app.routes.entradas_api.EntradaService')
    def test_post_entregar(self, mock_service, auth_client, auth_headers, test_user, app):
        """El endpoint de entrega funciona."""
        mock_entrada = MagicMock()
        mock_entrada.to_dict.return_value = {'id': 1, 'saldo': '50.00'}
        mock_service.registrar_entrega.return_value = mock_entrada

        with patch('app.decorators.current_user', test_user):
            response = auth_client.post(
                '/api/entradas/1/entregar',
                data=json.dumps({'cantidad': 50}),
                headers=auth_headers
            )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True


class TestObtenerSaldo:
    """Tests para GET /api/entradas/{id}/saldo"""

    @patch('app.routes.entradas_api.EntradaService')
    def test_get_saldo(self, mock_service, auth_client, test_user, app):
        """El endpoint de saldo retorna el balance."""
        mock_entrada = MagicMock()
        mock_entrada.id = 1
        mock_entrada.codigo = 'ENT001'
        mock_entrada.cantidad_recib = Decimal('100')
        mock_entrada.cantidad_entreg = Decimal('30')
        mock_entrada.saldo = Decimal('70')
        mock_service.obtener_entrada_por_id.return_value = mock_entrada

        with patch('app.decorators.current_user', test_user):
            response = auth_client.get('/api/entradas/1/saldo')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['success'] is True
        assert response_data['data']['saldo'] == '70'
        assert response_data['data']['cantidad_recib'] == '100'


class TestAutorizacion:
    """Tests de autorización."""

    def test_unauthorized_access(self, client):
        """Acceso sin autenticación retorna 401/403."""
        response = client.get('/api/entradas')

        assert response.status_code in [302, 401, 403]
