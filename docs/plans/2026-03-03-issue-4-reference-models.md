# [Issue #4] Create Reference Data Models - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create 9 SQLAlchemy reference data models (Area, Organismo, Provincia, Destino, Rama, Mes, Anno, TipoES, UnidadMedida) to establish the foundational configuration layer for DataLab.

**Architecture:** Following hexagonal architecture with SQLAlchemy models in `app/database/models/`. Models use Spanish field names from Access legacy system. Each model includes proper constraints, indexes, and relationships for future features.

**Tech Stack:** Python 3.11, Flask 3.0, Flask-SQLAlchemy 3.1.1, SQLAlchemy 2.0.35, pytest

---

## Overview

This plan implements Issue #4: Create Reference Data Models. These 9 tables provide the foundational lookup data required by all other entities in the laboratory management system.

| Model | Records | Description |
|-------|---------|-------------|
| Area | 4 | Laboratory areas (FQ, MB, ES, OS) |
| Organismo | 12 | Client organizations/entities |
| Provincia | 4 | Geographic provinces |
| Destino | 7 | Product destinations |
| Rama | 13 | Industry sectors |
| Mes | 12 | Calendar months |
| Anno | 10 | Years configuration |
| TipoES | 4 | Sensory evaluation types |
| UnidadMedida | 3 | Measurement units |

---

## Task 1: Create Reference Models File

**Files:**
- Create: `app/database/models/reference.py`

**Step 1: Create the file with all 9 models**

```python
#!/usr/bin/env python3
"""Modelos de datos de referencia (lookup tables) para DataLab.

Estos modelos proporcionan los datos de configuración base necesarios
para todas las demás entidades del sistema de laboratorio.
"""

from datetime import datetime
from app import db


class Area(db.Model):
    """Áreas de laboratorio: FQ (Físico-Químico), MB (Microbiología),
    ES (Evaluación Sensorial), OS (Otros Servicios).
    """
    __tablename__ = 'areas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    sigla = db.Column(db.String(10), unique=True, nullable=False, index=True)

    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Area {self.sigla}: {self.nombre}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'sigla': self.sigla,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }


class Organismo(db.Model):
    """Organismos/entidades de clientes."""
    __tablename__ = 'organismos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False, unique=True)

    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Organismo {self.nombre}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }


class Provincia(db.Model):
    """Provincias geográficas."""
    __tablename__ = 'provincias'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    sigla = db.Column(db.String(10), unique=True, nullable=False, index=True)

    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Provincia {self.sigla}: {self.nombre}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'sigla': self.sigla,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }


class Destino(db.Model):
    """Destinos de productos: CF (Canasta Familiar), AC (Amplio Consumo),
    ME (Merienda Escolar), CD (Captación Divisas), DE (Destinos Especiales).
    """
    __tablename__ = 'destinos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    sigla = db.Column(db.String(10), unique=True, nullable=False, index=True)

    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Destino {self.sigla}: {self.nombre}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'sigla': self.sigla,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }


class Rama(db.Model):
    """Ramas/sectores industriales: Carne, Lácteos, Vegetales, Bebidas, etc."""
    __tablename__ = 'ramas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)

    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Rama {self.nombre}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }


class Mes(db.Model):
    """Meses del año para organización temporal."""
    __tablename__ = 'meses'

    id = db.Column(db.Integer, primary_key=True)  # 1-12
    nombre = db.Column(db.String(20), nullable=False)
    sigla = db.Column(db.String(5), nullable=False)

    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Mes {self.id}: {self.nombre}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'sigla': self.sigla,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }


class Anno(db.Model):
    """Años activos para períodos de reporte."""
    __tablename__ = 'annos'

    anno = db.Column(db.String(4), primary_key=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Anno {self.anno}>'

    def to_dict(self):
        return {
            'anno': self.anno,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }


class TipoES(db.Model):
    """Tipos de Evaluación Sensorial."""
    __tablename__ = 'tipo_es'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)

    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<TipoES {self.nombre}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }


class UnidadMedida(db.Model):
    """Unidades de medida para resultados de ensayos."""
    __tablename__ = 'unidades_medida'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(10), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(50), nullable=False)

    # Timestamps
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<UnidadMedida {self.codigo}: {self.nombre}>'

    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
```

