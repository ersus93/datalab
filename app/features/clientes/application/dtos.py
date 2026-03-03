"""
Feature: Clientes
Capa: Application - DTOs y Commands
Objetos de transferencia de datos desacoplados del dominio.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class CrearClienteCommand:
    codigo: str
    nombre: str
    ruc_ci: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None


@dataclass
class ActualizarClienteCommand:
    id: int
    nombre: str
    ruc_ci: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None


@dataclass
class ClienteDTO:
    id: int
    codigo: str
    nombre: str
    ruc_ci: Optional[str]
    telefono: Optional[str]
    email: Optional[str]
    direccion: Optional[str]
    activo: bool

    @classmethod
    def from_entity(cls, cliente) -> "ClienteDTO":
        return cls(
            id=cliente.id,
            codigo=cliente.codigo,
            nombre=cliente.nombre,
            ruc_ci=cliente.ruc_ci,
            telefono=cliente.telefono,
            email=cliente.email,
            direccion=cliente.direccion,
            activo=cliente.activo,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "codigo": self.codigo,
            "nombre": self.nombre,
            "ruc_ci": self.ruc_ci,
            "telefono": self.telefono,
            "email": self.email,
            "direccion": self.direccion,
            "activo": self.activo,
        }
