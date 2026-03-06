"""Seed data for master tables (Cliente, Fabrica, Producto).

This module populates the database with sample master data for testing
and development purposes.
"""

from app import db
from app.database.models import Cliente, Fabrica, Producto, Organismo, Provincia, Destino, Rama


def get_or_create_organismo(nombre):
    """Get existing organismo or create new one."""
    existing = Organismo.query.filter_by(nombre=nombre).first()
    if existing:
        return existing
    org = Organismo(nombre=nombre)
    db.session.add(org)
    db.session.flush()
    return org


def get_or_create_provincia(nombre, sigla):
    """Get existing provincia or create new one."""
    existing = Provincia.query.filter_by(nombre=nombre).first()
    if existing:
        return existing
    prov = Provincia(nombre=nombre, sigla=sigla)
    db.session.add(prov)
    db.session.flush()
    return prov


def get_or_create_destino(nombre, sigla):
    """Get existing destino or create new one."""
    existing = Destino.query.filter_by(nombre=nombre).first()
    if existing:
        return existing
    dest = Destino(nombre=nombre, sigla=sigla)
    db.session.add(dest)
    db.session.flush()
    return dest


def get_or_create_rama(nombre):
    """Get existing rama or create new one."""
    existing = Rama.query.filter_by(nombre=nombre).first()
    if existing:
        return existing
    rama = Rama(nombre=nombre)
    db.session.add(rama)
    db.session.flush()
    return rama


# Sample data for testing
SAMPLE_CLIENTES = [
    # Organismo 1: Empresas de la Carne
    {"codigo": "CLI001", "nombre": "Empresa Cárnica de Pinar del Río", "organismo": "CARNE"},
    {"codigo": "CLI002", "nombre": "Empresa de Productos Carnicos de La Habana", "organismo": "CARNE"},
    {"codigo": "CLI003", "nombre": "Empresa Avícola de Camagüey", "organismo": "AVICOLA"},
    {"codigo": "CLI004", "nombre": "Combinado Porcino de Ciego de Ávila", "organismo": "CARNE"},
    {"codigo": "CLI005", "nombre": "Empresa de Embutidos de Villa Clara", "organismo": "CARNE"},
    # Organismo 2: Empresas Lácteas
    {"codigo": "CLI006", "nombre": "Empresa de Productos Lácteos Pinar del Río", "organismo": "LACTEOS"},
    {"codigo": "CLI007", "nombre": "Empresa Láctea de La Habana", "organismo": "LACTEOS"},
    {"codigo": "CLI008", "nombre": "Combinado Lácteo de Camagüey", "organismo": "LACTEOS"},
    {"codigo": "CLI009", "nombre": "Empresa de Quesos de Villa Clara", "organismo": "LACTEOS"},
    {"codigo": "CLI010", "nombre": "Lácteos de Santiago de Cuba", "organismo": "LACTEOS"},
    # Organismo 3: Bebidas
    {"codigo": "CLI011", "nombre": "Empresa de Bebidas de La Habana", "organismo": "BEBIDAS"},
    {"codigo": "CLI012", "nombre": "Cervecería de Pinar del Río", "organismo": "BEBIDAS"},
    {"codigo": "CLI013", "nombre": "Refrescos de Villa Clara", "organismo": "BEBIDAS"},
    {"codigo": "CLI014", "nombre": "Embotelladora de Camagüey", "organismo": "BEBIDAS"},
    {"codigo": "CLI015", "nombre": "Industria Vinícola de Cuba", "organismo": "BEBIDAS"},
    # Organismo 4: Conservas
    {"codigo": "CLI016", "nombre": "Empresa de Conservas de La Habana", "organismo": "CONSERVAS"},
    {"codigo": "CLI017", "nombre": "Conservas de Vegetales de Villa Clara", "organismo": "CONSERVAS"},
    {"codigo": "CLI018", "nombre": "Frutas Selectas de Cuba", "organismo": "CONSERVAS"},
    {"codigo": "CLI019", "nombre": "Industrial de Fruits de Ciego de Ávila", "organismo": "CONSERVAS"},
    {"codigo": "CLI020", "nombre": "Conservas del Sur", "organismo": "CONSERVAS"},
]

