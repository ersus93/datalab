"""
Feature: Clientes
Capa: Domain
Entidades puras de Python para el dominio de clientes.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.core.domain.base import AuditMixin, Entity, ValidationError


@dataclass
class Cliente(Entity, AuditMixin):
    """Entidad de dominio: Cliente del laboratorio."""
    codigo: str = ""
    nombre: str = ""
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    activo: bool = True
    organismo_id: Optional[int] = None
    tipo_cliente: Optional[int] = None

    def __post_init__(self):
        self._validar()

    def _validar(self):
        if not self.codigo:
            raise ValidationError("El código del cliente es obligatorio.")
        if not self.nombre:
            raise ValidationError("El nombre del cliente es obligatorio.")
        if len(self.codigo) > 20:
            raise ValidationError("El código no puede exceder 20 caracteres.")
        if len(self.nombre) > 200:
            raise ValidationError("El nombre no puede exceder 200 caracteres.")

    def desactivar(self):
        """Desactivar cliente (soft delete)."""
        self.activo = False

    def activar(self):
        """Activar cliente."""
        self.activo = True

    @property
    def esta_activo(self) -> bool:
        """Verificar si el cliente está activo."""
        return self.activo
