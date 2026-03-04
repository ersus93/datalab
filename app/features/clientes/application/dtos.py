"""
Feature: Clientes
Capa: Application
DTOs (Data Transfer Objects) para comandos y queries.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class CrearClienteCommand:
    """Comando para crear un nuevo cliente."""
    codigo: str
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    organismo_id: Optional[int] = None
    tipo_cliente: Optional[int] = None


@dataclass
class ActualizarClienteCommand:
    """Comando para actualizar un cliente existente."""
    id: int
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    organismo_id: Optional[int] = None
    tipo_cliente: Optional[int] = None


@dataclass
class ClienteDTO:
    """DTO de salida con datos del cliente."""
    id: int
    codigo: str
    nombre: str
    email: Optional[str]
    telefono: Optional[str]
    direccion: Optional[str]
    activo: bool
    organismo_id: Optional[int]
    tipo_cliente: Optional[int]