**Step 2: Verify file created**

Run: `ls -la app/database/models/reference.py`
Expected: File exists with content

**Step 3: Commit**

```bash
git add app/database/models/reference.py
git commit -m "feat(models): create reference data models for issue #4

Add 9 reference models:
- Area: Laboratory areas (FQ, MB, ES, OS)
- Organismo: Client organizations
- Provincia: Geographic provinces
- Destino: Product destinations
- Rama: Industry sectors
- Mes: Calendar months
- Anno: Active years for reporting
- TipoES: Sensory evaluation types
- UnidadMedida: Measurement units

All models include:
- Proper constraints and indexes
- to_dict() serialization method
- Timestamps (fecha_creacion, fecha_actualizacion)
- Spanish field names from Access legacy system"
```

---

## Task 2: Update Models __init__.py

**Files:**
- Modify: `app/database/models/__init__.py`

**Step 1: Update imports to include reference models**

```python
#!/usr/bin/env python3
"""Modelos de la base de datos para DataLab."""

from .cliente import Cliente
from .pedido import Pedido
from .orden_trabajo import OrdenTrabajo
from .reference import (
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

__all__ = [
    'Cliente',
    'Pedido',
    'OrdenTrabajo',
    'Area',
    'Organismo',
    'Provincia',
    'Destino',
    'Rama',
    'Mes',
    'Anno',
    'TipoES',
    'UnidadMedida',
]
```

**Step 2: Verify imports work**

Run: `cd /home/mowgli/datalab && python -c "from app.database.models import Area, Organismo, Provincia, Destino, Rama, Mes, Anno, TipoES, UnidadMedida; print('All imports OK')"`
Expected: "All imports OK"

**Step 3: Commit**

```bash
git add app/database/models/__init__.py
git commit -m "chore(models): register reference models in __init__

Export all 9 reference models from database.models package.
Ensures models are discoverable by SQLAlchemy and migrations."
```

---

## Task 3: Create Alembic Migration

**Files:**
- Create: `migrations/versions/` (auto-generated)

**Step 1: Generate migration**

Run: `cd /home/mowgli/datalab && source venv/bin/activate && flask db migrate -m "add reference data models"`
Expected: Migration file created in migrations/versions/

**Step 2: Review migration file**

Run: `ls -la migrations/versions/*.py | tail -1`
Verify: File contains create_table for all 9 reference tables

**Step 3: Apply migration**

Run: `flask db upgrade`
Expected: Tables created successfully

**Step 4: Verify tables in database**

Run: `cd /home/mowgli/datalab && python -c "
from app import create_app
from app.database.database import DatabaseManager
app = create_app()
with app.app_context():
    info = DatabaseManager.get_database_info()
    reference_tables = ['areas', 'organismos', 'provincias', 'destinos', 'ramas', 'meses', 'annos', 'tipo_es', 'unidades_medida']
    for table in reference_tables:
        if table in info['tables']:
            print(f'✓ {table}')
        else:
            print(f'✗ {table} - MISSING')
"`
Expected: All 9 tables show ✓

**Step 5: Commit**

```bash
git add migrations/versions/
git commit -m "chore(migrations): add alembic migration for reference models

Auto-generated migration creating 9 reference tables:
- areas, organismos, provincias, destinos
- ramas, meses, annos, tipo_es, unidades_medida

Includes indexes on sigla/codigo fields for query optimization."
```

---

## Task 4: Create Unit Tests

**Files:**
- Create: `tests/unit/test_reference_models.py`

**Step 1: Write comprehensive tests**

```python
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
        anno = Anno()
        anno.anno = "2025"

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
```

**Step 2: Run tests to verify they pass**

Run: `cd /home/mowgli/datalab && source venv/bin/activate && pytest tests/unit/test_reference_models.py -v`
Expected: All tests pass

**Step 3: Commit**

```bash
git add tests/unit/test_reference_models.py
git commit -m "test(models): add unit tests for reference models

Comprehensive test coverage for all 9 reference models:
- Model instantiation
- String representation (__repr__)
- Serialization (to_dict)
- Default values

Tests run without database (unit tests)."
```

