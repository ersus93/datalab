"""
Feature: Clientes
Capa: Domain
Puerto (interfaz) del repositorio de clientes.
"""
from abc import abstractmethod
from typing import List, Optional

from app.core.domain.base import Repository
from app.features.clientes.domain.models import Cliente


class ClienteRepository(Repository[Cliente]):
    """Interfaz del repositorio de clientes (puerto del dominio)."""

    @abstractmethod
    def get_by_codigo(self, codigo: str) -> Optional[Cliente]:
        """Obtener cliente por su código único."""
        ...

    @abstractmethod
    def exists_by_codigo(self, codigo: str) -> bool:
        """Verificar si existe un cliente con el código dado."""
        ...

    @abstractmethod
    def search(
        self,
        nombre: str = "",
        activo: Optional[bool] = None
    ) -> List[Cliente]:
        """Buscar clientes por nombre y/o estado."""
        ...
