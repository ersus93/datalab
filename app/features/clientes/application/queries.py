"""
Feature: Clientes
Capa: Application
Handlers para queries (CQRS - Query side).
"""
from typing import List, Optional

from app.core.domain.base import NotFoundError
from app.features.clientes.application.dtos import ClienteDTO


class ObtenerClienteQuery:
    """Query para obtener un cliente por ID."""

    def __init__(self, repository):
        self._repo = repository

    def execute(self, cliente_id: int) -> ClienteDTO:
        """Obtener cliente por ID."""
        cliente = self._repo.get_by_id(cliente_id)
        if not cliente:
            raise NotFoundError("Cliente", cliente_id)

        return ClienteDTO(
            id=cliente.id,
            codigo=cliente.codigo,
            nombre=cliente.nombre,
            email=cliente.email,
            telefono=cliente.telefono,
            direccion=cliente.direccion,
            activo=cliente.activo,
            organismo_id=cliente.organismo_id,
            tipo_cliente=cliente.tipo_cliente,
        )


class ListarClientesQuery:
    """Query para listar clientes con filtros."""

    def __init__(self, repository):
        self._repo = repository

    def execute(
        self,
        nombre: str = "",
        solo_activos: bool = False
    ) -> List[ClienteDTO]:
        """Listar clientes filtrados."""
        activo = True if solo_activos else None
        clientes = self._repo.search(nombre=nombre, activo=activo)

        return [
            ClienteDTO(
                id=c.id,
                codigo=c.codigo,
                nombre=c.nombre,
                email=c.email,
                telefono=c.telefono,
                direccion=c.direccion,
                activo=c.activo,
                organismo_id=c.organismo_id,
                tipo_cliente=c.tipo_cliente,
            )
            for c in clientes
        ]
