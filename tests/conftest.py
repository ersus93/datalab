"""
conftest.py — Fixtures compartidos para todos los tests de DataLab.

Provee:
- app: instancia Flask en modo testing (SQLite en memoria)
- db: base de datos de test con tablas creadas
- client: cliente HTTP de Flask para tests de integración
- Factories de entidades para tests unitarios
"""
import pytest

from app import create_app
from app.core.infrastructure.database import db as _db
from app.database.models.user import User, UserRole
from app.database.models.recent_search import RecentSearch
from app.database.models.reference import (
    Area, Organismo, Provincia, Destino, Rama,
    Mes, Anno, TipoES, UnidadMedida
)
from app.database.models.cliente import Cliente
from app.database.models.fabrica import Fabrica
from app.database.models.producto import Producto
from app.database.models.pedido import Pedido
from app.database.models.orden_trabajo import OrdenTrabajo
from app.database.models.entrada import Entrada


# ---------------------------------------------------------------------------
# App & DB fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope='session')
def app():
    """Crea una instancia de la app configurada para testing."""
    app = create_app('testing')
    return app


@pytest.fixture(scope='session')
def db(app):
    """Crea las tablas en la base de datos de testing (SQLite en memoria)."""
    with app.app_context():
        _db.create_all()
        _seed_reference_data()
        yield _db
        _db.drop_all()


@pytest.fixture(scope='function')
def db_session(db, app):
    """Provee una sesión de base de datos con rollback al finalizar cada test."""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()

        db.session.bind = connection

        yield db.session

        db.session.remove()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope='function')
def client(app, db):
    """Cliente HTTP de Flask para tests de integración."""
    with app.app_context():
        with app.test_client() as c:
            yield c


# ---------------------------------------------------------------------------
# Auth fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope='function')
def admin_user(db_session):
    """Crea y devuelve un usuario administrador de test."""
    user = User(
        username='test_admin',
        email='admin@test.datalab.local',
        nombre_completo='Admin Test',
        role=UserRole.ADMIN,
        activo=True
    )
    user.set_password('TestAdmin1234!')
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture(scope='function')
def manager_user(db_session):
    """Crea y devuelve un usuario gerente de laboratorio de test."""
    user = User(
        username='test_manager',
        email='manager@test.datalab.local',
        nombre_completo='Manager Test',
        role=UserRole.LABORATORY_MANAGER,
        activo=True
    )
    user.set_password('TestManager1234!')
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture(scope='function')
def technician_user(db_session):
    """Crea y devuelve un usuario técnico de test."""
    user = User(
        username='test_tech',
        email='tech@test.datalab.local',
        nombre_completo='Técnico Test',
        role=UserRole.TECHNICIAN,
        activo=True
    )
    user.set_password('TestTech1234!')
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture(scope='function')
def logged_in_admin(client, admin_user, app):
    """Cliente HTTP con sesión de admin activa."""
    with app.app_context():
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_user.id)
            sess['_fresh'] = True
    yield client


# ---------------------------------------------------------------------------
# Entity fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope='function')
def sample_organismo(db_session):
    """Organismo de prueba."""
    org = Organismo(nombre='Organismo Test')
    db_session.add(org)
    db_session.flush()
    return org


@pytest.fixture(scope='function')
def sample_cliente(db_session, sample_organismo):
    """Cliente de prueba."""
    cliente = Cliente(
        codigo='CLI-TEST-01',
        nombre='Cliente de Prueba S.A.',
        organismo_id=sample_organismo.id,
        tipo_cliente=1,
        activo=True
    )
    db_session.add(cliente)
    db_session.flush()
    return cliente


@pytest.fixture(scope='function')
def sample_provincia(db_session):
    """Provincia de prueba."""
    prov = Provincia(nombre='La Habana Test', sigla='LHT')
    db_session.add(prov)
    db_session.flush()
    return prov