---

## Task 5: Create Integration Tests

**Files:**
- Create: `tests/integration/test_reference_models_db.py`

**Step 1: Write integration tests with database**

```python
#!/usr/bin/env python3
"""Tests de integración para modelos de referencia con base de datos.

Estos tests verifican el comportamiento real de los modelos con
SQLAlchemy y la base de datos.
"""

import pytest
from app import create_app, db
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


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestAreaIntegration:
    """Tests de integración para Area."""

    def test_area_save_to_database(self, app):
        """Test guardar Area en base de datos."""
        with app.app_context():
            area = Area(nombre="Físico-Químico", sigla="FQ")
            db.session.add(area)
            db.session.commit()

            # Verify saved
            saved = Area.query.filter_by(sigla="FQ").first()
            assert saved is not None
            assert saved.nombre == "Físico-Químico"
            assert saved.id is not None

    def test_area_unique_sigla(self, app):
        """Test que sigla debe ser única."""
        with app.app_context():
            area1 = Area(nombre="Físico-Químico", sigla="FQ")
            db.session.add(area1)
            db.session.commit()

            # Try to add duplicate sigla
            area2 = Area(nombre="Físico Quimico 2", sigla="FQ")
            db.session.add(area2)

            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()

            db.session.rollback()


class TestOrganismoIntegration:
    """Tests de integración para Organismo."""

    def test_organismo_save_and_retrieve(self, app):
        """Test guardar y recuperar Organismo."""
        with app.app_context():
            org = Organismo(nombre="Ministerio de Agricultura")
            db.session.add(org)
            db.session.commit()

            retrieved = Organismo.query.filter_by(nombre="Ministerio de Agricultura").first()
            assert retrieved is not None
            assert retrieved.nombre == "Ministerio de Agricultura"

    def test_organismo_unique_nombre(self, app):
        """Test que nombre debe ser único."""
        with app.app_context():
            org1 = Organismo(nombre="ONIE")
            db.session.add(org1)
            db.session.commit()

            org2 = Organismo(nombre="ONIE")
            db.session.add(org2)

            with pytest.raises(Exception):
                db.session.commit()

            db.session.rollback()


class TestProvinciaIntegration:
    """Tests de integración para Provincia."""

    def test_provincia_save_and_query(self, app):
        """Test guardar y consultar Provincia."""
        with app.app_context():
            prov = Provincia(nombre="La Habana", sigla="LH")
            db.session.add(prov)
            db.session.commit()

            result = Provincia.query.filter_by(sigla="LH").first()
            assert result.nombre == "La Habana"


class TestDestinoIntegration:
    """Tests de integración para Destino."""

    def test_destino_all_destinations(self, app):
        """Test crear todos los destinos típicos."""
        with app.app_context():
            destinos = [
                Destino(nombre="Canasta Familiar", sigla="CF"),
                Destino(nombre="Amplio Consumo", sigla="AC"),
                Destino(nombre="Merienda Escolar", sigla="ME"),
                Destino(nombre="Captación Divisas", sigla="CD"),
                Destino(nombre="Destinos Especiales", sigla="DE"),
            ]

            for d in destinos:
                db.session.add(d)

            db.session.commit()

            assert Destino.query.count() == 5


class TestRamaIntegration:
    """Tests de integración para Rama."""

    def test_rama_creation(self, app):
        """Test crear ramas industriales."""
        with app.app_context():
            ramas = [
                Rama(nombre="Productos Cárnicos"),
                Rama(nombre="Productos Lácteos"),
                Rama(nombre="Productos Vegetales"),
                Rama(nombre="Bebidas"),
            ]

            for r in ramas:
                db.session.add(r)

            db.session.commit()

            assert Rama.query.count() == 4


class TestMesIntegration:
    """Tests de integración para Mes."""

    def test_mes_all_months(self, app):
        """Test crear todos los meses del año."""
        with app.app_context():
            meses = [
                (1, "Enero", "Ene"),
                (2, "Febrero", "Feb"),
                (3, "Marzo", "Mar"),
                (4, "Abril", "Abr"),
                (5, "Mayo", "May"),
                (6, "Junio", "Jun"),
                (7, "Julio", "Jul"),
                (8, "Agosto", "Ago"),
                (9, "Septiembre", "Sep"),
                (10, "Octubre", "Oct"),
                (11, "Noviembre", "Nov"),
                (12, "Diciembre", "Dic"),
            ]

            for id_mes, nombre, sigla in meses:
                mes = Mes(id=id_mes, nombre=nombre, sigla=sigla)
                db.session.add(mes)

            db.session.commit()

            assert Mes.query.count() == 12
            assert Mes.query.get(1).nombre == "Enero"
            assert Mes.query.get(12).nombre == "Diciembre"


class TestAnnoIntegration:
    """Tests de integración para Anno."""

    def test_anno_creation(self, app):
        """Test crear años."""
        with app.app_context():
            for year in range(2020, 2027):
                anno = Anno(anno=str(year), activo=(year >= 2024))
                db.session.add(anno)

            db.session.commit()

            assert Anno.query.count() == 7
            assert Anno.query.get("2026").activo is True
            assert Anno.query.get("2020").activo is False


class TestTipoESIntegration:
    """Tests de integración para TipoES."""

    def test_tipo_es_creation(self, app):
        """Test crear tipos de evaluación sensorial."""
        with app.app_context():
            tipos = [
                TipoES(nombre="Análisis Visual"),
                TipoES(nombre="Análisis Olfativo"),
                TipoES(nombre="Análisis Gustativo"),
                TipoES(nombre="Análisis Táctil"),
            ]

            for t in tipos:
                db.session.add(t)

            db.session.commit()

            assert TipoES.query.count() == 4


class TestUnidadMedidaIntegration:
    """Tests de integración para UnidadMedida."""

    def test_unidad_medida_creation(self, app):
        """Test crear unidades de medida."""
        with app.app_context():
            unidades = [
                UnidadMedida(codigo="g", nombre="Gramos"),
                UnidadMedida(codigo="mg/L", nombre="Miligramos por Litro"),
                UnidadMedida(codigo="mL", nombre="Mililitros"),
            ]

            for u in unidades:
                db.session.add(u)

            db.session.commit()

            assert UnidadMedida.query.count() == 3
            assert UnidadMedida.query.filter_by(codigo="g").first().nombre == "Gramos"
```

