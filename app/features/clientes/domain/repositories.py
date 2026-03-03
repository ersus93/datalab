"""
Feature: Clientes
Capa: Domain - Ports (Interfaces)
Define el contrato que deben cumplir los adaptadores de persistencia.
"""
from abc import abstractmethod
from typing import List, Optional

from app.core.domain.base import Repository
from app.features.clientes.domain.models import Cliente


class ClienteRepository(Repository[Cliente]):
    """Port: Interfaz del repositorio de clientes."""

    @abstractmethod
    def get_by_codigo(self, codigo: str) -> Optional[Cliente]:
        """Busca un cliente por su código único."""
        ...

    @abstractmethod
    def search(self, nombre: str = "", activo: Optional[bool] = None) -> List[Cliente]:
        """Búsqueda flexible de clientes."""
        ...

    @abstractmethod
    def exists_by_codigo(self, codigo: str) -> bool:
        """Verifica si ya existe un cliente con ese código."""
        ...
