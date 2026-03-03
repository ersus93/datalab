"""
Feature: Clientes
Capa: Application - Queries (Read Operations)
Consultas optimizadas para lectura.
"""
from typing import List, Optional

from app.core.domain.base import NotFoundError
from app.features.clientes.application.dtos import ClienteDTO
from app.features.clientes.domain.repositories import ClienteRepository


class ObtenerClienteQuery:
    """Query: Obtener un cliente por ID."""

    def __init__(self, repo: ClienteRepository):
        self.repo = repo

    def execute(self, cliente_id: int) -> ClienteDTO:
        cliente = self.repo.get_by_id(cliente_id)
        if not cliente:
            raise NotFoundError("Cliente", cliente_id)
        return ClienteDTO.from_entity(cliente)


class ListarClientesQuery:
    """Query: Listar todos los clientes con filtros opcionales."""

    def __init__(self, repo: ClienteRepository):
        self.repo = repo

    def execute(
        self, nombre: str = "", solo_activos: bool = True
    ) -> List[ClienteDTO]:
        activo = True if solo_activos else None
        clientes = self.repo.search(nombre=nombre, activo=activo)
        return [ClienteDTO.from_entity(c) for c in clientes]
