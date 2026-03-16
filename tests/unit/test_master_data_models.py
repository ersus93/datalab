#!/usr/bin/env python3
"""Tests unitarios para modelos de datos maestros.

Estos tests verifican la creación y validación básica de los modelos
de datos maestros (Cliente, Fabrica, Producto).
"""

import pytest
from datetime import datetime

# Import master data models
from app.database.models import (
    Cliente,
    Fabrica,
    Producto,
    Organismo,
    Provincia,
    Destino,
    Rama,
)


class TestClienteModel:
    """Tests para el modelo Cliente."""

    def test_cliente_creation(self):
        """Test creación básica de Cliente."""
        cliente = Cliente()
        cliente.codigo = "CLI001"
        cliente.nombre = "Empresa de Prueba"
        cliente.activo = True

        assert cliente.codigo == "CLI001"
        assert cliente.nombre == "Empresa de Prueba"
        assert cliente.activo is True

    def test_cliente_repr(self):
        """Test representación string de Cliente."""
        cliente = Cliente()
        cliente.codigo = "CLI001"
        cliente.nombre = "Test Company"

        assert repr(cliente) == "<Cliente Test Company>"

    def test_cliente_to_dict(self):
        """Test serialización a dict."""
        cliente = Cliente()
        cliente.id = 1
        cliente.codigo = "CLI001"
        cliente.nombre = "Empresa de Prueba"

        data = cliente.to_dict()

        assert data['id'] == 1
        assert data['codigo'] == "CLI001"
        assert data['nombre'] == "Empresa de Prueba"


class TestFabricaModel:
    """Tests para el modelo Fabrica."""

    def test_fabrica_creation(self):
        """Test creación básica de Fabrica."""
        fabrica = Fabrica()
        fabrica.nombre = "Planta Principal"
        fabrica.activo = True

        assert fabrica.nombre == "Planta Principal"
        assert fabrica.activo is True

    def test_fabrica_repr(self):
        """Test representación string de Fabrica."""
        fabrica = Fabrica()
        fabrica.nombre = "Planta de Producción"

        assert repr(fabrica) == "<Fabrica Planta de Producción>"

    def test_fabrica_to_dict(self):
        """Test serialización a dict."""
        fabrica = Fabrica()
        fabrica.id = 1
        fabrica.nombre = "Planta Principal"

        data = fabrica.to_dict()

        assert data['id'] == 1
        assert data['nombre'] == "Planta Principal"


class TestProductoModel:
    """Tests para el modelo Producto."""

    def test_producto_creation(self):
        """Test creación básica de Producto."""
        producto = Producto()
        producto.codigo = "PROD001"
        producto.nombre = "Producto de Prueba"
        producto.activo = True

        assert producto.codigo == "PROD001"
        assert producto.nombre == "Producto de Prueba"
        assert producto.activo is True

    def test_producto_repr(self):
        """Test representación string de Producto."""
        producto = Producto()
        producto.codigo = "PROD001"
        producto.nombre = "Test Product"

        assert repr(producto) == "<Producto Test Product>"

    def test_producto_to_dict(self):
        """Test serialización a dict."""
        producto = Producto()
        producto.id = 1
        producto.nombre = "Producto de Prueba"

        data = producto.to_dict()

        assert data['id'] == 1
        assert data['nombre'] == "Producto de Prueba"


class TestOrganismoModel:
    """Tests para el modelo Organismo."""

    def test_organismo_creation(self):
        """Test creación básica de Organismo."""
        org = Organismo()
        org.nombre = "Ministerio de Agricultura"

        assert org.nombre == "Ministerio de Agricultura"

    def test_organismo_repr(self):
        """Test representación string."""
        org = Organismo()
        org.nombre = "ONIE"

        assert repr(org) == "<Organismo ONIE>"


class TestProvinciaModel:
    """Tests para el modelo Provincia."""

    def test_provincia_creation(self):
        """Test creación básica de Provincia."""
        prov = Provincia()
        prov.nombre = "La Habana"
        prov.sigla = "LH"

        assert prov.nombre == "La Habana"
        assert prov.sigla == "LH"

    def test_provincia_repr(self):
        """Test representación string."""
        prov = Provincia()
        prov.sigla = "PRI"
        prov.nombre = "Pinar del Río"

        assert repr(prov) == "<Provincia PRI: Pinar del Río>"


class TestDestinoModel:
    """Tests para el modelo Destino."""

    def test_destino_creation(self):
        """Test creación básica de Destino."""
        dest = Destino()
        dest.nombre = "Consumo Familiar"
        dest.sigla = "CF"

        assert dest.nombre == "Consumo Familiar"
        assert dest.sigla == "CF"

    def test_destino_repr(self):
        """Test representación string."""
        dest = Destino()
        dest.sigla = "AC"
        dest.nombre = "Alimentación Colectiva"

        assert repr(dest) == "<Destino AC: Alimentación Colectiva>"


class TestRamaModel:
    """Tests para el modelo Rama."""

    def test_rama_creation(self):
        """Test creación básica de Rama."""
        rama = Rama()
        rama.nombre = "Industria Láctea"

        assert rama.nombre == "Industria Láctea"

    def test_rama_repr(self):
        """Test representación string."""
        rama = Rama()
        rama.nombre = "Carnes"

        assert repr(rama) == "<Rama Carnes>"