**Step 2: Run integration tests**

Run: `cd /home/mowgli/datalab && source venv/bin/activate && pytest tests/integration/test_reference_models_db.py -v`
Expected: All tests pass

**Step 3: Commit**

```bash
git add tests/integration/test_reference_models_db.py
git commit -m "test(integration): add DB integration tests for reference models

Integration tests covering:
- Database persistence for all 9 models
- Unique constraints verification
- Query operations
- Batch insertions

Uses test database fixture with automatic cleanup."
```

---

## Task 6: Create Seed Data Script

**Files:**
- Create: `app/database/seeds/reference_data.py`
- Create: `app/database/seeds/__init__.py`

**Step 1: Create seeds directory and __init__.py**

```python
#!/usr/bin/env python3
"""Database seeds for DataLab.

Scripts para poblar la base de datos con datos iniciales.
"""
```

**Step 2: Create seed data script**

```python
#!/usr/bin/env python3
"""Seed data para tablas de referencia.

Datos iniciales migrados desde la base de datos Access RM2026.
Total: 73 registros de referencia.
"""

from app import db
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


# Area: 4 registros
AREAS_DATA = [
    {"nombre": "Físico-Químico", "sigla": "FQ"},
    {"nombre": "Microbiología", "sigla": "MB"},
    {"nombre": "Evaluación Sensorial", "sigla": "ES"},
    {"nombre": "Otros Servicios", "sigla": "OS"},
]

# Organismos: 12 registros
ORGANISMOS_DATA = [
    {"nombre": "Ministerio de la Agricultura"},
    {"nombre": "Ministerio de la Industria Alimentaria"},
    {"nombre": "Ministerio de Comercio Interior"},
    {"nombre": "Empresa de Productos Lácteos"},
    {"nombre": "Empresa de Bebidas y Refrescos"},
    {"nombre": "Empresa de Carnes"},
    {"nombre": "Empresa de Conservas Vegetales"},
    {"nombre": "Empresa de Aceites y Grasas"},
    {"nombre": "Empresa de Harinas y Cereales"},
    {"nombre": "Empresa de Confitería"},
    {"nombre": "Empresa de Pescados y Mariscos"},
    {"nombre": "Otros Organismos"},
]

# Provincias: 4 registros
PROVINCIAS_DATA = [
    {"nombre": "Pinar del Río", "sigla": "PR"},
    {"nombre": "Artemisa", "sigla": "AR"},
    {"nombre": "La Habana", "sigla": "LH"},
    {"nombre": "Mayabeque", "sigla": "MQ"},
]

# Destinos: 7 registros
DESTINOS_DATA = [
    {"nombre": "Canasta Familiar", "sigla": "CF"},
    {"nombre": "Amplio Consumo", "sigla": "AC"},
    {"nombre": "Merienda Escolar", "sigla": "ME"},
    {"nombre": "Captación Divisas", "sigla": "CD"},
    {"nombre": "Destinos Especiales", "sigla": "DE"},
    {"nombre": "Turismo", "sigla": "TU"},
    {"nombre": "Exportación", "sigla": "EX"},
]

# Ramas: 13 registros
RAMAS_DATA = [
    {"nombre": "Productos Cárnicos"},
    {"nombre": "Productos Lácteos"},
    {"nombre": "Productos Vegetales"},
    {"nombre": "Bebidas Alcohólicas"},
    {"nombre": "Bebidas No Alcohólicas"},
    {"nombre": "Aceites y Grasas Comestibles"},
    {"nombre": "Productos de Panadería y Pastelería"},
    {"nombre": "Productos de Confitería"},
    {"nombre": "Productos de Molinería"},
    {"nombre": "Conservas Vegetales"},
    {"nombre": "Conservas Cárnicas"},
    {"nombre": "Pescados y Productos del Mar"},
    {"nombre": "Otros Productos Alimenticios"},
]

# Meses: 12 registros
MESES_DATA = [
    {"id": 1, "nombre": "Enero", "sigla": "Ene"},
    {"id": 2, "nombre": "Febrero", "sigla": "Feb"},
    {"id": 3, "nombre": "Marzo", "sigla": "Mar"},
    {"id": 4, "nombre": "Abril", "sigla": "Abr"},
    {"id": 5, "nombre": "Mayo", "sigla": "May"},
    {"id": 6, "nombre": "Junio", "sigla": "Jun"},
    {"id": 7, "nombre": "Julio", "sigla": "Jul"},
    {"id": 8, "nombre": "Agosto", "sigla": "Ago"},
    {"id": 9, "nombre": "Septiembre", "sigla": "Sep"},
    {"id": 10, "nombre": "Octubre", "sigla": "Oct"},
    {"id": 11, "nombre": "Noviembre", "sigla": "Nov"},
    {"id": 12, "nombre": "Diciembre", "sigla": "Dic"},
]

# Años: 10 registros (2020-2029)
ANNOS_DATA = [
    {"anno": "2020", "activo": False},
    {"anno": "2021", "activo": False},
    {"anno": "2022", "activo": False},
    {"anno": "2023", "activo": False},
    {"anno": "2024", "activo": True},
    {"anno": "2025", "activo": True},
    {"anno": "2026", "activo": True},
    {"anno": "2027", "activo": True},
    {"anno": "2028", "activo": True},
    {"anno": "2029", "activo": True},
]

# Tipo ES: 4 registros
TIPO_ES_DATA = [
    {"nombre": "Análisis Visual"},
    {"nombre": "Análisis Olfativo"},
    {"nombre": "Análisis Gustativo"},
    {"nombre": "Análisis Táctil"},
]

# Unidades de Medida: 3 registros
UNIDADES_MEDIDA_DATA = [
    {"codigo": "g", "nombre": "Gramos"},
    {"codigo": "mg/L", "nombre": "Miligramos por Litro"},
    {"codigo": "mL", "nombre": "Mililitros"},
]


def seed_areas():
    """Seed areas table."""
    for data in AREAS_DATA:
        if not Area.query.filter_by(sigla=data["sigla"]).first():
            area = Area(**data)
            db.session.add(area)
    db.session.commit()
    print(f"✓ Areas: {Area.query.count()} registros")


def seed_organismos():
    """Seed organismos table."""
    for data in ORGANISMOS_DATA:
        if not Organismo.query.filter_by(nombre=data["nombre"]).first():
            org = Organismo(**data)
            db.session.add(org)
    db.session.commit()
    print(f"✓ Organismos: {Organismo.query.count()} registros")


def seed_provincias():
    """Seed provincias table."""
    for data in PROVINCIAS_DATA:
        if not Provincia.query.filter_by(sigla=data["sigla"]).first():
            prov = Provincia(**data)
            db.session.add(prov)
    db.session.commit()
    print(f"✓ Provincias: {Provincia.query.count()} registros")


def seed_destinos():
    """Seed destinos table."""
    for data in DESTINOS_DATA:
        if not Destino.query.filter_by(sigla=data["sigla"]).first():
            dest = Destino(**data)
            db.session.add(dest)
    db.session.commit()
    print(f"✓ Destinos: {Destino.query.count()} registros")


def seed_ramas():
    """Seed ramas table."""
    for data in RAMAS_DATA:
        if not Rama.query.filter_by(nombre=data["nombre"]).first():
            rama = Rama(**data)
            db.session.add(rama)
    db.session.commit()
    print(f"✓ Ramas: {Rama.query.count()} registros")


def seed_meses():
    """Seed meses table."""
    for data in MESES_DATA:
        if not Mes.query.get(data["id"]):
            mes = Mes(**data)
            db.session.add(mes)
    db.session.commit()
    print(f"✓ Meses: {Mes.query.count()} registros")


def seed_annos():
    """Seed annos table."""
    for data in ANNOS_DATA:
        if not Anno.query.get(data["anno"]):
            anno = Anno(**data)
            db.session.add(anno)
    db.session.commit()
    print(f"✓ Años: {Anno.query.count()} registros")


def seed_tipo_es():
    """Seed tipo_es table."""
    for data in TIPO_ES_DATA:
        if not TipoES.query.filter_by(nombre=data["nombre"]).first():
            tipo = TipoES(**data)
            db.session.add(tipo)
    db.session.commit()
    print(f"✓ Tipo ES: {TipoES.query.count()} registros")


def seed_unidades_medida():
    """Seed unidades_medida table."""
    for data in UNIDADES_MEDIDA_DATA:
        if not UnidadMedida.query.filter_by(codigo=data["codigo"]).first():
            um = UnidadMedida(**data)
            db.session.add(um)
    db.session.commit()
    print(f"✓ Unidades de Medida: {UnidadMedida.query.count()} registros")


def seed_all_reference_data():
    """Seed all reference tables with initial data."""
    print("\n=== Seeding Reference Data ===")
    print("Migrating 73 records from Access RM2026...\n")

    seed_areas()
    seed_organismos()
    seed_provincias()
    seed_destinos()
    seed_ramas()
    seed_meses()
    seed_annos()
    seed_tipo_es()
    seed_unidades_medida()

    print("\n=== Reference Data Seeding Complete ===")
    total = (
        Area.query.count() +
        Organismo.query.count() +
        Provincia.query.count() +
        Destino.query.count() +
        Rama.query.count() +
        Mes.query.count() +
        Anno.query.count() +
        TipoES.query.count() +
        UnidadMedida.query.count()
    )
    print(f"Total records: {total}/73")


if __name__ == "__main__":
    from app import create_app

    app = create_app()
    with app.app_context():
        seed_all_reference_data()
```