SAMPLE_FABRICAS = [
    # Fabricas para CLI001 (Empresa Cárnica de Pinar del Río)
    {"cliente_codigo": "CLI001", "nombre": "Planta de Sacrificio Pinar", "provincia": "PRI"},
    {"cliente_codigo": "CLI001", "nombre": "Despostadora Los Palacitos", "provincia": "PRI"},
    {"cliente_codigo": "CLI001", "nombre": "Planta Embutidos San Juan", "provincia": "LTU"},
    # Fabricas para CLI002 (Productos Carnicos La Habana)
    {"cliente_codigo": "CLI002", "nombre": "Matadero Industrial La Habana", "provincia": "HAV"},
    {"cliente_codigo": "CLI002", "nombre": "Planta de Carnes Frescas", "provincia": "HAV"},
    {"cliente_codigo": "CLI002", "nombre": "Centro de Distribución Carnes", "provincia": "HAV"},
    # Fabricas para CLI006 (Lácteos Pinar del Río)
    {"cliente_codigo": "CLI006", "nombre": "Planta Láctea Pinar", "provincia": "PRI"},
    {"cliente_codigo": "CLI006", "nombre": "Centro de Recolección Leche", "provincia": "PRI"},
    # Fabricas para CLI007 (Lácteos La Habana)
    {"cliente_codigo": "CLI007", "nombre": "Planta Pasteurizadora Boyeros", "provincia": "HAV"},
    {"cliente_codigo": "CLI007", "nombre": "Planta de Yogur", "provincia": "HAV"},
    {"cliente_codigo": "CLI007", "nombre": "Planta de Quesos", "provincia": "HAV"},
    # Fabricas para CLI011 (Bebidas La Habana)
    {"cliente_codigo": "CLI011", "nombre": "Planta de Refrescos", "provincia": "HAV"},
    {"cliente_codigo": "CLI011", "nombre": "Planta de Jugos", "provincia": "HAV"},
    # Fabricas para CLI016 (Conservas La Habana)
    {"cliente_codigo": "CLI016", "nombre": "Planta de Conservas", "provincia": "HAV"},
    {"cliente_codigo": "CLI016", "nombre": "Planta de Concentrados", "provincia": "HAV"},
]

SAMPLE_PRODUCTOS = [
    {"codigo": "PROD001", "nombre": "Carne de Res Molida", "destino": "CF", "rama": "CARNE"},
    {"codigo": "PROD002", "nombre": "Carne de Cerdo Picada", "destino": "CF", "rama": "CARNE"},
    {"codigo": "PROD003", "nombre": "Pollo Entero", "destino": "CF", "rama": "AVICOLA"},
    {"codigo": "PROD004", "nombre": "Leche Entera UHT", "destino": "CF", "rama": "LACTEOS"},
    {"codigo": "PROD005", "nombre": "Yogur Natural", "destino": "CF", "rama": "LACTEOS"},
    {"codigo": "PROD006", "nombre": "Queso fresco", "destino": "CF", "rama": "LACTEOS"},
    {"codigo": "PROD007", "nombre": "Refresco de Naranja", "destino": "CF", "rama": "BEBIDAS"},
    {"codigo": "PROD008", "nombre": "Cerveza Lager", "destino": "CF", "rama": "BEBIDAS"},
    {"codigo": "PROD009", "nombre": "Conserva de Tomate", "destino": "CF", "rama": "CONSERVAS"},
    {"codigo": "PROD010", "nombre": "Mermelada de Mango", "destino": "CF", "rama": "CONSERVAS"},
    # Productos para alimentación colectiva
    {"codigo": "PROD011", "nombre": "Carne de Res para Cantinas", "destino": "AC", "rama": "CARNE"},
    {"codigo": "PROD012", "nombre": "Leche Descremada", "destino": "AC", "rama": "LACTEOS"},
    {"codigo": "PROD013", "nombre": "Refresco para Centros Escolares", "destino": "AC", "rama": "BEBIDAS"},
]


def seed_clientes():
    """Seed sample clientes."""
    print("  Seeding clientes...")
    count = 0
    for data in SAMPLE_CLIENTES:
        existing = Cliente.query.filter_by(codigo=data["codigo"]).first()
        if existing:
            continue
        org = get_or_create_organismo(data["organismo"])
        cliente = Cliente(
            codigo=data["codigo"],
            nombre=data["nombre"],
            organismo_id=org.id
        )
        db.session.add(cliente)
        count += 1
    db.session.commit()
    print(f"    Created {count} clientes")
    return count


def seed_fabricas():
    """Seed sample fabricas."""
    print("  Seeding fabricas...")
    count = 0
    for data in SAMPLE_FABRICAS:
        cliente = Cliente.query.filter_by(codigo=data["cliente_codigo"]).first()
        if not cliente:
            continue
        existing = Fabrica.query.filter_by(
            cliente_id=cliente.id,
            nombre=data["nombre"]
        ).first()
        if existing:
            continue
        provincia = get_or_create_provincia(data["provincia"], data["provincia"])
        fabrica = Fabrica(
            cliente_id=cliente.id,
            nombre=data["nombre"],
            provincia_id=provincia.id,
            activo=True
        )
        db.session.add(fabrica)
        count += 1
    db.session.commit()
    print(f"    Created {count} fabricas")
    return count


def seed_productos():
    """Seed sample productos."""
    print("  Seeding productos...")
    count = 0
    for data in SAMPLE_PRODUCTOS:
        existing = Producto.query.filter_by(codigo=data["codigo"]).first()
        if existing:
            continue
        destino = get_or_create_destino(data["destino"], data["destino"])
        rama = get_or_create_rama(data["rama"])
        producto = Producto(
            codigo=data["codigo"],
            nombre=data["nombre"],
            destino_id=destino.id,
            rama_id=rama.id,
            activo=True
        )
        db.session.add(producto)
        count += 1
    db.session.commit()
    print(f"    Created {count} productos")
    return count


def seed_all_master_data():
    """Seed all master data."""
    print("\n=== Seeding Master Data ===")
    seed_clientes()
    seed_fabricas()
    seed_productos()
    print("=== Master Data Complete ===\n")


if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_all_master_data()