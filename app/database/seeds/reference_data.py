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