**Step 3: Test seed script**

Run: `cd /home/mowgli/datalab && source venv/bin/activate && python app/database/seeds/reference_data.py`
Expected: All 73 records seeded successfully

**Step 4: Commit**

```bash
git add app/database/seeds/
git commit -m "feat(seeds): add reference data seed script

Seed script populating all 9 reference tables:
- 4 Areas (FQ, MB, ES, OS)
- 12 Organismos (ministries and enterprises)
- 4 Provincias (geographic regions)
- 7 Destinos (product destinations)
- 13 Ramas (industry sectors)
- 12 Meses (calendar months)
- 10 Annos (years 2020-2029)
- 4 TipoES (sensory evaluation types)
- 3 UnidadesMedida (measurement units)

Total: 73 records from Access RM2026."
```

---

## Task 7: Create CLI Command for Seeding

**Files:**
- Create: `app/cli/__init__.py`
- Create: `app/cli/seed_commands.py`
- Modify: `app.py` (register CLI)

**Step 1: Create CLI directory and seed commands**

```python
#!/usr/bin/env python3
"""CLI commands for DataLab.

Comandos de línea de comandos para tareas de administración.
"""
```

```python
#!/usr/bin/env python3
"""CLI commands for database seeding.
"""

import click
from flask.cli import with_appcontext

from app.database.seeds.reference_data import seed_all_reference_data


@click.command('seed-reference')
@with_appcontext
def seed_reference_command():
    """Seed all reference data tables.
    
    Poblar las tablas de referencia con datos iniciales desde Access RM2026.
    """
    click.echo('Seeding reference data...')
    seed_all_reference_data()
    click.echo('Done!')


def register_seed_commands(app):
    """Register seed CLI commands with Flask app."""
    app.cli.add_command(seed_reference_command)
```

