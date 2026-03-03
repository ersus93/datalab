"""
Tests unitarios: Feature Clientes
Sin base de datos real - usa repositorios falsos (mocks).
Demuestra la principal ventaja de la arquitectura hexagonal.
"""
import pytest
from typing import Dict, List, Optional

from app.core.domain.base import NotFoundError, ValidationError
from app.features.clientes.application.commands import (
    CrearClienteHandler,
    ActualizarClienteHandler,
    DesactivarClienteHandler,
)
from app.features.clientes.application.dtos import (
    CrearClienteCommand,
    ActualizarClienteCommand,
)
from app.features.clientes.application.queries import (
    ObtenerClienteQuery,
    ListarClientesQuery,
)
from app.features.clientes.domain.models import Cliente
from app.features.clientes.domain.repositories import ClienteRepository


# ──────────────────────────────────────────────────────────────
# Fake Repository (sin base de datos)
# ──────────────────────────────────────────────────────────────
class FakeClienteRepository(ClienteRepository):
    """Repositorio en memoria para tests unitarios."""

    def __init__(self):
        self._store: Dict[int, Cliente] = {}
        self._next_id = 1

    def get_by_id(self, entity_id: int) -> Optional[Cliente]:
        return self._store.get(entity_id)

    def get_by_codigo(self, codigo: str) -> Optional[Cliente]:
        for c in self._store.values():
            if c.codigo == codigo:
                return c
        return None

    def exists_by_codigo(self, codigo: str) -> bool:
        return any(c.codigo == codigo for c in self._store.values())

    def search(self, nombre: str = "", activo: Optional[bool] = None) -> List[Cliente]:
        results = list(self._store.values())
        if nombre:
            results = [c for c in results if nombre.lower() in c.nombre.lower()]
        if activo is not None:
            results = [c for c in results if c.activo == activo]
        return results

    def save(self, cliente: Cliente) -> Cliente:
        if cliente.id is None:
            cliente.id = self._next_id
            self._next_id += 1
        self._store[cliente.id] = cliente
        return cliente

    def delete(self, entity_id: int) -> None:
        self._store.pop(entity_id, None)

    def list_all(self) -> List[Cliente]:
        return self.search()


# ──────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────

class TestCrearCliente:
    def test_crear_cliente_exitoso(self):
        repo = FakeClienteRepository()
        handler = CrearClienteHandler(repo)
        cmd = CrearClienteCommand(codigo="CLI001", nombre="Empresa XYZ S.A.")

        dto = handler.handle(cmd)

        assert dto.id is not None
        assert dto.codigo == "CLI001"
        assert dto.nombre == "Empresa XYZ S.A."
        assert dto.activo is True

    def test_crear_cliente_codigo_duplicado_lanza_error(self):
        repo = FakeClienteRepository()
        handler = CrearClienteHandler(repo)
        cmd = CrearClienteCommand(codigo="CLI001", nombre="Empresa 1")
        handler.handle(cmd)

        with pytest.raises(ValidationError, match="CLI001"):
            handler.handle(CrearClienteCommand(codigo="CLI001", nombre="Empresa 2"))

    def test_crear_cliente_sin_codigo_lanza_error(self):
        with pytest.raises(ValidationError):
            Cliente(codigo="", nombre="Sin Código")

    def test_crear_cliente_sin_nombre_lanza_error(self):
        with pytest.raises(ValidationError):
            Cliente(codigo="CLI002", nombre="")

    def test_crear_cliente_codigo_muy_largo_lanza_error(self):
        with pytest.raises(ValidationError):
            Cliente(codigo="C" * 21, nombre="Empresa")


class TestActualizarCliente:
    def test_actualizar_cliente_exitoso(self):
        repo = FakeClienteRepository()
        # Setup
        crear = CrearClienteHandler(repo)
        dto = crear.handle(CrearClienteCommand(codigo="CLI001", nombre="Nombre Viejo"))

        actualizar = ActualizarClienteHandler(repo)
        resultado = actualizar.handle(
            ActualizarClienteCommand(
                id=dto.id,
                nombre="Nombre Nuevo",
                telefono="099-123-456",
            )
        )

        assert resultado.nombre == "Nombre Nuevo"
        assert resultado.telefono == "099-123-456"

    def test_actualizar_cliente_inexistente_lanza_error(self):
        repo = FakeClienteRepository()
        handler = ActualizarClienteHandler(repo)

        with pytest.raises(NotFoundError):
            handler.handle(ActualizarClienteCommand(id=999, nombre="No Existe"))


class TestDesactivarCliente:
    def test_desactivar_cliente_exitoso(self):
        repo = FakeClienteRepository()
        crear = CrearClienteHandler(repo)
        dto = crear.handle(CrearClienteCommand(codigo="CLI001", nombre="Empresa"))

        desactivar = DesactivarClienteHandler(repo)
        resultado = desactivar.handle(dto.id)

        assert resultado.activo is False

    def test_desactivar_cliente_inexistente_lanza_error(self):
        repo = FakeClienteRepository()
        handler = DesactivarClienteHandler(repo)

        with pytest.raises(NotFoundError):
            handler.handle(999)


class TestListarClientes:
    def test_listar_solo_activos(self):
        repo = FakeClienteRepository()
        crear = CrearClienteHandler(repo)
        dto1 = crear.handle(CrearClienteCommand(codigo="CLI001", nombre="Empresa A"))
        dto2 = crear.handle(CrearClienteCommand(codigo="CLI002", nombre="Empresa B"))
        DesactivarClienteHandler(repo).handle(dto2.id)

        query = ListarClientesQuery(repo)
        activos = query.execute(solo_activos=True)

        assert len(activos) == 1
        assert activos[0].codigo == "CLI001"

    def test_filtrar_por_nombre(self):
        repo = FakeClienteRepository()
        crear = CrearClienteHandler(repo)
        crear.handle(CrearClienteCommand(codigo="CLI001", nombre="Laboratorio Central"))
        crear.handle(CrearClienteCommand(codigo="CLI002", nombre="Farmacia Norte"))

        query = ListarClientesQuery(repo)
        resultados = query.execute(nombre="labora", solo_activos=True)

        assert len(resultados) == 1
        assert "Central" in resultados[0].nombre
