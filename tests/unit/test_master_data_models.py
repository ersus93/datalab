#!/usr/bin/env python3
"""Tests unitarios para modelos maestros (Master Data Models)."""

import pytest
from app.database.models import Cliente, Fabrica, Producto, EnsayoXProducto


class TestFabricaModel:
    """Tests para el modelo Fabrica."""

    def test_fabrica_creation(self):
        """Test crear una instancia de fábrica."""
        fabrica = Fabrica(
            cliente_id=1,
            nombre='Fábrica Principal',
            provincia_id=1,
            activo=True
        )

        assert fabrica.cliente_id == 1
        assert fabrica.nombre == 'Fábrica Principal'
        assert fabrica.provincia_id == 1
        assert fabrica.activo is True

    def test_fabrica_repr(self):
        """Test representación string de Fabrica."""
        fabrica = Fabrica(cliente_id=1, nombre='Fábrica Test')
        assert repr(fabrica) == '<Fabrica Fábrica Test>'

    def test_fabrica_to_dict(self):
        """Test conversión a diccionario."""
        fabrica = Fabrica(cliente_id=1, nombre='Fábrica Dict')
        fabrica.id = 1

        data = fabrica.to_dict()
        assert data['id'] == 1
        assert data['nombre'] == 'Fábrica Dict'
        assert data['cliente_id'] == 1
        assert 'creado_en' in data


class TestProductoModel:
    """Tests para el modelo Producto."""

    def test_producto_creation(self):
        """Test crear un producto."""
        producto = Producto(
            nombre='Producto Test',
            destino_id=1,
            activo=True
        )

        assert producto.nombre == 'Producto Test'
        assert producto.destino_id == 1
        assert producto.activo is True

    def test_producto_repr(self):
        """Test representación string de Producto."""
        producto = Producto(nombre='Leche Entera')
        assert repr(producto) == '<Producto Leche Entera>'

    def test_producto_to_dict(self):
        """Test conversión a diccionario."""
        producto = Producto(nombre='Producto Dict')
        producto.id = 1

        data = producto.to_dict()
        assert data['id'] == 1
        assert data['nombre'] == 'Producto Dict'


class TestEnsayoXProducto:
    """Tests para la tabla de unión EnsayoXProducto."""

    def test_ensayo_x_producto_creation(self):
        """Test crear relación ensayo-producto."""
        rel = EnsayoXProducto(
            producto_id=1,
            ensayo_id=2
        )

        assert rel.producto_id == 1
        assert rel.ensayo_id == 2

    def test_ensayo_x_producto_repr(self):
        """Test representación string."""
        rel = EnsayoXProducto(producto_id=1, ensayo_id=2)
        assert repr(rel) == '<EnsayoXProducto producto=1 ensayo=2>'


class TestClienteUpdated:
    """Tests para verificar actualizaciones del modelo Cliente."""

    def test_cliente_tipo_cliente(self):
        """Test campo tipo_cliente."""
        cliente = Cliente(
            codigo='CLI001',
            nombre='Cliente con Tipo',
            tipo_cliente=1
        )

        assert cliente.tipo_cliente == 1

    def test_cliente_to_dict_updated(self):
        """Test que to_dict incluye los nuevos campos."""
        cliente = Cliente(
            codigo='CLI002',
            nombre='Cliente Test',
            tipo_cliente=2,
            organismo_id=1
        )
        cliente.id = 1

        data = cliente.to_dict()
        assert data['tipo_cliente'] == 2
        assert data['organismo_id'] == 1
        assert 'total_fabricas' in data
        assert 'total_pedidos' in data

    def test_cliente_total_fabricas_empty(self):
        """Test total_fabricas cuando no hay fábricas."""
        cliente = Cliente(codigo='CLI003', nombre='Cliente 3')
        assert cliente.total_fabricas == 0

    def test_cliente_total_pedidos_empty(self):
        """Test total_pedidos cuando no hay pedidos."""
        cliente = Cliente(codigo='CLI004', nombre='Cliente 4')
        assert cliente.total_pedidos == 0