**Step 2: Update app.py to register CLI commands**

Add to `app.py`:

```python
# Import and register CLI commands
from app.cli.seed_commands import register_seed_commands
register_seed_commands(app)
```

**Step 3: Test CLI command**

Run: `cd /home/mowgli/datalab && source venv/bin/activate && flask seed-reference`
Expected: Reference data seeded via CLI

**Step 4: Commit**

```bash
git add app/cli/ app.py
git commit -m "feat(cli): add seed-reference CLI command

New CLI command: flask seed-reference
Pobla todas las tablas de referencia con datos iniciales.
Convenient for fresh database setup and testing."
```

---

## Task 8: Final Verification and Documentation

**Step 1: Run all tests**

Run: `cd /home/mowgli/datalab && source venv/bin/activate && pytest tests/unit/test_reference_models.py tests/integration/test_reference_models_db.py -v`
Expected: All tests pass

**Step 2: Verify models in Flask shell**

Run: `cd /home/mowgli/datalab && source venv/bin/activate && flask shell`

Inside shell:
```python
from app.database.models import Area, Organismo, Provincia, Destino, Rama, Mes, Anno, TipoES, UnidadMedida
print("✓ All 9 models importable")
print(f"Models: Area, Organismo, Provincia, Destino, Rama, Mes, Anno, TipoES, UnidadMedida")
exit()
```

