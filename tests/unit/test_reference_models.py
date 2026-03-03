#!/usr/bin/env python3
"""Tests unitarios para modelos de referencia.

Estos tests verifican la creación y validación básica de los modelos
de referencia sin necesidad de base de datos real.
"""

import pytest
from datetime import datetime

# Import all reference models
from app.database.models import (
    Area,
    Organismo,
    Provincia,
    Destino,
    Rama,
    Mes,
    Anno,
    TipoES,
    UnidadMedida,
)


class TestAreaModel:
    """Tests para el modelo Area."""

    def test_area_creation(self):
        """Test creación básica de Area."""
        area = Area()
        area.nombre = "Físico-Químico"
        area.sigla = "FQ"

        assert area.nombre == "Físico-Químico"
        assert area.sigla == "FQ"

    def test_area_repr(self):
        """Test representación string de Area."""
        area = Area()
        area.sigla = "MB"
        area.nombre = "Microbiología"

        assert repr(area) == "<Area MB: Microbiología>"

    def test_area_to_dict(self):
        """Test serialización a dict."""
        area = Area()
        area.id = 1
        area.nombre = "Evaluación Sensorial"
        area.sigla = "ES"

        data = area.to_dict()

        assert data['id'] == 1
        assert data['nombre'] == "Evaluación Sensorial"
        assert data['sigla'] == "ES"


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
        prov.sigla = "CM"
        prov.nombre = "Camagüey"

        assert repr(prov) == "<Provincia CM: Camagüey>"


class TestDestinoModel:
    """Tests para el modelo Destino."""

    def test_destino_creation(self):
        """Test creación básica de Destino."""
        dest = Destino()
        dest.nombre = "Canasta Familiar"
        dest.sigla = "CF"

        assert dest.nombre == "Canasta Familiar"
        assert dest.sigla == "CF"

    def test_destino_repr(self):
        """Test representación string."""
        dest = Destino()
        dest.sigla = "AC"
        dest.nombre = "Amplio Consumo"

        assert repr(dest) == "<Destino AC: Amplio Consumo>"


class TestRamaModel:
    """Tests para el modelo Rama."""

    def test_rama_creation(self):
        """Test creación básica de Rama."""
        rama = Rama()
        rama.nombre = "Productos Lácteos"

        assert rama.nombre == "Productos Lácteos"

    def test_rama_repr(self):
        """Test representación string."""
        rama = Rama()
        rama.nombre = "Carnes"

        assert repr(rama) == "<Rama Carnes>"


class TestMesModel:
    """Tests para el modelo Mes."""

    def test_mes_creation(self):
        """Test creación básica de Mes."""
        mes = Mes()
        mes.id = 1
        mes.nombre = "Enero"
        mes.sigla = "Ene"

        assert mes.id == 1
        assert mes.nombre == "Enero"
        assert mes.sigla == "Ene"

    def test_mes_repr(self):
        """Test representación string."""
        mes = Mes()
        mes.id = 3
        mes.nombre = "Marzo"

        assert repr(mes) == "<Mes 3: Marzo>"


class TestAnnoModel:
    """Tests para el modelo Anno."""

    def test_anno_creation(self):
        """Test creación básica de Anno."""
        anno = Anno()
        anno.anno = "2026"
        anno.activo = True

        assert anno.anno == "2026"
        assert anno.activo is True

    def test_anno_default_activo(self):
        """Test que activo tiene valor por defecto True."""
        anno = Anno(anno="2025", activo=True)

        assert anno.activo is True

    def test_anno_repr(self):
        """Test representación string."""
        anno = Anno()
        anno.anno = "2026"

        assert repr(anno) == "<Anno 2026>"

    def test_anno_to_dict(self):
        """Test serialización a dict."""
        anno = Anno()
        anno.anno = "2026"
        anno.activo = True

        data = anno.to_dict()

        assert data['anno'] == "2026"
        assert data['activo'] is True


class TestTipoESModel:
    """Tests para el modelo TipoES."""

    def test_tipo_es_creation(self):
        """Test creación básica de TipoES."""
        tipo = TipoES()
        tipo.nombre = "Análisis Visual"

        assert tipo.nombre == "Análisis Visual"

    def test_tipo_es_repr(self):
        """Test representación string."""
        tipo = TipoES()
        tipo.nombre = "Análisis Olfativo"

        assert repr(tipo) == "<TipoES Análisis Olfativo>"


class TestUnidadMedidaModel:
    """Tests para el modelo UnidadMedida."""

    def test_unidad_medida_creation(self):
        """Test creación básica de UnidadMedida."""
        um = UnidadMedida()
        um.codigo = "mg/L"
        um.nombre = "Miligramos por Litro"

        assert um.codigo == "mg/L"
        assert um.nombre == "Miligramos por Litro"

    def test_unidad_medida_repr(self):
        """Test representación string."""
        um = UnidadMedida()
        um.codigo = "g"
        um.nombre = "Gramos"

        assert repr(um) == "<UnidadMedida g: Gramos>"

    def test_unidad_medida_to_dict(self):
        """Test serialización a dict."""
        um = UnidadMedida()
        um.id = 1
        um.codigo = "mL"
        um.nombre = "Mililitros"

        data = um.to_dict()

        assert data['id'] == 1
        assert data['codigo'] == "mL"
        assert data['nombre'] == "Mililitros"