@pytest.fixture(scope='function')
def sample_fabrica(db_session, sample_cliente, sample_provincia):
    """Fábrica de prueba."""
    from app.database.models.fabrica import Fabrica as FabricaModel
    fab = FabricaModel(
        nombre='Fábrica Test',
        cliente_id=sample_cliente.id,
        provincia_id=sample_provincia.id,
        activo=True
    )
    db_session.add(fab)
    db_session.flush()
    return fab


@pytest.fixture(scope='function')
def sample_producto(db_session):
    """Producto de prueba."""
    prod = Producto(
        codigo='PROD-TEST-01',
        nombre='Producto Test',
        activo=True
    )
    db_session.add(prod)
    db_session.flush()
    return prod


@pytest.fixture(scope='function')
def sample_unidad_medida(db_session):
    """Unidad de medida de prueba."""
    um = UnidadMedida(codigo='KG', nombre='Kilogramo')
    db_session.add(um)
    db_session.flush()
    return um


@pytest.fixture(scope='function')
def sample_orden_trabajo(db_session, sample_cliente, admin_user):
    """Orden de trabajo de prueba."""
    ot = OrdenTrabajo(
        nro_ofic='OT-TEST-2026-001',
        codigo='OT-T-001',
        cliente_id=sample_cliente.id,
        descripcion='OT de prueba'
    )
    db_session.add(ot)
    db_session.flush()
    return ot


@pytest.fixture(scope='function')
def sample_pedido(db_session, sample_cliente, sample_producto, sample_orden_trabajo, sample_unidad_medida):
    """Pedido de prueba."""
    pedido = Pedido(
        codigo='PED-TEST-001',
        cliente_id=sample_cliente.id,
        producto_id=sample_producto.id,
        orden_trabajo_id=sample_orden_trabajo.id,
        unidad_medida_id=sample_unidad_medida.id
    )
    db_session.add(pedido)
    db_session.flush()
    return pedido


@pytest.fixture(scope='function')
def sample_entrada(db_session, sample_pedido, sample_producto, sample_fabrica,
                   sample_cliente, sample_unidad_medida):
    """Entrada de muestra de prueba."""
    entrada = Entrada(
        codigo='ENT-TEST-001',
        lote='A-1234',
        pedido_id=sample_pedido.id,
        producto_id=sample_producto.id,
        fabrica_id=sample_fabrica.id,
        cliente_id=sample_cliente.id,
        unidad_medida_id=sample_unidad_medida.id,
        cantidad_recib=100,
        cantidad_entreg=0
    )
    db_session.add(entrada)
    db_session.flush()
    return entrada


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _seed_reference_data():
    """Puebla datos de referencia mínimos para tests."""
    # Solo crear si no existen
    if not Area.query.first():
        areas = [
            Area(nombre='Físico-Químico', sigla='FQ'),
            Area(nombre='Microbiología', sigla='MB'),
            Area(nombre='Evaluación Sensorial', sigla='ES'),
            Area(nombre='Otros Servicios', sigla='OS'),
        ]
        _db.session.add_all(areas)

    if not Mes.query.first():
        meses = [
            Mes(nombre='Enero', sigla='ENE'),
            Mes(nombre='Febrero', sigla='FEB'),
            Mes(nombre='Marzo', sigla='MAR'),
            Mes(nombre='Abril', sigla='ABR'),
            Mes(nombre='Mayo', sigla='MAY'),
            Mes(nombre='Junio', sigla='JUN'),
            Mes(nombre='Julio', sigla='JUL'),
            Mes(nombre='Agosto', sigla='AGO'),
            Mes(nombre='Septiembre', sigla='SEP'),
            Mes(nombre='Octubre', sigla='OCT'),
            Mes(nombre='Noviembre', sigla='NOV'),
            Mes(nombre='Diciembre', sigla='DIC'),
        ]
        _db.session.add_all(meses)

    if not Anno.query.first():
        for y in range(2020, 2028):
            _db.session.add(Anno(anno=str(y), activo=True))

    _db.session.commit()