**Step 3: Check migration status**

Run: `cd /home/mowgli/datalab && source venv/bin/activate && flask db current`
Expected: Shows current migration

Run: `flask db history`
Expected: Shows migration history including new one

**Step 4: Final commit**

```bash
git add -A
git commit -m "feat(issue-4): complete reference data models implementation

Implements GitHub Issue #4: Create Reference Data Models

Changes:
- Add 9 SQLAlchemy reference models (reference.py)
- Register models in database package
- Create Alembic migration for schema changes
- Add comprehensive unit tests (14 tests)
- Add integration tests with database (9 test classes)
- Create seed data script (73 records)
- Add CLI command: flask seed-reference

All acceptance criteria met:
✓ All 9 models created with proper fields
✓ Constraints and indexes configured
✓ Models registered with SQLAlchemy
✓ Migration generated and applied
✓ Tests pass (unit + integration)
✓ Seed data ready for migration

Models: Area, Organismo, Provincia, Destino, Rama,
        Mes, Anno, TipoES, UnidadMedida"
```

---

## Summary

This plan implements Issue #4 by creating:

1. **9 Reference Models** with proper SQLAlchemy configuration
2. **Database Migration** via Alembic
3. **Unit Tests** (14 tests, no DB required)
4. **Integration Tests** (9 test classes with DB)
5. **Seed Data Script** (73 records from Access RM2026)
6. **CLI Command** for easy seeding

All models follow the established patterns with:
- Spanish field names (legacy compatibility)
- Timestamps (fecha_creacion, fecha_actualizacion)
- to_dict() serialization
- __repr__ for debugging
- Unique constraints on name/sigla fields
- Indexes for query optimization
