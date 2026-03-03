"""
Core Domain - Shared Kernel
Clases base para todas las entidades del dominio DataLab.
Sin dependencias de Flask, SQLAlchemy ni ningún framework.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar

T = TypeVar("T")


@dataclass
class Entity:
    """Clase base para todas las entidades del dominio."""
    id: Optional[int] = field(default=None, compare=False)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.id is not None and self.id == other.id


@dataclass
class AuditMixin:
    """Mixin para auditoría (quién y cuándo creó/modificó)."""
    creado_en: Optional[datetime] = field(default=None, compare=False)
    modificado_en: Optional[datetime] = field(default=None, compare=False)
    creado_por: Optional[str] = field(default=None, compare=False)


class DomainException(Exception):
    """Excepción base del dominio."""
    pass


class NotFoundError(DomainException):
    """Recurso no encontrado."""
    def __init__(self, entity: str, identifier: Any):
        super().__init__(f"{entity} con identificador '{identifier}' no encontrado.")


class ValidationError(DomainException):
    """Error de validación de reglas de negocio."""
    def __init__(self, message: str):
        super().__init__(message)


class Repository(ABC, Generic[T]):
    """Interfaz base (port) para todos los repositorios."""

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        ...

    @abstractmethod
    def save(self, entity: T) -> T:
        ...

    @abstractmethod
    def delete(self, entity_id: int) -> None:
        ...

    @abstractmethod
    def list_all(self) -> List[T]:
        ...
