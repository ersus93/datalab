#!/usr/bin/env python3
"""Tests unitarios para el modelo OrdenTrabajo."""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app import create_app, db
from app.database.models.orden_trabajo import OrdenTrabajo, OTStatus
from app.database.models.cliente import Cliente
from app.database.models.pedido import Pedido, PedidoStatus
from app.database.models.producto import Producto


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


@pytest.mark.skip(reason="Requiere refactorización de fixtures")
class TestOrdenTrabajoModel:
    """Tests para el modelo OrdenTrabajo."""

    # Creation Tests
    def test_crear_orden_trabajo(self, app, test_cliente):
        """Test crear una orden de trabajo correctamente."""
        with app.app_context():
            cliente = db.session.get(Cliente, test_cliente.id)

            ot = OrdenTrabajo(
                cliente_id=cliente.id,
                nro_ofic='OT-2024-001',
                codigo='OT-001',
                descripcion='Descripcion de prueba'
            )
            db.session.add(ot)
            db.session.commit()
            db.session.refresh(ot)

            assert ot.id is not None
            assert ot.nro_ofic == 'OT-2024-001'
            assert ot.codigo == 'OT-001'
            assert ot.descripcion == 'Descripcion de prueba'
            assert ot.cliente_id == cliente.id

            # Limpieza
            db.session.delete(ot)
            db.session.commit()

    def test_nro_ofic_unique_constraint(self, app, test_cliente):
        """Test que nro_ofic debe ser unico."""
        with app.app_context():
            cliente = db.session.get(Cliente, test_cliente.id)

            ot1 = OrdenTrabajo(
                cliente_id=cliente.id,
                nro_ofic='OT-UNIQUE-001',
                codigo='OT-U001'
            )
            db.session.add(ot1)
            db.session.commit()

            ot2 = OrdenTrabajo(
                cliente_id=cliente.id,
                nro_ofic='OT-UNIQUE-001',
                codigo='OT-U002'
            )
            db.session.add(ot2)

            with pytest.raises(IntegrityError):
                db.session.commit()

            db.session.rollback()

            # Limpieza
            db.session.delete(ot1)
            db.session.commit()

    def test_status_default_pendiente(self, app, test_cliente):
        """Test que el estado por defecto es PENDIENTE."""
        with app.app_context():
            cliente = db.session.get(Cliente, test_cliente.id)

            ot = OrdenTrabajo(
                cliente_id=cliente.id,
                nro_ofic='OT-DEFAULT-001',
                codigo='OT-D001'
            )
            db.session.add(ot)
            db.session.commit()
            db.session.refresh(ot)

            assert ot.status == OTStatus.PENDIENTE

            # Limpieza
            db.session.delete(ot)
            db.session.commit()

    # Relationship Tests
    def test_relacion_cliente(self, app, test_cliente):
        """Test relacion con cliente."""
        with app.app_context():
            cliente = db.session.get(Cliente, test_cliente.id)

            ot = OrdenTrabajo(
                cliente_id=cliente.id,
                nro_ofic='OT-REL-001',
                codigo='OT-R001'
            )
            db.session.add(ot)
            db.session.commit()
            db.session.refresh(ot)

            assert ot.cliente is not None
            assert ot.cliente.id == cliente.id
            assert ot.cliente.nombre == 'Cliente Test'

            # Limpieza
            db.session.delete(ot)
            db.session.commit()

    def test_relacion_pedidos(self, app, test_cliente, test_producto):
        """Test relacion con pedidos."""
        with app.app_context():
            cliente = db.session.get(Cliente, test_cliente.id)
            producto = db.session.get(Producto, test_producto.id)

            ot = OrdenTrabajo(
                cliente_id=cliente.id,
                nro_ofic='OT-PED-001',
                codigo='OT-P001'
            )
            db.session.add(ot)
            db.session.commit()

            pedido = Pedido(
                codigo='PED-REL-001',
                cliente_id=cliente.id,
                producto_id=producto.id,
                orden_trabajo_id=ot.id,
                status=PedidoStatus.PENDIENTE
            )
            db.session.add(pedido)
            db.session.commit()
            db.session.refresh(ot)

            assert ot.pedidos.count() == 1
            assert ot.pedidos.first().id == pedido.id

            # Limpieza
            db.session.delete(pedido)
            db.session.delete(ot)
            db.session.commit()

    # Property Tests
    def test_pedidos_count_property(self, app, test_cliente, test_producto):
        """Test propiedad pedidos_count."""
        with app.app_context():
            cliente = db.session.get(Cliente, test_cliente.id)
            producto = db.session.get(Producto, test_producto.id)

            ot = OrdenTrabajo(
                cliente_id=cliente.id,
                nro_ofic='OT-PC-001',
                codigo='OT-PC001'
            )
            db.session.add(ot)
            db.session.commit()

            assert ot.pedidos_count == 0

            pedido = Pedido(
                codigo='PED-PC-001',
                cliente_id=cliente.id,
                producto_id=producto.id,
                orden_trabajo_id=ot.id,
                status=PedidoStatus.PENDIENTE
            )
            db.session.add(pedido)
            db.session.commit()
            db.session.refresh(ot)

            assert ot.pedidos_count == 1

            # Limpieza
            db.session.delete(pedido)
            db.session.delete(ot)
            db.session.commit()

    def test_entradas_count_property(self, app, test_cliente):
        """Test propiedad entradas_count."""
        with app.app_context():
            cliente = db.session.get(Cliente, test_cliente.id)

            ot = OrdenTrabajo(
                cliente_id=cliente.id,
                nro_ofic='OT-EC-001',
                codigo='OT-EC001'
            )
            db.session.add(ot)
            db.session.commit()

            assert ot.entradas_count == 0

            # Limpieza
            db.session.delete(ot)
            db.session.commit()

    def test_progreso_calculation_empty(self, app, test_cliente):
        """Test progreso cuando no hay pedidos."""
        with app.app_context():
            cliente = db.session.get(Cliente, test_cliente.id)

            ot = OrdenTrabajo(
                cliente_id=cliente.id,
                nro_ofic='OT-PROG-001',
                codigo='OT-PROG001'
            )
            db.session.add(ot)
            db.session.commit()
            db.session.refresh(ot)

            assert ot.progreso == 0

            # Limpieza
            db.session.delete(ot)
            db.session.commit()

    def test_progreso_calculation_partial(self, app, test_cliente, test_producto):
        """Test progreso cuando algunos pedidos estan completados."""
        with app.app_context():
            cliente = db.session.get(Cliente, test_cliente.id)
            producto = db.session.get(Producto, test_producto.id)

            ot = OrdenTrabajo(
                cliente_id=cliente.id,
                nro_ofic='OT-PROG-002',
                codigo='OT-PROG002'
            )
            db.session.add(ot)
            db.session.commit()

            # Crear pedidos de prueba
            pedido1 = Pedido(
                codigo='PED-P1-001',
                cliente_id=cliente.id,
                producto_id=producto.id,
                orden_trabajo_id=ot.id,
                status=PedidoStatus.COMPLETADO
            )
            pedido2 = Pedido(
                codigo='PED-P1-002',
                cliente_id=cliente.id,
                producto_id=producto.id,
                orden_trabajo_id=ot.id,
                status=PedidoStatus.PENDIENTE
            )
            db.session.add_all([pedido1, pedido2])
            db.session.commit()
            db.session.refresh(ot)

            assert ot.progreso == 50

            # Limpieza
            db.session.delete(pedido1)
            db.session.delete(pedido2)
            db.session.delete(ot)
            db.session.commit()

    def test_progreso_calculation_complete(self, app, test_cliente, test_producto):
        """Test progreso cuando todos los pedidos estan completados."""
        with app.app_context():
            cliente = db.session.get(Cliente, test_cliente.id)
            producto = db.session.get(Producto, test_producto.id)

            ot = OrdenTrabajo(
                cliente_id=cliente.id,
                nro_ofic='OT-PROG-003',
                codigo='OT-PROG003'
            )
            db.session.add(ot)
            db.session.commit()

            # Crear pedidos completados
            pedido1 = Pedido(
                codigo='PED-P2-001',
                cliente_id=cliente.id,
                producto_id=producto.id,
                orden_trabajo_id=ot.id,
                status=PedidoStatus.COMPLETADO
            )
            pedido2 = Pedido(
                codigo='PED-P2-002',
                cliente_id=cliente.id,
                producto_id=producto.id,
                orden_trabajo_id=ot.id,
                status=PedidoStatus.COMPLETADO
            )
            db.session.add_all([pedido1, pedido2])
            db.session.commit()
            db.session.refresh(ot)

            assert ot.progreso == 100

            # Limpieza
            db.session.delete(pedido1)
            db.session.delete(pedido2)
            db.session.delete(ot)
            db.session.commit()

    # Status Workflow Tests
    def test_actualizar_estado_pendiente(self, app, test_cliente):
        """Test actualizar estado cuando no hay pedidos."""
        with app.app_context():
            cliente = db.session.get(Cliente, test_cliente.id)

            ot = OrdenTrabajo(
                cliente_id=cliente.id,
                nro_ofic='OT-AE-001',
                codigo='OT-AE001',
                status=OTStatus.EN_PROGRESO
            )
            db.session.add(ot)
            db.session.commit()

            ot.actualizar_estado()
            db.session.commit()

            assert ot.status == OTStatus.PENDIENTE

            # Limpieza
            db.session.delete(ot)
            db.session.commit()

    def test_actualizar_estado_en_progreso(self, app, test_cliente, test_producto):
        """Test actualizar estado cuando hay pedidos en progreso."""
        with app.app_context():
            cliente = db.session.get(Cliente, test_cliente.id)
            producto = db.session.get(Producto, test_producto.id)

            ot = OrdenTrabajo(
                cliente_id=cliente.id,
                nro_ofic='OT-AE-002',
                codigo='OT-AE002'
            )
            db.session.add(ot)
            db.session.commit()

            pedido = Pedido(
                codigo='PED-AE-001',
                cliente_id=cliente.id,
                producto_id=producto.id,
                orden_trabajo_id=ot.id,
                status=PedidoStatus.EN_PROCESO
            )
            db.session.add(pedido)
            db.session.commit()

            ot.actualizar_estado()
            db.session.commit()

            assert ot.status == OTStatus.EN_PROGRESO

            # Limpieza
            db.session.delete(pedido)
            db.session.delete(ot)
            db.session.commit()

    def test_actualizar_estado_completada(self, app, test_cliente, test_producto):
        """Test actualizar estado cuando todos los pedidos estan completados."""
        with app.app_context():
            cliente = db.session.get(Cliente, test_cliente.id)
            producto = db.session.get(Producto, test_producto.id)

            ot = OrdenTrabajo(
                cliente_id=cliente.id,
                nro_ofic='OT-AE-003',
                codigo='OT-AE003'
            )
            db.session.add(ot)
            db.session.commit()

            pedido = Pedido(
                codigo='PED-AE-002',
                cliente_id=cliente.id,
                producto_id=producto.id,
                orden_trabajo_id=ot.id,
                status=PedidoStatus.COMPLETADO
            )
            db.session.add(pedido)
            db.session.commit()

            ot.actualizar_estado()
            db.session.commit()

            assert ot.status == OTStatus.COMPLETADA

            # Limpieza
            db.session.delete(pedido)
            db.session.delete(ot)
            db.session.commit()

    def test_fech_completado_auto_set(self, app, test_cliente, test_producto):
        """Test que fech_completado se establece automaticamente al completar."""
        with app.app_context():
            cliente = db.session.get(Cliente, test_cliente.id)
            producto = db.session.get(Producto, test_producto.id)

            ot = OrdenTrabajo(
                cliente_id=cliente.id,
                nro_ofic='OT-FC-001',
                codigo='OT-FC001'
            )
            db.session.add(ot)
            db.session.commit()

            assert ot.fech_completado is None

            pedido = Pedido(
                codigo='PED-FC-001',
                cliente_id=cliente.id,
                producto_id=producto.id,
                orden_trabajo_id=ot.id,
                status=PedidoStatus.COMPLETADO
            )
            db.session.add(pedido)
            db.session.commit()

            ot.actualizar_estado()
            db.session.commit()

            assert ot.status == OTStatus.COMPLETADA
            assert ot.fech_completado is not None
            assert isinstance(ot.fech_completado, datetime)

            # Limpieza
            db.session.delete(pedido)
            db.session.delete(ot)
            db.session.commit()

    def test_fech_completado_auto_clear(self, app, test_cliente, test_producto):
        """Test que fech_completado se limpia al cambiar de completada."""
        with app.app_context():
            cliente = db.session.get(Cliente, test_cliente.id)
            producto = db.session.get(Producto, test_producto.id)

            ot = OrdenTrabajo(
                cliente_id=cliente.id,
                nro_ofic='OT-FC-002',
                codigo='OT-FC002',
                status=OTStatus.COMPLETADA,
                fech_completado=datetime.utcnow()
            )
            db.session.add(ot)
            db.session.commit()

            assert ot.fech_completado is not None

            # Agregar un pedido no completado
            pedido = Pedido(
                codigo='PED-FC-002',
                cliente_id=cliente.id,
                producto_id=producto.id,
                orden_trabajo_id=ot.id,
                status=PedidoStatus.PENDIENTE
            )
            db.session.add(pedido)
            db.session.commit()

            ot.actualizar_estado()
            db.session.commit()

            assert ot.status == OTStatus.EN_PROGRESO
            assert ot.fech_completado is None

            # Limpieza
            db.session.delete(pedido)
            db.session.delete(ot)
            db.session.commit()

    # Serialization Tests
    def test_to_dict_structure(self, app, test_cliente):
        """Test estructura del diccionario generado por to_dict."""
        with app.app_context():
            cliente = db.session.get(Cliente, test_cliente.id)

            ot = OrdenTrabajo(
                cliente_id=cliente.id,
                nro_ofic='OT-DICT-001',
                codigo='OT-DICT001',
                descripcion='OT de prueba'
            )
            db.session.add(ot)
            db.session.commit()
            db.session.refresh(ot)

            data = ot.to_dict()

            assert 'id' in data
            assert 'nro_ofic' in data
            assert 'codigo' in data
            assert 'cliente' in data
            assert 'descripcion' in data
            assert 'status' in data
            assert 'progreso' in data
            assert 'pedidos_count' in data
            assert 'entradas_count' in data
            assert 'fech_creacion' in data
            assert 'fech_completado' in data

            assert data['nro_ofic'] == 'OT-DICT-001'
            assert data['codigo'] == 'OT-DICT001'
            assert data['cliente'] == 'Cliente Test'
            assert data['descripcion'] == 'OT de prueba'
            assert data['status'] == OTStatus.PENDIENTE
            assert data['progreso'] == 0

            # Limpieza
            db.session.delete(ot)
            db.session.commit()

    def test_repr(self, app, test_cliente):
        """Test representacion string del modelo."""
        with app.app_context():
            cliente = db.session.get(Cliente, test_cliente.id)

            ot = OrdenTrabajo(
                cliente_id=cliente.id,
                nro_ofic='OT-REPR-001',
                codigo='OT-REPR001'
            )
            db.session.add(ot)
            db.session.commit()
            db.session.refresh(ot)

            assert repr(ot) == '<OrdenTrabajo OT-REPR-001>'

            # Limpieza
            db.session.delete(ot)
            db.session.commit()
