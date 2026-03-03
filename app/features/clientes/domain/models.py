"""
Feature: Clientes
Capa: Domain
Entidades puras de Python sin dependencias de frameworks.
"""
from dataclasses import dataclass, field
from typing import Optional

from app.core.domain.base import AuditMixin, Entity, ValidationError


@dataclass
class Cliente(Entity, AuditMixin):
    """Entidad de dominio: Cliente del laboratorio."""
    codigo: str = ""
    nombre: str = ""
    ruc_ci: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    activo: bool = True

    def __post_init__(self):
        self._validar()

    def _validar(self):
        if not self.codigo or not self.codigo.strip():
            raise ValidationError("El código del cliente es obligatorio.")
        if not self.nombre or not self.nombre.strip():
            raise ValidationError("El nombre del cliente es obligatorio.")
        if len(self.codigo) > 20:
            raise ValidationError("El código no puede superar 20 caracteres.")

    def activar(self):
        self.activo = True

    def desactivar(self):
        self.activo = False

    def actualizar_contacto(self, telefono: Optional[str], email: Optional[str]):
        self.telefono = telefono
        self.email = email
